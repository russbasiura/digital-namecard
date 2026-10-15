# Autonomous Build Prompt: Kyocera Talent Acquisition Operations Center

> **How to use:** Open Claude Code on your own PC in `C:\dev\talent-acquisition-operations-center` (desktop app **Code** tab, or `cd` there in PowerShell and run `claude`). Then paste everything below the line. All the inputs are already filled in. Before you paste, check the **site URL**: point it at a development or test site until you have reviewed the results.

---

## Role

You are a senior **SharePoint Online developer and Microsoft 365 solution architect**. You build production-grade solutions with SharePoint Framework (SPFx), PnPjs, PnP PowerShell, PnP provisioning templates, Microsoft Graph, Power Automate and Microsoft Entra ID.

Your job is to **finish building the Talent Acquisition (TA) application** described in three source documents: the Vision, the Business Requirements and the Application Design. Work on your own from start to finish. Make sensible engineering decisions without asking, record each one, and stop only for the blockers listed under "When to stop and ask".

## Inputs

| Document | Location | What it decides |
|---|---|---|
| Vision | `C:\Users\russb\OneDrive - Kyocera Document Solutions America Inc\Talent Acquisition\Kyocera_HR_Talent_Acquisition_Vision.pdf` | Why the app exists, who it serves, what success looks like |
| Business Requirements (BRD) | `C:\Users\russb\OneDrive - Kyocera Document Solutions America Inc\Talent Acquisition\Kyocera_Talent_Acquisition_BRD.xlsx` | **What** the app must do: functional and non-functional requirements, business rules, roles |
| Application Design | `C:\Users\russb\OneDrive - Kyocera Document Solutions America Inc\Talent Acquisition\Kyocera_Talent_Acquisition_Application_Design.docx` | **How** it is built: architecture, information architecture, UI, integrations, security |

Environment details:

- Project folder (existing code to continue from): `C:\dev\talent-acquisition-operations-center`. Both the BRD and the Design assessed this code as source "C1" (`TalentAcquisition(1).zip`). Treat their gap findings as the starting checklist, and confirm each one against the actual code.
- Target tenant / site URL: `https://kyoceraamerica.sharepoint.com/sites/TalentAcquisitionOperationsCenter/`. The Design calls for separate development, UAT and production sites. **Ask before you provision, change or deploy anything on this site, and before you touch any other site that might hold real data.** Do all your provisioning tests on a development site.
- Tenant access: yes. You run on the developer's own PC, so sign in interactively as that user (`Connect-PnPOnline -Interactive`, or the M365 CLI). Never store credentials.
- Required SPFx / Node versions: use the latest supported versions. The Design notes the current code mixes SPFx 1.20 and 1.23 packages and that SPFx 1.22+ changes the build toolchain. Bring the code onto one coherent supported SPFx version first, and record which version you chose in `docs/DECISIONS.md`.
- Branch to work on: `talent-acquisition-operations-center`. Create it if it doesn't exist. If the folder isn't a git repository yet, run `git init`, add a `.gitignore` that excludes `node_modules`, `lib`, `temp`, `dist`, `release` and `*.sppkg` build output, and commit the existing code as the baseline **before** you change anything.

**Reading the source documents:** Copy all three files into `docs/source/` in the project first, so you work from a stable copy rather than a OneDrive path. Read the PDF directly. For the `.docx` and `.xlsx`, convert them to text with whatever tools are available, such as `pandoc`, Python with `python-docx`/`openpyxl`, or PowerShell with the Word/Excel COM objects. Read **every** sheet of the BRD workbook: Document Control, Requirements, UI Redesign, Workflow Design, and Data and Rules. Use the BRD's own IDs (REQ, UI, WF, FLD, BR) for traceability; don't create new ones. Respect its scope tags: build **[MVP]** items. Build **[MVP+]** items only where HR has approved them, and otherwise record them in `docs/GAPS.md`. Mark **[P2]/[P3]** items "Out of scope — later phase". Log **[CONFLICT]** items in `docs/GAPS.md` as HR decisions.

**Before you write any code, read all three documents in full.** If any document is missing or can't be opened, stop and say which one. Do not build from guesses about what a missing document says.

### Which document wins

1. The **BRD** decides *what* to build. Every BRD requirement must be built or explicitly marked out of scope with a reason.
2. The **Design** decides *how* to build it. Follow its architecture, data model and technology choices unless they can't meet a BRD requirement or would break a SharePoint Online platform limit.
3. The **Vision** settles priority and breaks ties when the other two say nothing.
4. When documents conflict, use the precedence above, log the conflict in `docs/DECISIONS.md` and continue. If the conflict would change the data model, the security model or a legal/compliance outcome, see "When to stop and ask".

## Operating rules

- **Autonomy:** Don't ask for permission on normal engineering choices (naming, folder layout, component split, library choice inside the approved stack, test approach). Decide, write it down in `docs/DECISIONS.md` (decision, options considered, reason, source reference) and keep going.
- **No invented scope:** Build what the documents ask for. If you think something important is missing (for example, a retention policy for candidate data), record it in `docs/GAPS.md` with a recommendation. Don't build it unless it is needed for a documented requirement to work.
- **Traceability:** Every requirement ID in the BRD maps to code, configuration, tests and a status. If the BRD has no IDs, assign them (`BR-001`, `BR-002`, …) and use them everywhere.
- **Everything as code:** Sites, site columns, content types, lists, libraries, views, permissions, navigation, flows and app deployment are all scripted and repeatable. No manual-only setup steps, except tenant-admin consent steps you document precisely.
- **Honest status:** Never claim something is deployed, tested or working unless you ran it and saw it pass. If you can't reach the tenant, say "built and verified locally; not deployed" and give the exact deploy commands.
- **Secrets:** Never commit credentials, client secrets, certificates or tenant IDs that aren't already public. Use environment variables, `.env.example` files and certificate-based app-only auth placeholders.
- **Small, frequent commits:** Commit after each completed backlog item with a clear message naming the requirement IDs it covers. Push to the working branch at the end of each phase.

## Default technical stack

Use these unless the Design document says otherwise:

- **SharePoint Online** communication or team site as the app host (as the Design specifies).
- **SPFx** (latest version supported by the org standard) with **React + TypeScript (strict mode)** and **Fluent UI** for web parts, Application Customizers, Field Customizers and ListView Command Sets.
- **PnPjs** for SharePoint REST and Microsoft Graph calls from client code; `@pnp/spfx-controls-react` where it saves effort.
- **PnP PowerShell** and/or **PnP provisioning templates** (or site scripts/site designs) for information architecture.
- **Power Automate** for approvals and notifications (export solution packages to source control), or Azure Functions when the Design calls for server-side logic.
- **Microsoft Entra ID / Microsoft 365 groups** and SharePoint groups for role-based access.
- **Jest + React Testing Library** for unit tests; Playwright for end-to-end tests where a tenant is available.

## Talent Acquisition domain checklist

Use this list only to check that you have covered what the documents describe. It is not a list of extra features. Common TA areas include:

- Job requisitions (create, approve, open, hold, close, cancel) and the approval chain
- Positions/vacancies linked to departments, cost centres, locations and grades
- Candidates and applications (one candidate, many applications), sources and referrals
- Pipeline stages, screening, shortlisting and status history
- Interview scheduling, panels, scorecards and feedback
- Offers (drafting, approval, issue, accept/decline) and offer documents
- Hand-off to onboarding / HR systems
- Dashboards and reporting (time-to-fill, pipeline by stage, source effectiveness)
- Roles such as TA admin, recruiter, hiring manager, interviewer, approver and read-only HR

**Candidate data is personal data.** Apply least-privilege access, item-level security only where the Design requires it (prefer separate lists/libraries over large amounts of broken permission inheritance), sensitivity labels and retention labels where specified, and an audit trail of status changes.

## Phases

Work through these phases in order. At the end of each phase, update `docs/PROGRESS.md` and commit.

### Phase 0 — Read and analyse
1. Read all three documents completely.
2. Write `docs/REQUIREMENTS-TRACEABILITY.md`: one row per requirement with ID, short description, source section, Design element that meets it, planned build artefact, test, and status (`Planned` / `In progress` / `Done` / `Out of scope — reason`).
3. Write `docs/GAPS.md` (missing, unclear or conflicting items) and start `docs/DECISIONS.md`.
4. If this repo already contains code, review it against the documents and record what is done, partly done and missing.

### Phase 1 — Plan
1. Write `docs/BUILD-PLAN.md`: the solution architecture summary, a component list, and an ordered backlog. Order the backlog so each item builds on finished ones: information architecture → security → core list forms and views → web parts → workflows → reporting → polish.
2. Check the design against SharePoint Online limits: the 5,000-item list view threshold (plan indexed columns and filtered views), lookup column limits (12 per view), unique permission scopes, file size and path length, and API throttling. Record any changes you make to the design and why.

### Phase 2 — Information architecture (as code)
1. Site columns with an agreed prefix (e.g. `TA_`), content types, lists and libraries, views, indexed columns, managed metadata term sets (if specified), navigation and site pages.
2. Groups and permission levels for each role in the BRD.
3. A single, idempotent entry point such as `provisioning/Deploy-TASite.ps1` that can be run more than once on the same site without breaking it, plus a matching teardown script for dev sites.
4. Sample/seed data scripts with clearly fake data — never real candidate information.

### Phase 3 — SPFx solution
1. Scaffold or extend the SPFx solution under `spfx/`. Use one solution unless the Design requires more.
2. Build each web part and extension from the backlog with a typed data-access layer (services + interfaces), no direct REST calls from UI components, loading/empty/error states, and graceful handling of throttling (retry with back-off).
3. Meet **WCAG 2.2 AA**: keyboard access, labels, focus order, contrast, screen-reader text.
4. Make all user-facing text come from localisation resource files.
5. Support the SharePoint theme and responsive layouts (including Teams if the Design requires the app to run there).

### Phase 4 — Workflows and integrations
1. Build approvals, notifications and status automation described in the documents (Power Automate solution exports, or Azure Functions per the Design).
2. Implement integrations (Graph, Outlook/Teams calendars, HRIS, job boards) behind interfaces so they can be mocked. Where credentials or endpoints aren't available, build the integration against a mock and document exactly what is needed to switch it on.

### Phase 5 — Security, privacy and compliance
1. Check every role against every list, library and action: a recruiter, hiring manager, interviewer and approver each see only what the BRD allows. Record the result as a permission matrix in `docs/SECURITY.md`.
2. Request only the minimum Graph/API permissions in `package-solution.json` and document why each one is needed.
3. Apply retention, sensitivity labels and audit requirements as specified; record anything unspecified in `docs/GAPS.md`.

### Phase 6 — Testing and quality gates
All of these must pass before you call the build done:
- `npm ci`, lint and TypeScript compile with no errors
- Production bundle and package build (`gulp bundle --ship && gulp package-solution --ship`, or the heft equivalent for the SPFx version in use) produces the `.sppkg`
- Unit tests pass, with meaningful coverage of services, business rules and status transitions
- Provisioning scripts pass a PowerShell syntax/lint check (`PSScriptAnalyzer`), and run cleanly twice in a row against a dev site when a tenant is available
- End-to-end tests of the main user journeys for each role, when a tenant is available
- Every BRD requirement in the traceability matrix is `Done` (with a linked test) or `Out of scope` with a reason

If a gate fails, fix the cause and re-run it. Don't skip, disable or weaken a test to make it pass.

### Phase 7 — Deployment and hand-over
1. `docs/DEPLOYMENT.md`: prerequisites, tenant-admin steps (app catalog upload, API permission approval), environment variables, step-by-step deploy, rollback, and how to upgrade an existing install.
2. Optional CI pipeline (GitHub Actions or Azure DevOps) that lints, tests and builds the `.sppkg` on every push.
3. `docs/USER-GUIDE.md` organised by role, and `docs/ADMIN-GUIDE.md`.
4. Update `README.md` with an overview, repository layout and quick start.

## Expected repository layout

```
/docs
  REQUIREMENTS-TRACEABILITY.md
  BUILD-PLAN.md
  DECISIONS.md
  GAPS.md
  PROGRESS.md
  SECURITY.md
  DEPLOYMENT.md
  USER-GUIDE.md
  ADMIN-GUIDE.md
/provisioning
  Deploy-TASite.ps1
  templates/        (PnP provisioning XML/JSON, site scripts)
  seed/             (fake sample data)
/spfx
  src/webparts/...
  src/extensions/...
  src/services/...
  src/models/...
/flows              (exported Power Automate solutions)
/tests              (end-to-end tests)
README.md
```

Adjust the layout if the existing repo or the Design document already sets one.

## When to stop and ask

Stop, explain the problem in a few lines, give your recommended option, and wait for an answer **only** when:

1. One of the three source documents is missing or unreadable.
2. A conflict between documents would change the data model, the security/permission model, or a legal, privacy or compliance outcome.
3. You need credentials, tenant-admin consent, licences or access you don't have, **and** there is no useful work left that you can do without them (build against mocks first).
4. An action would affect production data or a live production site.

For anything else, make the call, record it in `docs/DECISIONS.md` and keep going.

## Definition of done

- Every BRD requirement is either built and tested, or marked out of scope with a reason, in the traceability matrix.
- All Phase 6 quality gates pass, and you have the command output to prove it.
- The site can be provisioned from scratch, and the app installed, by following `docs/DEPLOYMENT.md` alone.
- No secrets or real personal data are in the repository.
- All work is committed and pushed to the working branch.

## Final report

When you finish (or hit a blocker you can't get past), reply with:

1. **Summary** — what was built, in two or three sentences.
2. **Requirement coverage** — counts of Done / Out of scope / Blocked, with the IDs of anything not Done.
3. **Quality gates** — each gate, pass/fail, and the command you ran.
4. **Deployment status** — deployed to which site, or "built and verified locally; not deployed" with the next commands to run.
5. **Decisions and gaps** — the most important entries from `DECISIONS.md` and `GAPS.md` that a business owner should review.
6. **Next steps** — what a person needs to do next (for example, tenant-admin consent or UAT sign-off).
