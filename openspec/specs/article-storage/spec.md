## ADDED Requirements

### Requirement: Database schema
The system SHALL use an SQLite database at `data/articles.db` with an `articles` table containing: id (INTEGER PRIMARY KEY), title (TEXT NOT NULL), source_url (TEXT NOT NULL), summary (TEXT), category (TEXT NOT NULL), published_date (TEXT), slug (TEXT NOT NULL), created_at (TEXT NOT NULL).

#### Scenario: Table creation
- **WHEN** the database file does not exist or lacks the articles table
- **THEN** the system creates the table with the specified schema

#### Scenario: Schema validation
- **WHEN** the database is opened
- **THEN** all required columns MUST be present

### Requirement: Slug generation
The system SHALL generate URL-friendly slugs from article titles by converting to lowercase, replacing spaces and special characters with hyphens, and removing consecutive hyphens.

#### Scenario: Simple title
- **WHEN** title is "Apple Releases New iPhone"
- **THEN** slug becomes "apple-releases-new-iphone"

#### Scenario: Title with special characters
- **WHEN** title is "Breaking: Tech Company's Big Win!"
- **THEN** slug becomes "breaking-tech-companys-big-win"

### Requirement: Title normalization for deduplication
The system SHALL normalize titles for deduplication by converting to lowercase and stripping leading/trailing whitespace.

#### Scenario: Exact match after normalization
- **WHEN** existing title is "Tech News" and new title is " tech news "
- **THEN** the system identifies them as duplicates

### Requirement: Deduplication logic
The system SHALL consider an article a duplicate if both the normalized title and exact source URL match an existing database entry.

#### Scenario: Exact duplicate
- **WHEN** an article has the same normalized title and source URL as an existing entry
- **THEN** the system MUST skip processing and storage

#### Scenario: Same title, different URL
- **WHEN** an article has the same normalized title but different source URL
- **THEN** the system processes and stores it as a new article

#### Scenario: Different title, same URL
- **WHEN** an article has a different title but same source URL
- **THEN** the system MUST skip it as a duplicate

### Requirement: Timestamp format
The system SHALL store created_at timestamps in ISO 8601 format (YYYY-MM-DDTHH:MM:SS).

#### Scenario: Article insertion
- **WHEN** an article is stored
- **THEN** created_at MUST be set to the current UTC time in ISO 8601 format

### Requirement: Transaction handling
The system SHALL use database transactions when inserting articles to ensure data consistency.

#### Scenario: Successful insertion
- **WHEN** an article passes deduplication checks
- **THEN** the system commits the transaction after insertion

#### Scenario: Insertion error
- **WHEN** a database error occurs during insertion
- **THEN** the system MUST roll back the transaction and log the error

### Requirement: Database file location
The system SHALL create the `data/` directory if it does not exist before creating or opening the database.

#### Scenario: Missing data directory
- **WHEN** the `data/` directory does not exist
- **THEN** the system creates it before database operations
