# Solves questions that require multiple retrieval steps to answer.
# Step 1 — retrieve broadly on the original question.
# Step 2 — Claude reasons over the docs and identifies what's still missing.
# Step 3 — retrieve again on the follow-up gap question.
# Step 4 — combine all docs and produce a final answer.
# Important: a single retrieval often fails for complex questions
# because the answer isn't in one document — it spans multiple facts.

import json
from langgraph.graph import StateGraph, END
from langchain_anthropic import ChatAnthropic
from typing import TypedDict, List
from tools import retrieve

llm = ChatAnthropic(model="claude-opus-4-5")


# State is passed between nodes — every node reads and updates this dict.
class State(TypedDict):
    question: str
    docs: List[str]  # accumulates across both retrieval hops
    reasoning: str  # the follow-up question Claude generates
    answer: str


def retrieve_step(state: State) -> State:
    # First hop — broad search on the original question
    results = retrieve.retrieve_tool.invoke(state["question"])
    print(
        f"\n\n------------------------- [retrieve 1] -------------------------\n{results}"
    )
    return {**state, "docs": [results]}


def reason_step(state: State) -> State:
    # Claude reads the first hop docs and identifies what's still missing.
    # The output is a focused follow-up query for the second hop.
    context = "\n".join(state["docs"])
    prompt = f"""Given these docs:
{context}

Original question: {state['question']}

Using the context above, reason step by step to answer the question. 
Connect facts across the context even if no single sentence states the answer directly.
Give a confident answer based on what can be reasonably inferred."""

    follow_up = llm.invoke(prompt).content
    print(
        f"\n\n------------------------- [reason] Follow-up query: -------------------------\n{follow_up}"
    )
    return {**state, "reasoning": follow_up}


def retrieve_again(state: State) -> State:
    # Second hop — focused search on the gap Claude identified above.
    # Appends to docs so the final answer has context from both hops.
    more = retrieve.retrieve_tool.invoke(state["reasoning"])
    print(
        f"\n\n------------------------- [retrieve 2] -------------------------\n{more}"
    )
    return {**state, "docs": state["docs"] + [more]}


def answer_step(state: State) -> State:
    # Final step — combine all retrieved docs and generate the answer.
    all_context = "\n\n".join(state["docs"])
    prompt = f"""Context:
{all_context}

Answer this question using only the context above: {state['question']}"""
    answer = llm.invoke(prompt).content
    return {**state, "answer": answer}


# Wire the nodes into a linear graph: retrieve → reason → retrieve → answer
graph = StateGraph(State)
graph.add_node("retrieve1", retrieve_step)
graph.add_node("reason", reason_step)
graph.add_node("retrieve2", retrieve_again)
graph.add_node("answer", answer_step)

graph.set_entry_point("retrieve1")
graph.add_edge("retrieve1", "reason")
graph.add_edge("reason", "retrieve2")
graph.add_edge("retrieve2", "answer")
graph.add_edge("answer", END)

app = graph.compile()

result = app.invoke(
    {
        "question": "Who founded the company that provides RLHF services for GPT-4?",
        "docs": [],
        "reasoning": "",
        "answer": "",
    }
)

print(f"\n\n------------------------- Final output -------------------------\n")
print(result["answer"])
