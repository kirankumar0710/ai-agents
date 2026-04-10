#!/usr/bin/env python3
import anthropic
import sys

from lib import key
from lib import config
from tools import calculator as calc
from tools import weather
from tools import fileops

user_messages = [
    "I have 347 boxes, each has 28 items, and there are 4521 loose items too. Total?",
    "what is weather in Bengaluru",
    "write to file output.txt - content: Hello from Claude!",
]

try:
    cfg = config.load_config()
    api_key_path = cfg.require("claude.api.key_file")
    api_key = key.load_api_key(api_key_path)
except (FileNotFoundError, PermissionError, ValueError) as e:
    print(f"Error: {e}", file=sys.stderr)
    sys.exit(1)

client = anthropic.Anthropic(api_key=api_key)

# --- Tool Definitions ---
tools = [
    {
        "name": "calculator",
        "description": "Evaluates math expressions. Use for any arithmetic or calculations.",
        "input_schema": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "Math expression e.g. '2 ** 10'",
                }
            },
            "required": ["expression"],
        },
    },
    {
        "name": "get_weather",
        "description": "Gets current weather for a city. Returns temperature and conditions.",
        "input_schema": {
            "type": "object",
            "properties": {
                "city": {"type": "string", "description": "City name e.g. 'London'"}
            },
            "required": ["city"],
        },
    },
    {
        "name": "write_file",
        "description": "Writes text content to a file on disk.",
        "input_schema": {
            "type": "object",
            "properties": {
                "filename": {
                    "type": "string",
                    "description": "File path e.g. 'output.txt'",
                },
                "content": {"type": "string", "description": "Text content to write"},
            },
            "required": ["filename", "content"],
        },
    },
]


# --- Tool Router ---
def execute_tool(tool_name: str, tool_input: dict) -> str:
    """Routes tool calls to their implementations"""
    if tool_name == "calculator":
        return calc.calculator(**tool_input)
    elif tool_name == "get_weather":
        return weather.get_weather(**tool_input)
    elif tool_name == "write_file":
        return fileops.write_file(**tool_input)
    else:
        return f"Unknown tool: {tool_name}"


for message in user_messages:
    response = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=1024,
        tools=tools,
        messages=[{"role": "user", "content": message}],
    )

    # Extract what Claude decided
    tool_use_block = next((b for b in response.content if b.type == "tool_use"), None)
    if tool_use_block is None:
        print("Claude did not call a tool:", response.content)
        continue

    tool_name = tool_use_block.name  # "calculator"  — Claude picked this
    tool_input = (
        tool_use_block.input
    )  # {"expression": "347 * 28 + 4521"} — Claude extracted this
    tool_use_id = tool_use_block.id

    print(f"\nClaude wants to call: {tool_name}")
    print(f"With input: {tool_input}")

    tool_result = execute_tool(tool_name, tool_input)

    # Only set system prompt for weather responses
    system_prompt = (
        "Always use relevant emojis when presenting weather data."
        if tool_name == "get_weather"
        else anthropic.NOT_GIVEN
    )

    final_response = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=1024,
        # pass system parameter only for weather
        system=system_prompt,
        tools=tools,
        messages=[
            {"role": "user", "content": message},  # repeated — no memory
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

    text_block = next((b for b in final_response.content if b.type == "text"), None)
    print("\nFinal answer:", text_block.text if text_block else "(no text response)")
