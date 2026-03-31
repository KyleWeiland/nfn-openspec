# NoFrills.news

## Project Overview
A minimal news aggregation site. Articles are fetched from Google Alerts RSS feeds,
extracted/summarized, stored in SQLite, and built into a static Astro site deployed
to GitHub Pages via GitHub Actions.

## Architecture
- **Pipeline:** Python script (feedparser + trafilatura) → SQLite
- **Frontend:** Astro static site generator, reads from exported JSON
- **Storage:** SQLite database committed to repo at data/articles.db
- **CI/CD:** GitHub Actions daily cron
- **Hosting:** GitHub Pages

## Directory Structure
- `scripts/` — Python pipeline (fetch, extract, summarize, store, export)
- `site/` — Astro project
- `data/` — SQLite DB + exported JSON files
- `feeds.config.json` — RSS feed URLs and category names (edit this to add/remove feeds)
- `openspec/` — Specifications and change proposals

## Key Conventions
- No images or ads in the frontend
- Ship zero JS to the browser (Astro static mode)
- All article data flows: RSS → Python → SQLite → JSON export → Astro build
- Deduplication: check normalized title + source URL before processing
- Google Alerts RSS URLs contain redirects; extract actual article URL from the redirect
- Summaries should be concise (200-300 words max)
- Pagination: 20 articles per page
- Feed config is the single control point for adding/removing feeds

## Tech Stack
- Python 3.11+ with feedparser, trafilatura
- Node.js 20+ with Astro
- SQLite3 (standard library)
- GitHub Actions for CI/CD
- GitHub Pages for hosting

## Testing
- Use seed data (scripts/seed_data.py) for local frontend development
- Test pipeline locally before pushing: python scripts/fetch_articles.py
- Preview site locally: cd site && npm run dev