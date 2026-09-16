import os
import httpx
from typing import Optional
from backend.app.tools.base import BaseTool, ToolResult
from backend.app.security.permissions import PermissionLevel
from backend.app.core.logging import logger

class GitHubSearchReposTool(BaseTool):
    name = "github_search_repos"
    description = "Searches public GitHub repositories by topic or query."
    category = "GitHub"
    permission_level = PermissionLevel.SAFE
    parameters = {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Search query for repositories"}
        },
        "required": ["query"]
    }

    async def execute(self, query: str, **kwargs) -> ToolResult:
        try:
            token = os.getenv("GITHUB_TOKEN")
            headers = {"Accept": "application/vnd.github.v3+json", "User-Agent": "JARVIS-Assistant"}
            if token:
                headers["Authorization"] = f"token {token}"

            async with httpx.AsyncClient(timeout=15.0) as client:
                res = await client.get(f"https://api.github.com/search/repositories?q={query}&per_page=5", headers=headers)
                if res.status_code == 200:
                    items = res.json().get("items", [])
                    repos = [
                        {
                            "name": item["full_name"],
                            "description": item["description"],
                            "stars": item["stargazers_count"],
                            "url": item["html_url"]
                        }
                        for item in items
                    ]
                    return ToolResult(success=True, data={"repos": repos}, message=f"Found {len(repos)} GitHub repositories")
                return ToolResult(success=False, error=f"GitHub API status {res.status_code}: {res.text}")
        except Exception as e:
            return ToolResult(success=False, error=str(e))

class GitHubCreateIssueTool(BaseTool):
    name = "github_create_issue"
    description = "Creates a new issue in a GitHub repository (requires GITHUB_TOKEN)."
    category = "GitHub"
    permission_level = PermissionLevel.CONFIRM
    parameters = {
        "type": "object",
        "properties": {
            "repo": {"type": "string", "description": "Repository in 'owner/repo' format"},
            "title": {"type": "string", "description": "Issue title"},
            "body": {"type": "string", "description": "Issue description / body"}
        },
        "required": ["repo", "title"]
    }

    async def execute(self, repo: str, title: str, body: Optional[str] = "", **kwargs) -> ToolResult:
        token = os.getenv("GITHUB_TOKEN")
        if not token:
            return ToolResult(success=False, error="GITHUB_TOKEN is not set in environment. Authenticate first.")

        headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "JARVIS-Assistant"
        }
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                res = await client.post(f"https://api.github.com/repos/{repo}/issues", headers=headers, json={"title": title, "body": body})
                if res.status_code in [200, 201]:
                    data = res.json()
                    return ToolResult(success=True, data={"issue_url": data.get("html_url"), "number": data.get("number")}, message=f"Created issue #{data.get('number')}")
                return ToolResult(success=False, error=f"Failed to create issue: {res.text}")
        except Exception as e:
            return ToolResult(success=False, error=str(e))
