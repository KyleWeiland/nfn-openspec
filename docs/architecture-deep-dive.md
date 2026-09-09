# NoFrills.news — Architecture Deep Dive

**Branch:** `newspaper4k-gnews-migration`
**Date:** 2026-04-04

---

## Table of Contents

- [Part 1: System Architecture Overview](#part-1-system-architecture-overview)
- [Part 2: Backend Deep Dive (Python Pipeline)](#part-2-backend-deep-dive-python-pipeline)
- [Part 3: Frontend Deep Dive (Astro Static Site)](#part-3-frontend-deep-dive-astro-static-site)

---

# Part 1: System Architecture Overview

## What Is This?

NoFrills.news is a fully automated news aggregation platform. A Python pipeline discovers articles via Google News, extracts and summarizes them with NLP, stores them in SQLite, and exports JSON that an Astro static site consumes at build time. GitHub Actions orchestrates the daily cycle and deploys to GitHub Pages. Zero JavaScript is shipped to the browser.

## High-Level System Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                    GitHub Actions (Daily 6:00 UTC)                   │
│                    + Manual Dispatch Option                          │
└──────────────────────────────┬──────────────────────────────────────┘
                               │ triggers
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      PYTHON PIPELINE (scripts/)                     │
│                                                                     │
│  feeds.config.json ──► config.py ──► fetch_articles.py              │
│  (queries, gnews        (validate)    (GNews API discovery)         │
│   settings, excludes)                       │                       │
│                                             ▼                       │
│                                   article_processing.py             │
│                                   (Newspaper4k download/parse/NLP)  │
│                                             │                       │
│                                             ▼                       │
│                                      database.py                    │
│                                   (dedup + SQLite insert)           │
│                                             │                       │
│                                             ▼                       │
│                                    export_for_astro.py              │
│                                   (SQLite → JSON export)            │
└──────────────────────────────┬──────────────────────────────────────┘
                               │ writes
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      DATA LAYER (data/)                             │
│                                                                     │
│   articles.db (SQLite, ~1.3MB, ~250 articles, version-controlled)  │
│   articles.json (sorted by date DESC, consumed by Astro)           │
│   categories.json (9 unique categories, alphabetical)              │
└──────────────────────────────┬──────────────────────────────────────┘
                               │ read at build time
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                   ASTRO STATIC SITE (site/)                         │
│                                                                     │
│   Pages (getStaticPaths):                                          │
│     [...page].astro          → /  /2  /3  (paginated home)         │
│     article/[slug].astro     → /article/tesla-fsd-rollout          │
│     category/[cat]/[...page] → /category/cybersecurity/  /2        │
│     404.astro                → fallback                            │
│                                                                     │
│   Components:                                                       │
│     Navbar.astro       (categories nav, slugified links)           │
│     ArticleCard.astro  (title, date, truncated summary, badge)     │
│     Pagination.astro   (prev/next + smart page number truncation)  │
│                                                                     │
│   Output: site/dist/   → pure HTML, ZERO JavaScript shipped        │
└──────────────────────────────┬──────────────────────────────────────┘
                               │ deploy artifact
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│              GitHub Pages (kyleweiland.github.io/nfn-openspec/)     │
└─────────────────────────────────────────────────────────────────────┘
```

## End-to-End Data Flow

```
1. GNews API query: "Autonomous Vehicles" (language=en, country=US, period=1d, max=10)
       │
2. Returns: [{title, url, published_date (RFC 2822)}, ...]
       │
3. For each article:
       ├── Dedup check: normalized_title + source_url against SQLite → skip if exists
       ├── Newspaper4k: download HTML → parse text → NLP summarize (NLTK punkt_tab)
       │      └── Fallback: if NLP fails → truncate text to ~300 words
       ├── Date resolution: prefer gnews RFC 2822 → fallback newspaper date → fallback UTC now
       └── Insert: {title, source_url, summary, category, published_date, slug, created_at}
       │
4. Export: SELECT * ORDER BY published_date DESC → articles.json + categories.json
       │
5. Astro build: getStaticPaths() reads JSON → generates all HTML routes
       │
6. GitHub Actions: git commit data/ → deploy site/dist/ to Pages
```

## What Changed on This Branch (vs. main)

| Before (main) | After (this branch) |
|---|---|
| Google Alerts RSS via `feedparser` | `gnews` library (Google News API wrapper) |
| `trafilatura` for text extraction | `Newspaper4k` for extraction + NLP summarization |
| RSS URLs with Google redirect parsing | Direct article URLs — no redirect dance |
| Manual summary truncation | NLTK-powered abstractive summaries with fallback |
| `feeds.config.json` held RSS URLs | Now holds search queries + gnews settings |

## Tech Stack Summary

| Layer | Tech | Why |
|---|---|---|
| Article discovery | `gnews` | No API key needed, upstream filtering (language/country/domain exclusion) |
| Text extraction | `Newspaper4k` + `lxml_html_clean` | Full-text + NLP in one library |
| Summarization | NLTK (`punkt_tab`) | Bundled with Newspaper4k's `.nlp()` |
| Storage | SQLite3 (stdlib) | Zero infrastructure, committed to repo |
| Frontend | Astro 4 (static mode) | Zero JS, pre-rendered, fast |
| Styling | Vanilla CSS with custom properties | Light/dark mode, responsive, WCAG-compliant |
| CI/CD | GitHub Actions | Free tier, daily cron + manual dispatch |
| Hosting | GitHub Pages | Free, automatic from Actions |

## Architecture Decisions Worth Knowing

1. **SQLite committed to git** — Intentional simplicity. No external DB service, full history in git. Trade-off: binary blob growth over time. Fine at ~250 articles; revisit at 10k+.

2. **Zero JS shipped** — Astro `output: 'static'` means every page is pre-rendered HTML. No client-side search, no dynamic filtering. Pagination is statically generated.

3. **Deduplication is two-tier** — First checks exact `source_url` match, then `normalized_title + source_url`. Pragmatic, not perfect (won't catch same article under different URLs).

4. **NLP with graceful degradation** — `article.nlp()` uses NLTK for summarization. If it fails (common with short/malformed articles), falls back to first ~300 words. Pipeline never halts on a single article failure.

5. **`feeds.config.json` is the single control point** — Add a query + category, and the entire pipeline (fetch -> store -> export -> navbar -> category pages) picks it up automatically. No code changes needed.

## Pipeline Resilience Model

```
FATAL (pipeline halts):          GRACEFUL (skip & continue):
─────────────────────            ────────────────────────────
- Invalid config                 - Single article network timeout (30s)
- Missing gnews/newspaper4k      - Newspaper4k parse failure
- SQLite init failure            - NLP summarization failure → fallback
                                 - Duplicate detected → skip
                                 - Empty query results → log, next feed
```

## CI/CD Workflow

```
Trigger: cron 0 6 * * * UTC  OR  manual dispatch (with optional skip_fetch flag)
    │
    ├── Setup Python 3.11 + pip cache
    ├── pip install -r scripts/requirements.txt
    ├── python scripts/fetch_articles.py  (skippable via manual input)
    ├── python scripts/export_for_astro.py
    ├── Setup Node 20 + npm cache
    ├── cd site && npm ci && npm run build
    ├── git commit data/ with [skip ci] tag  (only if changes)
    └── Deploy site/dist/ → GitHub Pages
```

## Directory Structure

```
nfn-openspec/
├── scripts/                          # Python pipeline
│   ├── fetch_articles.py             # Main orchestrator & entry point
│   ├── article_fetching.py           # GNews API integration
│   ├── article_processing.py         # Newspaper4k extraction & NLP
│   ├── database.py                   # SQLite operations
│   ├── export_for_astro.py           # JSON export for frontend
│   ├── config.py                     # Configuration loading & validation
│   ├── url_extraction.py             # URL parsing utilities (vestigial)
│   ├── seed_data.py                  # Test data seeding
│   ├── test_modules.py               # Unit tests
│   └── requirements.txt              # Python dependencies
├── site/                             # Astro frontend
│   ├── src/
│   │   ├── pages/                    # Route definitions
│   │   │   ├── [...page].astro       # Home + pagination
│   │   │   ├── article/[slug].astro  # Article detail
│   │   │   ├── category/[category]/[...page].astro
│   │   │   └── 404.astro
│   │   ├── components/               # Reusable components
│   │   │   ├── Navbar.astro
│   │   │   ├── ArticleCard.astro
│   │   │   └── Pagination.astro
│   │   ├── layouts/
│   │   │   └── BaseLayout.astro      # HTML shell
│   │   └── styles/
│   │       └── global.css            # Full design system
│   ├── astro.config.mjs
│   ├── package.json
│   └── tsconfig.json
├── data/                             # Persisted data
│   ├── articles.db                   # SQLite database
│   ├── articles.json                 # Exported articles
│   └── categories.json               # Exported categories
├── feeds.config.json                 # Pipeline configuration
├── .github/workflows/
│   └── daily-build.yml               # CI/CD automation
└── openspec/                         # Specifications
```

## Current Categories (9)

Autonomous Trucks, Autonomous Vehicles, Connected Car, Cybersecurity, Image Recognition, IoT Cyber, Quantum Computers, Sim Racing, Smart Cities

## Things to Watch

- **GNews rate limits** — No API key, so you're on Google's good graces. 9 feeds x 10 results = ~90 queries/day is fine; scaling feeds significantly may hit limits.
- **NLTK download on cold start** — `nltk.download('punkt_tab')` runs at import time. Cached in Actions via pip cache, but first run on a new machine needs internet.
- **`url_extraction.py` is vestigial** — Google Alerts redirect parsing kept as a safety net but unused in the gnews flow. Could be pruned.
- **No automated tests in CI** — `test_modules.py` exists but isn't wired into the Actions workflow.
- **SQL injection safe** — All queries use parameterized statements in `database.py`.

---

# Part 2: Backend Deep Dive (Python Pipeline)

## Overview

The backend is a modular Python pipeline that runs as a batch job. Each module has a single responsibility and communicates via function calls and dictionaries. The pipeline is orchestrated by `fetch_articles.py`, which calls into the other modules sequentially.

```
feeds.config.json
    │
    ▼
config.py (validate)
    │
    ▼
fetch_articles.py (orchestrate)
    ├── article_fetching.py (discover via GNews)
    ├── article_processing.py (extract + summarize via Newspaper4k)
    ├── database.py (dedup + persist to SQLite)
    └── export_for_astro.py (SQLite → JSON)
```

## Module Reference

### config.py — Configuration Loading

**Purpose:** Load and validate `feeds.config.json`. Single source of truth for all pipeline behavior.

**Constants:**
```python
REPO_ROOT = Path(__file__).parent.parent
CONFIG_PATH = REPO_ROOT / "feeds.config.json"
REQUIRED_GNEWS_SETTINGS = ['language', 'country', 'max_results', 'period']
```

**Function: `load_config() -> dict | None`**

Loads and validates the JSON config file. Returns the config dict or `None` on failure.

Validation steps (in order):
1. File existence check
2. JSON parse (catches `json.JSONDecodeError`)
3. `gnews_settings` key exists
4. All 4 required gnews fields present (`language`, `country`, `max_results`, `period`)
5. `feeds` key exists and is a list
6. `excluded_domains` extracted with `[]` default
7. Each feed validated:
   - Must be a dict
   - Must have `query` (non-empty string)
   - Must have `category` (non-empty string)
   - Invalid feeds are skipped; valid ones collected
8. At least one valid feed required

**Validation strategy:** Collects all errors before failing. Logs each validation error individually so the user can fix them all in one pass.

**Config structure:**
```json
{
  "gnews_settings": {
    "language": "en",
    "country": "US",
    "max_results": 10,
    "period": "1d"
  },
  "excluded_domains": ["youtube.com", "reddit.com"],
  "feeds": [
    { "query": "Autonomous Trucks", "category": "Autonomous Trucks" },
    { "query": "Cybersecurity", "category": "Cybersecurity" }
  ]
}
```

---

### fetch_articles.py — Main Orchestrator

**Purpose:** Entry point for the entire pipeline. Coordinates fetching, processing, deduplication, and storage.

**Function: `check_dependencies() -> bool`**

Attempts to import `gnews`, `newspaper`, and `googlenewsdecoder`. Returns `True` if all succeed. On failure, logs an error with installation instructions and returns `False`.

**Function: `resolve_published_date(gnews_date: str | None, newspaper_date: datetime | None) -> str`**

Three-tier date resolution:
1. Parse `gnews_date` as RFC 2822 via `email.utils.parsedate_to_datetime()` → ISO 8601
2. If that fails, use `newspaper_date` (checks for `.isoformat()` method via `hasattr`)
3. If both unavailable, fall back to `datetime.utcnow()`

Always returns an ISO 8601 string.

**Function: `main() -> None`**

Complete pipeline execution:

```
1. check_dependencies()  ── fail → exit(1)
2. load_config()         ── fail → exit(1)
3. GNews(language, country, max_results, period, exclude_websites)
4. init_database()       → SQLite connection
5. For each feed in config:
   a. fetch_articles_from_feed(google_news, query, category)
   b. For each article:
      ├── is_duplicate(conn, title, url)?  → skip, count as skipped
      ├── process_article(url)             → None? skip, count as failed
      ├── resolve_published_date(gnews_date, newspaper_date)
      └── insert_article(conn, ...)        → success? count stored : count failed
6. conn.close()
7. Log summary statistics
8. exit(0)
```

**Statistics tracked:** `total_processed`, `total_stored`, `total_skipped`, `total_failed`

**Example pipeline output:**
```
============================================================
Pipeline execution complete
Total articles processed: 90
Articles stored: 12
Duplicates skipped: 65
Failed: 13
============================================================
```

---

### article_fetching.py — GNews Integration

**Purpose:** Discover articles via the GNews API and decode any Google News redirect URLs.

**Function: `decode_url(url: str) -> str`**

Handles Google News wrapped URLs. If `'news.google.com'` is in the URL, attempts to decode via `googlenewsdecoder.new_decoderv1()`. On any failure, returns the original URL unchanged. This is a defensive layer — GNews typically returns direct URLs on this branch.

**Function: `fetch_articles_from_feed(google_news: GNews, query: str, category: str) -> list[dict]`**

Calls `google_news.get_news(query)` and normalizes results into a consistent format.

For each result:
1. Validate `title` exists (skip if missing)
2. Validate `url` exists (skip if missing)
3. Decode URL via `decode_url()`
4. Extract `published_date` (RFC 2822 string)
5. Append `{title, url, gnews_date, category}` to results

Returns empty list on API failure. Individual missing-field results are skipped with warnings.

**Data structure returned:**
```python
[
    {
        "title": "Tesla FSD Update Rollout",
        "url": "https://example.com/article",
        "gnews_date": "Fri, 04 Apr 2026 14:32:00 GMT",
        "category": "Autonomous Vehicles"
    },
    ...
]
```

---

### article_processing.py — Newspaper4k Extraction & NLP

**Purpose:** Download article HTML, extract full text, and generate NLP summaries.

**Constants:**
```python
DOWNLOAD_TIMEOUT = 30  # seconds
BROWSER_USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 ...'
```

**Function: `process_article(url: str) -> dict | None`**

Full extraction pipeline for a single article:

```
1. Create newspaper.Config(timeout=30s, user_agent=Chrome 120)
2. article = newspaper.Article(url, config)
3. article.download()     → fetch HTML
4. article.parse()        → extract text + metadata
5. Validate: article.text must be non-empty
6. Try: article.nlp()     → NLTK abstractive summary
7. Catch: NLP failure     → fallback to first ~300 words of article.text
8. Validate: summary must be non-empty
9. Return {summary, publish_date} or None on failure
```

**Fallback chain:**
```
NLP summary (article.nlp())
    ↓ fails
Truncated text (first 300 words of article.text)
    ↓ still empty
Return None (article counted as failed)
```

**Error handling:** Download/parse failures return `None`. NLP failures trigger the fallback. The pipeline continues with the next article regardless.

---

### database.py — SQLite Persistence

**Purpose:** All database operations — schema management, deduplication, slug generation, and article insertion.

**Constants:**
```python
REPO_ROOT = Path(__file__).parent.parent
DB_PATH = REPO_ROOT / "data" / "articles.db"
```

**Schema:**
```sql
CREATE TABLE IF NOT EXISTS articles (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    source_url TEXT NOT NULL,
    summary TEXT,
    category TEXT NOT NULL,
    published_date TEXT,
    slug TEXT NOT NULL,
    created_at TEXT NOT NULL
);
```

**Function: `init_database() -> sqlite3.Connection`**

Creates the `data/` directory if needed, opens a connection to `articles.db`, creates the table if it doesn't exist, and returns the connection.

**Function: `generate_slug(title: str) -> str`**

Converts a title to a URL-safe slug:
```
"Apple Releases New iPhone!" → "apple-releases-new-iphone"
"Multiple   Spaces   Here"  → "multiple-spaces-here"
```

Steps: lowercase → remove non-word chars (except hyphens) → collapse spaces/hyphens → strip edge hyphens.

**Function: `normalize_title(title: str) -> str`**

Simple normalization for dedup: `title.lower().strip()`.

**Function: `is_duplicate(conn, title: str, source_url: str) -> bool`**

Two-tier deduplication:
1. **URL check:** `SELECT COUNT(*) FROM articles WHERE source_url = ?` — if > 0, it's a duplicate
2. **Title+URL check:** `SELECT COUNT(*) FROM articles WHERE LOWER(TRIM(title)) = ? AND source_url = ?`

URL-based dedup is the primary check (fastest, most reliable). Title normalization adds a secondary safety net.

**Function: `insert_article(conn, title, source_url, summary, category, published_date) -> bool`**

Generates a slug and timestamp, executes a parameterized INSERT, commits the transaction. On failure: logs the error, rolls back, returns `False`. All user input goes through `?` placeholders (SQL injection safe).

**Function: `get_iso8601_timestamp() -> str`**

Returns `datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S")`.

---

### export_for_astro.py — JSON Export

**Purpose:** Read from SQLite and write the JSON files that Astro consumes at build time.

**Constants:**
```python
ARTICLES_JSON = REPO_ROOT / "data" / "articles.json"
CATEGORIES_JSON = REPO_ROOT / "data" / "categories.json"
```

**Function: `export_articles() -> list[dict] | None`**

1. Validates the database file exists
2. Opens with `row_factory = sqlite3.Row` for dict-like access
3. Executes: `SELECT id, title, source_url, summary, category, published_date, slug FROM articles ORDER BY published_date DESC`
4. Converts rows to dicts
5. Writes to `data/articles.json` with `indent=2, ensure_ascii=False`
6. Returns the article list

**Function: `export_categories(articles: list[dict]) -> list[str] | None`**

Extracts unique categories from the articles list, sorts alphabetically, writes to `data/categories.json`.

**Output formats:**

`data/articles.json`:
```json
[
  {
    "id": 62,
    "title": "Global Elevator and Escalator Market...",
    "source_url": "https://vocal.media/...",
    "summary": "Long text...",
    "category": "Smart Cities",
    "published_date": "2026-04-04T06:08:30",
    "slug": "global-elevator-and-escalator-market-..."
  }
]
```

`data/categories.json`:
```json
[
  "Autonomous Trucks",
  "Autonomous Vehicles",
  "Connected Car",
  "Cybersecurity",
  "Image Recognition",
  "IoT Cyber",
  "Quantum Computers",
  "Sim Racing",
  "Smart Cities"
]
```

---

### url_extraction.py — URL Utilities (Vestigial)

**Purpose:** Parse Google Alerts redirect URLs to extract actual article URLs. Largely unused post-gnews migration but kept as a safety net.

| Function | Signature | Purpose |
|---|---|---|
| `is_google_alerts_redirect(url)` | `str -> bool` | Checks for `https://www.google.com/url` prefix |
| `extract_actual_url(redirect_url)` | `str -> str \| None` | Parses `?url=` query parameter, URL-decodes it |
| `is_valid_url(url)` | `str -> bool` | Checks scheme is http/https and netloc exists |
| `get_article_url(url)` | `str -> str \| None` | Dispatcher: redirect detection → extraction → validation |

---

### test_modules.py — Unit Tests

**Coverage:**
- Slug generation (4 cases: normal, special chars, multiple spaces, edge cases)
- Title normalization (4 cases: case conversion, whitespace stripping)
- URL redirect detection (3 cases: Google redirect, normal URL, http variant)
- URL validation (5 cases: https, http, ftp, garbage, empty string)
- URL extraction (2 cases: with `url` param, without)

**Execution:** `python test_modules.py` — prints results with pass/fail indicators. Not wired into CI.

---

### requirements.txt — Dependencies

```
gnews>=0.4.0              # Google News API wrapper
newspaper4k>=0.9.0        # Article extraction + NLP
lxml_html_clean>=0.1.0    # HTML sanitization (newspaper4k dep)
googlenewsdecoder>=0.1.0  # Google News URL decoder
requests>=2.28.0          # HTTP client (indirect dep)
```

**Transitive dependencies:** `nltk` (via newspaper4k), `lxml` (via newspaper4k).

---

## Inter-Module Data Flow

```
feeds.config.json
    │
    ▼
config.load_config()
    │  Returns: {gnews_settings, excluded_domains, feeds}
    ▼
fetch_articles.main()
    │  Creates: GNews(language, country, max_results, period, exclude_websites)
    │  Creates: SQLite connection via database.init_database()
    │
    ├── article_fetching.fetch_articles_from_feed(gnews, query, category)
    │       │  Calls: gnews.get_news(query)
    │       │  Calls: decode_url(raw_url)
    │       │  Returns: [{title, url, gnews_date, category}, ...]
    │       ▼
    ├── database.is_duplicate(conn, title, url)
    │       │  Returns: bool
    │       ▼
    ├── article_processing.process_article(url)
    │       │  Calls: newspaper.Article(url).download().parse().nlp()
    │       │  Returns: {summary, publish_date} | None
    │       ▼
    ├── fetch_articles.resolve_published_date(gnews_date, newspaper_date)
    │       │  Returns: ISO 8601 string
    │       ▼
    └── database.insert_article(conn, title, url, summary, category, published_date)
            │  Returns: bool
            ▼
        data/articles.db

export_for_astro.main()
    ├── export_articles()  → data/articles.json
    └── export_categories() → data/categories.json
```

## Error Handling Patterns

### Pattern 1: Graceful Skip with Logging
Used by: `article_fetching`, `article_processing`
```python
try:
    result = risky_operation()
except Exception as e:
    logging.warning(f"Failed: {e}")
    return None  # Caller skips this item, continues pipeline
```

### Pattern 2: Database Rollback
Used by: `database.insert_article`
```python
try:
    cursor.execute(...)
    conn.commit()
    return True
except Exception as e:
    logging.error(f"Error: {e}")
    conn.rollback()
    return False
```

### Pattern 3: Multi-Tier Fallback
Used by: `resolve_published_date`, `process_article`
```python
# Try best option
try:
    return parse_rfc2822(gnews_date)
except:
    pass
# Try next best
if newspaper_date:
    return newspaper_date.isoformat()
# Last resort
return datetime.utcnow().isoformat()
```

### Pattern 4: Validate-Then-Collect
Used by: `config.load_config`
```python
valid_feeds = []
for i, feed in enumerate(feeds):
    if not valid(feed):
        logging.error(f"Feed {i} invalid: ...")
        continue  # Log all errors, don't stop at first
    valid_feeds.append(feed)
```

## Date Handling

Three date sources with a priority chain:

| Priority | Source | Format | Example |
|---|---|---|---|
| 1 | GNews `published_date` | RFC 2822 | `"Fri, 04 Apr 2026 14:32:00 GMT"` |
| 2 | Newspaper4k `article.publish_date` | Python datetime | `datetime(2026, 4, 4, 14, 32)` |
| 3 | Current UTC time | Generated | `datetime.utcnow()` |

All dates are stored as ISO 8601 strings (`"2026-04-04T14:32:00"`) in both SQLite and JSON.

---

# Part 3: Frontend Deep Dive (Astro Static Site)

## Overview

The frontend is a pure static site built with Astro 4. It reads JSON data at build time, generates all HTML pages via `getStaticPaths()`, and ships zero JavaScript to the browser. The design system uses CSS custom properties for theming with automatic light/dark mode support.

```
data/articles.json ──┐
                     ├──► Astro Build ──► site/dist/ (pure HTML)
data/categories.json ┘
```

## Build Configuration

**`astro.config.mjs`:**
```javascript
export default defineConfig({
  output: 'static',           // Pure SSG — no runtime server
  base: '/nfn-openspec/',     // GitHub Pages subpath
  build: { assets: '_assets' }
});
```

**`package.json`:**
- Runtime: `astro@^4.16.18`
- Dev: `@astrojs/check`, `typescript@^5.6.3`
- Build command: `astro check && astro build` (type-check, then build)
- Engine: Node.js >= 20

**`tsconfig.json`:**
- Extends `astro/tsconfigs/strict` (strictest type checking)
- JSX configured for compile-time Astro syntax (no runtime React)

## Data Layer

Both JSON files are imported as static modules at build time. They are never shipped to the browser.

**Article interface:**
```typescript
interface Article {
  id: number;
  title: string;
  source_url: string;
  summary: string;
  category: string;
  published_date: string;  // ISO 8601
  slug: string;
}
```

**Categories:** Flat array of 9 strings, sorted alphabetically.

## Layout System

### BaseLayout.astro

Wraps every page. Provides the HTML shell, meta tags, and a two-slot architecture:

```
<html lang="en">
  <head>
    <title>{title} | NoFrills.news</title>
    <meta name="description" content="Minimal news aggregation without the noise" />
    <link rel="stylesheet" href="global.css" />
  </head>
  <body>
    <nav class="navbar">
      <slot name="nav" />       ← Navbar component goes here
    </nav>
    <main>
      <slot />                  ← Page content goes here
    </main>
    <footer>
      © {currentYear} NoFrills.news - Just the news, no frills
    </footer>
  </body>
</html>
```

**Usage in pages:**
```astro
<BaseLayout title="Home">
  <Navbar slot="nav" />
  <!-- Page content fills the default slot -->
  <h1>Latest News</h1>
  ...
</BaseLayout>
```

## Page Routing

Astro's file-based routing with `getStaticPaths()` generates all pages at build time.

### Route Map

| Route Pattern | URL Examples | Template |
|---|---|---|
| `[...page].astro` | `/`, `/2/`, `/3/` | Home with pagination |
| `article/[slug].astro` | `/article/tesla-fsd-rollout/` | Article detail |
| `category/[category]/[...page].astro` | `/category/cybersecurity/`, `/category/cybersecurity/2/` | Category archive |
| `404.astro` | Any invalid route | Error page |

### Home Page — `[...page].astro`

The rest parameter `[...page]` matches `/` (page 1), `/2/`, `/3/`, etc.

```typescript
export const getStaticPaths = (async ({ paginate }) => {
  const sortedArticles = [...articles].sort((a, b) =>
    new Date(b.published_date).getTime() - new Date(a.published_date).getTime()
  );
  return paginate(sortedArticles, { pageSize: 20 });
}) satisfies GetStaticPaths;
```

**What happens at build time:**
1. Import all articles from JSON
2. Sort by `published_date` descending (newest first)
3. `paginate()` splits into 20-article chunks
4. Each chunk becomes a page with `page.data` (articles), `page.currentPage`, `page.lastPage`, `page.url.prev`, `page.url.next`
5. Renders: heading → ArticleCard for each article → Pagination controls

### Article Detail — `article/[slug].astro`

One page per article. The slug parameter maps to the article's `slug` field.

```typescript
export const getStaticPaths = (async () => {
  return articles.map((article) => ({
    params: { slug: article.slug },
    props: { article }
  }));
}) satisfies GetStaticPaths;
```

**Renders:**
- Back link to home (`← Back to all articles`)
- Article title (h1)
- Category badge + formatted date (long format: "April 4, 2026")
- Full summary text (no truncation)
- "Read Original Article →" button (external link with `target="_blank"` and `rel="noopener noreferrer"`)

### Category Archive — `category/[category]/[...page].astro`

Nested route: category slug + optional page number.

```typescript
export const getStaticPaths = (async ({ paginate }) => {
  return categories.flatMap((category) => {
    const filtered = articles.filter(
      (a) => a.category.toLowerCase() === category.toLowerCase()
    );
    const sorted = [...filtered].sort(/* by date desc */);
    const categorySlug = slugify(category);
    return paginate(sorted, {
      params: { category: categorySlug },
      pageSize: 20,
      props: { categoryName: category }
    });
  });
}) satisfies GetStaticPaths;
```

**What happens at build time:**
1. For each of 9 categories:
   - Filter articles by category (case-insensitive)
   - Sort by date descending
   - Paginate into 20-article pages
2. Generates URLs like `/category/quantum-computers/`, `/category/quantum-computers/2/`
3. Renders same layout as home page but with category heading
4. Shows "No articles found in this category." if the filter returns empty

### 404 Page

Static error page with a link back to home. Served by GitHub Pages when a route doesn't match.

## Component Library

### Navbar.astro

**Data:** Imports `categories.json` directly. Uses `import.meta.env.BASE_URL` for link prefixing.

**Renders:**
```
┌──────────────────────────────────────────────────┐
│ NoFrills.news                                     │
│ Just the news, no frills                          │
│                                                    │
│ [All] [Autonomous Trucks] [Autonomous Vehicles]   │
│ [Connected Car] [Cybersecurity] [Image Rec...]     │
│ [IoT Cyber] [Quantum Computers] [Sim Racing]      │
│ [Smart Cities]                                     │
└──────────────────────────────────────────────────┘
```

**Slugification:** `"Quantum Computers"` → `"quantum-computers"` for URL construction.

**Responsive behavior:**
- Mobile: horizontal scroll with thin scrollbar
- Desktop (>=768px): flex-wrap, no scroll

### ArticleCard.astro

**Props:** Single `article` object with the full Article interface.

**Renders:**
```
┌──────────────────────────────────────────────────┐
│ [CYBERSECURITY]  Apr 4, 2026                      │
│                                                    │
│ Major Breach Discovered in Cloud Provider          │
│                                                    │
│ Security researchers have uncovered a critical...  │
└──────────────────────────────────────────────────┘
```

**Helper functions:**

| Function | Input → Output | Notes |
|---|---|---|
| `formatDate(dateString)` | `"2026-04-04T06:07:59"` → `"Apr 4, 2026"` | Short month format |
| `truncateSummary(text, 150)` | Long text → first 150 chars + `"..."` | Returns full text if under limit |
| `getCategoryClass(category)` | `"Quantum Computers"` → `"category-quantum-computers"` | Maps to CSS class |

**Links:** Title links to `/article/{slug}` (internal detail page, not external source).

### Pagination.astro

**Props:** Astro's `Page` object with `url.prev`, `url.next`, `currentPage`, `lastPage`.

**Smart page number truncation:**

```
≤7 pages:      [1] [2] [3] [4] [5] [6] [7]
Page 2 of 125: [1] [2] [3] [4] [5] ... [125]
Page 63 of 125: [1] ... [62] [63] [64] ... [125]
Page 124 of 125: [1] ... [121] [122] [123] [124] [125]
```

Logic:
- `last <= 7`: show all
- `current <= 3` (near start): show 1-5, ellipsis, last
- `current >= last - 2` (near end): show 1, ellipsis, last 5
- Otherwise (middle): show 1, ellipsis, current-1 to current+1, ellipsis, last

**URL reconstruction:** Strips trailing page number from current URL, rebuilds for each page. Page 1 gets `/` suffix, page N gets `/{N}` suffix.

**Accessibility:** `aria-label="Pagination"`, `aria-current="page"` on active, `rel="prev"`/`rel="next"` on nav links, 44px minimum touch targets.

## CSS Architecture

### Design System (global.css, ~461 lines)

**CSS Custom Properties:**

```css
:root {
  /* Core palette */
  --color-bg: #ffffff;
  --color-text: #1a1a1a;
  --color-text-muted: #666666;
  --color-border: #e0e0e0;
  --color-link: #0066cc;
  --color-link-hover: #004999;
  --color-accent: #f5f5f5;

  /* 9 category colors */
  --category-autonomous-trucks: #d4e7f0;
  --category-autonomous-vehicles: #d0f0d4;
  --category-connected-car: #f0e4d4;
  --category-cybersecurity: #f0d4d4;
  --category-image-recognition: #e4d4f0;
  --category-iot-cyber: #f0d4e4;
  --category-quantum-computers: #d4f0f0;
  --category-smart-cities: #f0f0d4;
  --category-sim-racing: #f0dcd4;

  /* Spacing scale (8-point grid) */
  --space-xs: 0.25rem;   /* 4px */
  --space-sm: 0.5rem;    /* 8px */
  --space-md: 1rem;      /* 16px */
  --space-lg: 1.5rem;    /* 24px */
  --space-xl: 2rem;      /* 32px */
  --space-2xl: 3rem;     /* 48px */

  /* Typography */
  --font-body: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, ...;
  --max-width: 70ch;     /* Optimal reading width */
}
```

**Dark mode:** All variables re-declared in `@media (prefers-color-scheme: dark)` with inverted palette. Category colors shift to darker tints. Text becomes light, backgrounds become dark.

### Typography

| Element | Size (mobile) | Size (desktop) | Line Height |
|---|---|---|---|
| Body | 16px | 18px | 1.6 |
| h1 | 32px | 45px | 1.2 |
| h2 | 24px | 31.5px | 1.2 |
| h3 | 20px | 22.5px | 1.2 |
| Article content | - | 18px | 1.7 |
| Metadata/badges | 12-14px | 13.5-15.75px | - |

Font stack: system fonts (`-apple-system`, `Segoe UI`, `Roboto`, etc.) — no external font loading.

### Layout

- Content max-width: `70ch` (optimal reading line length)
- Content width: `90%` of viewport
- Centered with `margin: 0 auto`
- Main area: `min-height: calc(100vh - 200px)` (fills viewport)

### Component Styles

**Article cards:**
- Border + border-radius (4px)
- 24px padding
- Subtle box-shadow on hover (`0 2px 8px rgba(0,0,0,0.1)`)
- 0.2s transition on all hover effects

**Category badges:**
- Inline-block, small (12px), uppercase, bold
- Each category has a distinct background color via CSS class
- `.category-quantum-computers { background: var(--category-quantum-computers) }`

**Pagination:**
- Flexbox centered
- 44x44px minimum touch targets (WCAG 2.1 AAA)
- Current page: blue background, white text
- Hover: accent background

**"Read Original Article" button (article detail):**
- Blue background, white text, 600 weight
- 16px vertical / 24px horizontal padding
- Hover darkens background

### Responsive Breakpoints

```
Mobile (default):
  - 16px base font
  - Category nav: horizontal scroll
  - Content: 90% width

Tablet+ (>=768px):
  - 18px base font
  - Category nav: flex-wrap (no scroll)
  - Content: same 90% width, but max 70ch
```

### Accessibility

| Feature | Implementation |
|---|---|
| Focus indicators | `2px solid var(--color-link)` with `outline-offset: 2px` |
| Reduced motion | `@media (prefers-reduced-motion: reduce)` disables all transitions/animations |
| Touch targets | 44x44px minimum on all interactive elements |
| Color contrast | Light: 16:1 (text), 8:1 (links). Dark: 11:1 (text). All AAA. |
| Semantic HTML | `<nav>`, `<main>`, `<article>`, `<time>`, `<header>`, `<footer>` |
| ARIA | `aria-label="Pagination"`, `aria-current="page"` |
| Language | `<html lang="en">` |
| External links | `rel="noopener noreferrer"` on all `target="_blank"` links |

### Category Color Map

| Category | Light Mode | Dark Mode |
|---|---|---|
| Autonomous Trucks | `#d4e7f0` (light blue) | `#2a4a5a` |
| Autonomous Vehicles | `#d0f0d4` (light green) | `#2a4a2a` |
| Connected Car | `#f0e4d4` (light beige) | `#4a3a2a` |
| Cybersecurity | `#f0d4d4` (light red) | `#4a2a2a` |
| Image Recognition | `#e4d4f0` (light purple) | `#3a2a4a` |
| IoT Cyber | `#f0d4e4` (light pink) | `#4a2a3a` |
| Quantum Computers | `#d4f0f0` (light cyan) | `#2a4a4a` |
| Smart Cities | `#f0f0d4` (light yellow) | `#4a4a2a` |
| Sim Racing | `#f0dcd4` (light orange) | `#4a3a2a` |

## Build Output

The Astro build generates a `site/dist/` directory with:

- ~125 index/pagination pages
- ~250+ article detail pages
- ~50+ category archive pages
- 1 static 404 page
- CSS bundle in `_assets/`

Total output: pure HTML + CSS. No JavaScript files. No runtime dependencies. Served entirely from GitHub Pages CDN.

## Environment Variables

Only one is used:

```typescript
import.meta.env.BASE_URL  // "/nfn-openspec/"
```

This is read from `astro.config.mjs` and used in every component that generates internal links (Navbar, ArticleCard, article detail back link).

## Helper Function Reference

| Function | Location | Signature | Example |
|---|---|---|---|
| `slugify` | Navbar, Category page | `(text: string) -> string` | `"IoT Cyber"` → `"iot-cyber"` |
| `formatDate` (short) | ArticleCard | `(dateString: string) -> string` | `"2026-04-04..."` → `"Apr 4, 2026"` |
| `formatDate` (long) | Article detail | `(dateString: string) -> string` | `"2026-04-04..."` → `"April 4, 2026"` |
| `truncateSummary` | ArticleCard | `(text: string, max?: number) -> string` | 150 char limit + `"..."` |
| `getCategoryClass` | ArticleCard, Article detail | `(category: string) -> string` | `"Quantum Computers"` → `"category-quantum-computers"` |
| `getPageNumbers` | Pagination | `(current: number, last: number) -> (number \| string)[]` | Smart truncation with ellipsis |

Note: `slugify` and `getCategoryClass` are nearly identical but defined independently in their respective components. `formatDate` exists in two variants (short month in cards, long month in detail pages).
