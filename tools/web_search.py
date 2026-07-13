"""web_search.py
Tool used by the Research Agent to fetch fresh, real-world info from the web."""


import os
from dotenv import load_dotenv
from tavily import TavilyClient

load_dotenv()

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")


def web_search(query: str, max_results: int = 3) -> list[dict]:
    if not TAVILY_API_KEY:
        raise ValueError("TAVILY_API_KEY not found in .env file")

    client = TavilyClient(api_key=TAVILY_API_KEY)

    response = client.search(
        query=query,
        max_results=max_results,
        search_depth="basic",
    )

    results = []
    for item in response.get("results", []):
        results.append({
            "title": item.get("title"),
            "url": item.get("url"),
            "snippet": item.get("content"),
        })

    return results


if __name__ == "__main__":
    query = "latest developments in multi-agent AI systems"
    results = web_search(query)

    print(f"\nFound {len(results)} results for: '{query}'\n")
    for i, r in enumerate(results, 1):
        print(f"{i}. {r['title']}")
        print(f"   {r['url']}")
        print(f"   {r['snippet']}\n")