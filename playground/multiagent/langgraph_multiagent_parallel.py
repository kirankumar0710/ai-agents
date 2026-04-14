import anthropic
import operator
from langgraph.graph import StateGraph, END
from langgraph.types import Send
from typing import TypedDict, Annotated

from textwrap import dedent

# ── Token Budget Configuration ─────────────────────────────────────────────
# IMPORTANT: max_tokens is a hard ceiling — Claude stops mid-sentence when hit.
# If output appears truncated, check response.stop_reason == "max_tokens".
#
# Rule of thumb: 1 token ≈ 4 characters
#   - Researchers: each gets its own budget (parallel, so cost is not additive)
#   - Synthesizer: needs more headroom — it ingests all researcher outputs combined
#
# To diagnose truncation:
#   if response.stop_reason == "max_tokens":
#       print(f"⚠️  Truncated! Increase max_tokens.")
#
RESEARCHER_MAX_TOKENS = 1024
NUMBER_OF_RESEARCHER = 3
SYNTHESIZER_MAX_TOKENS = RESEARCHER_MAX_TOKENS * NUMBER_OF_RESEARCHER


client = anthropic.Anthropic()


# ── State ──────────────────────────────────────────────────────────────────
class ParallelState(TypedDict):
    task: str
    # Annotated with operator.add = reducer that APPENDS concurrent writes
    # Without this, parallel nodes overwrite each other silently
    research_outputs: Annotated[list[str], operator.add]
    final_synthesis: str


# ── Parallel worker nodes ──────────────────────────────────────────────────

# ─────────────────────────────────────────────────────────────
# LANGGRAPH PARALLEL NODES — RETURN TYPE RULES
#
# ❌ WRONG: -> FullState
#
#   Parallel nodes must NOT return the full state type.
#   Two problems:
#
#   1. RACE CONDITION
#      All parallel nodes run concurrently. If each does
#      {**state, "field": my_value}, whichever finishes last
#      wins and silently overwrites the others.
#      The reducer is bypassed entirely.
#
#   2. MISLEADING INTENT
#      Returning full state forces you to carry fields you
#      don't own, making the node's responsibility unclear.
#
# ✅ CORRECT: -> dict
#
#   Return only the field(s) this node owns.
#   LangGraph passes the partial dict to the reducer:
#       Annotated[list, operator.add]
#   which APPENDS contributions from all parallel nodes
#   safely into shared state.
#
#   Rule: one parallel node → one owned field → one dict key.
# ─────────────────────────────────────────────────────────────


def tech_researcher(state: ParallelState) -> dict:
    print("⚙️  Tech researcher running...")
    response = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=RESEARCHER_MAX_TOKENS,
        messages=[
            {
                "role": "user",
                "content": f"Research the TECHNICAL aspects only: {state['task']}",
            }
        ],
    )
    # Return only the field this node owns — reducer merges it in
    return {"research_outputs": [f"[TECH]\n{response.content[0].text}"]}


def business_researcher(state: ParallelState) -> dict:
    print("💼  Business researcher running...")
    response = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=RESEARCHER_MAX_TOKENS,
        messages=[
            {
                "role": "user",
                "content": f"Research the BUSINESS and market aspects only: {state['task']}",
            }
        ],
    )
    return {"research_outputs": [f"[BUSINESS]\n{response.content[0].text}"]}


def risk_researcher(state: ParallelState) -> dict:
    print("⚠️  Risk researcher running...")
    response = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=RESEARCHER_MAX_TOKENS,
        messages=[
            {
                "role": "user",
                "content": f"Research RISKS, challenges, and limitations only: {state['task']}",
            }
        ],
    )
    return {"research_outputs": [f"[RISKS]\n{response.content[0].text}"]}


# ── Fan-out function — this IS the parallelism mechanism ──────────────────
def fan_out(state: ParallelState) -> list[Send]:
    """
    Returns a list of Send() objects.
    LangGraph spawns each as a concurrent branch.
    Each Send carries its own state slice — workers are independent.
    """
    return [
        Send(
            "tech_researcher",
            {"task": state["task"], "research_outputs": [], "final_synthesis": ""},
        ),
        Send(
            "business_researcher",
            {"task": state["task"], "research_outputs": [], "final_synthesis": ""},
        ),
        Send(
            "risk_researcher",
            {"task": state["task"], "research_outputs": [], "final_synthesis": ""},
        ),
    ]


# ── Join node — runs AFTER all branches complete ──────────────────────────
def synthesizer(state: ParallelState) -> dict:
    """
    LangGraph holds here until every Send() branch finishes.
    By this point, research_outputs has all 3 results merged by the reducer.
    """
    print(
        f"🔗  Synthesizer — received {len(state['research_outputs'])} research outputs"
    )

    combined = "\n\n".join(state["research_outputs"])

    prompt = dedent(
        f"""
        Synthesize these research perspectives into one coherent report:
                    
        {combined}

        Topic: {state['task']}
    """
    )

    response = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=SYNTHESIZER_MAX_TOKENS,
        messages=[{"role": "user", "content": prompt}],
    )
    return {"final_synthesis": response.content[0].text}


# ── Build the graph ────────────────────────────────────────────────────────
def build_graph():
    builder = StateGraph(ParallelState)

    builder.add_node("tech_researcher", tech_researcher)
    builder.add_node("business_researcher", business_researcher)
    builder.add_node("risk_researcher", risk_researcher)
    builder.add_node("synthesizer", synthesizer)

    # Fan-out edge: one conditional edge fans into N concurrent Send()s
    builder.add_conditional_edges(
        "__start__",  # LangGraph's built-in entry node
        fan_out,
        [
            "tech_researcher",
            "business_researcher",
            "risk_researcher",
        ],  # possible targets
    )

    # All branches converge to synthesizer — LangGraph waits for all
    builder.add_edge("tech_researcher", "synthesizer")
    builder.add_edge("business_researcher", "synthesizer")
    builder.add_edge("risk_researcher", "synthesizer")

    builder.add_edge("synthesizer", END)

    return builder.compile()


# ── Run ────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    graph = build_graph()

    result = graph.invoke(
        {
            "task": "Using LangGraph for production AI agents",
            "research_outputs": [],
            "final_synthesis": "",
        }
    )

    print("\n=== SYNTHESIS ===")
    synres = result.get("final_synthesis")
    print(f"\n Result Len: {len(synres)} chars\n")

    synoutfile = "synthesis_output.md"
    print(f"\n Synthesis output file: {synoutfile}\n")

    # NOTE: Do not print() large synthesis outputs directly to terminal —
    # non-printable characters and length cause silent truncation.
    with open(synoutfile, "w", encoding="utf-8") as f:
        f.write(result["final_synthesis"])
