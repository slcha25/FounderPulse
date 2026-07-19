import asyncio
from datetime import datetime, timezone

from tavily import TavilyClient

from .. import config

_client = TavilyClient(api_key=config.TAVILY_API_KEY)


async def search(query: str, max_results: int = 4) -> list[dict]:
    try:
        result = await asyncio.to_thread(
            _client.search, query=query, max_results=max_results, search_depth="basic"
        )
    except Exception:
        return []
    return result.get("results", [])


async def extract(url: str) -> str:
    try:
        result = await asyncio.to_thread(_client.extract, urls=[url])
    except Exception:
        return ""
    items = result.get("results", [])
    if items:
        return items[0].get("raw_content", "") or ""
    return ""


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()
