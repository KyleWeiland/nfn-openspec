## ADDED Requirements

### Requirement: Home page with pagination
The system SHALL provide a home page at `/` displaying all articles with pagination.

#### Scenario: Home page route
- **WHEN** a user visits the root URL
- **THEN** the home page MUST display the first page of articles

#### Scenario: Pagination size
- **WHEN** articles are displayed on any page
- **THEN** a maximum of 20 articles MUST be shown per page

#### Scenario: Newest first ordering
- **WHEN** the home page loads
- **THEN** articles MUST be ordered by published_date descending

#### Scenario: Paginated routes
- **WHEN** there are more than 20 articles
- **THEN** subsequent pages MUST be accessible at /2, /3, etc.

### Requirement: Category filtered pages
The system SHALL provide category-specific pages with pagination.

#### Scenario: Category page route
- **WHEN** a user visits /category/{category}/
- **THEN** only articles matching that category MUST be displayed

#### Scenario: Category pagination
- **WHEN** a category has more than 20 articles
- **THEN** subsequent pages MUST be accessible at /category/{category}/2, /category/{category}/3, etc.

#### Scenario: Category case handling
- **WHEN** a category URL is accessed
- **THEN** the category name MUST match case-insensitively

### Requirement: Individual article pages
The system SHALL provide dedicated pages for each article.

#### Scenario: Article page route
- **WHEN** a user visits /article/{slug}
- **THEN** the full article details MUST be displayed

#### Scenario: Slug-based routing
- **WHEN** an article page is requested
- **THEN** the slug MUST uniquely identify the article

### Requirement: Article card content
The system SHALL display article preview cards on listing pages.

#### Scenario: Card title
- **WHEN** an article card is displayed
- **THEN** it MUST show the article title as a clickable link to the article page

#### Scenario: Card category badge
- **WHEN** an article card is displayed
- **THEN** it MUST show the category as a badge

#### Scenario: Card date
- **WHEN** an article card is displayed
- **THEN** it MUST show the published_date in a human-readable format

#### Scenario: Card summary preview
- **WHEN** an article card is displayed
- **THEN** it MUST show the first 150 characters of the summary

### Requirement: Article page content
The system SHALL display complete article information on article pages.

#### Scenario: Full summary
- **WHEN** an article page loads
- **THEN** the complete summary text MUST be displayed

#### Scenario: Original article link
- **WHEN** an article page loads
- **THEN** a "Read Original Article" button MUST link to source_url with target="_blank"

#### Scenario: Back navigation
- **WHEN** an article page loads
- **THEN** a back link MUST be provided to return to the listing page

### Requirement: 404 handling
The system SHALL provide a 404 page for invalid routes.

#### Scenario: Invalid article slug
- **WHEN** a user visits /article/nonexistent
- **THEN** a 404 page MUST be displayed

#### Scenario: Invalid category
- **WHEN** a user visits /category/nonexistent
- **THEN** a 404 page MUST be displayed
