## ADDED Requirements

### Requirement: Error handling verification
All Python scripts SHALL have robust error handling for external operations (network, file I/O, subprocess calls).

#### Scenario: Network request error handling
- **WHEN** a script makes an HTTP request
- **THEN** the request MUST be wrapped in try/except
- **THEN** network errors MUST be caught and logged with meaningful messages
- **THEN** the script MUST handle the error gracefully (retry, skip, or exit with clear status)

#### Scenario: File I/O error handling
- **WHEN** a script reads or writes files
- **THEN** file operations MUST be wrapped in try/except
- **THEN** IOError and FileNotFoundError MUST be caught and logged
- **THEN** error messages MUST specify which file caused the error

#### Scenario: Subprocess error handling
- **WHEN** a script invokes external commands
- **THEN** subprocess calls MUST check return codes
- **THEN** non-zero exit codes MUST be logged and handled appropriately

### Requirement: Logging comprehensiveness
All Python scripts SHALL include comprehensive logging at appropriate levels.

#### Scenario: Info-level logging
- **WHEN** a script performs normal operations
- **THEN** it MUST log INFO messages for major steps (e.g., "Processing feed", "Stored article")
- **THEN** INFO logs MUST provide progress visibility without overwhelming output

#### Scenario: Error-level logging
- **WHEN** a script encounters an error
- **THEN** it MUST log ERROR messages with details
- **THEN** ERROR logs MUST include context (what failed, why, what input caused it)

#### Scenario: Debug-level logging
- **WHEN** detailed troubleshooting is needed
- **THEN** DEBUG logs MAY be used for verbose details
- **THEN** DEBUG logs MUST NOT clutter normal operation output

### Requirement: Configuration verification
All configuration values SHALL be externalized (no hardcoded URLs, paths, or magic numbers).

#### Scenario: Feed URLs in configuration
- **WHEN** the system needs RSS feed URLs
- **THEN** URLs MUST come from `feeds.config.json`, not hardcoded in scripts

#### Scenario: File paths as constants or config
- **WHEN** scripts reference file paths
- **THEN** paths MUST be defined as constants at module top or in configuration
- **THEN** paths MUST be relative to repository root or use proper path resolution (e.g., `os.path.join`)

#### Scenario: No magic numbers
- **WHEN** scripts use numeric constants (e.g., page size, timeouts)
- **THEN** values MUST be defined as named constants, not inline literals
- **THEN** constants MUST have descriptive names

### Requirement: Path handling robustness
All file path operations SHALL work correctly from any working directory.

#### Scenario: Relative path resolution
- **WHEN** a script references data files, config files, or output directories
- **THEN** paths MUST be resolved relative to the repository root
- **THEN** scripts MUST work when run from any subdirectory

#### Scenario: Path compatibility
- **WHEN** constructing file paths
- **THEN** scripts MUST use `os.path.join()` or `pathlib.Path` for cross-platform compatibility
- **THEN** hardcoded forward/backslashes MUST be avoided

### Requirement: Gitignore completeness
The `.gitignore` file SHALL cover all generated files and dependency directories.

#### Scenario: Node.js artifacts ignored
- **WHEN** Node.js dependencies are installed
- **THEN** `.gitignore` MUST exclude `node_modules/`
- **THEN** `.gitignore` MUST exclude `.astro/` (Astro cache directory)
- **THEN** `.gitignore` MUST exclude `site/dist/` (build output)

#### Scenario: Python artifacts ignored
- **WHEN** Python code is executed
- **THEN** `.gitignore` MUST exclude `__pycache__/`
- **THEN** `.gitignore` MUST exclude `*.pyc` files
- **THEN** `.gitignore` MUST exclude `.pytest_cache/` (if tests are added)

#### Scenario: Generated data files ignored
- **WHEN** the pipeline exports data
- **THEN** `.gitignore` MUST exclude `data/articles.json` (generated file)
- **THEN** `.gitignore` MUST exclude `data/categories.json` (generated file)
- **THEN** `.gitignore` MUST NOT exclude `data/articles.db` (source of truth, version-controlled)

#### Scenario: Environment files ignored
- **WHEN** developers create local config
- **THEN** `.gitignore` MUST exclude `.env` files
- **THEN** `.gitignore` MUST exclude `.env.local` variants

### Requirement: End-to-end testing
The system SHALL be testable through a manual end-to-end workflow.

#### Scenario: Full pipeline test
- **WHEN** a developer runs the manual end-to-end test
- **THEN** they MUST be able to run seed_data.py (if available)
- **THEN** they MUST run export_for_astro.py successfully
- **THEN** they MUST run the Astro build command successfully
- **THEN** they MUST verify site/dist contains expected output
- **THEN** they MUST run `npm run preview` and spot-check article rendering
