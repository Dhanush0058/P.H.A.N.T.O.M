import webbrowser
import httpx
import re
from typing import Optional
from duckduckgo_search import DDGS
from backend.app.tools.base import BaseTool, ToolResult
from backend.app.security.permissions import PermissionLevel
from backend.app.core.logging import logger

class OpenBrowserTool(BaseTool):
    name = "open_browser"
    description = "Opens a URL in the user's default web browser."
    category = "Browser"
    permission_level = PermissionLevel.SAFE
    parameters = {
        "type": "object",
        "properties": {
            "url": {"type": "string", "description": "URL to navigate to (e.g. 'https://github.com')"}
        },
        "required": ["url"]
    }

    async def execute(self, url: str, **kwargs) -> ToolResult:
        try:
            if not url.startswith("http://") and not url.startswith("https://"):
                url = f"https://{url}"
            webbrowser.open(url)
            return ToolResult(success=True, data={"url": url}, message=f"Opened browser at {url}")
        except Exception as e:
            return ToolResult(success=False, error=str(e))

class SearchWebTool(BaseTool):
    name = "search_web"
    description = "Performs a live web search using DuckDuckGo to obtain up-to-date information, news, or answers."
    category = "Browser"
    permission_level = PermissionLevel.SAFE
    parameters = {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Search query keywords"},
            "max_results": {"type": "integer", "description": "Number of results to retrieve (default 5)"}
        },
        "required": ["query"]
    }

    async def execute(self, query: str, max_results: int = 5, **kwargs) -> ToolResult:
        try:
            logger.info(f"Web search for: '{query}'")
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=max_results))
            return ToolResult(
                success=True,
                data={"query": query, "results": results},
                message=f"Retrieved {len(results)} search results for '{query}'"
            )
        except Exception as e:
            logger.error(f"Search failed: {str(e)}")
            return ToolResult(success=False, error=str(e))

class GetPageContentTool(BaseTool):
    name = "get_page_content"
    description = "Fetches and extracts clean readable text from a given web page URL."
    category = "Browser"
    permission_level = PermissionLevel.SAFE
    parameters = {
        "type": "object",
        "properties": {
            "url": {"type": "string", "description": "Web page URL to fetch text from"}
        },
        "required": ["url"]
    }

    async def execute(self, url: str, **kwargs) -> ToolResult:
        try:
            if not url.startswith("http://") and not url.startswith("https://"):
                url = f"https://{url}"
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
            async with httpx.AsyncClient(timeout=20.0, follow_redirects=True) as client:
                res = await client.get(url, headers=headers)
                res.raise_for_status()
                html = res.text

            # Simple clean regex parser
            cleaned = re.sub(r'<(script|style).*?</\1>', '', html, flags=re.DOTALL | re.IGNORECASE)
            cleaned = re.sub(r'<[^>]+>', ' ', cleaned)
            cleaned = re.sub(r'\s+', ' ', cleaned).strip()
            summary = cleaned[:3000]

            return ToolResult(success=True, data={"url": url, "text": summary}, message=f"Extracted text from {url}")
        except Exception as e:
            return ToolResult(success=False, error=str(e))
