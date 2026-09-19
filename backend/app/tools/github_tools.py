import os
import subprocess
import httpx
from typing import Optional, List, Dict
from backend.app.tools.base import BaseTool, ToolResult
from backend.app.security.permissions import PermissionLevel
from backend.app.core.logging import logger

def get_default_github_user() -> str:
    """Detects GitHub username from environment, git config, or default workspace repo."""
    user = os.getenv("GITHUB_USERNAME")
    if user:
        return user
    try:
        res = subprocess.run(["git", "config", "user.name"], capture_output=True, text=True, timeout=3)
        if res.returncode == 0 and res.stdout.strip():
            return res.stdout.strip()
    except Exception:
        pass
    try:
        res = subprocess.run(["git", "remote", "get-url", "origin"], capture_output=True, text=True, timeout=3)
        if res.returncode == 0 and "github.com" in res.stdout:
            parts = res.stdout.strip().replace(".git", "").split("github.com/")
            if len(parts) > 1:
                return parts[1].split("/")[0]
    except Exception:
        pass
    return "Dhanush0058"

class GitHubSearchReposTool(BaseTool):
    name = "github_search_repos"
    description = "Searches GitHub repositories. If searching for the user's own repos, set user_only to true or specify username."
    category = "GitHub"
    permission_level = PermissionLevel.SAFE
    parameters = {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Search query keywords or repo name"},
            "username": {"type": "string", "description": "Filter by GitHub username (defaults to the current user Dhanush0058 if searching personal repos)"},
            "user_only": {"type": "boolean", "description": "Whether to search only the user's personal repositories (default true if user mentioned 'my repo')"}
        },
        "required": ["query"]
    }

    async def execute(self, query: str, username: Optional[str] = None, user_only: bool = False, **kwargs) -> ToolResult:
        try:
            token = os.getenv("GITHUB_TOKEN")
            headers = {"Accept": "application/vnd.github.v3+json", "User-Agent": "PHANTOM-Assistant"}
            if token:
                headers["Authorization"] = f"token {token}"

            user_target = username or get_default_github_user()
            search_query = query.strip()
            
            # If user_only or query indicates personal repository
            if user_only or any(w in search_query.lower() for w in ["my", "mine", "personal", "own"]):
                clean_q = search_query
                for w in ["my repo", "my github", "my repositories", "my"]:
                    clean_q = clean_q.replace(w, "").strip()
                search_query = f"user:{user_target} {clean_q}".strip() if clean_q else f"user:{user_target}"

            async with httpx.AsyncClient(timeout=15.0) as client:
                res = await client.get(f"https://api.github.com/search/repositories?q={search_query}&per_page=10", headers=headers)
                if res.status_code == 200:
                    items = res.json().get("items", [])
                    repos = [
                        {
                            "name": item["full_name"],
                            "description": item.get("description") or "No description",
                            "stars": item.get("stargazers_count", 0),
                            "language": item.get("language"),
                            "url": item["html_url"]
                        }
                        for item in items
                    ]
                    return ToolResult(
                        success=True,
                        data={"repos": repos, "target_user": user_target},
                        message=f"Found {len(repos)} GitHub repositories for query '{search_query}'"
                    )
                return ToolResult(success=False, error=f"GitHub API status {res.status_code}: {res.text}")
        except Exception as e:
            return ToolResult(success=False, error=str(e))

class GitHubGetUserReposTool(BaseTool):
    name = "github_get_user_repos"
    description = "Fetches the complete list of all public GitHub repositories owned by the user (e.g. Dhanush0058)."
    category = "GitHub"
    permission_level = PermissionLevel.SAFE
    parameters = {
        "type": "object",
        "properties": {
            "username": {"type": "string", "description": "GitHub username (defaults to user Dhanush0058 if omitted)"},
            "include_forks": {"type": "boolean", "description": "Whether to include forked repositories (default true)"}
        }
    }

    async def execute(self, username: Optional[str] = None, include_forks: bool = True, **kwargs) -> ToolResult:
        try:
            target_user = username or get_default_github_user()
            token = os.getenv("GITHUB_TOKEN")
            headers = {"Accept": "application/vnd.github.v3+json", "User-Agent": "PHANTOM-Assistant"}
            if token:
                headers["Authorization"] = f"token {token}"

            all_repos = []
            async with httpx.AsyncClient(timeout=20.0) as client:
                for page in range(1, 4):  # Fetch up to 300 repositories across pages
                    res = await client.get(
                        f"https://api.github.com/users/{target_user}/repos?sort=updated&per_page=100&page={page}",
                        headers=headers
                    )
                    if res.status_code == 200:
                        items = res.json()
                        if not items:
                            break
                        for item in items:
                            if not include_forks and item.get("fork"):
                                continue
                            all_repos.append({
                                "name": item["name"],
                                "full_name": item["full_name"],
                                "description": item.get("description") or "No description",
                                "language": item.get("language") or "N/A",
                                "stars": item.get("stargazers_count", 0),
                                "forks": item.get("forks_count", 0),
                                "url": item["html_url"],
                                "updated_at": item.get("updated_at")
                            })
                        if len(items) < 100:
                            break
                    else:
                        break

            repo_names = [r["name"] for r in all_repos]
            return ToolResult(
                success=True,
                data={"total_count": len(all_repos), "username": target_user, "repositories": all_repos, "repository_names": repo_names},
                message=f"Found {len(all_repos)} repositories for user '{target_user}': {', '.join(repo_names)}"
            )
        except Exception as e:
            return ToolResult(success=False, error=str(e))

class GitHubGetRepoContentTool(BaseTool):
    name = "github_get_repo_content"
    description = "Fetches file content or README from a specific GitHub repository (e.g. repo='Dhanush0058/P.H.A.N.T.O.M', path='README.md')."
    category = "GitHub"
    permission_level = PermissionLevel.SAFE
    parameters = {
        "type": "object",
        "properties": {
            "repo": {"type": "string", "description": "Repository in 'owner/repo' format (e.g. 'Dhanush0058/P.H.A.N.T.O.M')"},
            "path": {"type": "string", "description": "File path to read (default 'README.md')"}
        },
        "required": ["repo"]
    }

    async def execute(self, repo: str, path: str = "README.md", **kwargs) -> ToolResult:
        import base64
        try:
            token = os.getenv("GITHUB_TOKEN")
            headers = {"Accept": "application/vnd.github.v3+json", "User-Agent": "PHANTOM-Assistant"}
            if token:
                headers["Authorization"] = f"token {token}"

            clean_repo = repo.strip()
            if "/" not in clean_repo:
                clean_repo = f"{get_default_github_user()}/{clean_repo}"

            async with httpx.AsyncClient(timeout=15.0) as client:
                res = await client.get(f"https://api.github.com/repos/{clean_repo}/contents/{path}", headers=headers)
                if res.status_code == 200:
                    data = res.json()
                    if "content" in data and data.get("encoding") == "base64":
                        decoded = base64.b64decode(data["content"]).decode("utf-8", errors="replace")
                        return ToolResult(
                            success=True,
                            data={"repo": clean_repo, "path": path, "content": decoded[:4000]},
                            message=f"Fetched content of '{path}' from {clean_repo}"
                        )
                    return ToolResult(success=True, data=data, message=f"Fetched {path} metadata from {clean_repo}")
                return ToolResult(success=False, error=f"Could not read '{path}' from {clean_repo}: HTTP {res.status_code}")
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
            "User-Agent": "PHANTOM-Assistant"
        }
        try:
            clean_repo = repo.strip()
            if "/" not in clean_repo:
                clean_repo = f"{get_default_github_user()}/{clean_repo}"
            async with httpx.AsyncClient(timeout=15.0) as client:
                res = await client.post(f"https://api.github.com/repos/{clean_repo}/issues", headers=headers, json={"title": title, "body": body})
                if res.status_code in [200, 201]:
                    data = res.json()
                    return ToolResult(success=True, data={"issue_url": data.get("html_url"), "number": data.get("number")}, message=f"Created issue #{data.get('number')}")
                return ToolResult(success=False, error=f"Failed to create issue: {res.text}")
        except Exception as e:
            return ToolResult(success=False, error=str(e))

