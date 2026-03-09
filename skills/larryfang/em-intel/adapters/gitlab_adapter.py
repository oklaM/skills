"""GitLab REST API adapter for merge requests and branches."""

import logging
import os
from datetime import datetime, timedelta, timezone
from typing import List
from urllib.parse import quote_plus

import requests

from .base import Branch, CodeAdapter, MergeRequest

logger = logging.getLogger(__name__)


class GitLabAdapter(CodeAdapter):
    """Fetch merge requests and branches from GitLab groups."""

    def __init__(
        self,
        url: str | None = None,
        token: str | None = None,
        group: str | None = None,
    ):
        self.url = (url or os.getenv("GITLAB_URL", "https://gitlab.com")).rstrip("/")
        self.token = token or os.getenv("GITLAB_TOKEN", "")
        self.group = group or os.getenv("GITLAB_GROUP", "")
        self.headers = {"PRIVATE-TOKEN": self.token}

    def _get(self, path: str, params: dict | None = None) -> list:
        """Paginated GET helper. Returns all results across pages."""
        results: list = []
        params = params or {}
        params.setdefault("per_page", 100)
        page = 1
        while True:
            params["page"] = page
            try:
                resp = requests.get(
                    f"{self.url}/api/v4{path}",
                    headers=self.headers,
                    params=params,
                    timeout=30,
                )
                resp.raise_for_status()
            except requests.RequestException as exc:
                logger.warning("GitLab API error on %s: %s", path, exc)
                break
            data = resp.json()
            if not data:
                break
            results.extend(data)
            page += 1
        return results

    def get_merge_requests(self, days: int = 30) -> List[MergeRequest]:
        """Fetch merged and open MRs from the configured group."""
        since = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
        encoded_group = quote_plus(self.group)
        mrs: List[MergeRequest] = []

        for state in ("merged", "opened"):
            raw = self._get(
                f"/groups/{encoded_group}/merge_requests",
                params={"state": state, "created_after": since},
            )
            for item in raw:
                merged_at = None
                if item.get("merged_at"):
                    merged_at = datetime.fromisoformat(
                        item["merged_at"].replace("Z", "+00:00")
                    )
                mrs.append(
                    MergeRequest(
                        id=str(item["iid"]),
                        title=item.get("title", ""),
                        author=item.get("author", {}).get("username", "unknown"),
                        source_branch=item.get("source_branch", ""),
                        state=item.get("state", state),
                        created_at=datetime.fromisoformat(
                            item["created_at"].replace("Z", "+00:00")
                        ),
                        merged_at=merged_at,
                        url=item.get("web_url", ""),
                    )
                )
        return mrs

    def get_branches(self, days: int = 30) -> List[Branch]:
        """Fetch branches from all projects in the group."""
        encoded_group = quote_plus(self.group)
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)

        # First get projects in the group
        projects = self._get(f"/groups/{encoded_group}/projects", params={"archived": "false"})
        branches: List[Branch] = []

        for proj in projects:
            proj_id = proj["id"]
            raw = self._get(f"/projects/{proj_id}/repository/branches")
            for item in raw:
                commit = item.get("commit", {})
                committed_date_str = commit.get("committed_date", "")
                if not committed_date_str:
                    continue
                last_commit = datetime.fromisoformat(
                    committed_date_str.replace("Z", "+00:00")
                )
                if last_commit < cutoff:
                    continue
                branches.append(
                    Branch(
                        name=item["name"],
                        author=commit.get("author_name", "unknown"),
                        last_commit_at=last_commit,
                        last_commit_sha=commit.get("id", ""),
                    )
                )
        return branches
