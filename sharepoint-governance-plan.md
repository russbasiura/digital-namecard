# Kyocera SharePoint Governance Plan

*Prepared as a SharePoint architect engagement for Kyocera. Assumes a multi-year, organically-grown SharePoint Online tenant with no enforced governance. Adjust the placeholder assumptions (tenant size, site count, compliance regime) once real numbers are available.*

Generated from the prompt in `sharepoint-governance-prompt.md`. A live, editable version of this plan is also published as a Claude Docs artifact.

## Executive Summary

Kyocera's SharePoint environment currently has uncontrolled site sprawl, inconsistent permissions, unclear ownership, and no enforced retention or information architecture. This plan moves the tenant from **no control → governed and sustainable** in three phases, each escalating in effort and organizational impact:

| Phase | Theme | User Impact | Duration (typical) |
|---|---|---|---|
| 1 | Stabilize & Gain Visibility | None — admin-side only | 4–6 weeks |
| 2 | Standardize & Control | Moderate — new processes for site owners | 2–4 months |
| 3 | Optimize & Govern at Scale | High — automated, policy-enforced environment | Ongoing, 6+ months to mature |

---

## Phase 1 — Stabilize & Gain Visibility
**Low impact, foundational control. No changes required from end users.**

### Objectives & Success Criteria
- Full inventory of every SharePoint site, Teams-connected site, and OneDrive account exists and is kept current.
- Every site has an identified, accountable owner (or is flagged for remediation).
- A governance team and decision-making structure (RACI) is established and chartered.
- Baseline auditing/reporting is active tenant-wide.
- **Success = ** 100% of sites inventoried and owned or flagged; governance charter signed off by IT leadership.

### Initiatives / Actions
- [ ] Run a full site inventory (SharePoint Admin Center + PnP PowerShell / Graph API) covering site collections, Teams-connected sites, and OneDrive.
- [ ] Identify orphaned sites (no active owner, no recent activity) and flag for Phase 2 cleanup.
- [ ] Stand up a Governance Team: M365 admin lead, one rep each from IT security, legal/compliance, and 2–3 business units.
- [ ] Draft and publish a RACI for site creation, ownership, access requests, and content lifecycle decisions.
- [ ] Enable/verify unified audit logging and SharePoint usage reporting in Microsoft Purview.
- [ ] Document current-state architecture (hub sites, site collections, permission model) as a baseline snapshot.
- [ ] Define (but do not yet enforce) naming conventions and a site-creation request process.
- [ ] Require existing site owners to complete a lightweight ownership attestation survey.

### Roles & Responsibilities
| Role | Responsibility |
|---|---|
| M365/SharePoint Admin | Inventory, audit log configuration, reporting |
| Governance Team Lead | Charter, RACI, stakeholder alignment |
| Business Unit Reps | Ownership attestation, identifying orphaned sites in their unit |
| Legal/Compliance | Input on retention/compliance requirements for later phases |

### Tools & Features
SharePoint Admin Center, Microsoft Purview (audit/reporting), PnP PowerShell or Microsoft Graph API (inventory scripts), Excel/Power BI (inventory tracking), Teams/SharePoint usage reports.

### Risks
- **Risk of not acting:** Continued invisible sprawl; compliance/legal exposure grows; no baseline to measure improvement against.
- **Risk of this phase:** Minimal — read-only/reporting activities. Main risk is stakeholder fatigue if the ownership survey isn't well-communicated.

### Timeline & Dependencies
Weeks 1–2: inventory + audit logging. Weeks 2–4: governance charter + RACI. Weeks 3–6: ownership attestation. No dependencies on other phases — this is the foundation for everything after.

---

## Phase 2 — Standardize & Control
**Moderate impact, structural changes. Requires communication and change management for site owners.**

### Objectives & Success Criteria
- Site provisioning follows an enforced template/workflow — no more unmanaged self-service sprawl.
- Permissions model shifts from unique/broken permissions to group-based access.
- An information architecture (hub sites, taxonomy, metadata standards) is in place.
- Retention and inactive-site cleanup policies are enforced.
- External sharing policy is defined and applied.
- **Success =** >90% of active sites use group-based permissions; site provisioning requests go through the new workflow; retention policy applied tenant-wide.

### Initiatives / Actions
- [ ] Implement a site provisioning workflow (approval + template selection) via Power Automate or a governance app (e.g., PnP Provisioning, ShareGate, AvePoint).
- [ ] Define standard site templates by use case (team site, project site, department portal).
- [ ] Audit and remediate unique/broken permissions; migrate to SharePoint/AAD groups.
- [ ] Establish hub site structure aligned to business units/divisions.
- [ ] Define managed metadata/taxonomy standards for major content types.
- [ ] Roll out retention/expiration policies (via Purview retention labels) and an inactive-site archival/deletion policy.
- [ ] Define and enforce external sharing policy (who can share externally, approval process, guest access review cadence).
- [ ] Communicate and train site owners on new provisioning process, permission model, and their ongoing responsibilities.
- [ ] Remediate orphaned sites flagged in Phase 1 (assign new owner, archive, or decommission).

### Roles & Responsibilities
| Role | Responsibility |
|---|---|
| M365/SharePoint Admin | Provisioning workflow, permission remediation, retention policy config |
| Governance Team | Template/taxonomy standards, sharing policy approval |
| Site Owners | Adopt new provisioning process, maintain group-based access, attend training |
| Legal/Compliance | Sign off on retention schedules and external sharing policy |
| Comms/Change Management | Owner training materials, rollout communications |

### Tools & Features
Power Automate (provisioning workflows), Microsoft Purview (retention labels, sensitivity groundwork), Azure AD groups, SharePoint hub sites, Managed Metadata Service, third-party governance tooling if licensed (ShareGate/AvePoint), Access Reviews (Entra ID Governance) for guest access.

### Risks
- **Risk of not acting:** Permission sprawl continues to compound; compliance/legal risk from ungoverned retention and external sharing; user confusion persists.
- **Risk of this phase:** Direct impact on site owners' workflows — poor change management can cause friction or shadow-IT workarounds. Permission remediation can temporarily break inherited access if not carefully tested.

### Timeline & Dependencies
Depends on Phase 1 inventory and ownership data. Months 1–2: provisioning workflow + templates + hub structure. Months 2–3: permission remediation + retention policy rollout. Months 3–4: sharing policy enforcement + owner training completion.

---

## Phase 3 — Optimize & Govern at Scale
**Highest impact, mature governance. Sustained, ongoing effort.**

### Objectives & Success Criteria
- Site lifecycle (provisioning → archival → deletion) is fully automated and policy-driven.
- Sensitivity labels and DLP are integrated into SharePoint content protection.
- Records management and compliance controls are formalized for regulated content.
- A standing governance council operates with KPIs/metrics and periodic access reviews.
- Self-service provisioning exists but is fully policy-enforced (guardrails, not gates).
- **Success =** Governance operates as a continuous program with measurable KPIs (e.g., % sites with active owners, % orphaned sites, average time-to-provision, audit findings trend).

### Initiatives / Actions
- [ ] Automate full site lifecycle: provisioning, inactivity detection, archival, and deletion via Power Automate/Purview Data Lifecycle Management.
- [ ] Deploy sensitivity labels (Purview Information Protection) and integrate with DLP policies for SharePoint/OneDrive.
- [ ] Stand up records management for regulated/legal-hold content (retention labels tied to record types, disposition review).
- [ ] Formalize the Governance Council as a standing body (quarterly cadence) with defined KPIs and a reporting dashboard (Power BI).
- [ ] Implement periodic access reviews (Entra ID Access Reviews) for site membership, guest access, and privileged roles.
- [ ] Enable policy-enforced self-service site creation (templates + guardrails baked into the provisioning workflow from Phase 2, with automated compliance checks).
- [ ] Establish a continuous improvement process: quarterly governance health reports, policy revisions based on audit findings.
- [ ] Consider Microsoft Syntex or AI-assisted content classification if content volume justifies it.

### Roles & Responsibilities
| Role | Responsibility |
|---|---|
| Governance Council | Ongoing policy ownership, KPI review, escalations |
| M365/SharePoint Admin | Lifecycle automation, labels/DLP configuration, dashboards |
| Compliance/Legal | Records management policy, disposition review, audit response |
| Security Team | DLP policy tuning, access review enforcement |
| Site Owners | Operate within self-service guardrails, respond to access reviews |

### Tools & Features
Microsoft Purview (Data Lifecycle Management, Information Protection, DLP, Records Management), Entra ID Governance (Access Reviews, entitlement management), Power BI (governance KPI dashboards), Power Automate (lifecycle automation), Microsoft Syntex (optional, content AI).

### Risks
- **Risk of not acting:** Compliance exposure remains for regulated content; governance regresses to sprawl without continuous enforcement; no visibility into program effectiveness.
- **Risk of this phase:** Highest organizational impact — automation errors (e.g., premature deletion) can cause real business disruption. Requires thorough testing, staged rollout, and clear rollback/exception processes. Sensitivity label/DLP misconfiguration can block legitimate work if not piloted first.

### Timeline & Dependencies
Depends on Phase 2's group-based permissions, retention foundation, and provisioning workflow. Months 1–2: sensitivity labels/DLP pilot. Months 2–4: lifecycle automation + records management. Ongoing from month 4: governance council operating cadence, KPI dashboard, access review cycles.

---

## Cross-Phase Notes
- **Dependencies run strictly forward:** Phase 2's permission and retention work depends on Phase 1's inventory/ownership data; Phase 3's automation depends on Phase 2's standardized provisioning and group model. Don't start automating lifecycle decisions (Phase 3) on data that hasn't been cleaned up (Phase 1–2).
- **Communication cadence:** Phase 1 is silent to end users; Phase 2 needs active change management; Phase 3 needs a permanent governance communication channel (e.g., a "SharePoint Governance" Teams channel or intranet page).
- **Kyocera-specific tailoring needed:** tenant/site counts, applicable compliance regimes (e.g., export control, ISO), existing Purview/Syntex licensing, and any industry-specific records requirements should be layered in before presenting to leadership.
