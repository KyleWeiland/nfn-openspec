## MODIFIED Requirements

### Requirement: Navbar component
The system SHALL provide a two-part navigation: masthead (title + tagline) and section nav bar (category links).

#### Scenario: Masthead rendering
- **WHEN** the Navbar is rendered
- **THEN** it MUST display "NoFrills.news" as a linked title with tagline in a masthead bar

#### Scenario: Section nav rendering
- **WHEN** the Navbar is rendered
- **THEN** it MUST display category links in a separate section nav bar below the masthead

#### Scenario: Desktop layout
- **WHEN** viewed on desktop (768px+)
- **THEN** category links MUST display as inline flow with CSS middot separators

#### Scenario: Mobile layout
- **WHEN** viewed on mobile (<768px)
- **THEN** category links MUST display in a 2-column grid

#### Scenario: Active state
- **WHEN** the user is on a category page or article within a category
- **THEN** the corresponding category link MUST be visually highlighted

### Requirement: ArticleLatest component
The system SHALL provide an ArticleLatest component for prominent article display on the homepage Latest section.

#### Scenario: Content display
- **WHEN** an ArticleLatest is rendered
- **THEN** it MUST display: title (linked to article page), summary hook (1-2 sentences), category label, relative timestamp, and source name

#### Scenario: Lead story sizing
- **WHEN** the first ArticleLatest is rendered in the Latest grid
- **THEN** it MUST span full width with larger title (1.5rem)

### Requirement: ArticleCompact component
The system SHALL provide an ArticleCompact component for category grid sections on the homepage.

#### Scenario: Content display
- **WHEN** an ArticleCompact is rendered
- **THEN** it MUST display: title (linked to article page), source name, and relative timestamp

#### Scenario: No summary
- **WHEN** an ArticleCompact is rendered
- **THEN** it MUST NOT display a summary hook (title-only for density)

### Requirement: ArticleItem component
The system SHALL provide an ArticleItem component for full article listings on category pages.

#### Scenario: Content display
- **WHEN** an ArticleItem is rendered
- **THEN** it MUST display: title (linked to article page), summary hook (clamped to 2 lines), relative timestamp, and source name

#### Scenario: Summary clamping
- **WHEN** a summary hook is displayed
- **THEN** it MUST be clamped to 2 lines using -webkit-line-clamp

### Requirement: RelatedArticles component
The system SHALL provide a RelatedArticles component showing articles from the same category.

#### Scenario: Content display
- **WHEN** RelatedArticles is rendered
- **THEN** it MUST display up to 4 recent articles from the same category, excluding the current article

#### Scenario: Desktop sidebar
- **WHEN** viewport is 1000px or wider
- **THEN** RelatedArticles MUST render as a sticky sidebar with left border

#### Scenario: Mobile stacking
- **WHEN** viewport is narrower than 1000px
- **THEN** RelatedArticles MUST render below the article content with top border

### Requirement: Pagination component
The system SHALL provide a Pagination component with updated styling.

#### Scenario: Styling
- **WHEN** pagination is rendered
- **THEN** it MUST use subtle borders, current page fills with text color, and smaller typography (0.8rem)

## REMOVED Requirements

### ArticleCard component
The ArticleCard component is replaced by ArticleLatest, ArticleCompact, and ArticleItem components which serve distinct layout contexts.

## UNCHANGED Requirements

- Base layout component (BaseLayout)
- Pagination Previous/Next/page number logic
- Footer with site information
- Global CSS loading via BaseLayout
