# Tasks

## 1. Lock Python dependencies

- [x] 1.1 Create `scripts/requirements.in` from the current direct dependencies and comments in `scripts/requirements.txt` (keep `googlenewsdecoder>=0.2.0,<0.3.0`), and verify it lists the same 7 packages
- [x] 1.2 Compile `scripts/requirements.txt` with pip-compile `--strip-extras` on Linux / Python 3.11 (Docker command from design D2), and verify every line is an exact `==` pin with a `# via` annotation, including `googlenewsdecoder==0.2.1`
- [x] 1.3 In a clean Python 3.11 venv, run `pip install -r scripts/requirements.txt` and `pip check`, and verify both succeed and `pip freeze` matches the lock versions
- [x] 1.4 Run `python scripts/fetch_articles.py` locally against the locked environment and verify it completes and stores articles

## 2. Single manifest location

- [x] 2.1 Delete the root `requirements.txt`, and verify `git ls-files '*requirements*'` lists only files under `scripts/`
- [x] 2.2 Change the install hint in `scripts/fetch_articles.py` to `pip install -r scripts/requirements.txt`, and verify with grep that no reference to a root-level `requirements.txt` remains
- [x] 2.3 Add a "Dependencies" section to `scripts/README.md` covering the `.in`/`.txt` split, the regenerate command and the Dependabot flow, and verify the command in it runs as written
- [x] 2.4 Update `README.md` (project tree), `docs/architecture-deep-dive.md` (the `requirements.txt — Dependencies` section and tree), and `CLAUDE.md` (Tech Stack/Key Conventions: pinned lock, edit `requirements.in`), and verify that each mentions `requirements.in`

## 3. Validate dependency changes on PRs

- [ ] 3.1 Add `.github/workflows/dependency-check.yml` (pull_request, paths `scripts/**` and `.github/workflows/**`; Python 3.11; install lock; `pip check`; import `config`, `database`, `article_fetching`, `article_processing`, `fetch_articles` and `export_for_astro` from `scripts/`, printing the failing module), and verify it passes on the PR for this change (verified locally in a python:3.11 container on 2026-09-23: all 9 imports pass; the PR run is still pending)
- [ ] 3.2 Prove the check catches the incident: on a throwaway branch, keep `googlenewsdecoder==0.2.1` locked and restore the pre-`c52ce8e` `from googlenewsdecoder import new_decoderv1` in `scripts/article_fetching.py` (this reproduces the Sep 21–23 break), open a draft PR, verify the check fails and names `article_fetching`, then close it (reproduced locally on 2026-09-23: exit 1, `FAIL import article_fetching`, `ImportError: cannot import name 'new_decoderv1'`; the GitHub PR run is still pending)
- [ ] 3.3 Add `.github/dependabot.yml` (pip, `/scripts`, weekly, one group matching `*`, `open-pull-requests-limit: 2`), and after merge verify that Insights → Dependency graph → Dependabot shows the pip manifest being monitored without errors

## 4. Failure notification

- [x] 4.1 Add `issues: write` to the `permissions` block in `daily-build.yml`, and verify the workflow still passes `actionlint` (or the GitHub workflow editor shows no errors)
- [x] 4.2 Add a `report-status` job to `daily-build.yml` per design D5 (`needs: fetch-and-build`, skips when cancelled, `gh label create --force`, then comment/create on failure and comment/close on success), and verify with `actionlint`
- [ ] 4.3 Test the failure path: temporarily make the fetch step fail on a manual dispatch (for example a branch where `fetch_articles.py` exits 1, run via `workflow_dispatch` on that ref), and verify one `pipeline-failure` issue opens with the run link, event, SHA and `@KyleWeiland @Darthmaul` mentions, and that both of you receive the notification
- [ ] 4.4 Dispatch the failing ref again, and verify a comment is added to the same issue and no second issue appears
- [ ] 4.5 Run a normal manual dispatch on `main`, and verify the issue gets a success comment and is closed

## 5. Wrap-up

- [ ] 5.1 After merge, verify the next scheduled `daily-build` run succeeds, installs exactly the locked versions (from the install step log), and leaves no pipeline-failure issue open
- [x] 5.2 Run `openspec validate harden-ci-dependencies --strict` and verify it passes
