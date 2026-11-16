import re

from core.github_client import github_get


KEYWORDS = [
    "feature", "support", "add", "integration", "export", "api",
    "plugin", "extension", "error", "cannot", "failed"
]


def fetch_issues(owner, repo):
    """Fetch open issues through GitHub's official REST API."""
    if not isinstance(owner, str) or not re.fullmatch(r"[A-Za-z0-9-]{1,39}", owner):
        raise ValueError("Invalid GitHub owner.")
    if not isinstance(repo, str) or not re.fullmatch(r"[A-Za-z0-9_.-]{1,100}", repo):
        raise ValueError("Invalid GitHub repository name.")
    url = f"https://api.github.com/repos/{owner}/{repo}/issues"
    return github_get(url, {"state": "open", "per_page": 10})


def score_issue(issue):
    score = 0
    title = issue.get("title", "").lower()
    comments = issue.get("comments", 0)
    score += comments * 2
    for word in KEYWORDS:
        if word in title:
            score += 3
    if len(title) > 40:
        score += 2
    return score


def extract_issue_insights(issues):
    insights = []
    for issue in issues:
        if "pull_request" not in issue:
            insights.append({
                "title": issue["title"],
                "comments": issue["comments"],
                "url": issue["html_url"],
                "score": score_issue(issue),
            })
    insights.sort(key=lambda x: x["score"], reverse=True)
    return insights
