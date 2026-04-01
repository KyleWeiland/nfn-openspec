## ADDED Requirements

### Requirement: Database file persistence
The workflow SHALL commit the updated articles.db file back to the repository after processing articles.

#### Scenario: Database update commit
- **WHEN** fetch_articles.py updates the articles.db file
- **THEN** the workflow MUST add the file to git staging
- **THEN** the workflow MUST commit the file with message "chore: daily article update [skip ci]"

### Requirement: JSON files persistence
The workflow SHALL commit the updated articles.json and categories.json files back to the repository after export.

#### Scenario: JSON export commit
- **WHEN** export_for_astro.py creates articles.json and categories.json
- **THEN** the workflow MUST add both files to git staging
- **THEN** the workflow MUST commit both files with the database in a single commit

### Requirement: Conditional commits
The workflow SHALL only create a commit if there are actual changes to the data files.

#### Scenario: No changes detected
- **WHEN** the workflow stages data files and git diff shows no changes
- **THEN** the workflow MUST skip the commit step
- **THEN** the workflow MUST log "No changes to commit"

#### Scenario: Changes detected
- **WHEN** the workflow stages data files and git diff shows changes
- **THEN** the workflow MUST create a commit with the updated files
- **THEN** the workflow MUST push the commit to the repository

### Requirement: Dynamic commit message format
The workflow SHALL use a commit message that reflects the trigger type and operation mode, always including [skip ci] tag.

#### Scenario: Scheduled daily run commit
- **WHEN** the workflow runs via cron schedule and creates a commit
- **THEN** the commit message MUST be "chore: daily article update [skip ci]"

#### Scenario: Manual run with fetch commit
- **WHEN** the workflow is manually triggered with skip_fetch=false or unset and creates a commit
- **THEN** the commit message MUST be "chore: manual article update [skip ci]"

#### Scenario: Manual rebuild commit
- **WHEN** the workflow is manually triggered with skip_fetch=true and creates a commit
- **THEN** the commit message MUST be "chore: manual rebuild [skip ci]"

#### Scenario: Commit authorship
- **WHEN** the workflow creates a commit
- **THEN** the git author name MUST be "github-actions[bot]"
- **THEN** the git author email MUST be "github-actions[bot]@users.noreply.github.com"

#### Scenario: Skip CI tag always present
- **WHEN** the workflow creates any commit
- **THEN** the commit message MUST include "[skip ci]" to prevent recursive workflow triggers

### Requirement: Git authentication
The workflow SHALL use the GITHUB_TOKEN for authenticating git operations.

#### Scenario: Authenticated push
- **WHEN** the workflow pushes commits to the repository
- **THEN** it MUST use the automatically provided GITHUB_TOKEN secret
- **THEN** the push MUST succeed without requiring additional credentials

### Requirement: Repository checkout
The workflow SHALL check out the repository with full history to enable git operations.

#### Scenario: Full repository checkout
- **WHEN** the workflow begins
- **THEN** it MUST check out the repository with fetch-depth: 0
- **THEN** it MUST use the GITHUB_TOKEN for checkout authentication
