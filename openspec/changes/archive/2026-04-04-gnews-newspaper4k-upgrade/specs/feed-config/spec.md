## MODIFIED Requirements

### Requirement: Configuration file format
The system SHALL use a JSON configuration file named `feeds.config.json` located at the repository root containing a top-level `gnews_settings` object, an `excluded_domains` array, and a `feeds` array of feed objects.

#### Scenario: Valid configuration structure
- **WHEN** the configuration file is read
- **THEN** it MUST contain a top-level `gnews_settings` object, an `excluded_domains` array, and a `feeds` array

#### Scenario: Each feed entry has required fields
- **WHEN** a feed object is parsed
- **THEN** it MUST contain `query` and `category` string fields

### Requirement: gnews settings block
The system SHALL read global gnews parameters from the `gnews_settings` top-level key.

#### Scenario: gnews_settings present
- **WHEN** the config contains a `gnews_settings` object with `language`, `country`, `max_results`, and `period` fields
- **THEN** the system passes these values when instantiating the GNews client

#### Scenario: gnews_settings missing field
- **WHEN** a required gnews_settings field is absent
- **THEN** the system MUST raise a configuration error and exit

### Requirement: Excluded domains list
The system SHALL read a list of domains to exclude from results from the `excluded_domains` top-level key.

#### Scenario: Excluded domains applied
- **WHEN** `excluded_domains` contains `["youtube.com", "reddit.com"]`
- **THEN** the system passes these as `exclude_websites` to the GNews client

#### Scenario: Empty excluded domains
- **WHEN** `excluded_domains` is an empty array
- **THEN** the system creates the GNews client with no domain exclusions

### Requirement: Category naming
The system SHALL accept any non-empty string as a category name.

#### Scenario: Valid category name
- **WHEN** a feed has category "Technology"
- **THEN** the system uses this category for all articles from that feed

#### Scenario: Empty category name
- **WHEN** a feed has an empty category string
- **THEN** the system MUST log an error and skip that feed

## REMOVED Requirements

### Requirement: Feed URL validation
**Reason**: Feed entries no longer contain URLs. Feeds are now identified by a search query string, not an RSS URL. URL validation belongs to article-level processing, not feed config.
**Migration**: Remove any URL validation logic from feed config parsing. Each feed entry uses a `query` field instead of a `url` field.
