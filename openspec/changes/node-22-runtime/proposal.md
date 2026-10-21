# Proposal

## Why

Both workflows build the site on Node 20, which reached end of life on 2026-04-30 and
no longer receives security fixes. GitHub will drop it from the runner images at some
point, which would turn every daily run red on a day of GitHub's choosing. It is also
the first prerequisite for the planned Astro upgrade: Astro 5.18 still runs on Node 20,
but Astro 6 and 7.0 require Node 22.12 and Astro 7.4 requires 22.22. Moving the runtime
on its own, before any Astro change, keeps the two risks apart: if the next daily run
fails, there is exactly one thing that changed.

## What Changes

- `daily-build.yml` and `dependency-check.yml` set up Node 22 instead of Node 20.
- `site/package.json` raises `engines.node` to `>=22.12.0`, the floor the planned
  Astro versions need, so a local build on an older Node warns at `npm ci` time.
- README, CLAUDE.md and the architecture deep-dive say Node 22.
- Three main specs that pinned "Node.js 20+" now say Node.js 22+. The
  `project-documentation` tech-stack requirement is restated in full, so its stale
  "feedparser and trafilatura" line is corrected to gnews and Newspaper4k at the same
  time; the current README already says that.

No application code changes. Astro stays at 4.16.19 in this change.

## Capabilities

### New Capabilities

_None._

### Modified Capabilities

- `automated-pipeline`: the workflow's Node.js environment is 22+ rather than 20+.
- `astro-project-setup`: `engines.node` requires 22.12 or higher.
- `project-documentation`: the tech-stack section names Node.js 22+ and the current
  Python libraries.

## Impact

- **Files changed:** `.github/workflows/daily-build.yml`,
  `.github/workflows/dependency-check.yml`, `site/package.json`, `README.md`,
  `CLAUDE.md`, `docs/architecture-deep-dive.md`
- **Verification:** Dependency Check runs on workflow changes, so the PR's `site-build`
  job itself builds on Node 22. After merge, a manual `workflow_dispatch` with
  `skip_fetch` exercises the daily workflow on Node 22 without fetching.
- **Rollback:** revert the merge commit. Nothing else depends on it until the Astro
  change starts.
- **Local development:** contributors need Node 22.12 or newer. Astro 7.4 will need
  22.22; that is noted in the Astro change, not enforced here.
