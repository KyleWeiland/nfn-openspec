## ADDED Requirements

### Requirement: GitHub Pages configuration
The workflow SHALL configure GitHub Pages environment using the official configure-pages action.

#### Scenario: Pages environment setup
- **WHEN** the workflow prepares for deployment
- **THEN** it MUST use actions/configure-pages@v4 to set up the Pages environment
- **THEN** the configuration MUST complete successfully before artifact upload

### Requirement: Artifact upload
The workflow SHALL upload the built Astro site from site/dist/ as a Pages artifact.

#### Scenario: Built site upload
- **WHEN** the Astro build completes successfully
- **THEN** the workflow MUST upload the site/dist directory using actions/upload-pages-artifact@v3
- **THEN** the artifact MUST be prepared for Pages deployment

### Requirement: Pages deployment
The workflow SHALL deploy the uploaded artifact to GitHub Pages using the official deploy-pages action.

#### Scenario: Successful deployment
- **WHEN** the Pages artifact is uploaded
- **THEN** the workflow MUST use actions/deploy-pages@v4 to deploy
- **THEN** the deployment MUST complete and the site MUST be accessible at the GitHub Pages URL

### Requirement: Deployment permissions
The workflow SHALL request and receive the necessary permissions for GitHub Pages deployment.

#### Scenario: Required permissions
- **WHEN** the workflow is configured
- **THEN** it MUST declare pages: write permission
- **THEN** it MUST declare id-token: write permission for OIDC authentication
- **THEN** it MUST declare contents: write permission for committing data files

### Requirement: Deployment dependency
The workflow SHALL only deploy to GitHub Pages after successfully committing data changes.

#### Scenario: Sequential deployment
- **WHEN** the workflow executes deployment steps
- **THEN** it MUST complete the git commit step before configuring Pages
- **THEN** it MUST complete Pages configuration before uploading artifacts
- **THEN** it MUST complete artifact upload before deploying

### Requirement: Deployment failure handling
The workflow SHALL fail the entire job if deployment to GitHub Pages fails.

#### Scenario: Deployment failure
- **WHEN** the deploy-pages action fails
- **THEN** the workflow job MUST be marked as failed
- **THEN** the failure MUST be visible in the GitHub Actions UI for debugging

### Requirement: Repository Pages configuration
The repository SHALL be configured to deploy from GitHub Actions before the workflow can succeed.

#### Scenario: Pages source configuration
- **WHEN** the workflow attempts to deploy
- **THEN** the repository Settings → Pages → Source MUST be set to "GitHub Actions"
- **THEN** the deployment MUST fail with a clear error if Pages is not properly configured
