# langgraph_memory.py
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage
from typing import TypedDict, Annotated
import operator


# State definition
class AgentState(TypedDict):
    messages: Annotated[list, operator.add]
    user_id: str


llm = ChatAnthropic(model="claude-opus-4-5")


def chat_node(state: AgentState) -> AgentState:
    system = SystemMessage(
        content="You are a helpful assistant with persistent memory."
    )
    response = llm.invoke([system] + state["messages"])
    return {"messages": [response]}


# Build graph
builder = StateGraph(AgentState)
builder.add_node("chat", chat_node)
builder.set_entry_point("chat")
builder.add_edge("chat", END)

# MemorySaver = in-memory checkpointing (swap with SqliteSaver for persistence)
memory = MemorySaver()
graph = builder.compile(checkpointer=memory)


def chat_with_memory(user_input: str, thread_id: str = "thread_1"):
    """thread_id is the session identifier — same thread = same memory"""
    config = {"configurable": {"thread_id": thread_id}}

    result = graph.invoke(
        {"messages": [HumanMessage(content=user_input)], "user_id": "kiran_k_saravana"},
        config=config,
    )
    return result["messages"][-1].content


# Same thread_id = continuous memory
print(chat_with_memory("I'm building a travel agent.", thread_id="session_42"))
print(chat_with_memory("What am I building?", thread_id="session_42"))  # Remembers!
print(chat_with_memory("Hello, who are you?", thread_id="new_session"))  # Fresh memory
