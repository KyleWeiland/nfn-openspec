## Why

The NoFrills.news site needs a reliable, automated pipeline to fetch news articles from Google Alerts RSS feeds, extract clean content, generate summaries, and store them in a structured database for the static site to consume.

## What Changes

- Add `feeds.config.json` at repo root for managing RSS feed URLs and categories
- Create Python script `scripts/fetch_articles.py` for the complete pipeline
- Implement SQLite database schema at `data/articles.db` for article storage
- Add feed parsing with feedparser library
- Add article extraction and summarization with trafilatura
- Implement deduplication logic using normalized titles and source URLs
- Add Google Alerts redirect URL extraction
- Create database initialization and article storage logic
- Add error handling for network failures and extraction issues

## Capabilities

### New Capabilities
- `feed-config`: Configuration file management for RSS feed URLs and category mappings
- `article-fetching`: RSS feed parsing and article discovery from Google Alerts feeds
- `url-extraction`: Extract actual article URLs from Google Alerts redirect parameters
- `article-processing`: Download, extract, and summarize article content
- `article-storage`: SQLite database schema and storage operations with deduplication
- `pipeline-orchestration`: Main pipeline script that coordinates all fetching and processing steps

### Modified Capabilities
<!-- No existing capabilities are being modified -->

## Impact

- New Python dependencies: feedparser, trafilatura, sqlite3 (standard library)
- New files: `feeds.config.json`, `scripts/fetch_articles.py`, `data/articles.db`
- Database will be committed to the repository
- Pipeline will be invoked by GitHub Actions (to be implemented separately)
- Frontend will consume exported JSON from this database (export functionality to be added later)
