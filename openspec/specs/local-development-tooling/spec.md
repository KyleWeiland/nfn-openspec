## ADDED Requirements

### Requirement: Local development convenience script
The system SHALL provide a convenience script at `scripts/run_local.sh` that automates the local development workflow.

#### Scenario: Running local development script
- **WHEN** a developer executes `./scripts/run_local.sh`
- **THEN** the script MUST export articles from SQLite to JSON using `export_for_astro.py`
- **THEN** the script MUST start the Astro development server in the `site/` directory

### Requirement: Script executable permissions
The `run_local.sh` script SHALL be executable without requiring manual chmod.

#### Scenario: Script is committed with execute permissions
- **WHEN** the script is checked into version control
- **THEN** it MUST have executable permissions set (`chmod +x`)
- **THEN** developers can run it immediately after cloning the repository

### Requirement: Cross-platform compatibility
The script SHALL work on Unix-like systems (Linux, macOS) and Windows with Git Bash.

#### Scenario: Running on Unix systems
- **WHEN** a developer runs the script on Linux or macOS
- **THEN** the script MUST execute successfully

#### Scenario: Running on Windows with Git Bash
- **WHEN** a developer runs the script using Git Bash on Windows
- **THEN** the script MUST execute successfully

### Requirement: Clear output messages
The script SHALL provide clear status messages during execution.

#### Scenario: Script execution with status messages
- **WHEN** the script runs
- **THEN** it MUST print a message before exporting JSON
- **THEN** it MUST print a message before starting the dev server
- **THEN** status messages MUST be human-readable and helpful

### Requirement: Error handling
The script SHALL handle errors gracefully and provide meaningful error messages.

#### Scenario: Python export fails
- **WHEN** `export_for_astro.py` fails during execution
- **THEN** the script MUST display an error message
- **THEN** the script MUST exit with a non-zero status code
- **THEN** the Astro dev server MUST NOT start

#### Scenario: Astro dev server fails to start
- **WHEN** the Astro dev server fails to start
- **THEN** the script MUST display an error message indicating the failure
- **THEN** the script MUST exit with a non-zero status code
