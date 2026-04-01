## ADDED Requirements

### Requirement: Single global stylesheet
The system SHALL use a single global.css file for all styling.

#### Scenario: Global CSS location
- **WHEN** styles are applied
- **THEN** they MUST be loaded from src/styles/global.css

#### Scenario: No CSS framework
- **WHEN** the site is built
- **THEN** no third-party CSS frameworks MUST be included

### Requirement: CSS custom properties for theming
The system SHALL use CSS custom properties for colors, spacing, and typography.

#### Scenario: Color variables
- **WHEN** colors are defined
- **THEN** they MUST use CSS custom properties (e.g., --color-primary)

#### Scenario: Theme switching
- **WHEN** CSS custom properties are used
- **THEN** they MUST enable easy theme modifications

### Requirement: Dark mode support
The system SHALL support dark mode using prefers-color-scheme media query.

#### Scenario: Dark mode detection
- **WHEN** user's system is set to dark mode
- **THEN** dark color scheme MUST be applied automatically

#### Scenario: Light mode default
- **WHEN** user's system is set to light mode
- **THEN** light color scheme MUST be applied

#### Scenario: No JavaScript required
- **WHEN** dark mode is toggled
- **THEN** the transition MUST happen via CSS only, without JavaScript

### Requirement: Typography
The system SHALL use clean, readable typography with monospace or sans-serif fonts.

#### Scenario: Font stack
- **WHEN** text is rendered
- **THEN** it MUST use system fonts or widely available web-safe fonts

#### Scenario: Readable line height
- **WHEN** body text is displayed
- **THEN** line-height MUST be at least 1.5 for readability

#### Scenario: Heading hierarchy
- **WHEN** headings are styled
- **THEN** they MUST have clear visual hierarchy through size and weight

### Requirement: Mobile-first responsive design
The system SHALL use mobile-first CSS with progressive enhancement for larger screens.

#### Scenario: Base styles for mobile
- **WHEN** styles are defined
- **THEN** default styles MUST be optimized for mobile viewports

#### Scenario: Breakpoints
- **WHEN** responsive styles are applied
- **THEN** media queries MUST progressively enhance for tablet and desktop

#### Scenario: Touch targets
- **WHEN** interactive elements are styled on mobile
- **THEN** they MUST have minimum 44x44px touch targets

### Requirement: Color palette
The system SHALL use a muted, high-contrast color palette.

#### Scenario: Background and text contrast
- **WHEN** text is displayed on backgrounds
- **THEN** contrast ratio MUST meet WCAG AA standards (4.5:1)

#### Scenario: Subtle category colors
- **WHEN** category badges are styled
- **THEN** each category MUST have a distinct but muted color

#### Scenario: Link visibility
- **WHEN** links are displayed
- **THEN** they MUST be clearly distinguishable from body text

### Requirement: Readable line lengths
The system SHALL constrain content width for optimal readability.

#### Scenario: Article content width
- **WHEN** article text is displayed
- **THEN** max-width MUST be set to approximately 65-75 characters per line

#### Scenario: Centered layout
- **WHEN** content is narrower than viewport
- **THEN** it MUST be horizontally centered

### Requirement: Minimal visual design
The system SHALL emphasize content over decoration.

#### Scenario: No decorative images
- **WHEN** pages are rendered
- **THEN** no decorative images MUST be included

#### Scenario: Inline SVG icons
- **WHEN** icons are needed
- **THEN** inline SVG icons MAY be used

#### Scenario: Whitespace usage
- **WHEN** layout is styled
- **THEN** generous whitespace MUST separate content sections

### Requirement: Zero client-side JavaScript
The system SHALL implement all styling and interactions with CSS only.

#### Scenario: No JS dependencies
- **WHEN** styles are applied
- **THEN** no JavaScript MUST be required for styling or animations

#### Scenario: CSS-only interactions
- **WHEN** hover, focus, or active states are needed
- **THEN** they MUST be implemented with CSS pseudo-classes
