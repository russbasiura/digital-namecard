---
description: Phase 5 — version bump, provision, deploy to tenant app catalog, smoke test, tag
---
Run **Phase 5 — Deploy** from CLAUDE.md §5. Version bump type: "$ARGUMENTS" (use `patch` if empty).

Preconditions: the latest `/verify` passed on the current commit (re-run it if code changed since).
Steps: `node scripts/bump-version.mjs <type>` → `scripts/build.sh` → `node scripts/provision.mjs` → `scripts/deploy.sh` → `cd tests/e2e && npx playwright test --grep @smoke` → update `docs/RELEASE_NOTES.md` → commit → tag `vX.Y.Z` → push with tags → open/update PR to `main`.
On post-deploy failure, roll back with `scripts/deploy.sh --from-tag <previous tag>` and log the incident.
