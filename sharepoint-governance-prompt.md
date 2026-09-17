# Prompt: Kyocera SharePoint Governance Plan

Use this prompt with an AI assistant (or as a briefing document for a working session) to generate a phased SharePoint governance plan for Kyocera.

---

## Prompt

You are a SharePoint architect engaged by Kyocera to bring order to an existing, ungoverned SharePoint Online environment. Produce a **SharePoint Governance Plan** that Kyocera's IT and Microsoft 365 teams can execute in three sequential phases.

**Context to assume (adjust if Kyocera specifics are provided):**
- The tenant has been in use for several years with organic, largely unmanaged growth: uncontrolled site creation, inconsistent permissions, unclear ownership, and no enforced information architecture or retention policy.
- Stakeholders include IT/M365 administrators, site owners across business units, legal/compliance, and end users.
- The goal is to move from "no control" to "governed, sustainable, and scalable" without disrupting daily business operations.

**Structure the plan in three phases, ordered strictly by effort/impact/risk — start with what is simplest and lowest-impact to users, and build toward the most transformative changes:**

- **Phase 1 – Stabilize & Gain Visibility (low impact, foundational control).**
  Focus on changes that establish visibility and baseline control without disrupting users: inventory all sites/Teams-connected sites, identify ownership gaps, establish a governance team/RACI, document current state, turn on auditing/reporting, define naming and site-creation conventions, and put lightweight guardrails in place (e.g., admin monitoring, site owner attestation). Nothing here should require end users to change how they work yet.

- **Phase 2 – Standardize & Control (moderate impact, structural changes).**
  Introduce enforced structure: site provisioning workflows/templates, permission model standardization (reduce unique/broken permissions, move to group-based access), information architecture guidelines (hub sites, taxonomy/metadata), content lifecycle policies (retention/expiration, inactive site cleanup), sharing/external access policies, and training/communication for site owners. These changes touch how people create and manage content, so they require change management and communication.

- **Phase 3 – Optimize & Govern at Scale (highest impact, mature governance).**
  Implement the most transformative and sustained-effort changes: automated lifecycle management (provisioning, archival, deletion via policy and automation/Power Automate), sensitivity labels and DLP integration, records management and compliance controls, ongoing governance council with KPIs/metrics and periodic access reviews, self-service provisioning with policy enforcement, and continuous improvement processes. These changes reshape how the organization operates within SharePoint long-term.

**For each phase, include:**
1. Objectives and success criteria
2. Specific initiatives/actions (as a checklist)
3. Roles and responsibilities
4. Tools/features used (e.g., SharePoint Admin Center, Microsoft Purview, PowerShell/PnP, Power Automate, Access Reviews)
5. Risks of not acting and risks of the change itself
6. Rough sequencing/timeline and dependencies on prior phases

**Output format:** A structured document (headings per phase, tables for actions/owners/timelines where useful) suitable for presenting to Kyocera IT leadership for approval.

---

## Usage notes
- Provide any Kyocera-specific details (tenant size, number of sites, industry compliance requirements such as ISO/export control, existing tools like Purview/Syntex licensing) to tailor the generated plan.
- Re-run per phase for a deeper, more detailed sub-plan if the full three-phase output needs more granularity.
