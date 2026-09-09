# NoFrills.news

A minimal news aggregation site that delivers articles without the clutter. No images, no ads, no tracking, no client-side frameworks — just clean, readable content focused on tech topics like autonomous vehicles, cybersecurity, quantum computing, and smart cities.

## What is NoFrills.news?

NoFrills.news automatically searches Google News for a curated set of topics, extracts and summarizes each article, stores them in a SQLite database, and builds them into a fast, minimal static site deployed to GitHub Pages. The entire pipeline runs daily via GitHub Actions.

**Live site:** https://kyleweiland.github.io/nfn-openspec/

## Architecture

```
┌─────────────────┐
│  Google News    │
│  search queries │
│  (via gnews)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Python Script  │
│  gnews +        │
│  Newspaper4k    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  SQLite DB      │
│  articles.db    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  JSON Export    │
│  articles.json  │
│  categories.json│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Astro Build    │
│  Static Site    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  GitHub Pages   │
│  Deployment     │
└─────────────────┘
```

**Data Flow:**
1. **Google News** → `gnews` runs one search query per configured category
2. **Python Pipeline** → Downloads each article, extracts the text, generates an NLP summary
3. **SQLite Storage** → Stores articles with deduplication (normalized title + source URL)
4. **JSON Export** → Exports data for frontend consumption
5. **Astro Build** → Generates static HTML pages
6. **GitHub Pages** → Deploys and hosts the site

No API key is required. `gnews` queries Google News directly and returns direct article URLs, so there are no redirect URLs to unwrap.

## Technology Stack

- **Python 3.11+** — Backend pipeline
  - `gnews` — Google News search and article discovery
  - `newspaper4k` — Article extraction and NLP summarization
  - `googlenewsdecoder` — Resolves Google News wrapper URLs when they appear
  - `lxml_html_clean` — HTML sanitization (Newspaper4k dependency)
  - `requests` — HTTP requests
- **Node.js 20+** — Frontend tooling
  - `Astro` — Static site generator (static output mode)
- **SQLite3** — Database (standard library, no separate installation)
- **GitHub Actions** — CI/CD automation
- **GitHub Pages** — Static site hosting

### A note on JavaScript

The site ships no client-side framework and no interactive components. The only JavaScript in the build is Astro's prefetch runtime (~17 KB total), enabled by `prefetch.prefetchAll` in `site/astro.config.mjs`, which preloads linked pages for instant navigation. Removing that option produces a build with zero JavaScript, at the cost of the instant navigation.

## Quick Start

### Prerequisites

- Python 3.11 or higher
- Node.js 20 or higher
- Git

### Clone and Setup

```bash
# Clone the repository
git clone https://github.com/KyleWeiland/nfn-openspec.git
cd nfn-openspec

# Install Python dependencies
pip install -r scripts/requirements.txt

# Install Node.js dependencies
cd site
npm install
cd ..
```

Newspaper4k needs NLTK's `punkt_tab` tokenizer for summarization. The pipeline downloads it automatically on first run — no action needed.

### Run Locally

The easiest way to run the site locally:

```bash
./scripts/run_local.sh
```

This convenience script:
1. Exports articles from SQLite to JSON
2. Starts the Astro development server at http://localhost:4321

**Manual alternative** (if you prefer to run commands separately):

```bash
# Export data from SQLite to JSON
python scripts/export_for_astro.py

# Start Astro dev server
cd site
npm run dev
```

## Local Development

### Using Existing Data

The repository includes a pre-populated `data/articles.db`. You can immediately export and preview:

```bash
python scripts/export_for_astro.py
cd site && npm run dev
```

### Fetching New Articles

To fetch fresh articles:

```bash
python scripts/fetch_articles.py
```

This will:
- Read search queries and settings from `feeds.config.json`
- Query Google News for each configured topic
- Download each article and extract its text with Newspaper4k
- Generate an NLP summary (falling back to a ~300-word truncation if NLP fails)
- Store in `data/articles.db` with deduplication

### Building for Production

```bash
# Export latest data
python scripts/export_for_astro.py

# Build static site
cd site
npm run build

# Preview production build locally
npm run preview
```

The production build outputs to `site/dist/`.

## Feed Management

Feeds are plain Google News search queries. `feeds.config.json` in the repository root is the single control point.

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
    {
      "query": "Autonomous Trucks",
      "category": "Autonomous Trucks"
    }
  ]
}
```

**Settings:**
- `gnews_settings.language` / `country` — locale for the search
- `gnews_settings.max_results` — max articles returned per query, per run
- `gnews_settings.period` — how far back to look (`"1d"`, `"7d"`, and so on)
- `excluded_domains` — domains filtered out of every query
- `feeds[].query` — the search term sent to Google News
- `feeds[].category` — display name used to group articles on the site

### Adding a New Feed

Add an entry to the `feeds` array with a `query` and a `category`. Nothing else needs to change — the site's categories are derived from the articles actually stored, so a new category appears after its first successful fetch.

### Removing a Feed

Delete the corresponding entry from `feeds.config.json`. Articles already collected under that category remain in the database and stay on the site.

## Article Provenance

Articles carry an `extraction_method` field recording which pipeline produced them:

- `trafilatura` — the original pipeline (Google Alerts RSS + feedparser + trafilatura), used through September 2026
- `newspaper4k` — the current pipeline (Google News search + Newspaper4k)

The two produce noticeably different summaries: the legacy pipeline truncated the article's opening to roughly 300 words, while Newspaper4k generates a shorter extractive summary. Legacy articles are labelled *archived summary* in the byline on their article page.

`init_database()` migrates older databases in place, adding the column and backfilling unmarked rows as `trafilatura`. The migration is idempotent and safe to re-run.

## CI/CD Pipeline

### Daily Automated Builds

The site updates automatically every day via GitHub Actions:

```
┌──────────────┐
│  Daily Cron  │  6:00 AM UTC
│  Trigger     │
└──────┬───────┘
       │
       ▼
┌──────────────────────┐
│  Fetch New Articles  │  scripts/fetch_articles.py
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│  Export to JSON      │  scripts/export_for_astro.py
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│  Build Astro Site    │  npm run build
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│  Commit Changes      │  data/articles.db, articles.json, etc.
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│  Deploy to Pages     │  GitHub Pages deployment
└──────────────────────┘
```

**Schedule:** Daily at 6:00 AM UTC

**Workflow file:** `.github/workflows/daily-build.yml`

### Manual Triggers

You can manually trigger the workflow from the GitHub Actions UI:

1. Go to **Actions** tab in the repository
2. Select **Daily Article Update and Deployment** workflow
3. Click **Run workflow**
4. Choose options:
   - **skip_fetch:** Check this to rebuild the site without fetching new articles (useful for frontend changes or fixing broken builds)

**Using GitHub CLI:**

```bash
# Full update (fetch + build + deploy)
gh workflow run daily-build.yml

# Rebuild only (skip fetching new articles)
gh workflow run daily-build.yml -f skip_fetch=true
```

### Commit Messages

The workflow uses dynamic commit messages:
- **Daily automated run:** `chore: daily article update [skip ci]`
- **Manual run (with fetch):** `chore: manual article update [skip ci]`
- **Manual rebuild (skip_fetch):** `chore: manual rebuild [skip ci]`

## Project Structure

```
nfn-openspec/
├── .github/
│   └── workflows/
│       └── daily-build.yml      # CI/CD automation
├── data/
│   ├── articles.db              # SQLite database (version-controlled)
│   ├── articles.json            # Exported data (generated)
│   └── categories.json          # Exported categories (generated)
├── docs/
│   └── architecture-deep-dive.md
├── scripts/
│   ├── fetch_articles.py        # Main pipeline script
│   ├── export_for_astro.py      # JSON export for frontend
│   ├── article_fetching.py      # gnews search and URL decoding
│   ├── article_processing.py    # Newspaper4k extraction & summarization
│   ├── database.py              # SQLite operations and schema migration
│   ├── url_extraction.py        # Legacy URL utilities (unused by the pipeline)
│   ├── config.py                # Configuration loader
│   ├── requirements.txt         # Python dependencies
│   └── run_local.sh             # Local development convenience script
├── site/
│   ├── src/
│   │   ├── components/          # Astro components
│   │   ├── layouts/             # Page layouts
│   │   ├── pages/               # Static pages and routes
│   │   ├── styles/              # global.css
│   │   └── utils/               # formatTime.ts helpers
│   ├── public/                  # Static assets
│   ├── astro.config.mjs         # Astro configuration
│   └── package.json             # Node.js dependencies
├── openspec/                    # Specs and change proposals
├── feeds.config.json            # Search queries and gnews settings
├── CLAUDE.md                    # AI assistant instructions
└── README.md                    # This file
```

## Known Limitations

- **Repository size.** `data/articles.db` is committed on every run and is currently around 52 MB, past GitHub's 50 MB advisory threshold. At present growth it reaches the hard 100 MB per-file limit in roughly 6-12 months, at which point the daily push begins to fail. Pruning old articles or dropping the database from version control are the two obvious remedies.
- **Slug collisions.** Slugs derive from the title alone, while deduplication keys on title *and* URL. A headline republished at a different URL produces a second row with the same slug, and only one of them gets a page. About 2% of stored articles are currently unreachable this way.
- **Stale unit tests.** `scripts/test_modules.py` still exercises the retired Google Alerts redirect helpers. CI does not run it.

## Future Enhancements

The following improvements are documented for potential future implementation. These are possibilities, not commitments — contributions welcome!

### Article Processing Improvements

**HTML tag cleanup in article titles:**
- Issue: Some titles currently include raw HTML tags
- Fix: Strip HTML before storing titles

**Smart deduplication with date-aware logic:**
- Current: Simple title + URL normalization
- Upgrade: Date-aware checking
  - Same title within 30-day window → duplicate (skip)
  - Same title 6+ months apart → different story (keep both)
  - Configurable `window_days` parameter

### AI-Powered Summaries (Premium Option)

**Claude Haiku API integration** for high-quality abstractive summaries:
- **Cost analysis:** ~1,350 articles/month × ~2K tokens ≈ $0.75/month (trivial)
- **Hybrid approach:** Use Newspaper4k first, fall back to Claude for failures
- **Alternative:** Premium upgrade path when quality matters most

### Additional Features

- **Custom domain:** Use a custom domain instead of github.io
- **Dark mode toggle:** The site already follows the OS setting via `prefers-color-scheme`; a manual override is not yet available
- **Client-side search:** Add search functionality using lunr.js or similar
- **RSS feed output:** Generate RSS feed of the site itself
- **Category filtering:** Filter homepage by category

## Contributing

Contributions are welcome! Feel free to:
- Open issues for bugs or feature requests
- Submit pull requests for improvements
- Suggest new feed sources or categories

## License

This project is open source. See LICENSE file for details.
