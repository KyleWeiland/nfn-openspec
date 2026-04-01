## Why

The NoFrills.news platform requires automated daily updates to fetch new articles from Google Alerts RSS feeds and deploy the updated static site to GitHub Pages. Manual execution of the pipeline is not scalable for a news site that needs fresh content daily. Automation ensures consistent updates without manual intervention.

## What Changes

- Create GitHub Actions workflow file at `.github/workflows/daily-build.yml`
- Configure daily cron trigger (6 AM UTC) for automated execution
- Set up manual workflow dispatch for on-demand runs with optional skip_fetch parameter
- Add rebuild-only mode for manual runs that skip article fetching (useful for DB edits or config changes)
- Implement dynamic commit messages that reflect trigger type (scheduled, manual fetch, or manual rebuild)
- Create `scripts/requirements.txt` for Python dependency management
- Automate the full pipeline: fetch → process → export → build → commit → deploy
- Commit updated database and JSON files back to the repository
- Deploy built Astro site to GitHub Pages

## Capabilities

### New Capabilities
- `automated-pipeline`: Daily automated workflow that fetches articles, processes them, builds the static site, and deploys to GitHub Pages
- `data-persistence`: Automatic commit of updated articles.db, articles.json, and categories.json back to the repository after each run
- `github-pages-deployment`: Deployment of the built Astro site to GitHub Pages using official actions

### Modified Capabilities
<!-- No existing capabilities are being modified -->

## Impact

- **New files**:
  - `.github/workflows/daily-build.yml` — GitHub Actions workflow configuration
  - `scripts/requirements.txt` — Python dependency list (feedparser, trafilatura)
- **Repository settings**: Requires GitHub Pages to be enabled and configured to deploy from GitHub Actions
- **Permissions**: Workflow needs `contents: write` for commits, `pages: write` and `id-token: write` for deployment
- **Dependencies**: Uses official GitHub actions (checkout@v4, setup-python@v5, setup-node@v4, configure-pages@v4, upload-pages-artifact@v3, deploy-pages@v4)
- **No breaking changes**: Existing manual pipeline execution remains functional
