## ADDED Requirements

### Requirement: Google Alerts redirect detection
The system SHALL detect when a link is a Google Alerts redirect URL.

#### Scenario: Google Alerts redirect URL
- **WHEN** a link starts with "https://www.google.com/url"
- **THEN** the system identifies it as a redirect URL requiring extraction

#### Scenario: Direct article URL
- **WHEN** a link does not match Google redirect pattern
- **THEN** the system uses the link as-is without extraction

### Requirement: URL parameter extraction
The system SHALL extract the actual article URL from the "url" query parameter in Google redirect URLs.

#### Scenario: Valid redirect with url parameter
- **WHEN** a redirect URL contains a "url" query parameter
- **THEN** the system extracts and URL-decodes the parameter value as the actual article URL

#### Scenario: Missing url parameter
- **WHEN** a redirect URL lacks a "url" query parameter
- **THEN** the system MUST log an error and skip that article

### Requirement: URL decoding
The system SHALL properly decode URL-encoded characters in extracted URLs.

#### Scenario: URL-encoded special characters
- **WHEN** an extracted URL contains %20, %3A, or other encoded characters
- **THEN** the system decodes them to their actual characters

### Requirement: Extracted URL validation
The system SHALL validate that extracted URLs are well-formed HTTP or HTTPS URLs.

#### Scenario: Valid extracted URL
- **WHEN** extraction produces "https://example.com/article"
- **THEN** the system accepts it for further processing

#### Scenario: Invalid extracted URL
- **WHEN** extraction produces a malformed URL
- **THEN** the system MUST log an error and skip that article
