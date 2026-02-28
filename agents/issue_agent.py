import requests
from core.github_client import HEADERS


KEYWORDS = [
    "feature",
    "support",
    "add",
    "integration",
    "export",
    "api",
    "plugin",
    "extension",
    "error",
    "cannot",
    "failed"
]


def fetch_issues(owner, repo):
    url = f"https://api.github.com/repos/{owner}/{repo}/issues"
    params = {
        "state": "open",
        "per_page": 10
    }

    response = requests.get(url, headers=HEADERS, params=params)
    return response.json()


def score_issue(issue):
    score = 0

    title = issue.get("title", "").lower()
    comments = issue.get("comments", 0)

    # Comment weight
    score += comments * 2

    # Keyword weight
    for word in KEYWORDS:
        if word in title:
            score += 3

    # Title length bonus
    if len(title) > 40:
        score += 2

    return score


def extract_issue_insights(issues):
    insights = []

    for issue in issues:
        if "pull_request" not in issue:
            issue_score = score_issue(issue)

            insights.append({
                "title": issue["title"],
                "comments": issue["comments"],
                "url": issue["html_url"],
                "score": issue_score
            })

    # Sort by score descending
    insights.sort(key=lambda x: x["score"], reverse=True)

    return insights