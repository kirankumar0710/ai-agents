import requests


def web_search(query: str) -> str:
    """Uses DuckDuckGo Instant Answer API (free, no key needed)"""
    try:
        resp = requests.get(
            "https://api.duckduckgo.com/",
            params={"q": query, "format": "json", "no_html": 1},
            timeout=5,
        )
        data = resp.json()

        # Extract best available answer
        if data.get("AbstractText"):
            return data["AbstractText"][:500]
        elif data.get("Answer"):
            return data["Answer"]
        elif data.get("RelatedTopics"):
            topics = [
                t.get("Text", "")
                for t in data["RelatedTopics"][:3]
                if isinstance(t, dict)
            ]
            return " | ".join(topics)[:500]
        else:
            return f"No direct answer found for: {query}. Try rephrasing."
    except Exception as e:
        return f"Search error: {e}"
