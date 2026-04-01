# NoFrills.news

A minimal news aggregation site that delivers articles without the clutter. No images, no ads, no JavaScript—just clean, readable content focused on tech topics like autonomous vehicles, cybersecurity, quantum computing, and smart cities.

## What is NoFrills.news?

NoFrills.news automatically fetches articles from curated Google Alerts RSS feeds, extracts and summarizes the content, stores them in a SQLite database, and builds them into a fast, minimal static site deployed to GitHub Pages. The entire pipeline runs daily via GitHub Actions.

**Live site:** https://kyleweiland.github.io/nfn-openspec/

## Architecture

```
┌─────────────────┐
│  Google Alerts  │
│   RSS Feeds     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Python Script  │
│  feedparser +   │
│  trafilatura    │
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
1. **RSS Feeds** → Google Alerts provides RSS feeds for specific search topics
2. **Python Pipeline** → Fetches articles, extracts content, generates summaries
3. **SQLite Storage** → Stores articles with deduplication (normalized title + source URL)
4. **JSON Export** → Exports data for frontend consumption
5. **Astro Build** → Generates static HTML pages (zero JavaScript shipped to browser)
6. **GitHub Pages** → Deploys and hosts the site

## Technology Stack

- **Python 3.11+** — Backend pipeline
  - `feedparser` — RSS feed parsing
  - `trafilatura` — Article content extraction
  - `requests` — HTTP requests
- **Node.js 20+** — Frontend tooling
  - `Astro` — Static site generator
- **SQLite3** — Database (standard library, no separate installation)
- **GitHub Actions** — CI/CD automation
- **GitHub Pages** — Static site hosting

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

The repository includes a pre-populated `data/articles.db` with articles. You can immediately export and preview:

```bash
python scripts/export_for_astro.py
cd site && npm run dev
```

### Fetching New Articles

To fetch fresh articles from RSS feeds:

```bash
python scripts/fetch_articles.py
```

This will:
- Read feed URLs from `feeds.config.json`
- Fetch articles from each feed
- Extract article URLs from Google Alerts redirects
- Download and extract article content
- Generate summaries (up to 300 words)
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

### Adding a New Feed

Edit `feeds.config.json` and add a new feed entry:

```json
{
  "feeds": [
    {
      "url": "https://www.google.com/alerts/feeds/YOUR_FEED_ID_HERE",
      "category": "Your Category Name"
    }
  ]
}
```

**Feed structure:**
- `url` — Google Alerts RSS feed URL
- `category` — Display name for categorizing articles on the site

### Removing a Feed

Simply delete the corresponding entry from `feeds.config.json`.

### How to Get Google Alerts RSS Feed URLs

1. Go to https://www.google.com/alerts
2. Create an alert for your topic
3. Set "Deliver to" → RSS feed
4. Copy the RSS feed URL from the alert

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
2. Select **Daily Build and Deploy** workflow
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
├── scripts/
│   ├── fetch_articles.py        # Main pipeline script
│   ├── export_for_astro.py      # JSON export for frontend
│   ├── article_fetching.py      # RSS feed parsing
│   ├── article_processing.py    # Content extraction & summarization
│   ├── database.py              # SQLite operations
│   ├── url_extraction.py        # Google Alerts redirect handling
│   ├── config.py                # Configuration loader
│   ├── requirements.txt         # Python dependencies
│   └── run_local.sh             # Local development convenience script
├── site/
│   ├── src/
│   │   ├── components/          # Astro components
│   │   ├── layouts/             # Page layouts
│   │   └── pages/               # Static pages and routes
│   ├── public/                  # Static assets
│   ├── astro.config.mjs         # Astro configuration
│   └── package.json             # Node.js dependencies
├── feeds.config.json            # RSS feed URLs and categories
├── CLAUDE.md                    # AI assistant instructions
└── README.md                    # This file
```

## Future Enhancements

The following improvements are documented for potential future implementation. These are possibilities, not commitments—contributions welcome!

### Content Aggregation Upgrade

**Replace Google Alerts RSS with GNews API** for better quality control:
- **Benefits:** Language filtering, date range control, country targeting, website exclusion
- **Tradeoff:** Requires API key and rate limits, but filtering happens upstream vs. per-article checks
- **Use case:** Filter out inaccessible articles, wrong language content, and low-quality sources before processing

### Article Processing Improvements

**Replace trafilatura with Newspaper4k:**
- Current: trafilatura only extracts text
- Upgrade: Newspaper4k provides built-in NLP summarization
- Benefit: Higher quality summaries without manual extraction

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

### Frontend Redesign

Visual polish while maintaining core tenets (no images/ads, zero JS):
- Improved typography (font choices, sizing, line-height)
- Better spacing and whitespace design
- Refined color palette beyond basic styles
- Enhanced card design (shadows, borders, hover states)
- Category badge styling improvements
- Dark mode support (user toggle)

### Additional Features

- **Custom domain:** Use a custom domain instead of github.io
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
