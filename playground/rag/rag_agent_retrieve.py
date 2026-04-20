# Creates a ReAct agent that has retrieve() as an optional tool.
# The agent reasons first — if it already knows the answer it responds directly.
# If it needs external knowledge it calls retrieve(), reads the docs, then answers.
# This is the core shift from vanilla RAG (always retrieves) to agentic RAG (retrieves only when needed).

from langchain.agents import create_agent

# from langgraph.prebuilt import create_react_agent
from langchain_anthropic import ChatAnthropic
from tools import retrieve

llm = ChatAnthropic(model="claude-sonnet-4-6")

agent = create_agent(llm, tools=[retrieve.retrieve_tool])

# Claude knows 2+2 — will NOT call retrieve()
result = agent.invoke({"messages": [("user", "What is 2 + 2?")]})
print(result["messages"][-1].content)

# Claude doesn't know this from training — WILL call retrieve()
result = agent.invoke({"messages": [("user", "Who founded Scale AI?")]})
print(result["messages"][-1].content)
