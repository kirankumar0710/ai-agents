# AI Agents

Learning and building AI agents using Claude (Anthropic).

## Structure

| Folder | Purpose |
|--------|---------|
| `lib/` | Reusable utilities — key loading, auth, config loading |
| `tools/` | Tool implementations — calculator, weather, fileops |
| `playground/` | Learning experiments — basic tools, RAG, memory, agents, MCP |
| `projects/` | Production work |

## Playground

| Folder | What it covers |
|--------|---------------|
| `basic/single_tool/` | One tool, basic call 1 → execute → call 2 cycle |
| `basic/multi_tool/` | Multiple tools, routing by tool_name |
| `basic/agent_loop_cli/` | Interactive agent loop with CLI, weather + file tools |
| `rag/` | RAG pipeline — chunking, retrieval, cross-encoder reranking, query rewrite, multi-hop, RAGAS eval |
| `memory/` | In-context memory, external DB memory, LangGraph memory store |
| `multiagent/` | LangGraph parallel agents, supervisor/subagent pattern |
| `langgraph/` | LangGraph basics, human-in-the-loop travel planner |
| `mcp/` | MCP server implementation and inspector usage |

Export them before running:

```bash
export CONFIG_FILE=$HOME/projects/ai-agents/playground/config.json
export CLAUDE_API_KEY_FILE=/path/to/your/claude_api.key
```

## Concepts Covered

- Tool calling — Claude decides, you execute
- Tool routing — multiple tools, Claude picks the right one
- Stateless calls — why full history is re-sent every call
- ReAct pattern — Thought → Action → Observation loop

## Setup

1. Clone the repo
```
   git clone https://github.com/yourname/ai-agent.git
   cd ai-agent
```

2. Create virtual environment
```
   python3 -m venv venv
```

3. Activate virtual environment
```
   source venv/bin/activate        # Mac / Linux
   venv\Scripts\activate           # Windows
```

4. Install dependencies
```
   python3 -m pip install -r requirements.txt
```

5. Install dev tools
```
   python3 -m pip install -r requirements-dev.txt
```

6. Install project as package (run once)
```
   python3 -m pip install -e .
```

7. Add your API key — store it outside this repo
```
   /path/to/keys/claude_api_key.txt
```

## VS Code Extensions (install these)

- Python          (ms-python.python)
- Black Formatter (ms-python.black-formatter)
- Pylint          (ms-python.pylint)
- Ruff            (charliermarsh.ruff)
- Claude Code     (anthropic.claude-code)
