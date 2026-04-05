## MODIFIED Requirements

### Requirement: Article object structure with source name
The system SHALL include a `source_name` field in exported article objects.

#### Scenario: Source name extraction
- **WHEN** an article is exported
- **THEN** it MUST include a `source_name` field containing the domain name extracted from `source_url` (with www. prefix stripped)

#### Scenario: Title cleaning
- **WHEN** an article is exported
- **THEN** the `title` field MUST have the " - Source" suffix removed (splitting on the last ` - ` delimiter)

#### Scenario: Article object fields
- **WHEN** an article is exported
- **THEN** it MUST include id, title (cleaned), source_url, source_name, summary, category, published_date, and slug fields

## UNCHANGED Requirements

- Articles JSON export to data/articles.json
- JSON array format
- Categories JSON export to data/categories.json
- Alphabetical category ordering
- Date ordering (newest first)
- File overwrite behavior
- Script at scripts/export_for_astro.py
- Data directory creation
