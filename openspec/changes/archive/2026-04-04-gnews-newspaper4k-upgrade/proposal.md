## Why

The current pipeline relies on Google Alerts RSS feeds (via feedparser) for article discovery and trafilatura for extraction. Google Alerts RSS is unreliable — feeds go stale, URLs require redirect parsing, and coverage is inconsistent. Replacing both components in one change cleans up the tightly-coupled source/extraction logic and improves article quality and pipeline reliability.

## What Changes

- Replace `feedparser` + Google Alerts RSS URLs with the `gnews` Python library for article discovery
- Replace `trafilatura` with `Newspaper4k` for full-text extraction and NLP summarization
- Change `feeds.config.json` format: RSS feed URLs → query/category pairs with global gnews settings
- Remove Google Alerts redirect-parsing logic (no longer needed — gnews returns direct URLs)
- Add NLTK `punkt_tab` tokenizer download at pipeline startup (required by Newspaper4k NLP)
- Update `requirements.txt`: remove `feedparser`, `trafilatura`; add `gnews`, `newspaper4k`, `lxml_html_clean`

## Capabilities

### New Capabilities

_(none — this change replaces existing capabilities, not adding new ones)_

### Modified Capabilities

- `feed-config`: Config format changes from RSS feed URLs to query/category pairs; adds global `gnews_settings` block (language, country, max_results, period) and `excluded_domains` list
- `article-fetching`: Replaces feedparser + Google Alerts RSS with gnews library; removes redirect URL parsing; fetches articles via search query instead of polling RSS feed URLs
- `article-processing`: Replaces trafilatura with Newspaper4k for full-text extraction; NLP summary via `article.nlp()` replaces manual summarization; adds NLTK dependency at startup
- `url-extraction`: Capability is removed — gnews returns direct article URLs, no redirect resolution needed

## Impact

- `scripts/fetch_articles.py` — primary implementation file; significant rewrite
- `feeds.config.json` — format breaking change (existing RSS URLs replaced with queries)
- `scripts/requirements.txt` — dependency swap
- `CLAUDE.md` — architecture notes updated
- `README.md` — feed configuration and setup docs updated
- No changes to `data/articles.db` schema, `scripts/export_for_astro.py`, or `site/`
