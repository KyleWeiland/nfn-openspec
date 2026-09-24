# Proposal

## Why

On 2026-09-20 `googlenewsdecoder` published 0.2.1, which removed `new_decoderv1`. Our
`googlenewsdecoder>=0.1.0` floor let CI pick it up, and the scheduled runs on Sep 21, 22
and 23 crashed on import. Nobody noticed for three days, and the site stayed stale until
a manual run. Every other Python dependency has only a minimum version too, so any
upstream release can break the pipeline the same way. And a failed scheduled run
currently notifies only whoever last edited the workflow's cron line.

## What Changes

- Split Python dependencies into a human-edited input file (direct dependencies, pinned
  exactly) and a compiled, fully pinned lock file covering every transitive
  dependency. CI and local setup install from the lock file only.
- Pin the site's npm dependencies exactly in `site/package.json` too, at the versions
  `package-lock.json` already resolves, so no installed version changes.
- Add Dependabot for both pip and npm to propose dependency upgrades as grouped weekly
  pull requests, so upgrades happen deliberately rather than at install time.
- Add a pull-request check that installs the locked dependencies and imports every
  pipeline module. A dependency bump that breaks an import fails before merge instead
  of in production.
- When the daily workflow fails, open a GitHub issue (or comment on the existing open
  one) linking the failed run. The next successful run closes it.
- **BREAKING** (developer workflow only): remove the duplicate root `requirements.txt`.
  `scripts/` becomes the only place dependencies are declared. Anyone running
  `pip install -r requirements.txt` from the repo root must use
  `pip install -r scripts/requirements.txt`.

## Capabilities

### New Capabilities

_None._

### Modified Capabilities

- `automated-pipeline`: Python setup installs from a pinned lock file instead of
  floor-only ranges. Adds requirements for a single dependency manifest location,
  validating dependency changes before merge, and reporting workflow failures as a
  GitHub issue that resolves itself on the next success.

## Impact

- **Files added:** `scripts/requirements.in`, `.github/dependabot.yml`,
  `.github/workflows/dependency-check.yml`, `site/.npmrc`
- **Files changed:** `scripts/requirements.txt` (becomes compiled output),
  `site/package.json` and `site/package-lock.json` (exact pins),
  `.github/workflows/daily-build.yml` (issues permission, failure/recovery reporting
  job), `scripts/fetch_articles.py` (install hint path), `README.md`,
  `scripts/README.md`, `docs/architecture-deep-dive.md`, `CLAUDE.md`
- **Files removed:** root `requirements.txt`
- **Tooling:** pip-tools (`pip-compile`) is needed only when regenerating the lock file.
  Neither CI nor normal local setup needs it.
- **Repository settings:** Dependabot version updates must be allowed on the repo, and
  the workflow needs `issues: write`. No new secrets are required.
- **Pipeline behavior:** fetch, extract and summarize logic is unchanged. Package
  versions only change when a lock-file PR is merged.
