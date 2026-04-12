import anthropic
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage, SystemMessage
from langchain_anthropic import ChatAnthropic
from langchain_core.tools import tool
import json

from tools import calculator as calc
from tools import fileops
from tools import websearch

# export ANTHROPIC_API_KEY


# ─── 1. Define State ──────────────────────────────────────────────
class AgentState(TypedDict):
    messages: Annotated[list, add_messages]


# ─── 2. Tools ──────────────────────────────────────────────
tool_list = [websearch.web_search_tool, calc.calculator_tool, fileops.write_file_tool]
tools_by_name = {t.name: t for t in tool_list}

# ─── 3. LLM with tools bound ──────────────────────────────────────
llm = ChatAnthropic(model="claude-sonnet-4-20250514")
llm_with_tools = llm.bind_tools(tool_list)


# ─── 4. Node functions ────────────────────────────────────────────
def call_claude(state: AgentState) -> dict:
    """Claude node: calls the LLM, returns message to append."""
    response = llm_with_tools.invoke(state["messages"])
    return {"messages": [response]}


def run_tools(state: AgentState) -> dict:
    """Tool node: executes all tool calls from the last AI message."""
    last_message = state["messages"][-1]
    tool_results = []

    for tool_call in last_message.tool_calls:
        tool_name = tool_call["name"]
        tool_args = tool_call["args"]

        print(f"\n🔧 Calling tool: {tool_name}")
        print(f"   Args: {tool_args}")

        result = tools_by_name[tool_name].invoke(tool_args)

        print(f"   Result: {result}")

        tool_results.append(
            ToolMessage(
                content=str(result), tool_call_id=tool_call["id"], name=tool_name
            )
        )

    return {"messages": tool_results}


# ─── 5. Routing function (the brain of the graph) ─────────────────
def should_continue(state: AgentState) -> str:
    """Decide: keep going (more tool calls) or we're done."""
    last_message = state["messages"][-1]

    # If the last message has tool_calls, go to tools
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "continue"

    # Otherwise Claude gave a final text answer → done
    return "end"


# ─── 6. Build the graph ───────────────────────────────────────────
def build_agent():
    graph = StateGraph(AgentState)

    graph.add_node("claude", call_claude)
    graph.add_node("tools", run_tools)

    graph.set_entry_point("claude")

    graph.add_conditional_edges(
        "claude", should_continue, {"continue": "tools", "end": END}
    )

    # After tools always go back to Claude
    graph.add_edge("tools", "claude")

    return graph.compile()


# ─── 7. Run it ────────────────────────────────────────────────────
if __name__ == "__main__":
    app = build_agent()

    # Stream mode — see each step as it happens
    print("=" * 50)
    print("LangGraph Agent Starting")
    print("=" * 50)

    inputs = {
        "messages": [
            SystemMessage(
                content="You are a helpful research assistant. Use tools when needed."
            ),
            HumanMessage(
                content="Search for the latest Python version, then calculate 3.12 * 1000, and save a summary to 'python_summary.txt'"
            ),
        ]
    }

    for step in app.stream(inputs, stream_mode="values"):
        last_msg = step["messages"][-1]
        msg_type = type(last_msg).__name__
        print(f"\n[{msg_type}]")
        if hasattr(last_msg, "content") and last_msg.content:
            print(last_msg.content[:200])

    print("\n✅ Agent finished")
