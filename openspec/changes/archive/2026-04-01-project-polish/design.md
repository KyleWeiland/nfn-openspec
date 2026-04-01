## Context

NoFrills.news has a working CI/CD pipeline and functional site, but lacks developer-facing polish. New contributors (or the original developer returning later) would struggle to understand the project architecture, set up a local environment, or contribute confidently.

**Current State:**
- Python pipeline scripts work but require manual JSON export before local Astro preview
- No unified local development workflow
- No project documentation beyond code comments and CLAUDE.md (AI-facing, not user-facing)
- No systematic verification of error handling, logging, or configurability
- .gitignore exists but may have gaps

**Constraints:**
- Must maintain compatibility with existing GitHub Actions workflow
- Documentation should be accessible to developers unfamiliar with the project
- Scripts must work cross-platform (Windows, Linux, macOS where possible)

## Goals / Non-Goals

**Goals:**
- Provide one-command local development workflow (`./scripts/run_local.sh`)
- Create comprehensive, user-friendly README for onboarding and reference
- Verify code quality through systematic review (error handling, logging, paths, configurability)
- Test end-to-end pipeline to catch integration issues
- Document future enhancement opportunities to guide evolution

**Non-Goals:**
- Refactoring or rewriting existing functional code (unless critical issues found)
- Implementing future enhancements (only documenting them)
- Creating developer guides beyond README (keep it concise)
- Automated testing framework (manual end-to-end test is sufficient for now)

## Decisions

### 1. Local Development Script: Bash vs. Python vs. Make
**Decision:** Use Bash script (`scripts/run_local.sh`) for simplicity.

**Rationale:**
- Bash is already used in GitHub Actions workflow
- Simple two-step process: export JSON, start Astro dev server
- No additional dependencies beyond what's already required
- Most developers have bash (Git Bash on Windows, native on Unix)

**Alternative Considered:** Python script
- Rejected: Overkill for two shell commands, adds Python invocation overhead

**Alternative Considered:** Makefile
- Rejected: Make not universally installed on Windows, adds learning curve

### 2. README Structure: Single File vs. Multiple Docs
**Decision:** Single comprehensive README.md at repository root.

**Rationale:**
- Project is small enough for single-file documentation
- Easier to search and navigate for new contributors
- GitHub displays README.md by default
- Can be scanned quickly to understand entire project

**Sections:**
1. Project overview (what it is, why it exists)
2. Architecture diagram (ASCII art showing data flow)
3. Quick start (get running fast)
4. Local development (setup, run_local.sh, seed data)
5. Adding/removing feeds (edit feeds.config.json)
6. CI/CD (how daily updates work, manual triggers)
7. Future enhancements (roadmap ideas)

**Alternative Considered:** Separate docs/ directory with multiple files
- Rejected: Adds navigation complexity, risk of docs getting out of sync

### 3. Code Review Scope: Full Rewrite vs. Targeted Review
**Decision:** Targeted code review focusing on production readiness concerns.

**Rationale:**
- Code is already functional and deployed
- Focus on robustness: error handling, logging, path handling
- Verify configurability: no hardcoded values that should be in config
- Check .gitignore completeness

**Review Checklist:**
- Error handling: All external calls (network, file I/O, subprocess) wrapped in try/except with meaningful errors
- Logging: INFO for progress, ERROR for failures, DEBUG for details
- File paths: All paths relative to repo root or use proper path resolution
- Configurability: No hardcoded URLs, paths, or magic numbers (should be in feeds.config.json or constants)
- .gitignore: Covers node_modules, __pycache__, .astro, dist, data/*.json (generated), .env

**Alternative Considered:** Full refactoring pass
- Rejected: Functional code shouldn't be rewritten without clear bugs or requirements

### 4. End-to-End Testing: Automated vs. Manual
**Decision:** Manual end-to-end test with documented steps.

**Rationale:**
- Project is small, automated testing infrastructure would be overkill
- Manual test validates the most critical path: data flow through entire pipeline
- Serves as smoke test before relying on daily automation

**Test Steps:**
1. Run `python scripts/seed_data.py` (if exists, otherwise skip)
2. Run `python scripts/export_for_astro.py`
3. Run `cd site && npm run build`
4. Verify site/dist contains expected files
5. Run `npm run preview` and spot-check article rendering

**Alternative Considered:** Pytest + GitHub Actions test workflow
- Rejected: Over-engineering for current project scale, adds maintenance burden

### 5. Future Enhancements: Section in README vs. Separate Roadmap
**Decision:** Brief "Future Enhancements" section in README.

**Rationale:**
- Keeps ideas visible and accessible
- Encourages contributions
- Doesn't commit to a timeline (just possibilities)

**Ideas to Document:**

**Content Aggregation Upgrade:**
- Replace Google Alerts RSS with GNews API for better quality control
- Benefits: language filtering, date range control, country targeting, website exclusion
- Tradeoff: requires API key and rate limits, but filtering is upstream vs. per-article checks
- Can filter inaccessible articles, wrong language, low-quality sources

**Article Processing Improvements:**
- Replace trafilatura with Newspaper4k for built-in NLP summarization
- Trafilatura only extracts text; Newspaper4k generates actual summaries
- Add HTML tag cleanup in article titles (currently including raw HTML tags)
- Implement smart deduplication: title + URL + date-aware checking
  - Same title within 30-day window → duplicate
  - Same title 6+ months apart → different story, keep both
  - Configurable window_days parameter

**AI-Powered Summaries (Premium Option):**
- Claude Haiku API for high-quality abstractive summaries
- Cost analysis: ~1,350 articles/month × ~2K tokens = ~$0.75/month (trivial)
- Hybrid approach: Newspaper4k first, fall back to Claude for failures
- Alternative: Use as premium upgrade path when quality matters most

**Frontend Redesign:**
- Visual polish while maintaining core tenets (no images/ads, zero JS)
- Improved typography (font choices, sizing, line-height)
- Better spacing and whitespace design
- Refined color palette beyond basic styles
- Enhanced card design for articles (shadows, borders, hover states)
- Category badge styling improvements
- Dark mode support (user toggle)

**Additional Features:**
- Custom domain (instead of github.io)
- Client-side search (lunr.js or similar)
- RSS feed output for the site itself
- Category filtering on homepage

## Risks / Trade-offs

### Risk: run_local.sh Won't Work on Windows
**Impact:** Windows developers can't use convenience script.

**Mitigation:**
- Git Bash (bundled with Git for Windows) can run bash scripts
- README provides manual alternative: run commands individually
- Consider .bat or PowerShell version in future if demand exists

### Risk: Code Review Misses Critical Issues
**Impact:** Bugs discovered in production after daily automation starts.

**Mitigation:**
- Manual end-to-end test catches integration issues
- GitHub Actions will fail visibly if pipeline breaks
- Database is version-controlled, easy to rollback

### Trade-off: Single README vs. Wiki
**Pro:** Single file is easier to maintain and search.

**Con:** May become unwieldy if project grows significantly.

**Justification:** Current project scope fits comfortably in a single README. Can split later if needed.

### Trade-off: Manual Testing vs. Automated Tests
**Pro:** Quick to execute, validates the most critical path.

**Con:** Not repeatable in CI, relies on human diligence.

**Justification:** For a personal project with daily automation, manual test is sufficient. Automated testing can be added if project becomes multi-contributor.

## Migration Plan

### Deployment Steps
1. Create `scripts/run_local.sh` and make executable
2. Write README.md at repository root
3. Perform code review pass, fix any issues found
4. Update .gitignore if gaps found
5. Run manual end-to-end test
6. Commit all changes with message documenting the polish work

### Verification
- Test `./scripts/run_local.sh` on local machine
- Read through README as if you're a new contributor (clarity check)
- Verify .gitignore by running `git status` after build (should show no unwanted files)
- Check GitHub Pages site for any regressions after deploy

### Rollback Strategy
- If README or scripts cause confusion: revert specific files
- If code changes break pipeline: revert to previous commit, CI will redeploy working version
- No data migration or schema changes, so rollback is low-risk

## Open Questions

**None.** All decisions are resolved. Implementation can proceed.
