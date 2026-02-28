# Copilot / AI Agent Instructions for github_mining_system

This repo is a small GitHub mining toolkit. These notes help AI coding agents quickly become productive by describing architecture, important files, patterns, and workflow commands specific to this project.

Summary
- Purpose: query GitHub for repositories and surface issue-based signals (star-based repo search -> fetch issues -> extract insights).
- Entrypoint: [main.py](main.py) — runs `run_signal_scan()` which calls the client + agent helpers.

Key components
- `core/github_client.py`: HTTP wrapper around the GitHub Search and REST API. Uses `requests` + `python-dotenv` to pull `GITHUB_TOKEN` from environment.
- `core/agents/issue_agent.py`: agent helper functions:
  - `fetch_issues(owner, repo)` — GET /repos/{owner}/{repo}/issues; default `per_page=5`, `state=open`.
  - `extract_issue_insights(issues)` — ignores PRs (checks for `pull_request`) and returns `title`, `comments`, `url`.
- `agents/` (top-level): reserved for multi-agent orchestrations; currently empty.

Project-specific patterns and conventions
- Keep API calls in `core/github_client.py`; agent logic (filtering, summarization) belongs in `core/agents/*`.
- Small-memory, sample-first approach: functions request a small page (`per_page=5`) and post-process results locally.
- PRs are intentionally ignored when extracting issue signals (see `extract_issue_insights`).
- Auth: token read from environment via `.env` + `load_dotenv()`; code expects `GITHUB_TOKEN` to be set.

Running & debugging
- Install deps: `pip install -r requirements.txt`.
- Set credentials: create a `.env` file with `GITHUB_TOKEN=...` (do NOT commit secrets). The repo currently contains a `.env` file — rotate and remove any leaked tokens before sharing.
- Run the scanner: from repo root:
```
python main.py
```
If needing to call `run_signal_scan()` interactively, import from `main` and call directly.

Notable implementation details discovered
- `main.py` orchestrates calls to `search_repositories()` and then to `fetch_issues()` + `extract_issue_insights()`; it prints the top 3 repos by stars.
- `core/github_client.py` builds `HEADERS` once using `GITHUB_TOKEN` and uses `requests.get(..., headers=HEADERS)` for all calls.
- `issue_agent.fetch_issues()` returns raw JSON; callers are responsible for filtering and presentation.

What the AI agent should do first (practical checklist)
1. Ensure no secrets are leaked: scan `.env` and advise token rotation if present.
2. Run `pip install -r requirements.txt` and `python main.py` locally to confirm the end-to-end flow (with a valid token).
3. When modifying API calls, follow the existing pattern: add params in `core/github_client.py` wrappers and keep agents focused on post-processing.
4. Preserve current behavior: limit per-page size and ignore PRs in issue insights unless explicitly changing semantics.

Examples (call patterns)
- Search repositories:
```py
from core.github_client import search_repositories
data = search_repositories('topic:multi-agent stars:>500')
```
- Pull issues and extract insights:
```py
from core.agents.issue_agent import fetch_issues, extract_issue_insights
issues = fetch_issues('owner', 'repo')
insights = extract_issue_insights(issues)
```

Files to inspect for context
- [main.py](main.py)
- [core/github_client.py](core/github_client.py)
- [core/agents/issue_agent.py](core/agents/issue_agent.py)
- [requirements.txt](requirements.txt)

If anything here is unclear or you'd like a different level of detail (more examples, tests, or a short developer checklist), tell me which sections to expand.
