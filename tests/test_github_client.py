import json
import unittest
from unittest.mock import Mock, patch

import requests

from core.github_client import GitHubAPIError, github_get, search_repositories
from agents.issue_agent import fetch_issues


class GitHubClientTests(unittest.TestCase):
    def response(self, payload, status=200, headers=None):
        response = Mock()
        response.status_code = status
        response.headers = headers or {}
        response.iter_content.return_value = [json.dumps(payload).encode("utf-8")]
        response.raise_for_status.side_effect = None
        response.close.return_value = None
        return response

    @patch("core.github_client.requests.get")
    def test_public_request_omits_authorization_when_token_missing(self, get):
        response = self.response({"items": []})
        get.return_value = response
        with patch("core.github_client.HEADERS", {"Accept": "application/vnd.github+json"}):
            self.assertEqual(search_repositories("topic:multi-agent"), {"items": []})
        kwargs = get.call_args.kwargs
        self.assertEqual(kwargs["timeout"], 15)
        self.assertTrue(kwargs["stream"])
        self.assertNotIn("Authorization", kwargs["headers"])

    @patch("core.github_client.requests.get")
    def test_rejects_non_github_hosts(self, get):
        with self.assertRaises(ValueError):
            github_get("https://example.com/api")
        get.assert_not_called()

    @patch("core.github_client.requests.get")
    def test_surfaces_rate_limit_without_retrying_or_scraping(self, get):
        response = self.response({}, 403, {"X-RateLimit-Remaining": "0", "X-RateLimit-Reset": "123"})
        get.return_value = response
        with self.assertRaisesRegex(GitHubAPIError, "rate limit"):
            github_get("https://api.github.com/search/repositories")
        get.assert_called_once()

    @patch("core.github_client.requests.get")
    def test_rejects_oversized_response(self, get):
        response = self.response({})
        response.headers = {"Content-Length": str(5 * 1024 * 1024)}
        get.return_value = response
        with self.assertRaisesRegex(GitHubAPIError, "4 MB"):
            github_get("https://api.github.com/search/repositories")

    @patch("agents.issue_agent.github_get")
    def test_issue_endpoint_uses_validated_owner_repo_and_official_api(self, api):
        api.return_value = []
        self.assertEqual(fetch_issues("octocat", "hello-world"), [])
        api.assert_called_once_with(
            "https://api.github.com/repos/octocat/hello-world/issues",
            {"state": "open", "per_page": 10},
        )
        with self.assertRaises(ValueError):
            fetch_issues("../evil", "repo")


if __name__ == "__main__":
    unittest.main()
