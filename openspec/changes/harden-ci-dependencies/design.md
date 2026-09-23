# Design

## Context

- `scripts/requirements.txt` lists 7 direct dependencies, all with minimum versions only
  except `googlenewsdecoder>=0.2.0,<0.3.0` (Kyle's hotfix in `c52ce8e`). The root
  `requirements.txt` is a byte-for-byte copy that nothing in CI reads.
- `daily-build.yml` is a single job, `fetch-and-build`. It runs only on `schedule` and
  `workflow_dispatch`, so nothing runs on pull requests today.
- The workflow installs with `pip install -r scripts/requirements.txt` on
  `ubuntu-latest` / Python 3.11.
- The pipeline modules in `scripts/` import each other by bare module name
  (`from article_fetching import ...`), so an import smoke test has to run with
  `scripts/` as the working directory.
- Contributors run the pipeline locally on Windows as well as Linux.

See proposal.md for motivation.

## Goals / Non-Goals

**Goals:**
- Installed package versions change only when someone merges a lock-file change.
- A dependency bump that breaks an import is caught on its PR.
- Maintainers get a GitHub notification within one run of a failure, and the
  notification clears itself once the pipeline recovers.

**Non-Goals:**
- Pinning GitHub Actions to commit SHAs or adding Dependabot for the `github-actions`
  ecosystem. That's a reasonable follow-up, but it's a separate supply-chain concern.
- Pinning Node dependencies. `site/package-lock.json` already does this through `npm ci`.
- End-to-end testing of fetching or extraction on PRs. That needs network access to
  Google News, and the results change from day to day.
- Adding a canary job that runs against unpinned "latest" versions (step 5 of the
  original analysis; deferred).
- Fixing `scripts/test_modules.py` or getting it into CI.

## Decisions

### D1: pip-tools layout, `requirements.in` → `requirements.txt`

`scripts/requirements.in` holds the direct dependencies with compatible ranges and the
explanatory comments (such as the nltk note). `pip-compile` writes the fully pinned
`scripts/requirements.txt`, and every existing instruction and the workflow keep
pointing at that path.

Why this layout: `requirements.txt` stays the file that CI, README and
`fetch_articles.py` already reference, so the install command doesn't change. It's the
standard pip-tools convention, and Dependabot's `pip` ecosystem recognizes it. When a
`requirements.in` sits next to a compiled `requirements.txt`, Dependabot updates the
`.in` and recompiles the `.txt`.

Alternatives considered:
- **`pyproject.toml` + `uv.lock`:** a cleaner lock format, but it means packaging
  `scripts/` as a project and changing every install instruction to `uv sync`. That's
  too much churn for a folder of 7 scripts.
- **`pip freeze` into a separate `requirements.lock`:** it captures whatever happens to
  be installed, including dev leftovers, has no link back to the direct dependencies,
  and Dependabot doesn't understand it.
- **Upper bounds only (`<next-major`):** this would not have prevented this incident,
  because 0.1.7 → 0.2.1 was a minor bump under semver-0 rules, and transitive
  dependencies would stay unbounded.

### D2: Compile on Linux / Python 3.11, without `--generate-hashes`

Compile the lock with Python 3.11 on Linux to match CI, using
`pip-compile --strip-extras` so the nltk extra resolves to explicit pins.

Leave hashes out. With `--require-hashes`, pip refuses any package that isn't in the
file, and a lock compiled on Linux leaves out Windows-only transitive dependencies
(for example `colorama`, which `tqdm`/`click` need on Windows). Local installs on
Windows would then fail. Without hashes, pip installs the pins and still resolves the
missing platform-only transitive dependency itself. The incident was about version
drift, not tampering, so exact pins without hashes cover the risk we actually have.

For contributors without a Linux box, add a short "regenerating the lock" section to
`scripts/README.md` with the Docker one-liner
(`docker run --rm -v "$PWD":/w -w /w/scripts python:3.11 sh -c "pip install pip-tools && pip-compile --strip-extras requirements.in"`).
In practice, Dependabot will do most of the recompiling.

### D3: Dependabot, weekly, one grouped PR

`.github/dependabot.yml` sets `package-ecosystem: pip`, `directory: /scripts`,
`schedule.interval: weekly`, a single `groups` entry matching `*`, and
`open-pull-requests-limit: 2`.

Grouping means one PR a week, which keeps review light for a two-person project. The
trade-off is that one bad package blocks the whole group. When that happens, the
maintainer drops that package from the PR (or pins it in `requirements.in`) and merges
the rest.

Dependabot security updates stay on their default (ungrouped, immediate).

### D4: `dependency-check.yml` PR workflow with an import smoke test

A new workflow runs on `pull_request` with a paths filter on `scripts/**` and
`.github/workflows/**`. It sets up Python 3.11, installs `scripts/requirements.txt`, and
from `scripts/` runs a short Python snippet that imports every pipeline module:
`config`, `database`, `article_fetching`, `article_processing`, `fetch_articles`,
`export_for_astro`. The snippet exits non-zero and prints the failing module and
exception.

It also runs `pip check` to catch conflicting pins.

The check is kept separate from `daily-build.yml`. Adding a `pull_request` trigger to
`daily-build.yml` would require guarding the fetch, commit and deploy steps, and would
share the `pages` concurrency group.

`url_extraction.py` and `test_modules.py` are excluded from the import list, because
CLAUDE.md records them as dead code.

This check alone would have caught the `googlenewsdecoder` incident: the import of
`new_decoderv1` fails at module load.

It doesn't catch behavioral changes where the import succeeds, like the
`status` → `success` result-key rename. That's an accepted gap (see Risks).

### D5: A `report-status` job in `daily-build.yml` using `gh`

The job is `needs: fetch-and-build`, `if: always() && needs.fetch-and-build.result != 'cancelled'`,
on `ubuntu-latest`, and needs no checkout (it passes `gh` a `--repo` flag). It uses
`GITHUB_TOKEN` with `issues: write`, which gets added to the workflow's `permissions`
block.

- **Failure:** ensure the `pipeline-failure` label exists
  (`gh label create --force`). Then look up an open issue with that label
  (`gh issue list --label pipeline-failure --state open --limit 1`). If there is one,
  comment on it; otherwise create one titled "Daily pipeline failing". The body links
  `${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}`
  and includes the event name and short SHA. The body of a new issue @mentions the
  maintainers (`@KyleWeiland @Darthmaul`), which are kept in a `MAINTAINERS` env var at
  the top of the job. A mention both notifies each maintainer and subscribes them to
  the issue, so later failure comments and the closing comment reach them without
  repeating the mention.
- **Success:** if an open labeled issue exists, comment with the run link and close it.

Why a separate job instead of a final step: a job-level `needs`/`if` still runs when
the failure is in checkout or setup, and it keeps the reporting logic out of the
build steps.

All triggers are reported, including manual ones. Deduplication keeps that down to a
single comment, and one rule is simpler than two.

Alternatives considered:
- **Third-party "create issue" actions:** another dependency to pin, for about 15 lines
  of `gh`.
- **Email/Slack via a webhook secret:** needs secret management, and an issue also
  gives a place to discuss the failure.

### D6: Removing the root `requirements.txt` is a plain delete

Nothing in CI, the scripts or the docs references the root copy. The only relative
reference is `fetch_articles.py:29`'s hint (`pip install -r requirements.txt`), which
gets corrected to `scripts/requirements.txt`. The docs already point at
`scripts/requirements.txt`.

## Risks / Trade-offs

- **[Lock goes stale and security fixes lag]** → Dependabot security updates stay
  enabled and ungrouped. The weekly version PRs keep the gap to about a week.
- **[Import check misses semantic API changes, like the `status`/`success` rename]** →
  Accepted. The failure issue still surfaces these within one daily run. A decoder unit
  test with a recorded response could close the gap later.
- **[Grouped PR is blocked by one bad package]** → Remove or cap that package in the
  PR (D3). The import check says which one broke.
- **[Lock compiled on the wrong platform or Python version adds or drops pins]** →
  D2 documents compiling on Linux/3.11. Dependabot compiles on Linux. The PR check
  installs on 3.11 and would fail on an unresolvable pin.
- **[Dependabot pushes and the daily bot commit race on `main`]** → Dependabot PRs are
  merged by hand, and the daily job already pushes after its own commit. No new race
  is introduced.
- **[A maintainer changes their GitHub handle, or the team changes]** → Handles live in
  a single `MAINTAINERS` env var in `daily-build.yml`. A mention of a handle that
  doesn't exist fails silently, so step 4.3 checks that both people actually receive
  the notification.

## Migration Plan

1. Merge the change with the new lock file compiled from the current ranges. The pinned
   versions should match what the Sep 23 manual run installed, so no behavior changes.
2. Confirm the next scheduled run passes, then manually trigger a failure (see tasks) to
   check that the issue opens and then closes.
3. **Rollback:** revert the commit. The workflow falls back to installing the (now
   pinned) `requirements.txt`, which still works; pins without the lock tooling do
   no harm.
