# langgrap_multi_agent_supervisor_subagent.py
import anthropic
import json
from typing import TypedDict, Literal
from langgraph.graph import StateGraph, END
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

client = anthropic.Anthropic()
llm = ChatAnthropic(model="claude-opus-4-5")


# ── State ──────────────────────────────────────────────
class MultiAgentState(TypedDict):
    task: str  # Original user task
    plan: str  # Supervisor's plan
    research_output: str  # From researcher agent
    written_output: str  # From writer agent
    next_agent: str  # Supervisor routing decision
    final_output: str  # Combined result
    iteration: int  # Guard against infinite loops


# ── Supervisor Agent ────────────────────────────────────
SUPERVISOR_SYSTEM = """You are a supervisor agent that routes tasks to specialized sub-agents.

Sub-agents available:
- researcher: Searches and gathers information, facts, data
- writer: Takes research and writes polished content
- finish: Task is complete, return final output

Given the current state, decide which agent should act next.
Respond ONLY with valid JSON: {"next": "researcher"|"writer"|"finish", "reasoning": "..."}
"""


def supervisor_node(state: MultiAgentState) -> MultiAgentState:
    print(f"\n🎯 SUPERVISOR — iteration {state['iteration']}")

    context = f"""
Task: {state['task']}
Research done: {state.get('research_output', 'None yet')}
Writing done: {state.get('written_output', 'None yet')}

Who should act next?
"""

    response = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=256,
        system=SUPERVISOR_SYSTEM,
        messages=[{"role": "user", "content": context}],
    )

    raw = response.content[0].text.strip()

    try:
        decision = json.loads(raw)
    except json.JSONDecodeError:
        # Fallback parsing
        if "researcher" in raw:
            decision = {"next": "researcher", "reasoning": "Parsed from text"}
        elif "writer" in raw:
            decision = {"next": "writer", "reasoning": "Parsed from text"}
        else:
            decision = {"next": "finish", "reasoning": "Defaulting to finish"}

    print(f"   Decision: {decision['next']} — {decision['reasoning']}")

    return {
        **state,
        "next_agent": decision["next"],
        "plan": decision.get("reasoning", ""),
        "iteration": state["iteration"] + 1,
    }


# ── Researcher Sub-Agent ────────────────────────────────
RESEARCHER_SYSTEM = """You are a research specialist. 
Given a task, produce thorough, factual research with key points, data, and insights.
Structure your output clearly with sections."""


def researcher_node(state: MultiAgentState) -> MultiAgentState:
    print(f"\n🔍 RESEARCHER — working on: {state['task'][:60]}...")

    response = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=1024,
        system=RESEARCHER_SYSTEM,
        messages=[
            {
                "role": "user",
                "content": f"Research this topic thoroughly: {state['task']}",
            }
        ],
    )

    research = response.content[0].text
    # print(f"   Research complete ({len(research)} chars)")

    print(
        f"""
    Research complete:
    Length: ({len(research)} chars)
    Content:
    {research[:500]}...
    """
    )
    print(f"{' END OF RESEARCH ':█^80}")

    return {**state, "research_output": research}


# ── Writer Sub-Agent ────────────────────────────────────
WRITER_SYSTEM = """You are a professional writer.
Given research notes, write polished, engaging, well-structured content.
Make it clear, compelling, and ready to publish."""


def writer_node(state: MultiAgentState) -> MultiAgentState:
    print(f"\n✍️  WRITER — drafting from research...")

    prompt = f"""
Task: {state['task']}

Research notes:
{state.get('research_output', 'No research available')}

Write a polished response based on this research.
"""

    response = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=1024,
        system=WRITER_SYSTEM,
        messages=[{"role": "user", "content": prompt}],
    )

    written = response.content[0].text
    # print(f"   Writing complete ({len(written)} chars)")

    print(
        f"""
    Research complete:
    Length: ({len(written)} chars)
    Content:
    {written[:500]}...
    """
    )
    print(f"{' END OF WRITE ':█^80}")

    return {**state, "written_output": written, "final_output": written}


# ── Routing Logic ────────────────────────────────────────
def route_supervisor(
    state: MultiAgentState,
) -> Literal["researcher", "writer", "finish"]:
    """Conditional edge — supervisor decides where to go"""
    next_agent = state.get("next_agent", "finish")

    # Safety: prevent infinite loops
    if state["iteration"] >= 6:
        print("   ⚠️  Max iterations reached, finishing")
        return "finish"

    return next_agent


# ── Build the Graph ──────────────────────────────────────
def build_multi_agent_graph():
    builder = StateGraph(MultiAgentState)

    # Add all nodes
    builder.add_node("supervisor", supervisor_node)
    builder.add_node("researcher", researcher_node)
    builder.add_node("writer", writer_node)

    # Entry point
    builder.set_entry_point("supervisor")

    # Supervisor routes conditionally
    builder.add_conditional_edges(
        "supervisor",
        route_supervisor,
        {"researcher": "researcher", "writer": "writer", "finish": END},
    )

    # Sub-agents always return to supervisor
    builder.add_edge("researcher", "supervisor")
    builder.add_edge("writer", "supervisor")

    return builder.compile()


# ── Run it ───────────────────────────────────────────────
def run_multi_agent(task: str) -> str:
    graph = build_multi_agent_graph()

    initial_state = MultiAgentState(
        task=task,
        plan="",
        research_output="",
        written_output="",
        next_agent="",
        final_output="",
        iteration=0,
    )

    print(f"\n{'='*60}")
    print(f"TASK: {task}")
    print(f"{'='*60}")

    result = graph.invoke(initial_state)

    print(f"\n{'='*60}")
    print("FINAL OUTPUT:")
    print(f"{'='*60}")
    print(result["final_output"])

    return result["final_output"]


if __name__ == "__main__":
    final_output = run_multi_agent(
        "Write a short guide on the top 3 benefits of LangGraph for production AI agents"
    )

    print(
        f"""
    Final:
    Length: ({len(final_output)} chars)
    Content:
    {final_output}
    """
    )

    print(f"{' END OF FINAL ':█^80}")
