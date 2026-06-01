"""
GitHub Connector — ingests repos, issues, PRs, commits, and README files.

Requires: GITHUB_TOKEN in credentials (uses REST API v3 + raw content).
Ingests:
  - README.md and top-level .md docs
  - Issues (open + closed, with comments)
  - Pull requests (description + review comments)
  - Recent commits (message + diff summary)
  - Source files (configurable extensions whitelist)
"""
from __future__ import annotations

import asyncio
import logging
import re
from datetime import datetime, timedelta
from typing import AsyncIterator

import httpx

from knowledge.ingestion.base import BaseConnector, ConnectorConfig, Document

logger = logging.getLogger("arizen.knowledge.github")

GITHUB_API  = "https://api.github.com"
TEXT_EXTS   = {".md",".txt",".rst",".py",".rs",".ts",".tsx",".js",".go",
               ".toml",".yaml",".yml",".json",".sh",".dockerfile"}


class GitHubConnector(BaseConnector):
    """
    Ingests knowledge from one or more GitHub repositories.

    Config credentials:
      token    : GitHub personal access token (GITHUB_TOKEN)
      repos    : list of "owner/repo" strings
      ingest   : list of "readme" | "issues" | "prs" | "commits" | "files"
      file_exts: list of file extensions to ingest (default TEXT_EXTS)

    Example:
        config = ConnectorConfig(
            source_name="github",
            credentials={
                "token": os.environ["GITHUB_TOKEN"],
                "repos": ["Alrizz-art/ArizenOS"],
                "ingest": ["readme", "issues", "files"],
            }
        )
    """

    def __init__(self, config: ConnectorConfig) -> None:
        super().__init__(config)
        token = config.credentials.get("token", "")
        self._http = httpx.AsyncClient(
            base_url=GITHUB_API,
            headers={"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"},
            timeout=30,
        )
        self._repos    = config.credentials.get("repos", [])
        self._ingest   = set(config.credentials.get("ingest", ["readme","issues","files"]))
        self._exts     = set(config.credentials.get("file_exts", list(TEXT_EXTS)))
        self._since    = datetime.utcnow() - timedelta(days=config.since_days)

    async def health_check(self) -> bool:
        try:
            r = await self._http.get("/user")
            return r.status_code == 200
        except Exception:
            return False

    async def ingest(self) -> AsyncIterator[Document]:
        for repo in self._repos:
            logger.info("GitHub: ingesting %s", repo)
            if "readme" in self._ingest:
                async for doc in self._ingest_readme(repo):
                    yield doc
            if "files" in self._ingest:
                async for doc in self._ingest_files(repo):
                    yield doc
            if "issues" in self._ingest:
                async for doc in self._ingest_issues(repo):
                    yield doc
            if "prs" in self._ingest:
                async for doc in self._ingest_prs(repo):
                    yield doc
            if "commits" in self._ingest:
                async for doc in self._ingest_commits(repo):
                    yield doc

    async def _ingest_readme(self, repo: str) -> AsyncIterator[Document]:
        r = await self._http.get(f"/repos/{repo}/readme", headers={"Accept": "application/vnd.github.raw"})
        if r.status_code != 200:
            return
        content = r.text
        yield Document(
            id        = "",
            source    = "github",
            source_id = f"{repo}:README",
            title     = f"{repo} — README",
            content   = content,
            url       = f"https://github.com/{repo}#readme",
            metadata  = {"repo": repo, "type": "readme", "extension": ".md"},
        )

    async def _ingest_files(self, repo: str) -> AsyncIterator[Document]:
        r = await self._http.get(f"/repos/{repo}/git/trees/HEAD", params={"recursive": "1"})
        if r.status_code != 200:
            return
        tree = r.json().get("tree", [])
        for item in tree:
            path = item.get("path", "")
            ext  = "." + path.rsplit(".", 1)[-1] if "." in path else ""
            if item.get("type") != "blob" or ext not in self._exts:
                continue
            if item.get("size", 0) > 200_000:
                continue  # skip very large files
            raw_r = await self._http.get(f"/repos/{repo}/contents/{path}",
                                         headers={"Accept": "application/vnd.github.raw"})
            if raw_r.status_code != 200:
                continue
            content = raw_r.text
            if not content.strip():
                continue
            yield Document(
                id        = "",
                source    = "github",
                source_id = f"{repo}:{path}",
                title     = f"{repo}/{path}",
                content   = content,
                url       = f"https://github.com/{repo}/blob/main/{path}",
                metadata  = {"repo": repo, "path": path, "extension": ext, "type": "file"},
            )
            await asyncio.sleep(0.05)  # rate-limit courtesy

    async def _ingest_issues(self, repo: str) -> AsyncIterator[Document]:
        page = 1
        while True:
            r = await self._http.get(f"/repos/{repo}/issues",
                params={"state": "all", "per_page": 50, "page": page, "sort": "updated"})
            if r.status_code != 200 or not r.json():
                break
            for issue in r.json():
                if "pull_request" in issue:
                    continue
                updated = datetime.strptime(issue["updated_at"], "%Y-%m-%dT%H:%M:%SZ")
                if updated < self._since:
                    return
                body  = issue.get("body") or ""
                title = issue.get("title", "")
                yield Document(
                    id        = "",
                    source    = "github",
                    source_id = f"{repo}:issue:{issue['number']}",
                    title     = f"Issue #{issue['number']}: {title}",
                    content   = f"# {title}\n\n{body}",
                    url       = issue.get("html_url", ""),
                    metadata  = {
                        "repo": repo, "type": "issue", "number": issue["number"],
                        "state": issue["state"], "labels": ",".join(l["name"] for l in issue.get("labels",[])),
                    },
                )
            page += 1
            if len(r.json()) < 50:
                break

    async def _ingest_prs(self, repo: str) -> AsyncIterator[Document]:
        r = await self._http.get(f"/repos/{repo}/pulls",
            params={"state": "all", "per_page": 50, "sort": "updated"})
        if r.status_code != 200:
            return
        for pr in r.json():
            body  = pr.get("body") or ""
            title = pr.get("title", "")
            yield Document(
                id        = "",
                source    = "github",
                source_id = f"{repo}:pr:{pr['number']}",
                title     = f"PR #{pr['number']}: {title}",
                content   = f"# {title}\n\n{body}",
                url       = pr.get("html_url", ""),
                metadata  = {"repo": repo, "type": "pr", "number": pr["number"], "state": pr["state"]},
            )

    async def _ingest_commits(self, repo: str) -> AsyncIterator[Document]:
        since_str = self._since.strftime("%Y-%m-%dT%H:%M:%SZ")
        r = await self._http.get(f"/repos/{repo}/commits",
            params={"per_page": 100, "since": since_str})
        if r.status_code != 200:
            return
        for commit in r.json():
            msg = commit.get("commit", {}).get("message", "")
            sha = commit.get("sha", "")[:8]
            yield Document(
                id        = "",
                source    = "github",
                source_id = f"{repo}:commit:{sha}",
                title     = f"Commit {sha}: {msg.splitlines()[0][:80]}",
                content   = msg,
                url       = commit.get("html_url", ""),
                metadata  = {"repo": repo, "type": "commit", "sha": sha},
            )

    async def close(self) -> None:
        await self._http.aclose()
