"""Small, bounded client for GitHub's official REST API.

The mining pipeline uses API endpoints rather than scraping GitHub HTML.
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from urllib.parse import urlparse

import requests
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("GITHUB_TOKEN")

BASE_HEADERS = {
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
    "User-Agent": "github-mining-system/1.0",
}
HEADERS = {**BASE_HEADERS, **({"Authorization": f"Bearer {TOKEN}"} if TOKEN else {})}

REQUEST_TIMEOUT_SECONDS = 15
MAX_RESPONSE_BYTES = 4 * 1024 * 1024


class GitHubAPIError(RuntimeError):
    """A bounded, user-safe error returned by the GitHub API client."""


def github_get(url: str, params: dict | None = None) -> dict:
    """GET a public GitHub API resource with explicit time and size limits."""
    parsed = urlparse(url)
    if parsed.scheme != "https" or parsed.hostname != "api.github.com" or parsed.username or parsed.password:
        raise ValueError("Only HTTPS requests to api.github.com are allowed.")

    response = requests.get(
        url,
        headers=HEADERS,
        params=params,
        timeout=REQUEST_TIMEOUT_SECONDS,
        stream=True,
    )
    try:
        if response.status_code == 403 and response.headers.get("X-RateLimit-Remaining") == "0":
            reset = response.headers.get("X-RateLimit-Reset")
            suffix = f" Reset epoch: {reset}." if reset else ""
            raise GitHubAPIError("GitHub API rate limit reached." + suffix)
        try:
            response.raise_for_status()
        except requests.HTTPError as exc:
            raise GitHubAPIError(f"GitHub API returned HTTP {response.status_code}.") from exc

        declared = response.headers.get("Content-Length")
        if declared and declared.isdigit() and int(declared) > MAX_RESPONSE_BYTES:
            raise GitHubAPIError("GitHub API response exceeded the 4 MB safety limit.")

        chunks: list[bytes] = []
        total = 0
        for chunk in response.iter_content(chunk_size=64 * 1024):
            if not chunk:
                continue
            total += len(chunk)
            if total > MAX_RESPONSE_BYTES:
                raise GitHubAPIError("GitHub API response exceeded the 4 MB safety limit.")
            chunks.append(chunk)
        try:
            payload = json.loads(b"".join(chunks).decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise GitHubAPIError("GitHub API returned invalid JSON.") from exc
        if not isinstance(payload, dict):
            raise GitHubAPIError("GitHub API returned an unexpected response shape.")
        return payload
    finally:
        response.close()


def search_repositories(query: str) -> dict:
    if not isinstance(query, str) or not query.strip() or len(query) > 256:
        raise ValueError("query must be a non-empty string of at most 256 characters.")
    return github_get(
        "https://api.github.com/search/repositories",
        {"q": query, "sort": "stars", "order": "desc", "per_page": 30},
    )
