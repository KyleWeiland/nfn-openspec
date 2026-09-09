## MODIFIED Requirements

### Requirement: Wide fluid layout
The system SHALL use a fluid layout with 1200px max-width instead of character-based width.

#### Scenario: Page max-width
- **WHEN** any page is rendered
- **THEN** the content container MUST have a max-width of 1200px

#### Scenario: Fluid width
- **WHEN** viewport is narrower than 1200px
- **THEN** content MUST fill 94% of the viewport width

#### Scenario: Reading column constraint
- **WHEN** article body text is displayed
- **THEN** the reading column MUST be constrained to 72ch for comfortable line lengths

### Requirement: Newspaper-style section headers
The system SHALL use section headers with bold rules to delineate content areas.

#### Scenario: Section header styling
- **WHEN** a section header is rendered
- **THEN** it MUST have a 2px solid bottom border, uppercase title text, and 0.85rem font size

#### Scenario: Section header with link
- **WHEN** a section header includes a navigation link
- **THEN** the link MUST be right-aligned with smaller muted text (e.g., "All articles →")

### Requirement: Divider-separated list items
The system SHALL use subtle dividers between article list items instead of bordered cards.

#### Scenario: Article item separation
- **WHEN** articles are listed on any page
- **THEN** they MUST be separated by 1px light border-bottom dividers

#### Scenario: No card borders
- **WHEN** article items are rendered
- **THEN** they MUST NOT have surrounding border, box-shadow, or border-radius

### Requirement: Responsive grid layouts
The system SHALL use CSS Grid for multi-column layouts at appropriate breakpoints.

#### Scenario: Homepage category grid
- **WHEN** viewport is 1100px or wider
- **THEN** category sections MUST display in a 3-column grid

#### Scenario: Homepage category grid tablet
- **WHEN** viewport is 768px–1099px
- **THEN** category sections MUST display in a 2-column grid

#### Scenario: Category page article grid
- **WHEN** viewport is 900px or wider on category pages
- **THEN** article items MUST display in a 2-column grid

#### Scenario: Mobile single column
- **WHEN** viewport is narrower than 768px
- **THEN** all content MUST display in a single column

### Requirement: Category navigation styling
The system SHALL style category navigation as inline text with middot separators on desktop and a 2-column grid on mobile.

#### Scenario: Desktop nav separators
- **WHEN** category nav is rendered on desktop (768px+)
- **THEN** items MUST be inline with CSS-generated middot (·) separators between them

#### Scenario: Mobile nav grid
- **WHEN** category nav is rendered on mobile (<768px)
- **THEN** items MUST display in a 2-column grid with all categories visible

#### Scenario: Nav typography
- **WHEN** category nav links are rendered
- **THEN** they MUST use uppercase text, 0.7rem font size, and 600 font weight

### Requirement: Masthead styling
The system SHALL style the site masthead as a newspaper nameplate.

#### Scenario: Masthead border
- **WHEN** the masthead is rendered
- **THEN** it MUST have a 3px solid bottom border

#### Scenario: Masthead title
- **WHEN** the site title is displayed
- **THEN** it MUST use 1.75rem, weight 800, with tight letter-spacing (-0.03em)

## UNCHANGED Requirements

- Single global stylesheet (global.css)
- CSS custom properties for theming
- Dark mode support via prefers-color-scheme (no toggle)
- Typography with system font stack
- Mobile-first responsive design
- WCAG AA contrast ratios
- Zero client-side JavaScript for styling
- Minimal visual design (no decorative images)
- Touch targets minimum 44x44px on mobile
