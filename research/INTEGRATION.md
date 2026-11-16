# GitHub mining research adapters

This repository's core purpose is repository discovery/mining. Keep the collector focused on public GitHub metadata and repository content that the authenticated account is authorized to read; do not turn it into a general-purpose stealth scraper.

## Adapter map
- GitHub REST/GraphQL APIs and GitHub's supported search endpoints are preferred for repository metadata, branches, commits, issues and files. Observe API rate limits and conditional requests.
- **Scrapy** may be used only for public documentation or project pages where crawling is permitted; it is not a replacement for GitHub APIs.
- **MarkItDown** can normalize operator-supplied README, PDF and Office research files.
- **Crawl4AI** can convert permitted public technical documentation into Markdown.
- **AutoScraper / Scrapling** should operate on saved fixtures for extraction stability, not access-control evasion.

## Required provenance
Every collected item should record canonical URL, repository full name when applicable, retrieval time, HTTP/API status, content hash and source type. Keep API-derived data distinct from HTML-derived data. Never collect secrets, private keys, environment files or tokens. Do not ingest repository .env files into the research index.

## Safety
Respect GitHub API terms, authentication scopes and rate limits. Do not scrape private repositories beyond granted permissions, bypass access controls or crawl arbitrary user-supplied hosts. Add explicit allowlists, request budgets, redaction and secret scanning before indexing content.

## Delivery status
This is an adapter plan only; no runtime code or dependencies are changed. Implement API-first collectors and fixture tests before enabling any HTML crawler.