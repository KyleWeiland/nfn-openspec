## Context

The article pipeline has two stages: discovery (finding article URLs) and processing (extracting text and generating summaries). Currently discovery uses feedparser to parse Google Alerts RSS feeds, which requires redirect URL parsing to get real article URLs. Processing uses trafilatura for text extraction with a manual word-count summary.

Both stages are being replaced in one change because they're tightly coupled in `fetch_articles.py` — the output of discovery (article URLs) is the direct input to processing, and both libraries are imported and used in the same script.

## Goals / Non-Goals

**Goals:**
- Replace feedparser + Google Alerts RSS with gnews for article discovery
- Replace trafilatura with Newspaper4k for full-text extraction and NLP-driven summarization
- Resolve gnews' internal Google News URLs to real article URLs via `googlenewsdecoder`
- Preserve all existing behavior visible to downstream systems (same DB schema, same JSON export, same slug format)

**Non-Goals:**
- Changing deduplication logic (separate change)
- Improving pagination, categories, or frontend behavior
- Adding retry logic beyond what Newspaper4k provides
- Supporting authenticated/paywalled articles

## Decisions

### Use gnews over feedparser + Google Alerts RSS

**Decision:** Instantiate `GNews` with settings from config (language, country, max_results, period). Call `google_news.get_news(query)` per feed entry.

**Rationale:** Google Alerts RSS feeds are unreliable and produce redirect URLs that require parsing. gnews wraps Google News RSS directly — no API key, stable result structure. Results include `title`, `url`, `published_date`, `description`, `publisher` as a dict. Note: gnews returns Google News internal URLs (`news.google.com/rss/articles/CBMi...`) which must be decoded to real article URLs using `googlenewsdecoder` before passing to Newspaper4k.

**Alternative considered:** Keep feedparser but switch from Google Alerts to standard RSS feeds — rejected because it doesn't solve the discovery quality problem and still requires URL redirect parsing.

### Use Newspaper4k directly (not gnews' `get_full_article()`)

**Decision:** Import `newspaper` (Newspaper4k) and create `newspaper.Article(url)` instances manually.

**Rationale:** gnews' `get_full_article()` uses the old newspaper3k library internally, which is unmaintained. Newspaper4k is the maintained fork with better extraction quality.

**Alternative considered:** Use gnews `get_full_article()` for simplicity — rejected due to quality and maintenance concerns.

### Use Newspaper4k's built-in NLP summary

**Decision:** Call `article.nlp()` and use `article.summary`. Fallback: if summary is empty but `article.text` exists, truncate to ~300 words.

**Rationale:** Newspaper4k's NLP summary is keyword-based and significantly better than truncating the first N words. Requires NLTK `punkt_tab` tokenizer downloaded at startup.

**Alternative considered:** Keep the word-truncation approach from trafilatura — rejected because Newspaper4k's NLP is readily available and produces better results at no extra cost.

### Breaking config format change

**Decision:** Rewrite `feeds.config.json` to replace the `feeds[].url` field with `feeds[].query`, and add top-level `gnews_settings` and `excluded_domains` keys.

**Rationale:** The old URL-based config is meaningless with gnews. A clean format change is simpler than supporting both. Existing config is only consumed by the Python pipeline, not the frontend.

**Alternative considered:** Keep the `url` field and derive gnews queries from it — rejected because it creates confusion and the old URLs are not reusable.

### published_date handling

**Decision:** Use gnews' `published_date` (an RFC 2822 string, e.g. `"Tue, 16 Feb 2021 11:50:43 GMT"`) as primary. Parse with `email.utils.parsedate_to_datetime` and convert to ISO format for SQLite storage. Fall back to `article.publish_date` (datetime) from Newspaper4k if gnews date is missing, then to current UTC timestamp.

**Rationale:** gnews 0.4.x returns published_date as an RFC 2822 string, not a datetime object. `email.utils.parsedate_to_datetime` is stdlib and handles this format reliably. The DB stores dates as text in ISO format — existing convention.

## Risks / Trade-offs

- **gnews is an unofficial library** → Mitigation: gnews wraps a stable Google RSS URL format that has been consistent for years; acceptable risk for a personal project.
- **Newspaper4k download failures (paywalls, bot detection)** → Mitigation: wrap in try/except, log warning, skip article; pipeline continues. Failed articles counted in end-of-run summary.
- **NLTK punkt_tab download at startup adds latency** → Mitigation: `quiet=True` suppresses output; download is a no-op if already cached; acceptable for a daily batch job.
- **feeds.config.json format is a breaking change** → Mitigation: both files are changed atomically in the same PR; no external consumers of this config.
- **gnews `period` parameter limits lookback window** → Trade-off: `'1d'` avoids duplicate articles but may miss articles on pipeline downtime days. Acceptable given deduplication handles overlap.

## Migration Plan

1. Update `scripts/requirements.txt` — swap deps
2. Update `feeds.config.json` — new format with queries matching existing category names
3. Rewrite `scripts/fetch_articles.py` — replace both discovery and processing
4. Update docs (`CLAUDE.md`, `README.md`)
5. No database migration needed — schema unchanged
6. Rollback: revert the four changed files; no data loss (DB rows written by new code are valid under old schema)

## Open Questions

_(none — implementation details fully specified in the change proposal)_
