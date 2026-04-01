## Context

NoFrills.news is a static news aggregation site built with Astro. Articles are fetched from Google Alerts RSS feeds, processed with Python (feedparser + trafilatura), stored in SQLite, exported to JSON, and built into a static site deployed on GitHub Pages.

Currently, the pipeline must be run manually. For a news site to stay current, daily automation is essential. GitHub Actions is already integrated with GitHub Pages and provides free CI/CD for public repositories.

**Current State:**
- Python scripts exist: `scripts/fetch_articles.py` (fetch + process) and `scripts/export_for_astro.py` (SQLite → JSON)
- Astro site in `site/` directory with `npm run build` command
- Database and JSON files are committed to the repo at `data/`
- No automation exists

**Constraints:**
- Must use GitHub-hosted runners (ubuntu-latest)
- Must preserve existing manual execution capability
- Must not trigger recursive workflows
- Must only deploy when site successfully builds

## Goals / Non-Goals

**Goals:**
- Automate daily article fetching and site deployment
- Persist updated data (articles.db, JSON files) back to the repository
- Deploy updated static site to GitHub Pages
- Support manual triggering for testing/urgent updates
- Use dependency caching to minimize workflow execution time

**Non-Goals:**
- Custom runner configuration or self-hosted runners
- Deployment to platforms other than GitHub Pages
- Notifications or alerting (can be added later)
- Parallel processing of multiple feeds (current script is sequential)

## Decisions

### 1. Workflow Orchestration: Single Job vs. Multiple Jobs
**Decision:** Use a single job (`fetch-and-build`) with sequential steps.

**Rationale:**
- Steps have clear dependencies: fetch → export → build → commit → deploy
- Data flows through shared filesystem (SQLite DB, JSON files, built artifacts)
- Splitting into jobs would require artifact passing, adding complexity and latency
- Single job simplifies debugging and reduces workflow execution time

**Alternative Considered:** Separate jobs for fetch/process, build, and deploy
- Rejected because artifact upload/download overhead outweighs benefits
- Would complicate error handling if intermediate steps fail

### 2. Data Persistence: Git Commit vs. External Storage
**Decision:** Commit updated `data/articles.db`, `data/articles.json`, and `data/categories.json` back to the repository.

**Rationale:**
- Aligns with current architecture (DB is already in repo)
- Provides version history and easy rollback
- No external storage costs or configuration needed
- Database grows slowly (news articles, <100MB over years)

**Alternative Considered:** Store database in GitHub Artifacts or external blob storage
- Rejected: Adds complexity, costs, and breaks existing local development workflow

### 3. Preventing Recursive Workflows: [skip ci] Tag
**Decision:** Use `[skip ci]` in commit message: "chore: daily article update [skip ci]"

**Rationale:**
- Standard GitHub Actions convention to prevent workflow re-triggering
- Prevents infinite loop when workflow commits back to repo
- Simple and well-documented approach

**Alternative Considered:** Branch filtering or path-based triggers
- Rejected: More complex, harder to debug, less explicit

### 4. Deployment: Commit Before Deploy vs. Deploy First
**Decision:** Commit data changes before deploying to GitHub Pages.

**Rationale:**
- Ensures data persistence even if deployment fails
- Maintains consistency: repo state matches deployed site
- Easier rollback: just revert the commit

**Alternative Considered:** Deploy first, then commit
- Rejected: Site might deploy but data loss occurs if commit fails
- Current approach prioritizes data integrity

### 5. Dependency Caching: Strategy
**Decision:** Cache both pip dependencies (`cache: 'pip'`) and npm dependencies (`cache: 'npm'`).

**Rationale:**
- Reduces workflow runtime by 30-60 seconds per run
- Official actions support these cache keys natively
- Minimal configuration required

**Alternative Considered:** No caching or custom cache key
- Rejected: Unnecessary runtime overhead and cost

### 6. Permissions: Least Privilege
**Decision:** Request only required permissions:
- `contents: write` — for git commits
- `pages: write` — for Pages deployment
- `id-token: write` — for OIDC authentication with Pages

**Rationale:**
- Security best practice (least privilege)
- GitHub requires explicit permissions for Pages deployment
- Scoped tokens reduce risk if compromised

### 7. Rebuild-Only Mode: Workflow Input vs. Separate Workflow
**Decision:** Add a `skip_fetch` boolean input parameter to `workflow_dispatch` instead of creating a separate workflow.

**Rationale:**
- Supports manual DB edits or config changes that require rebuild without fetching new articles
- Single workflow file easier to maintain than duplicating steps across two workflows
- GitHub Actions UI provides clear checkbox when manually triggering
- Cron schedule always runs full pipeline (inputs default to false for scheduled runs)
- Conditional step execution (`if: ${{ !inputs.skip_fetch }}`) is simple and explicit

**Alternative Considered:** Separate `rebuild-deploy.yml` workflow
- Rejected: Would duplicate Node.js setup, build, and deploy steps
- Harder to keep both workflows in sync when making changes

### 8. Dynamic Commit Messages: Contextual vs. Static
**Decision:** Generate commit message dynamically based on trigger type and skip_fetch input.

**Rationale:**
- Commit history should clearly indicate whether update was scheduled, manual fetch, or manual rebuild
- Makes troubleshooting easier (can see at a glance what type of run created a commit)
- Three distinct messages:
  - `"chore: daily article update [skip ci]"` — scheduled cron
  - `"chore: manual article update [skip ci]"` — manual trigger with fetch
  - `"chore: manual rebuild [skip ci]"` — manual trigger without fetch

**Implementation:**
- Use `${{ github.event_name }}` to detect scheduled vs. manual trigger
- Use `${{ inputs.skip_fetch }}` to detect rebuild-only mode
- Shell script logic constructs appropriate message before commit

**Alternative Considered:** Static "article update" message for all triggers
- Rejected: Loses valuable context in git history

## Risks / Trade-offs

### Risk: Workflow Failure During Article Fetch
**Impact:** No updates for that day, stale content.

**Mitigation:**
- Manual trigger (`workflow_dispatch`) allows immediate retry
- Fetch script has error handling and logging
- Next day's cron run will fetch new articles (no data loss)

### Risk: Database Merge Conflicts
**Impact:** If someone commits to `data/articles.db` manually while workflow runs, merge conflict occurs.

**Mitigation:**
- **Unlikely scenario:** Only workflow should modify database in practice
- Workflow uses `git pull` before commit (if needed in future)
- Document in README: avoid manual database commits

### Risk: GitHub Pages Deployment Failure
**Impact:** Site not updated, but data is committed.

**Mitigation:**
- Workflow fails visibly in Actions tab
- Manual re-run can retry deployment step
- Data is already saved, only deployment needs retry

### Trade-off: Database in Repository
**Pro:** Simple, version-controlled, no external dependencies.

**Con:** Repository grows over time (albeit slowly), not ideal for very large datasets.

**Justification:** For a news aggregation site, database growth is manageable (~1-5MB/month for typical article volume). Git LFS can be added later if needed.

### Trade-off: Daily Cron vs. Hourly
**Decision:** Daily at 6 AM UTC.

**Rationale:**
- News aggregation doesn't require minute-by-minute updates
- Reduces GitHub Actions usage (cost for private repos)
- Aligns with RSS feed update frequency (most feeds update daily)

**Future Consideration:** If real-time news is needed, switch to hourly or event-driven triggers.

## Migration Plan

### Deployment Steps
1. **Merge workflow file:** Add `.github/workflows/daily-build.yml` and `scripts/requirements.txt` to main branch
2. **Enable GitHub Pages:**
   - Go to repository Settings → Pages
   - Set Source to "GitHub Actions"
3. **Verify permissions:** Ensure workflow has required permissions (GitHub auto-grants for Actions-based Pages)
4. **Test workflow:**
   - Trigger manually via Actions tab → "Daily Article Update and Deployment" → "Run workflow"
   - Monitor execution in Actions tab
   - Verify commit appears in repo history
   - Verify site deploys to GitHub Pages

### Rollback Strategy
- **If workflow fails:** Delete `.github/workflows/daily-build.yml`, revert to manual execution
- **If deployment broken:** Revert commit, redeploy previous version
- **If data corruption:** Restore from previous commit (database is version-controlled)

### Post-Deployment Verification
- Check Actions tab for successful green checkmark
- Verify `data/` directory updated with new articles
- Visit GitHub Pages URL to confirm site reflects new content
- Monitor for 2-3 days to ensure stability

## Open Questions

**None.** All technical decisions are resolved. Implementation can proceed.
