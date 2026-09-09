## MODIFIED Requirements

### Requirement: Home page structure
The system SHALL provide a homepage that functions as a newspaper front page with Latest section and category grid.

#### Scenario: Latest section
- **WHEN** a user visits the root URL
- **THEN** the top section MUST display the 5 most recent articles with full prominence (title, hook, category, time, source)

#### Scenario: Lead story
- **WHEN** the Latest section is rendered on desktop
- **THEN** the first article MUST span full width with larger typography

#### Scenario: Category grid
- **WHEN** the homepage is rendered below the Latest section
- **THEN** all categories MUST be displayed as sections, each showing 2–3 most recent headlines with "View all" links

#### Scenario: No pagination on homepage
- **WHEN** the homepage is rendered
- **THEN** there MUST NOT be pagination controls (homepage is a curated front page)

### Requirement: Category page with article count
The system SHALL display article count and page info on category pages.

#### Scenario: Page header
- **WHEN** a category page is rendered
- **THEN** it MUST display the category name, total article count, and "Page X of Y"

#### Scenario: 2-column article grid
- **WHEN** a category page is viewed on desktop (900px+)
- **THEN** article items MUST display in a 2-column grid layout

### Requirement: Article page with related content
The system SHALL display related articles from the same category on article pages.

#### Scenario: Related articles
- **WHEN** an article page is rendered
- **THEN** it MUST display up to 4 recent articles from the same category (excluding current)

#### Scenario: Back navigation
- **WHEN** an article page is rendered
- **THEN** the back link MUST navigate to the article's category page (not the home page)

#### Scenario: Source attribution
- **WHEN** an article page is rendered
- **THEN** it MUST display the source domain name in the article byline

#### Scenario: Source link container
- **WHEN** an article page is rendered
- **THEN** it MUST display the source link in a visually distinct container with label "Read the original article"

## UNCHANGED Requirements

- Category filtered pages at /category/{category}/ with pagination (20 per page)
- Category case-insensitive matching
- Individual article pages at /article/{slug}
- Slug-based routing
- Full summary display on article pages
- Original article link (source_url) with target="_blank"
- 404 handling for invalid routes
- 20 articles per page on category pages
- Newest-first ordering
