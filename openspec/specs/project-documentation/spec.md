## ADDED Requirements

### Requirement: README existence and location
The system SHALL have a comprehensive README.md file at the repository root.

#### Scenario: README at repository root
- **WHEN** a developer opens the repository on GitHub or locally
- **THEN** a README.md file MUST be present at the root directory
- **THEN** GitHub MUST automatically display the README on the repository homepage

### Requirement: Project overview section
The README SHALL include a project overview explaining what NoFrills.news is and its purpose.

#### Scenario: Overview content
- **WHEN** a developer reads the project overview section
- **THEN** it MUST describe NoFrills.news as a minimal news aggregation site
- **THEN** it MUST explain that articles are fetched from Google Alerts RSS feeds
- **THEN** it MUST mention the static site is deployed to GitHub Pages

### Requirement: Architecture documentation
The README SHALL include an architecture section with a data flow diagram.

#### Scenario: Architecture diagram
- **WHEN** a developer reads the architecture section
- **THEN** it MUST include an ASCII diagram showing the data flow
- **THEN** the diagram MUST show: RSS → Python → SQLite → JSON → Astro → GitHub Pages
- **THEN** the diagram MUST be clear and easy to understand

### Requirement: Local setup instructions
The README SHALL provide comprehensive local development setup instructions.

#### Scenario: Setup steps documented
- **WHEN** a new developer follows the setup instructions
- **THEN** instructions MUST cover installing Python dependencies
- **THEN** instructions MUST cover installing Node.js dependencies
- **THEN** instructions MUST explain how to use seed data for local development
- **THEN** instructions MUST reference the `run_local.sh` convenience script

### Requirement: Feed management documentation
The README SHALL explain how to add or remove RSS feeds.

#### Scenario: Adding feeds
- **WHEN** a maintainer wants to add a new feed
- **THEN** the README MUST explain editing `feeds.config.json`
- **THEN** the README MUST show the JSON structure for feed entries
- **THEN** the README MUST explain the URL and category fields

#### Scenario: Removing feeds
- **WHEN** a maintainer wants to remove a feed
- **THEN** the README MUST explain removing entries from `feeds.config.json`

### Requirement: CI/CD pipeline documentation
The README SHALL document how the daily automated pipeline works.

#### Scenario: Pipeline description
- **WHEN** a developer reads about the CI/CD pipeline
- **THEN** it MUST explain the daily cron schedule (6 AM UTC)
- **THEN** it MUST describe the workflow steps (fetch, export, build, commit, deploy)
- **THEN** it MUST include a visual diagram of the pipeline flow

#### Scenario: Manual trigger documentation
- **WHEN** a maintainer needs to trigger the workflow manually
- **THEN** the README MUST explain using the GitHub Actions UI
- **THEN** the README MUST explain the `skip_fetch` parameter for rebuild-only runs
- **THEN** the README MUST optionally mention the `gh` CLI command for triggering workflows

### Requirement: Future enhancements section
The README SHALL include a section documenting potential future improvements.

#### Scenario: Enhancement ideas documented
- **WHEN** a contributor reads the future enhancements section
- **THEN** it MUST list potential improvements like Claude Haiku summaries, custom domain, search, RSS output, and dark mode
- **THEN** ideas MUST be presented as possibilities, not commitments
- **THEN** the section MUST encourage contributions

### Requirement: Technology stack documentation
The README SHALL list the key technologies and dependencies used.

#### Scenario: Tech stack listed
- **WHEN** a developer reads the tech stack section
- **THEN** it MUST mention Python 3.11+ with feedparser and trafilatura
- **THEN** it MUST mention Node.js 20+ with Astro
- **THEN** it MUST mention SQLite3 for data storage
- **THEN** it MUST mention GitHub Actions and GitHub Pages for CI/CD and hosting
