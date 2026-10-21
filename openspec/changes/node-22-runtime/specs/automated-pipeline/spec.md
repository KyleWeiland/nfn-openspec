# Spec Delta

## MODIFIED Requirements

### Requirement: Node.js environment setup
The workflow SHALL set up Node.js 22+ with npm dependency caching before building the Astro site.

#### Scenario: Node.js dependencies installation
- **WHEN** the workflow sets up the Node.js environment
- **THEN** it MUST install dependencies using npm ci in the site/ directory
- **THEN** it MUST use npm caching based on site/package-lock.json

#### Scenario: Supported Node.js release
- **WHEN** the workflow sets up the Node.js environment
- **THEN** it MUST request a Node.js major version that is still receiving security fixes
- **THEN** the same major version MUST be used by every workflow that builds the site
