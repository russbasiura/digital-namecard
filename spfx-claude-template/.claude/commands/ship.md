---
description: Autonomous end-to-end delivery — ingest, plan, build, verify, deploy, report
---
Deliver this SPFx application end to end, autonomously, following CLAUDE.md.

1. `/ingest` (skip if `requirements.json` is current with the files in `requirements/`).
2. `/plan` (refresh if requirements changed).
3. For each unfinished increment in `docs/PLAN.md`: `/build` → `/verify` → `/deploy minor` (use `patch` for fix-only increments).
4. Continue until every `Must` and `Should` requirement is delivered or deferred with a reason in `requirements/status.json`.
5. Finish with the Phase 6 report.

Only stop early for a Hard Stop (CLAUDE.md §10). Make and document decisions; do not ask questions.
Additional instructions: $ARGUMENTS
