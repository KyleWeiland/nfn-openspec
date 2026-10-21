# Spec Delta

## MODIFIED Requirements

### Requirement: Required dependencies
The system SHALL include necessary npm dependencies for Astro static site generation.

#### Scenario: Astro core dependency
- **WHEN** package.json is read
- **THEN** astro package MUST be listed in dependencies

#### Scenario: Node version requirement
- **WHEN** package.json is read
- **THEN** engines.node MUST specify version 22.12 or higher
