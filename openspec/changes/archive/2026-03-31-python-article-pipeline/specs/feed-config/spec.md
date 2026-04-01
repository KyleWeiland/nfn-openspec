## ADDED Requirements

### Requirement: Configuration file format
The system SHALL use a JSON configuration file named `feeds.config.json` located at the repository root containing an array of feed objects.

#### Scenario: Valid configuration structure
- **WHEN** the configuration file is read
- **THEN** it MUST contain a top-level "feeds" key with an array value

#### Scenario: Each feed entry has required fields
- **WHEN** a feed object is parsed
- **THEN** it MUST contain "url" and "category" string fields

### Requirement: Feed URL validation
The system SHALL validate that each feed URL is a valid HTTP or HTTPS URL.

#### Scenario: Valid HTTP/HTTPS URL
- **WHEN** a feed has url "https://www.google.com/alerts/feeds/..."
- **THEN** the system accepts the feed for processing

#### Scenario: Invalid URL format
- **WHEN** a feed has an invalid URL format
- **THEN** the system MUST log an error and skip that feed

### Requirement: Category naming
The system SHALL accept any non-empty string as a category name.

#### Scenario: Valid category name
- **WHEN** a feed has category "Technology"
- **THEN** the system uses this category for all articles from that feed

#### Scenario: Empty category name
- **WHEN** a feed has an empty category string
- **THEN** the system MUST log an error and skip that feed
