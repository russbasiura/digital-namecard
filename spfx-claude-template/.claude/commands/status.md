---
description: Report delivery status — coverage, versions, open questions
---
Without changing code, report:
- Requirement coverage from `python3 scripts/traceability.py --report-only` (Must/Should/Could delivered vs total).
- Repo solution version (`spfx/config/package-solution.json`) vs. version in the tenant app catalog (`scripts/m365-login.sh && m365 spo app list --appCatalogScope tenant --output json`, filter to this solution).
- Increments done/remaining from `docs/PLAN.md`.
- Open items from `docs/OPEN_QUESTIONS.md` and High/Medium items in `docs/DESIGN_REVIEW.md`.
- Pending API permission requests (`m365 spo serviceprincipal permissionrequest list`).
