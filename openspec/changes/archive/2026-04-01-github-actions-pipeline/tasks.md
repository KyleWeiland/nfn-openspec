## 1. Setup and Prerequisites

- [x] 1.1 Create .github/workflows directory in repository root
- [x] 1.2 Create scripts/requirements.txt with Python dependencies (feedparser>=6.0.0, trafilatura>=1.6.0)

## 2. Workflow File Creation

- [x] 2.1 Create .github/workflows/daily-build.yml file
- [x] 2.2 Add workflow name "Daily Article Update and Deployment"
- [x] 2.3 Configure cron schedule trigger for daily execution at 6 AM UTC (0 6 * * *)
- [x] 2.4 Add workflow_dispatch trigger for manual execution
- [x] 2.5 Add skip_fetch boolean input to workflow_dispatch with default false
- [x] 2.6 Set permissions: contents: write, pages: write, id-token: write
- [x] 2.7 Configure concurrency control with group "pages" and cancel-in-progress: false

## 3. Repository Checkout Step

- [x] 3.1 Add checkout step using actions/checkout@v4
- [x] 3.2 Configure fetch-depth: 0 for full history
- [x] 3.3 Configure token: ${{ secrets.GITHUB_TOKEN }}

## 4. Python Environment Setup

- [x] 4.1 Add Python setup step using actions/setup-python@v5
- [x] 4.2 Configure python-version: '3.11'
- [x] 4.3 Configure cache: 'pip' for dependency caching
- [x] 4.4 Configure cache-dependency-path: 'scripts/requirements.txt'
- [x] 4.5 Add step to install Python dependencies with pip install -r scripts/requirements.txt

## 5. Article Fetch and Export Steps

- [x] 5.1 Add step to run python scripts/fetch_articles.py
- [x] 5.2 Add conditional to fetch step: if: ${{ !inputs.skip_fetch }}
- [x] 5.3 Add step to run python scripts/export_for_astro.py

## 6. Node.js Environment Setup

- [x] 6.1 Add Node.js setup step using actions/setup-node@v4
- [x] 6.2 Configure node-version: '20'
- [x] 6.3 Configure cache: 'npm' for dependency caching
- [x] 6.4 Configure cache-dependency-path: 'site/package-lock.json'
- [x] 6.5 Add step to install Node dependencies with npm ci in site/ directory

## 7. Astro Site Build

- [x] 7.1 Add step to build Astro site with npm run build in site/ directory

## 8. Data Persistence (Git Commit)

- [x] 8.1 Add step to configure git user.name as 'github-actions[bot]'
- [x] 8.2 Add step to configure git user.email as 'github-actions[bot]@users.noreply.github.com'
- [x] 8.3 Add git add command for data/articles.db, data/articles.json, data/categories.json
- [x] 8.4 Add conditional logic to check if there are changes (git diff --cached --quiet)
- [x] 8.5 Add dynamic commit message logic based on github.event_name and inputs.skip_fetch
- [x] 8.6 Set COMMIT_MSG to "chore: daily article update [skip ci]" for schedule trigger
- [x] 8.7 Set COMMIT_MSG to "chore: manual article update [skip ci]" for manual trigger with fetch
- [x] 8.8 Set COMMIT_MSG to "chore: manual rebuild [skip ci]" for manual trigger without fetch
- [x] 8.9 Add git commit command using $COMMIT_MSG variable
- [x] 8.10 Add git push command (only executes if changes exist)

## 9. GitHub Pages Deployment

- [x] 9.1 Add step to configure GitHub Pages using actions/configure-pages@v4
- [x] 9.2 Add step to upload Pages artifact using actions/upload-pages-artifact@v3 with path: 'site/dist'
- [x] 9.3 Add step to deploy to GitHub Pages using actions/deploy-pages@v4 with id: deployment

## 10. Testing and Verification

- [x] 10.1 Commit workflow file to repository
- [x] 10.2 Enable GitHub Pages in repository settings with Source: "GitHub Actions"
- [x] 10.3 Trigger workflow manually via GitHub Actions UI
- [x] 10.4 Verify workflow completes successfully in Actions tab
- [x] 10.5 Verify data files (articles.db, articles.json, categories.json) are committed
- [x] 10.6 Verify site is deployed and accessible at GitHub Pages URL
- [x] 10.7 Monitor cron-triggered run the next day to ensure scheduled execution works
