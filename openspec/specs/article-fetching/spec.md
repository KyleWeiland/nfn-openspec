## ADDED Requirements

### Requirement: RSS feed parsing
The system SHALL use the gnews library to fetch articles by executing a search query for each configured feed.

#### Scenario: Successful feed query
- **WHEN** a valid query string is provided (e.g., "Technology")
- **THEN** the system returns a list of article dicts each containing title, url, published_date, description, and publisher

#### Scenario: Feed fetch failure
- **WHEN** gnews raises an exception for a query
- **THEN** the system MUST log the error and continue processing other feeds

### Requirement: Google News URL decoding
The system SHALL decode Google News internal URLs (matching `news.google.com`) to actual article URLs using the `googlenewsdecoder` library before passing them to the processing stage.

#### Scenario: Google News internal URL decoded
- **WHEN** gnews returns a URL matching `news.google.com/rss/articles/...`
- **THEN** the system decodes it to the actual article URL before processing

#### Scenario: Decoding fails
- **WHEN** `googlenewsdecoder` raises an exception or returns no decoded URL
- **THEN** the system MUST log a warning and use the original URL as a fallback

#### Scenario: Non-Google URL passed through
- **WHEN** gnews returns a URL that does not contain `news.google.com`
- **THEN** the system uses it as-is without decoding

### Requirement: Article metadata extraction
The system SHALL extract title, url, published_date, description, and publisher from each gnews result dict.

#### Scenario: Complete metadata present
- **WHEN** a gnews result contains title, url, and published_date
- **THEN** the system extracts all fields for processing

#### Scenario: Missing published date
- **WHEN** a gnews result lacks a published_date
- **THEN** the system MUST use the current timestamp as published_date

#### Scenario: Missing title
- **WHEN** a gnews result lacks a title
- **THEN** the system MUST skip that entry and log a warning

### Requirement: Feed processing order
The system SHALL process feeds in the order they appear in the configuration file.

#### Scenario: Sequential feed processing
- **WHEN** multiple feeds are configured
- **THEN** the system processes each feed to completion before moving to the next

### Requirement: Entry limit per feed
The system SHALL limit results per feed to the `max_results` value from `gnews_settings`.

#### Scenario: max_results applied
- **WHEN** `gnews_settings.max_results` is set to 10
- **THEN** each feed query returns at most 10 articles

#### Scenario: Feed returns zero results
- **WHEN** a query returns an empty list
- **THEN** the system MUST log a warning and continue to the next feed without error

### Requirement: Lookback period
The system SHALL apply the `period` setting from `gnews_settings` to limit results to articles published within that window.

#### Scenario: Period applied to query
- **WHEN** `gnews_settings.period` is `"1d"`
- **THEN** gnews only returns articles published in the last 24 hours
