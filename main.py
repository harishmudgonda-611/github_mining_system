import json
from core.github_client import search_repositories
from agents.issue_agent import fetch_issues, extract_issue_insights


def run_signal_scan():
    query = "topic:multi-agent stars:>500"
    data = search_repositories(query)

    top_repos = data.get("items", [])[:3]

    results = []

    for repo in top_repos:
        repo_info = {
            "name": repo["full_name"],
            "stars": repo["stargazers_count"],
            "issues": []
        }

        print(f"\n🔎 Repo: {repo['full_name']} - ⭐ {repo['stargazers_count']}")

        owner, repo_name = repo["full_name"].split("/")
        issues = fetch_issues(owner, repo_name)
        insights = extract_issue_insights(issues)

        for issue in insights:
            print(f"   🧠 Issue: {issue['title']} ({issue['comments']} comments)")
            repo_info["issues"].append(issue)

        results.append(repo_info)

    with open("output/weekly_scan.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    run_signal_scan()