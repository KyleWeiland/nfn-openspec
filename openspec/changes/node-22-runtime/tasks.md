# Tasks

## 1. Runtime

- [x] 1.1 Set `node-version: '22'` in `.github/workflows/daily-build.yml` and `.github/workflows/dependency-check.yml`, and verify no other workflow step references Node 20
- [x] 1.2 Set `engines.node` to `>=22.12.0` in `site/package.json`, and verify `npm ci` on the local Node (22.14) raises no engine warning

## 2. Documentation

- [x] 2.1 Update the Node version in `README.md` (tech stack and prerequisites), `CLAUDE.md` (tech stack) and `docs/architecture-deep-dive.md` (workflow diagram and engine line), and verify `grep -n "Node.js 20\|Node 20" README.md CLAUDE.md docs/*.md` returns nothing

## 3. Verification

- [ ] 3.1 Open the PR and verify the `site-build` job of Dependency Check passes on Node 22 (the workflow change triggers it)
- [ ] 3.2 After merge, run `workflow_dispatch` on `daily-build.yml` with `skip_fetch: true`, and verify the run succeeds and the "Set up Node.js" step log shows a 22.x version
- [ ] 3.3 Verify the next scheduled run succeeds and no `pipeline-failure` issue is open
- [x] 3.4 Run `openspec validate node-22-runtime --strict` and verify it passes (passed 2026-10-21)
