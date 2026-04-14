import requests
import httpx
from langchain_core.tools import tool

WEB_SERVER_ULR = "https://api.duckduckgo.com/"


def _build_params(query: str) -> dict:
    return {"q": query, "format": "json", "no_html": 1}


def _parse_response(data: dict, query: str) -> str:
    if data.get("AbstractText"):
        return data["AbstractText"][:500]
    elif data.get("Answer"):
        return data["Answer"]
    elif data.get("RelatedTopics"):
        topics = [
            t.get("Text", "") for t in data["RelatedTopics"][:3] if isinstance(t, dict)
        ]
        return " | ".join(topics)[:500]
    return f"No direct answer found for: {query}. Try rephrasing."


def web_search(query: str) -> str:
    """Synchronous - Uses DuckDuckGo Instant Answer API (free, no key needed)"""
    try:
        resp = requests.get(
            WEB_SERVER_ULR,
            params=_build_params(query),
            timeout=5,
        )

        return _parse_response(resp.json(), query)
    except Exception as e:
        return f"Search error: {e}"


async def web_search_async(query: str) -> str:
    """Asynchronous DuckDuckGo search."""
    try:
        async with httpx.AsyncClient() as http:
            resp = await http.get(
                WEB_SERVER_ULR, params=_build_params(query), timeout=5
            )
            return _parse_response(resp.json(), query)
    except Exception as e:
        return f"Search error: {e}"


@tool
def web_search_tool(query: str) -> str:
    """Search the web for current information on a topic."""
    return web_search(query)
