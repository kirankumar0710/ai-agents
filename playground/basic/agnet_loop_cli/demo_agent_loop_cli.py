#!/usr/bin/env python3
import anthropic
import sys

from lib import key
from lib import config
from tools import calculator as calc
from tools import weather
from tools import fileops
from tools import websearch

try:
    cfg = config.load_config()
    api_key_path = cfg.require("claude.api.key_file")
    api_key = key.load_api_key(api_key_path)
except (FileNotFoundError, PermissionError, ValueError) as e:
    print(f"Error: {e}", file=sys.stderr)
    sys.exit(1)

client = anthropic.Anthropic(api_key=api_key)


# Tools definintion

tools = [
    {
        "name": "web_search",
        "description": (
            "Search the web for current information. "
            "Use for facts, news, prices, or anything requiring up-to-date data."
        ),
        "input_schema": {
            "type": "object",
            "properties": {"query": {"type": "string", "description": "Search query"}},
            "required": ["query"],
        },
    },
    {
        "name": "calculator",
        "description": "Evaluate mathematical expressions. Supports +, -, *, /, **, sqrt, etc.",
        "input_schema": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "Expression to evaluate",
                }
            },
            "required": ["expression"],
        },
    },
    {
        "name": "write_file",
        "description": "Write text content to a file. Use to save results, reports, or summaries.",
        "input_schema": {
            "type": "object",
            "properties": {
                "filename": {"type": "string"},
                "content": {"type": "string"},
            },
            "required": ["filename", "content"],
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
]


def execute_tool(name: str, inputs: dict) -> str:
    handlers = {
        "web_search": websearch.web_search,
        "calculator": calc.calculator,
        "write_file": fileops.write_file,
        "get_weather": weather.get_weather,
    }

    handler = handlers.get(name)
    return handler(**inputs) if handler else f"Unknown tool: {name}"


def run_agent(query: str) -> str:
    messages = [{"role": "user", "content": query}]

    print(f"\n🤖 Agent starting...")

    for i in range(15):
        response = client.messages.create(
            model="claude-opus-4-5",
            max_tokens=4096,
            tools=tools,
            system=(
                "You are a research assistant agent. "
                "Use tools to find information, calculate, and save results. "
                "Always save important findings to files when asked."
            ),
            messages=messages,
        )

        messages.append({"role": "assistant", "content": response.content})

        if response.stop_reason == "end_turn":
            return next((b.text for b in response.content if hasattr(b, "text")), "")

        if response.stop_reason == "tool_use":
            results = []
            for block in response.content:
                if block.type == "tool_use":
                    print(
                        f"  🔧 {block.name}({list(block.input.values())[0][:50]}...)"
                        if block.input
                        else f"  🔧 {block.name}"
                    )
                    result = execute_tool(block.name, block.input)
                    print(f"  ✓  {result[:80]}...")
                    results.append(
                        {
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": result,
                        }
                    )
            messages.append({"role": "user", "content": results})

    return "Max iterations reached"


def main():
    print("🚀 CLI Agent — Claude + Tool Use")
    print("Type 'quit' to exit\n")

    while True:
        query = input("You: ").strip()
        if query.lower() in ("quit", "exit", "q"):
            break
        if not query:
            continue

        result = run_agent(query)
        print(f"\nAgent: {result}\n")
        print("\n" + "=" * 80)


if __name__ == "__main__":
    main()
