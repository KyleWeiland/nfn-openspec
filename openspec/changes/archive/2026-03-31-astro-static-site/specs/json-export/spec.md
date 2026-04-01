## ADDED Requirements

### Requirement: Articles JSON export
The system SHALL export all articles from SQLite to `data/articles.json`.

#### Scenario: Complete article export
- **WHEN** the export script is executed
- **THEN** all articles in the database MUST be written to data/articles.json

#### Scenario: JSON array format
- **WHEN** articles.json is read
- **THEN** it MUST contain a JSON array of article objects

#### Scenario: Article object structure
- **WHEN** an article is exported
- **THEN** it MUST include id, title, source_url, summary, category, published_date, and slug fields

### Requirement: Categories JSON export
The system SHALL export unique category values to `data/categories.json`.

#### Scenario: Category extraction
- **WHEN** the export script is executed
- **THEN** all unique category values MUST be written to data/categories.json

#### Scenario: JSON array format
- **WHEN** categories.json is read
- **THEN** it MUST contain a JSON array of category strings

#### Scenario: Alphabetical ordering
- **WHEN** categories are exported
- **THEN** they MUST be sorted alphabetically

### Requirement: Date ordering
The system SHALL export articles ordered by published_date descending (newest first).

#### Scenario: Chronological order
- **WHEN** articles.json is read
- **THEN** articles MUST be ordered from newest to oldest by published_date

### Requirement: File overwrite behavior
The system SHALL overwrite existing JSON files on each export.

#### Scenario: Clean export
- **WHEN** the export script is run multiple times
- **THEN** JSON files MUST reflect the current database state, replacing previous exports

### Requirement: Script location and execution
The system SHALL provide the export script at `scripts/export_for_astro.py`.

#### Scenario: Script execution
- **WHEN** a user runs `python scripts/export_for_astro.py`
- **THEN** both JSON files MUST be created or updated in the data/ directory

### Requirement: Data directory creation
The system SHALL create the `data/` directory if it does not exist.

#### Scenario: Missing directory
- **WHEN** data/ does not exist and export runs
- **THEN** the directory MUST be created before writing JSON files
