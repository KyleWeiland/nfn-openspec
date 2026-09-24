# Spec Delta

## MODIFIED Requirements

### Requirement: Python environment setup
The workflow SHALL set up Python 3.11+ with pip dependency caching before executing Python scripts, and SHALL install Python dependencies only from a lock file that pins an exact version of every direct and transitive dependency.

#### Scenario: Python dependencies installation
- **WHEN** the workflow sets up the Python environment
- **THEN** it MUST install dependencies from scripts/requirements.txt
- **THEN** it MUST use pip caching to speed up subsequent runs

#### Scenario: Locked versions are installed
- **WHEN** the workflow installs Python dependencies
- **THEN** every installed package MUST match an exact version pinned in scripts/requirements.txt
- **THEN** no package MUST resolve to a version that is not pinned in the lock file

#### Scenario: Upstream release does not change installed versions
- **WHEN** a dependency publishes a new release and the lock file has not been changed
- **THEN** the next workflow run MUST install the same package versions as the previous run

## ADDED Requirements

### Requirement: Single dependency manifest location
Python dependencies SHALL be declared only in the scripts/ directory: a human-edited input file listing direct dependencies, and the compiled lock file generated from it. No other requirements file SHALL exist in the repository.

#### Scenario: Adding a direct dependency
- **WHEN** a maintainer adds a new direct Python dependency
- **THEN** they MUST add it to the input file in scripts/
- **THEN** they MUST regenerate scripts/requirements.txt from the input file in the same change

#### Scenario: No duplicate manifest
- **WHEN** the repository is inspected for Python requirements files
- **THEN** no requirements file MUST exist outside scripts/

### Requirement: Deliberate dependency upgrades
Dependency upgrades SHALL arrive as pull requests that update the lock file, never as a side effect of a workflow run.

#### Scenario: Weekly upgrade proposal
- **WHEN** newer versions of locked Python dependencies are available
- **THEN** an automated pull request MUST be opened, at most weekly, updating the lock file
- **THEN** related upgrades MUST be grouped into a single pull request rather than one per package

### Requirement: Dependency change validation
Any pull request that changes Python dependency files SHALL be validated by installing the locked dependencies on the CI Python version and importing every pipeline module before merge.

#### Scenario: Upgrade removes an API the pipeline uses
- **WHEN** a pull request changes the lock file to a version that removes a function or module the pipeline imports
- **THEN** the validation check MUST fail on that pull request
- **THEN** the failure output MUST name the import that failed

#### Scenario: Compatible upgrade
- **WHEN** a pull request changes the lock file and all pipeline modules import successfully
- **THEN** the validation check MUST pass

#### Scenario: Unrelated pull request
- **WHEN** a pull request does not touch Python dependency files, pipeline scripts or the site
- **THEN** the validation check MUST NOT be required to run

### Requirement: Site dependency change validation
Any pull request that changes the site or its npm dependency files SHALL be validated by installing the locked npm dependencies on the CI Node version and building the site before merge.

#### Scenario: npm upgrade breaks the site build
- **WHEN** a pull request changes site/package.json or site/package-lock.json to versions that fail type checking or the build
- **THEN** the validation check MUST fail on that pull request

#### Scenario: Compatible npm upgrade
- **WHEN** a pull request changes the npm lock file and the site builds successfully
- **THEN** the validation check MUST pass

### Requirement: Failure notification
The daily workflow SHALL report any failed run as a GitHub issue so maintainers are notified without having to check the Actions tab.

#### Scenario: First failure
- **WHEN** a workflow run fails and no open pipeline-failure issue exists
- **THEN** a new issue MUST be opened with a pipeline-failure label
- **THEN** the issue MUST link to the failed run and state its trigger type and commit
- **THEN** the issue MUST @mention every maintainer so each receives a GitHub notification and is subscribed to later updates

#### Scenario: Repeated failure
- **WHEN** a workflow run fails and an open pipeline-failure issue already exists
- **THEN** a comment linking the new failed run MUST be added to that issue
- **THEN** no second issue MUST be opened

#### Scenario: Cancelled run
- **WHEN** a workflow run is cancelled
- **THEN** no issue MUST be opened or commented on

### Requirement: Failure issue resolution
A successful workflow run SHALL close any open pipeline-failure issue.

#### Scenario: Recovery after failure
- **WHEN** a workflow run succeeds and an open pipeline-failure issue exists
- **THEN** a comment linking the successful run MUST be added to the issue
- **THEN** the issue MUST be closed

#### Scenario: Success with no open issue
- **WHEN** a workflow run succeeds and no open pipeline-failure issue exists
- **THEN** no issue activity MUST occur
