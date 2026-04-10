# AI Agent

Learning and building AI agents using Claude (Anthropic).

## Structure

| Folder | Purpose |
|--------|---------|
| `lib/` | Reusable utilities — key loading, auth |
| `tools/` | Tool implementations — calculator, weather, fileops |
| `playground/` | Learning experiments — single tool, multi tool |
| `projects/` | Production work |

## Playground

| Folder | What it covers |
|--------|---------------|
| `single_tool/` | One tool, basic call 1 → execute → call 2 cycle |
| `multi_tool/` | Multiple tools, routing by tool_name |

## Concepts Covered

- Tool calling — Claude decides, you execute
- Tool routing — multiple tools, Claude picks the right one
- Stateless calls — why full history is re-sent every call
- ReAct pattern — Thought → Action → Observation loop

## Setup

1. Clone the repo
   git clone https://github.com/yourname/ai-agent.git
   cd ai-agent

2. Create virtual environment
   python3 -m venv venv

3. Activate virtual environment
   source venv/bin/activate        # Mac / Linux
   venv\Scripts\activate           # Windows

4. Install dependencies
   pip install -r requirements.txt

5. Install dev tools
   pip install -r requirements-dev.txt

6. Install project as package (run once)
   pip install -e .

7. Add your API key — store it outside this repo
   /path/to/keys/claude_api_key.txt

## VS Code Extensions (install these)

- Python          (ms-python.python)
- Black Formatter (ms-python.black-formatter)
- Pylint          (ms-python.pylint)
- Ruff            (charliermarsh.ruff)
- Claude Code     (anthropic.claude-code)
