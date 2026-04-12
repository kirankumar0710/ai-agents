from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage


from tools import flight
from tools import hotel

# export ANTHROPIC_API_KEY


# ─── State ────────────────────────────────────────────────────────
class TripState(TypedDict):
    messages: Annotated[list, add_messages]
    pending_bookings: list  # Track what's about to be booked


# ─── Tools ────────────────────────────────────────────────────────

tool_list = [
    flight.mock_search_flights,
    hotel.mock_search_hotels,
    flight.mock_book_flight,
    hotel.mock_book_hotel,
]
tools_by_name = {t.name: t for t in tool_list}

BOOKING_TOOLS = {"mock_book_flight", "mock_book_hotel"}  # These need human approval


# ─── LLM ──────────────────────────────────────────────────────────
llm = ChatAnthropic(model="claude-sonnet-4-20250514")
llm_with_tools = llm.bind_tools(tool_list)

SYSTEM_PROMPT = """You are an expert travel agent. Help users plan and book trips.
1. Always search for flights AND hotels before recommending
2. Present options clearly with prices
3. Ask for confirmation before booking — say "I'll proceed to book X" before calling booking tools
4. After booking, provide a clear summary"""


# ─── Nodes ────────────────────────────────────────────────────────
def call_claude(state: TripState) -> dict:
    messages = [SystemMessage(content=SYSTEM_PROMPT)] + state["messages"]
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}


def run_tools(state: TripState) -> dict:
    last_message = state["messages"][-1]
    results = []

    for tc in last_message.tool_calls:
        print(f"  🔧 {tc['name']}({tc['args']})")
        result = tools_by_name[tc["name"]].invoke(tc["args"])
        results.append(
            ToolMessage(content=str(result), tool_call_id=tc["id"], name=tc["name"])
        )

    return {"messages": results}


def should_continue(state: TripState) -> str:
    last = state["messages"][-1]
    if hasattr(last, "tool_calls") and last.tool_calls:
        # Check if any upcoming tool call is a booking action
        for tc in last.tool_calls:
            if tc["name"] in BOOKING_TOOLS:
                return "booking"  # Route to booking path (will be interrupted)
        return "tools"  # Safe search tools, run without interruption
    return "end"


# ─── Graph ────────────────────────────────────────────────────────
def build_trip_agent():
    graph = StateGraph(TripState)

    graph.add_node("claude", call_claude)
    graph.add_node("tools", run_tools)
    graph.add_node("booking", run_tools)  # Same function, separate node for interrupt

    graph.set_entry_point("claude")

    graph.add_conditional_edges(
        "claude",
        should_continue,
        {
            "tools": "tools",  # searches → run freely
            "booking": "booking",  # bookings → will be interrupted
            "end": END,
        },
    )
    graph.add_edge("tools", "claude")
    graph.add_edge("booking", "claude")

    memory = MemorySaver()

    return graph.compile(
        checkpointer=memory,
        interrupt_before=["booking"],  # Only pause before booking actions
    )


# ─── CLI Runner ───────────────────────────────────────────────────
def run_trip_planner():
    app = build_trip_agent()
    config = {"configurable": {"thread_id": "trip-session-1"}}

    print("\n🌍 Trip Planner Agent")
    print("=" * 50)
    print("Type your travel request. Type 'quit' to exit.\n")

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() == "quit":
            break

        state_input = {"messages": [HumanMessage(content=user_input)]}

        # Run until interrupt or end
        interrupted = False
        for step in app.stream(state_input, config=config, stream_mode="values"):
            last = step["messages"][-1]

            if (
                hasattr(last, "content")
                and last.content
                and not getattr(last, "tool_calls", None)
            ):
                if type(last).__name__ == "AIMessage":
                    print(f"\nAgent: {last.content}\n")

        # Check if we're paused at a booking node
        state = app.get_state(config)
        if state.next and "booking" in state.next:
            interrupted = True
            last_ai = [
                m for m in state.values["messages"] if type(m).__name__ == "AIMessage"
            ][-1]

            print("\n⏸️  BOOKING APPROVAL REQUIRED")
            print("-" * 35)
            for tc in last_ai.tool_calls:
                print(f"  Action: {tc['name']}")
                for k, v in tc["args"].items():
                    print(f"  {k}: {v}")
            print("-" * 35)

            approval = input("Approve booking? (y/n): ").strip().lower()

            if approval == "y":
                print("▶ Proceeding with booking...\n")
                for step in app.stream(None, config=config, stream_mode="values"):
                    last = step["messages"][-1]
                    if type(last).__name__ == "AIMessage":
                        if last.content and not last.tool_calls:  # empty list = falsy
                            print(f"Agent: {last.content}\n")
            else:
                # Update state to tell Claude booking was rejected
                app.update_state(
                    config,
                    {
                        "messages": [
                            HumanMessage(
                                content="The user rejected the booking. Acknowledge this and ask if they want to modify the selection."
                            )
                        ]
                    },
                    as_node="claude",
                )
                for step in app.stream(None, config=config, stream_mode="values"):
                    last = step["messages"][-1]

                    if type(last).__name__ == "AIMessage":
                        if last.content and not last.tool_calls:  # empty list = falsy
                            print(f"Agent: {last.content}\n")


if __name__ == "__main__":
    run_trip_planner()
