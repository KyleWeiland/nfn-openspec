## ADDED Requirements

### Requirement: Base layout component
The system SHALL provide a BaseLayout component for consistent page structure.

#### Scenario: HTML head metadata
- **WHEN** a page uses BaseLayout
- **THEN** it MUST include proper HTML5 doctype, charset, and viewport meta tags

#### Scenario: Page title
- **WHEN** a page uses BaseLayout with a title prop
- **THEN** the HTML title tag MUST be set to the provided title

#### Scenario: Navigation inclusion
- **WHEN** a page uses BaseLayout
- **THEN** it MUST include the Navbar component

#### Scenario: Footer inclusion
- **WHEN** a page uses BaseLayout
- **THEN** it MUST include a footer with basic site information

#### Scenario: Global styles
- **WHEN** a page uses BaseLayout
- **THEN** global.css MUST be loaded

### Requirement: Navbar component
The system SHALL provide a Navbar component for site navigation.

#### Scenario: Site branding
- **WHEN** the Navbar is rendered
- **THEN** it MUST display "NoFrills.news" as a linked site name

#### Scenario: Tagline
- **WHEN** the Navbar is rendered
- **THEN** it MUST display a tagline describing the site

#### Scenario: Category links
- **WHEN** the Navbar is rendered
- **THEN** it MUST display links to all categories from categories.json

#### Scenario: Home link
- **WHEN** the Navbar is rendered
- **THEN** it MUST include a link to the home page

#### Scenario: Mobile responsiveness
- **WHEN** the Navbar is viewed on mobile
- **THEN** category links MUST be horizontally scrollable

#### Scenario: Desktop layout
- **WHEN** the Navbar is viewed on desktop
- **THEN** category links MUST be displayed inline

### Requirement: ArticleCard component
The system SHALL provide an ArticleCard component for article previews.

#### Scenario: Title display
- **WHEN** an ArticleCard is rendered
- **THEN** it MUST display the article title as a clickable link

#### Scenario: Category badge
- **WHEN** an ArticleCard is rendered
- **THEN** it MUST display the category as a styled badge

#### Scenario: Published date
- **WHEN** an ArticleCard is rendered
- **THEN** it MUST display the published_date in a readable format

#### Scenario: Summary excerpt
- **WHEN** an ArticleCard is rendered
- **THEN** it MUST display the first 150 characters of the summary

#### Scenario: Link target
- **WHEN** a user clicks the article title
- **THEN** they MUST navigate to /article/{slug}

### Requirement: Pagination component
The system SHALL provide a Pagination component for page navigation.

#### Scenario: Previous page link
- **WHEN** pagination is rendered and not on first page
- **THEN** a "Previous" link MUST be displayed pointing to the prior page

#### Scenario: Next page link
- **WHEN** pagination is rendered and not on last page
- **THEN** a "Next" link MUST be displayed pointing to the next page

#### Scenario: Current page indicator
- **WHEN** pagination is rendered
- **THEN** the current page number MUST be visually distinct

#### Scenario: Page number links
- **WHEN** pagination is rendered
- **THEN** page number links MUST be displayed for nearby pages

#### Scenario: First page boundary
- **WHEN** pagination is on the first page
- **THEN** no "Previous" link MUST be shown

#### Scenario: Last page boundary
- **WHEN** pagination is on the last page
- **THEN** no "Next" link MUST be shown
