---
description: Phase 1 — parse the BRD (.xlsx) and inventory the design package
---
Run **Phase 1 — Ingest** exactly as defined in CLAUDE.md §5.

1. Confirm `requirements/` contains at least one `.xlsx` and `requirements/design/` is non-empty (otherwise Hard Stop 3).
2. `python3 scripts/parse-brd.py` and review its warnings.
3. Correct `requirements/requirements.json` by reading the raw sheets (IDs, priorities, acceptance criteria, splitting compound items).
4. Read **every** image in `requirements/design/**` and `requirements/design/_from-brd/**` and write `docs/DESIGN_INVENTORY.md`.
5. Map each requirement to a component type; mark anything you will not build in `requirements/status.json` with a reason.
6. If a previous `requirements.json` exists in git, summarize added/changed/removed requirements at the top of `docs/PLAN.md` under "Requirement changes".
7. Commit: `docs(requirements): ingest BRD and design package`.

$ARGUMENTS
