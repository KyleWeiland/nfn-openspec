# Article Pipeline Scripts

This directory contains the Python scripts for the NoFrills.news article fetching and processing pipeline.

## Installation

Install the required dependencies:

```bash
pip install -r requirements.txt
```

Newspaper4k requires the NLTK `punkt_tab` tokenizer for NLP summarization. The pipeline downloads it automatically on first run (silently, no action needed).

## Usage

### Run the Pipeline

To fetch and process articles from all configured feeds:

```bash
python fetch_articles.py
```

The script will:
1. Load feed queries and settings from `feeds.config.json`
2. Fetch articles via gnews for each configured query
3. Download and extract article content using Newspaper4k
4. Generate NLP summaries
5. Store articles in `data/articles.db` with deduplication

### Test the Modules

To run basic unit tests on the pipeline modules:

```bash
python test_modules.py
```

This tests:
- Slug generation
- Title normalization

## Configuration

Edit `feeds.config.json` in the repository root to add or remove feeds:

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
      "query": "Technology",
      "category": "Technology"
    }
  ]
}
```

- `gnews_settings.period` — how far back to look (`"1d"`, `"7d"`, etc.)
- `gnews_settings.max_results` — max articles returned per query
- `excluded_domains` — domains to exclude from all queries
- `feeds[].query` — search term passed to Google News
- `feeds[].category` — category label stored with each article

## Module Overview

- `fetch_articles.py` - Main pipeline script
- `config.py` - Configuration file loading and validation
- `article_fetching.py` - gnews-based article discovery
- `article_processing.py` - Article download, extraction, and NLP summarization (Newspaper4k)
- `url_extraction.py` - URL utilities
- `database.py` - SQLite database operations
- `test_modules.py` - Unit tests for core functions

## Database Schema

Articles are stored in `data/articles.db` with the following schema:

```sql
CREATE TABLE articles (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    source_url TEXT NOT NULL,
    summary TEXT,
    category TEXT NOT NULL,
    published_date TEXT,
    slug TEXT NOT NULL,
    created_at TEXT NOT NULL,
    extraction_method TEXT
);
```

`extraction_method` records which pipeline produced the row. Articles fetched
before the gnews/Newspaper4k migration are marked `trafilatura`; everything
written since is marked `newspaper4k`. `init_database()` adds the column and
backfills unmarked rows automatically, so an older database upgrades in place
on the next run.

## Error Handling

The pipeline is designed to be resilient:
- Individual article failures don't stop the entire pipeline
- Network errors are logged and the pipeline continues
- Duplicates are automatically skipped
- Missing or malformed config causes immediate exit
- Zero results for a query logs a warning and continues

## Logging

All operations are logged to stdout with timestamps:
- INFO: Successful operations
- WARNING: Skipped entries or non-fatal failures
- ERROR: Fatal failures

Check the logs to debug issues or monitor progress.
