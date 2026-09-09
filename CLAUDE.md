# NoFrills.news

## Project Overview
A minimal news aggregation site. Articles are found via Google News search queries,
extracted/summarized, stored in SQLite, and built into a static Astro site deployed
to GitHub Pages via GitHub Actions.

## Architecture
- **Pipeline:** Python script (gnews + Newspaper4k) → SQLite — no API key needed
- **Frontend:** Astro static site generator, reads from exported JSON
- **Storage:** SQLite database committed to repo at data/articles.db
- **CI/CD:** GitHub Actions daily cron
- **Hosting:** GitHub Pages, served at the custom domain nofrills.news

## Directory Structure
- `scripts/` — Python pipeline (fetch, extract, summarize, store, export)
- `site/` — Astro project
- `data/` — SQLite DB + exported JSON files
- `docs/` — Architecture deep-dive
- `feeds.config.json` — Search queries, category names, and gnews settings (edit this to add/remove feeds)
- `openspec/` — Specifications and change proposals

## Key Conventions
- No images or ads in the frontend
- No client-side frameworks. The only JS in the build is Astro's ~17 KB prefetch
  runtime, from `prefetch.prefetchAll` in site/astro.config.mjs
- All article data flows: gnews query → Python → SQLite → JSON export → Astro build
- Deduplication: check normalized title + source URL before processing
- gnews returns direct article URLs — no redirect parsing needed
- Summaries generated via Newspaper4k NLP; fallback truncates to ~300 words
- Every row records `extraction_method`: `newspaper4k` for current rows,
  `trafilatura` for rows predating the migration. `init_database()` adds the column
  and backfills older databases in place; the migration is idempotent
- Categories are derived from the articles actually stored, not from
  feeds.config.json — a new category only appears after its first successful fetch
- Pagination: 20 articles per page
- Feed config is the single control point for adding/removing feeds
- `site/astro.config.mjs` sets `base: '/'` for the custom domain; it must go back to
  `/nfn-openspec/` if the site ever returns to github.io

## Tech Stack
- Python 3.11+ with gnews, Newspaper4k (NLTK `punkt_tab` downloads on first run)
- Node.js 20+ with Astro
- SQLite3 (standard library)
- GitHub Actions for CI/CD
- GitHub Pages for hosting

## Known Issues
- `data/articles.db` is committed every run and is ~52 MB, past GitHub's 50 MB
  advisory. It reaches the hard 100 MB per-file limit in roughly 6-12 months, after
  which the daily push fails
- Slugs derive from the title alone while dedup keys on title + URL, so a headline
  republished at a different URL collides and only one row gets a page (~2% of articles)
- `scripts/url_extraction.py` is dead code from the Google Alerts era; only
  `scripts/test_modules.py` still imports it, and that test file still exercises the
  retired redirect path. CI does not run it

## Testing
- Test pipeline locally before pushing: `python scripts/fetch_articles.py`
- Export and preview: `./scripts/run_local.sh`, or `python scripts/export_for_astro.py`
  then `cd site && npm run dev`
- The committed `data/articles.db` is already populated, so no seed data is needed
  for frontend work — export it and run the dev server
