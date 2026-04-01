## ADDED Requirements

### Requirement: Astro project initialization
The system SHALL create an Astro project in the `site/` directory at the repository root.

#### Scenario: Project directory creation
- **WHEN** the Astro project is initialized
- **THEN** a `site/` directory MUST exist at repository root with Astro scaffolding

### Requirement: Static output configuration
The system SHALL configure Astro for static output mode with no client-side JavaScript.

#### Scenario: Static output mode
- **WHEN** the Astro config is read
- **THEN** output MUST be set to 'static'

#### Scenario: Zero JavaScript shipping
- **WHEN** the site is built
- **THEN** no JavaScript files MUST be included in the output directory

### Requirement: GitHub Pages base path
The system SHALL configure a base path for GitHub Pages deployment.

#### Scenario: Base path configuration
- **WHEN** the Astro config is read
- **THEN** a base path placeholder MUST be configured for future deployment URL

### Requirement: Required dependencies
The system SHALL include necessary npm dependencies for Astro static site generation.

#### Scenario: Astro core dependency
- **WHEN** package.json is read
- **THEN** astro package MUST be listed in dependencies

#### Scenario: Node version requirement
- **WHEN** package.json is read
- **THEN** engines.node MUST specify version 20 or higher

### Requirement: Build and dev scripts
The system SHALL provide npm scripts for development and production builds.

#### Scenario: Development server script
- **WHEN** npm run dev is executed
- **THEN** a local development server MUST start

#### Scenario: Production build script
- **WHEN** npm run build is executed
- **THEN** static HTML/CSS files MUST be generated in dist/ directory

#### Scenario: Preview script
- **WHEN** npm run preview is executed
- **THEN** the built site MUST be served locally for testing
