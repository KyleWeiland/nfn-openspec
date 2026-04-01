## ADDED Requirements

### Requirement: Main script location
The system SHALL provide a main pipeline script at `scripts/fetch_articles.py` that can be executed directly with Python.

#### Scenario: Script execution
- **WHEN** a user runs `python scripts/fetch_articles.py`
- **THEN** the system executes the complete pipeline

### Requirement: Pipeline execution flow
The system SHALL execute pipeline stages in the following order for each feed: read config, parse feed, process each entry (extract URL, check duplicates, download, extract content, generate summary, store in database).

#### Scenario: Complete pipeline run
- **WHEN** the script is executed
- **THEN** all configured feeds are processed in sequence

### Requirement: Error isolation
The system SHALL continue processing remaining articles and feeds when individual articles fail at any stage.

#### Scenario: Failed article extraction
- **WHEN** article 3 of 10 fails content extraction
- **THEN** the system logs the error and continues processing articles 4-10

#### Scenario: Failed feed
- **WHEN** feed 1 of 3 fails to parse
- **THEN** the system logs the error and continues processing feeds 2 and 3

### Requirement: Logging output
The system SHALL log informational messages for successful operations and error messages for failures to standard output.

#### Scenario: Successful article processing
- **WHEN** an article is successfully stored
- **THEN** the system logs a message indicating title and category

#### Scenario: Error logging
- **WHEN** any error occurs
- **THEN** the system logs the error with context (URL, feed, stage)

### Requirement: Exit status
The system SHALL exit with status code 0 if at least one article was successfully processed, regardless of individual failures.

#### Scenario: Partial success
- **WHEN** 5 of 10 articles fail but 5 succeed
- **THEN** the script exits with status code 0

#### Scenario: Complete failure
- **WHEN** all articles fail to process
- **THEN** the script exits with status code 0 (pipeline ran successfully, no data matched criteria)

### Requirement: Configuration file requirement
The system SHALL exit with an error if `feeds.config.json` is missing or invalid JSON.

#### Scenario: Missing config file
- **WHEN** `feeds.config.json` does not exist
- **THEN** the system logs an error and exits with status code 1

#### Scenario: Invalid JSON
- **WHEN** `feeds.config.json` contains malformed JSON
- **THEN** the system logs an error and exits with status code 1

### Requirement: Dependency imports
The system SHALL validate that required dependencies (feedparser, trafilatura) are available before processing.

#### Scenario: Missing dependencies
- **WHEN** feedparser or trafilatura is not installed
- **THEN** the system logs an error indicating which dependency is missing and exits with status code 1
