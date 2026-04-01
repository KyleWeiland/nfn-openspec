## ADDED Requirements

### Requirement: Daily automated execution
The workflow SHALL execute automatically at 6 AM UTC daily using a cron schedule trigger.

#### Scenario: Scheduled daily run
- **WHEN** the clock reaches 6:00 AM UTC on any day
- **THEN** the workflow executes automatically without manual intervention

### Requirement: Manual trigger capability
The workflow SHALL support manual execution via workflow_dispatch for on-demand updates.

#### Scenario: Manual workflow trigger
- **WHEN** a user triggers the workflow manually from the GitHub Actions UI
- **THEN** the workflow executes immediately with the same steps as scheduled runs

### Requirement: Skip fetch input parameter
The workflow SHALL provide a workflow_dispatch input parameter to skip fetching new articles for rebuild-only scenarios.

#### Scenario: Manual trigger with fetch skipped
- **WHEN** a user triggers the workflow manually with skip_fetch=true
- **THEN** the fetch_articles.py step MUST be skipped
- **THEN** the export, build, commit, and deploy steps MUST still execute

#### Scenario: Manual trigger with fetch enabled
- **WHEN** a user triggers the workflow manually with skip_fetch=false or unset
- **THEN** all steps including fetch_articles.py MUST execute

#### Scenario: Scheduled run ignores skip parameter
- **WHEN** the workflow runs via cron schedule
- **THEN** the fetch step MUST always execute regardless of any input parameter defaults

### Requirement: Pipeline execution sequence
The workflow SHALL execute the following steps in order: fetch articles, export data, build site, commit changes, deploy to Pages.

#### Scenario: Successful pipeline execution
- **WHEN** the workflow runs
- **THEN** it MUST execute fetch_articles.py before export_for_astro.py
- **THEN** it MUST export data before building the Astro site
- **THEN** it MUST build the site before committing data changes
- **THEN** it MUST commit changes before deploying to GitHub Pages

### Requirement: Python environment setup
The workflow SHALL set up Python 3.11+ with pip dependency caching before executing Python scripts.

#### Scenario: Python dependencies installation
- **WHEN** the workflow sets up the Python environment
- **THEN** it MUST install dependencies from scripts/requirements.txt
- **THEN** it MUST use pip caching to speed up subsequent runs

### Requirement: Node.js environment setup
The workflow SHALL set up Node.js 20+ with npm dependency caching before building the Astro site.

#### Scenario: Node.js dependencies installation
- **WHEN** the workflow sets up the Node.js environment
- **THEN** it MUST install dependencies using npm ci in the site/ directory
- **THEN** it MUST use npm caching based on site/package-lock.json

### Requirement: Workflow failure handling
The workflow SHALL fail and halt execution if any critical step fails.

#### Scenario: Python script failure
- **WHEN** fetch_articles.py or export_for_astro.py exits with non-zero status
- **THEN** the workflow MUST fail and not proceed to subsequent steps

#### Scenario: Build failure
- **WHEN** the Astro build command fails
- **THEN** the workflow MUST fail and not commit or deploy

### Requirement: Concurrency control
The workflow SHALL prevent concurrent executions to avoid conflicts during deployment.

#### Scenario: Concurrent workflow prevention
- **WHEN** a workflow is already running
- **THEN** subsequent triggers MUST wait or cancel based on concurrency group configuration
- **THEN** the concurrency group MUST be "pages" to prevent overlapping deployments
