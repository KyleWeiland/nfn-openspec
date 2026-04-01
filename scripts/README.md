# Article Pipeline Scripts

This directory contains the Python scripts for the NoFrills.news article fetching and processing pipeline.

## Installation

Install the required dependencies:

```bash
pip install -r ../requirements.txt
```

## Usage

### Run the Pipeline

To fetch and process articles from all configured feeds:

```bash
python fetch_articles.py
```

The script will:
1. Load feed URLs from `feeds.config.json`
2. Parse each RSS feed
3. Extract article URLs from Google Alerts redirects
4. Download and extract article content
5. Generate summaries (200-300 words)
6. Store articles in `data/articles.db` with deduplication

### Test the Modules

To run basic unit tests on the pipeline modules:

```bash
python test_modules.py
```

This tests:
- Slug generation
- Title normalization
- URL extraction from Google Alerts redirects
- URL validation

## Configuration

Edit `feeds.config.json` in the repository root to add or remove RSS feeds:

```json
{
  "feeds": [
    {
      "url": "https://www.google.com/alerts/feeds/...",
      "category": "Technology"
    }
  ]
}
```

## Module Overview

- `fetch_articles.py` - Main pipeline script
- `config.py` - Configuration file loading and validation
- `article_fetching.py` - RSS feed parsing
- `url_extraction.py` - Google Alerts redirect URL extraction
- `article_processing.py` - Article download, extraction, and summarization
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
    created_at TEXT NOT NULL
);
```

## Error Handling

The pipeline is designed to be resilient:
- Individual article failures don't stop the entire pipeline
- Network errors are logged and the pipeline continues
- Duplicates are automatically skipped
- Missing or malformed config causes immediate exit

## Logging

All operations are logged to stdout with timestamps:
- INFO: Successful operations
- WARNING: Skipped entries
- ERROR: Failed operations

Check the logs to debug issues or monitor progress.
