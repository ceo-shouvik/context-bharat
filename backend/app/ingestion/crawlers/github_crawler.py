"""GitHub crawler — fetches Markdown docs from GitHub repos via API."""
from __future__ import annotations

import logging

import httpx

from app.ingestion.crawlers.web_crawler import RawDocument

logger = logging.getLogger(__name__)

GITHUB_API = "https://api.github.com"
DOC_EXTENSIONS = {".md", ".mdx", ".rst", ".txt"}
SKIP_DIRS = {"node_modules", ".github", "test", "tests", "__pycache__", "dist", "build"}
MAX_FILES_PER_REPO = 300


class GitHubCrawler:
    """
    Fetches documentation files from a GitHub repository via the GitHub API.
    No cloning required — uses the tree API + raw file fetch.
    Supports both public and private repos (with GITHUB_TOKEN).
    """

    def __init__(self, token: str | None = None):
        self.token = token
        self.headers = {"Authorization": f"token {token}"} if token else {}

    async def crawl(self, repos: list[str], config: dict) -> list[RawDocument]:
        docs = []
        async with httpx.AsyncClient(
            headers={**self.headers, "Accept": "application/vnd.github.v3+json"},
            timeout=30,
        ) as client:
            for repo in repos:
                try:
                    repo_docs = await self._crawl_repo(client, repo, config)
                    docs.extend(repo_docs)
                    logger.info(f"GitHub: {repo} → {len(repo_docs)} docs")
                except Exception as e:
                    logger.error(f"GitHub crawl failed for {repo}: {e}")
        return docs

    async def _crawl_repo(
        self, client: httpx.AsyncClient, repo: str, config: dict
    ) -> list[RawDocument]:
        # Get default branch
        resp = await client.get(f"{GITHUB_API}/repos/{repo}")
        resp.raise_for_status()
        default_branch = resp.json().get("default_branch", "main")

        # Get full file tree
        resp = await client.get(
            f"{GITHUB_API}/repos/{repo}/git/trees/{default_branch}?recursive=1"
        )
        resp.raise_for_status()
        tree = resp.json().get("tree", [])

        # Filter doc files
        doc_files = [
            f for f in tree
            if f.get("type") == "blob"
            and any(f["path"].endswith(ext) for ext in DOC_EXTENSIONS)
            and not any(skip in f["path"].split("/") for skip in SKIP_DIRS)
        ][:MAX_FILES_PER_REPO]

        # Fetch file contents
        docs = []
        for file_info in doc_files:
            raw_url = (
                f"https://raw.githubusercontent.com/{repo}/{default_branch}/{file_info['path']}"
            )
            try:
                content_resp = await client.get(raw_url)
                if content_resp.status_code == 200:
                    docs.append(RawDocument(
                        url=f"https://github.com/{repo}/blob/{default_branch}/{file_info['path']}",
                        content=content_resp.text,
                        content_type="markdown",
                        metadata={"repo": repo, "path": file_info["path"]},
                        library_id=config.get("library_id", ""),
                    ))
            except Exception as e:
                logger.warning(f"Failed to fetch {raw_url}: {e}")

        return docs
