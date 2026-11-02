---
description: Phase 4 — all quality gates incl. live-tenant visual, a11y and design-fidelity review
---
Run **Phase 4 — Verify** from CLAUDE.md §5. All gates must pass:
1. `scripts/build.sh` (production).
2. `python3 scripts/traceability.py`.
3. Deploy to the tenant (`node scripts/provision.mjs && scripts/deploy.sh`), then `cd tests/e2e && npm ci && npx playwright test`.
4. Design fidelity review: Read each screenshot in `tests/e2e/artifacts/screenshots/` next to its design file (mapping in `tests/e2e/pages.json`) and write `docs/DESIGN_REVIEW.md`. Fix High/Medium deviations, redeploy, re-review (max 3 loops).
5. Update visual baselines for accepted screens and commit them.

Never weaken a test or rule to pass a gate. $ARGUMENTS
