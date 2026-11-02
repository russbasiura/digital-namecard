# Kickoff prompt

Paste this as the **first message** in a new Claude Code session on a project repo that contains this template.
Fill in the bracketed parts. For later sessions, `/ship` or a single phase command (`/build`, `/deploy`, ...) is enough.

---

```text
You are delivering a new SharePoint Framework application. Follow CLAUDE.md exactly. It is your
operating manual and overrides your defaults.

Project: [Application name]
Business owner / audience: [e.g. HR team, all employees]
Hosts: [SharePoint pages | Teams tab | Teams personal app | Viva Connections dashboard]
Deployment scope: [target site only | tenant-wide]
Constraints or preferences not in the BRD: [e.g. "brand color #0B5CAB", "no Graph Mail permissions", or "none"]

Inputs are committed in /requirements:
- BRD: requirements/[file].xlsx
- Design package: requirements/design/ ([n] screenshots + [other files])

Run /ship: ingest the BRD and design package, plan increments, build, verify (build, tests,
traceability, live-tenant visual and accessibility checks, design-fidelity review), and deploy each
increment to the tenant app catalog and the target site, until every Must and Should requirement is
delivered or deferred with a reason.

Work autonomously. Do not ask me questions. Log decisions in docs/DECISIONS.md and anything for me to
confirm in docs/OPEN_QUESTIONS.md. Stop only for a Hard Stop in CLAUDE.md §10. When you finish, give me
the Phase 6 report.
```

---

## Follow-up prompts

| Situation | Prompt |
|---|---|
| BRD or design updated | `The files in /requirements changed (see the latest commit). Re-run /ingest, plan the delta, then /ship.` |
| Bug report | `Bug: [description + screenshot]. Reproduce it with a failing test, fix it, /verify, /deploy patch.` |
| Change request | `Change request: [text]. Add it to requirements.json as a new REQ ID (priority [Must/Should]), then /ship.` |
| Check status | `/status` |
| Roll back | `Production issue in v[X.Y.Z]: [symptom]. Roll back to v[previous] with scripts/deploy.sh --from-tag, then investigate and fix forward.` |
