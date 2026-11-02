# SPFx × Claude Code — autonomous delivery template

This template lets Claude Code on the web take a **BRD (.xlsx)** and an **application design package
(screenshots)** and build, test and deploy a SharePoint Framework solution to your Microsoft 365 tenant
without supervision.

| File | Purpose |
|---|---|
| `CLAUDE.md` | **The master prompt.** Claude Code loads it automatically in every session. |
| `KICKOFF_PROMPT.md` | The first message to paste into a new project session, plus follow-up prompts. |
| `.claude/commands/*.md` | Slash commands `/ingest` `/plan` `/build` `/verify` `/deploy` `/ship` `/status` |
| `.claude/settings.json` | Pre-approved tools, a denylist of destructive tenant commands, and the SessionStart hook |
| `scripts/` | Setup, login, build, deploy/rollback, provisioning, BRD parser, traceability gate |
| `tests/e2e/` | Playwright: tenant sign-in, visual capture and regression, axe accessibility checks, smoke test |
| `provisioning/` | Declarative list/field/view definitions (additive, idempotent) |
| `.github/workflows/` | `ci.yml` (PR build and test gate), `release.yml` (manual redeploy/rollback from Actions) |

You do the one-time setup (sections 1–3) once per tenant. Section 4 is repeated for every project.

---

## 1. One-time: Entra ID app registration (certificate auth)

1. **Create a certificate** (on your workstation, not in a Claude session):
   ```bash
   openssl req -x509 -newkey rsa:2048 -sha256 -days 730 -nodes -keyout spfx-deploy.key -out spfx-deploy.cer -subj "/CN=spfx-claude-deploy"
   ```
   ```bash
   openssl pkcs12 -export -out spfx-deploy.pfx -inkey spfx-deploy.key -in spfx-deploy.cer -passout pass:'CHOOSE-A-PASSWORD'
   ```
   ```bash
   base64 -w0 spfx-deploy.pfx > spfx-deploy.pfx.b64
   ```
   (On macOS: `base64 -i spfx-deploy.pfx -o spfx-deploy.pfx.b64`.) Store the `.pfx` and its password in your vault.
2. **Register the app** in Entra admin center → *App registrations → New registration*. Name it `SPFx Claude Deploy`,
   single tenant, no redirect URI.
3. *Certificates & secrets → Certificates → Upload* `spfx-deploy.cer`.
4. *API permissions → Add* (all **Application** permissions), then **Grant admin consent**:
   - **SharePoint** → `Sites.FullControl.All` (app catalog upload/deploy, app install, list provisioning)
   - **Microsoft Graph** → `Sites.FullControl.All` (CLI commands that go through Graph)
   - *Optional, Teams apps:* **Microsoft Graph** → `AppCatalog.ReadWrite.All`
5. Write down the **Directory (tenant) ID** and the **Application (client) ID**.
6. Make sure a **tenant app catalog** exists (SharePoint admin center → *More features → Apps*). Note its URL.

> Approving `webApiPermissionRequests` (Graph scopes the web part asks for) still needs a SharePoint
> admin in *SharePoint admin center → Advanced → API access*. Claude reports pending requests after each deployment.

## 2. One-time: Playwright test account

1. Create a licensed user, e.g. `spfx-test@contoso.com`, with a long random password.
2. **Exclude it from MFA** with a targeted Conditional Access exclusion (ideally limited to trusted
   locations/the SharePoint app) so headless sign-in works. Give it **Member** (or Visitor, if that's what end users have) on the target site.
3. Do not give this account admin roles.

## 3. One-time: Claude Code cloud environment

Open the cloud environment menu in the session title bar → **Edit**.

**Setup script:** paste the contents of `scripts/cloud-setup.sh`. (Setup scripts can't read
environment variables or secrets. It only installs tools.)

**Environment variables / secrets** (values come from sections 1–2):

| Name | Value |
|---|---|
| `M365_TENANT_ID` | Directory (tenant) ID |
| `M365_APP_ID` | Application (client) ID |
| `M365_CERT_BASE64` | Contents of `spfx-deploy.pfx.b64` |
| `M365_CERT_PASSWORD` | `.pfx` password |
| `SPO_TENANT_URL` | `https://contoso.sharepoint.com` |
| `SPO_APP_CATALOG_URL` | `https://contoso.sharepoint.com/sites/appcatalog` (optional; auto-discovered) |
| `SPO_TARGET_SITE_URL` | Site to install the app on and test against |
| `SPO_TEST_USER` / `SPO_TEST_PASSWORD` | Test account from section 2 |
| `TEAMS_SYNC` | `true` to sync Teams-enabled solutions to Teams (optional) |

Never paste these values into a chat. Claude reads them only from the environment.
For one tenant per project, create one cloud environment per tenant/target site.

**Network access:** choose *Limited* and add these to **Allowed domains**, with *Allow package managers* left ticked:
```
*.sharepoint.com
login.microsoftonline.com
*.microsoftonline.com
graph.microsoft.com
aadcdn.msftauth.net
*.msauth.net
*.msftauth.net
login.live.com
*.office.com
*.office.net
*.cdn.office.net
res-1.cdn.office.net
*.sharepointonline.com
*.akamaihd.net
raw.githubusercontent.com
learn.microsoft.com
```
(Or choose full access.) If something is still blocked, Claude names the denied host. See
https://code.claude.com/docs/en/cloud-environments#network-access.

**Optional, GitHub Actions fallback:** add the same names as **repository secrets** (or as an Environment
named `production`) so `release.yml` can redeploy or roll back without a Claude session.

---

## 4. Every project

1. Create a GitHub repo and **copy everything in this folder (including dot-folders) to the repo root**:
   ```bash
   cp -r spfx-claude-template/. /path/to/new-repo/
   ```
2. Commit the inputs:
   - `requirements/<BRD>.xlsx`
   - `requirements/design/*` (screenshots named like `01-home-desktop.png`, `01-home-mobile.png`, ...)
3. Start a Claude Code on the web session on that repo, using the environment from section 3.
4. Paste the prompt from `KICKOFF_PROMPT.md`, filled in.
5. Claude runs ingest → plan → build → verify → deploy per increment and finishes with a report. Review
   `docs/OPEN_QUESTIONS.md`, `docs/DESIGN_REVIEW.md` and the PR it opens.

### What "autonomous" covers here

Claude has **full authority to deploy to production** once every gate passes: build, lint, unit tests,
traceability, live-site smoke, visual and accessibility checks, and design review. It will **not**:
delete or retype lists/fields, remove other apps, change tenant settings, weaken tests, or force-push.
The `.claude/settings.json` denylist enforces the most destructive of these as well. It stops and reports
on the Hard Stops in `CLAUDE.md` §10.

### Things to verify on your first project

- `scripts/deploy.sh` install→upgrade fallback and Teams sync (`TEAMS_SYNC`) against your tenant. CLI for
  Microsoft 365 output field names occasionally change between major versions.
- Sign-in selectors in `tests/e2e/auth.setup.ts` against your tenant's sign-in page (custom branding can change them).
- Whether the app-only identity can approve API permission requests in your tenant (usually it can't).
