## ADDED Requirements

### Requirement: Source domain extraction
The system SHALL extract a clean domain name from article source URLs during JSON export.

#### Scenario: Standard URL
- **WHEN** source_url is "https://www.govinfosecurity.com/blogs/some-article"
- **THEN** source_name MUST be "govinfosecurity.com"

#### Scenario: URL without www prefix
- **WHEN** source_url is "https://vocal.media/trader/some-article"
- **THEN** source_name MUST be "vocal.media"

#### Scenario: URL with subdomain
- **WHEN** source_url is "https://telecom.economictimes.indiatimes.com/news/article"
- **THEN** source_name MUST be "economictimes.indiatimes.com" (strip only www., keep other subdomains as judgment call — or keep full subdomain)

#### Scenario: Malformed URL
- **WHEN** source_url cannot be parsed
- **THEN** source_name MUST fall back to the raw source_url domain or empty string

### Requirement: Title suffix cleaning
The system SHALL remove source name suffixes from article titles.

#### Scenario: Standard suffix
- **WHEN** title is "The Theranos Playbook Is Quietly Returning - govinfosecurity.com"
- **THEN** cleaned title MUST be "The Theranos Playbook Is Quietly Returning"

#### Scenario: Multiple hyphens in title
- **WHEN** title contains multiple " - " delimiters
- **THEN** only the last " - " segment MUST be removed (preserving hyphens in the actual title)

#### Scenario: No suffix present
- **WHEN** title does not contain " - " delimiter
- **THEN** title MUST be returned unchanged
