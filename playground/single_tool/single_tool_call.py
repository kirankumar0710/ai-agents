import anthropic
import sys
from lib import key
from tools import calculator as cal

try:
    api_key = key.load_api_key("../../../../key/claude_api_key.txt")
except (FileNotFoundError, PermissionError, ValueError) as e:
    print(f"Error: {e}")
    sys.exit(1)

client = anthropic.Anthropic(api_key=api_key)

# Define a tool — this is just a JSON schema
# Claude reads this and decides when/how to call it
#
# name        = critical — choose it carefully, it carries the most weight
# description = important — needed when name alone is ambiguous e.g. "process_data"
# property    = format guide — tells Claude how to structure the input
tools = [
    {
        "name": "calculator",
        "description": "Performs basic arithmetic. Use this when you need to compute numbers.",
        "input_schema": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "Math expression to evaluate, e.g. '(23 * 4) + 17'",
                }
            },
            "required": ["expression"],
        },
    }
]

# =================================================================================
# HOW TOOL CALLING WORKS (2 API calls required)
#
# Call 1:  Claude reads the question, decides to use a tool, tells you what to run
#          You → Claude   "I have 347 boxes, each has 28 items, and there are 4521 loose items too. Total?"
#          Claude → You   "Use calculator with '347 * 28 + 4521'"
#                          Claude STOPS here. Waits for tool result.
#
# YOU run the tool locally and get the result.
#
# Call 2:  You send the tool result back, Claude forms the final answer
#          You → Claude   "Here's the tool result: 14237"
#          Claude → You   "The answer is 14237"
# ---------------------------------------------------------------------------------
# Claude's only role is:
#   Natural language → structured JSON
#   "I have 347 boxes..."  →  { "expression": "347 * 28 + 4521" }
#
# Claude did 3 things:
#   1. Understood the user's natural language question
#   2. Decided which tool to use (calculator)
#   3. Extracted the expression into correct JSON format
#
# The actual math? Pure Python eval() — nothing to do with Claude.
# =================================================================================

# User message stored once — reused in both API calls to avoid mismatch
user_message = (
    "I have 347 boxes, each has 28 items, and there are 4521 loose items too. Total?"
)

# -------------------------------------------------------------
# CALL 1 — Send user question, Claude decides to use a tool
# -------------------------------------------------------------
response = client.messages.create(
    model="claude-opus-4-5",
    max_tokens=1024,
    tools=tools,
    messages=[{"role": "user", "content": user_message}],
)

print("Stop reason:", response.stop_reason)  # tool_use
print("Response content:", response.content)

# Extract what Claude decided
tool_use_block = next(b for b in response.content if b.type == "tool_use")
tool_name = tool_use_block.name  # "calculator"  — Claude picked this
tool_input = (
    tool_use_block.input
)  # {"expression": "347 * 28 + 4521"} — Claude extracted this
tool_use_id = tool_use_block.id

print(f"\nClaude wants to call: {tool_name}")
print(f"With input: {tool_input}")

# YOU execute the tool Claude picked — Claude cannot run code itself
if tool_name == "calculator":
    tool_result = cal.calculator(tool_input["expression"])
print(f"Tool result: {tool_result}")

# -------------------------------------------------------------
# CALL 2 — Send tool result back, Claude forms final answer
#
# Claude is stateless — no memory between calls.
# Must re-send full conversation history:
#   - user_message          (repeated — Claude has no memory)
#   - response.content      (call 1 reply — what Claude said)
#   - tool_result           (new — what your code computed)
# -------------------------------------------------------------
final_response = client.messages.create(
    model="claude-opus-4-5",
    max_tokens=1024,
    tools=tools,
    messages=[
        {"role": "user", "content": user_message},  # repeated — no memory
        {"role": "assistant", "content": response.content},  # call 1 response
        {
            "role": "user",
            "content": [
                {
                    "type": "tool_result",
                    "tool_use_id": tool_use_id,
                    "content": tool_result,  # new — tool output
                }
            ],
        },
    ],
)

print("\nFinal answer:", final_response.content[0].text)
