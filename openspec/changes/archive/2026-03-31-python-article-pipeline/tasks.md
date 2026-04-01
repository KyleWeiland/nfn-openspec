## 1. Project Setup

- [x] 1.1 Create `data/` directory at repository root
- [x] 1.2 Create `scripts/` directory at repository root
- [x] 1.3 Create Python requirements file with feedparser and trafilatura dependencies

## 2. Feed Configuration

- [x] 2.1 Create `feeds.config.json` at repository root with proper JSON structure
- [x] 2.2 Add 2-3 placeholder Google Alerts RSS feed URLs with categories
- [x] 2.3 Implement config file loading function with JSON validation
- [x] 2.4 Add error handling for missing or malformed config files

## 3. URL Extraction Module

- [x] 3.1 Create function to detect Google Alerts redirect URLs
- [x] 3.2 Implement URL parameter extraction from redirect URLs
- [x] 3.3 Add URL decoding for extracted URLs
- [x] 3.4 Implement extracted URL validation (HTTP/HTTPS check)
- [x] 3.5 Add error handling for missing or invalid URL parameters

## 4. Database Schema and Operations

- [x] 4.1 Create SQLite connection and initialization function
- [x] 4.2 Implement articles table schema creation with all required columns
- [x] 4.3 Create slug generation function (lowercase, hyphenate, remove special chars)
- [x] 4.4 Implement title normalization function for deduplication
- [x] 4.5 Create deduplication check function (normalized title + source URL)
- [x] 4.6 Implement article insertion function with transaction handling
- [x] 4.7 Add ISO 8601 timestamp generation for created_at field

## 5. Article Fetching

- [x] 5.1 Implement RSS feed parsing with feedparser
- [x] 5.2 Add feed entry metadata extraction (title, link, published date)
- [x] 5.3 Handle missing published dates with current timestamp fallback
- [x] 5.4 Add error handling for network failures during feed fetching
- [x] 5.5 Implement feed entry validation (skip entries without titles)

## 6. Article Processing

- [x] 6.1 Implement article HTML download with HTTP GET requests
- [x] 6.2 Add timeout handling for download requests
- [x] 6.3 Add HTTP error status handling (404, 403, 5xx)
- [x] 6.4 Implement content extraction using trafilatura
- [x] 6.5 Add error handling for failed extractions
- [x] 6.6 Create summary generation function (first 200-300 words)
- [x] 6.7 Implement word counting logic (split on whitespace)
- [x] 6.8 Ensure summaries are plain text without HTML markup

## 7. Pipeline Orchestration

- [x] 7.1 Create main `scripts/fetch_articles.py` entry point script
- [x] 7.2 Implement dependency validation (check for feedparser, trafilatura)
- [x] 7.3 Add configuration file loading at script start
- [x] 7.4 Implement main pipeline loop to iterate through all feeds
- [x] 7.5 Integrate all pipeline stages: parse feed → extract URL → check duplicates → download → extract → summarize → store
- [x] 7.6 Add error isolation logic to continue on individual failures
- [x] 7.7 Implement logging for successful operations and errors
- [x] 7.8 Add exit status handling (0 for success/partial success, 1 for config errors)

## 8. Testing and Validation

- [x] 8.1 Test pipeline with sample Google Alerts RSS feed
- [x] 8.2 Verify deduplication works correctly on repeated runs
- [x] 8.3 Test error handling for unreachable URLs
- [x] 8.4 Verify database schema and data integrity
- [x] 8.5 Test slug generation with various title formats
- [x] 8.6 Verify summary generation stays within 200-300 word limit
