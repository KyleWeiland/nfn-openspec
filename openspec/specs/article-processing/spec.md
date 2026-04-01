## ADDED Requirements

### Requirement: Article content download
The system SHALL download article HTML content from the extracted URL using HTTP GET requests.

#### Scenario: Successful download
- **WHEN** an article URL is accessible
- **THEN** the system retrieves the HTML content

#### Scenario: Network timeout
- **WHEN** a download request times out after a reasonable period
- **THEN** the system MUST log an error and skip that article

#### Scenario: HTTP error status
- **WHEN** the server returns 404, 403, or 5xx status codes
- **THEN** the system MUST log the error and skip that article

### Requirement: Content extraction
The system SHALL use trafilatura to extract clean article text from HTML content.

#### Scenario: Successful extraction
- **WHEN** trafilatura successfully extracts text from HTML
- **THEN** the system uses the extracted text for summarization

#### Scenario: Extraction failure
- **WHEN** trafilatura cannot extract meaningful text
- **THEN** the system MUST log an error and skip that article

### Requirement: Summary generation
The system SHALL generate a summary by taking the first 200-300 words of the extracted article text.

#### Scenario: Article longer than 300 words
- **WHEN** extracted text contains 500 words
- **THEN** the system creates a summary of approximately 200-300 words from the beginning

#### Scenario: Article shorter than 200 words
- **WHEN** extracted text contains 150 words
- **THEN** the system uses the entire text as the summary

### Requirement: Word counting
The system SHALL count words by splitting text on whitespace.

#### Scenario: Standard word counting
- **WHEN** text is "The quick brown fox jumps"
- **THEN** the system counts 5 words

### Requirement: Summary storage format
The system SHALL store summaries as plain text without HTML markup.

#### Scenario: Clean text summary
- **WHEN** a summary is generated
- **THEN** it MUST NOT contain HTML tags, scripts, or style elements
