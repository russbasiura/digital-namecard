#!/usr/bin/env bash
# Deploy the SPFx package to the tenant app catalog and install/upgrade it on the target site.
#   scripts/deploy.sh                 -> deploy spfx/sharepoint/solution/*.sppkg (run build.sh first)
#   scripts/deploy.sh --from-tag v1.2.0  -> rebuild that tag in a temp worktree and deploy it (rollback)
# Env: SPO_TARGET_SITE_URL (required), SPO_APP_CATALOG_URL (optional), TEAMS_SYNC=true (optional)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SPFX_DIR="${SPFX_DIR:-$ROOT/spfx}"
: "${SPO_TARGET_SITE_URL:?SPO_TARGET_SITE_URL is not set}"

jget() { node -e 'let s="";process.stdin.on("data",d=>s+=d).on("end",()=>{let v=JSON.parse(s);for(const k of process.argv[1].split("."))v=v?.[k];process.stdout.write(v==null?"":String(v))})' "$1"; }

if [ "${1:-}" = "--from-tag" ]; then
  TAG="${2:?usage: deploy.sh --from-tag <tag>}"
  WT="$(mktemp -d)/rollback"
  git -C "$ROOT" worktree add --detach "$WT" "$TAG"
  trap 'git -C "$ROOT" worktree remove --force "$WT"' EXIT
  # SharePoint won't downgrade an installed app, so ship the old code under a NEW, higher version.
  CUR="$(jget solution.version < "$ROOT/spfx/config/package-solution.json")"
  NEXT="$(node -e 'const [a,b,c]=process.argv[1].split(".").map(Number);console.log(`${a}.${b}.${c+1}`)' "$CUR")"
  SPFX_DIR="$WT/spfx" node "$ROOT/scripts/bump-version.mjs" "$NEXT"
  echo "Rollback: deploying code from $TAG as v$NEXT — commit this version bump to the repo afterwards"
  SPFX_DIR="$WT/spfx" bash "$ROOT/scripts/build.sh"
  SPFX_DIR="$WT/spfx" ROLLBACK=1 bash "$ROOT/scripts/deploy.sh"
  exit 0
fi

bash "$ROOT/scripts/m365-login.sh"

PKG="$(ls -t "$SPFX_DIR"/sharepoint/solution/*.sppkg 2>/dev/null | head -1 || true)"
[ -n "$PKG" ] || { echo "No .sppkg found — run scripts/build.sh first" >&2; exit 1; }
PKG_NAME="$(basename "$PKG")"
PS="$SPFX_DIR/config/package-solution.json"
VERSION="$(jget solution.version < "$PS")"
SKIP_FEATURE="$(jget solution.skipFeatureDeployment < "$PS")"

CATALOG="${SPO_APP_CATALOG_URL:-}"
if [ -z "$CATALOG" ]; then
  CATALOG="$(m365 spo tenant appcatalogurl get --output text | tr -d '\r\n')"
fi
[ -n "$CATALOG" ] || { echo "Tenant app catalog not found — an admin must create it" >&2; exit 1; }

echo "== Deploying $PKG_NAME v$VERSION to $CATALOG =="
m365 spo app add --filePath "$PKG" --appCatalogScope tenant --appCatalogUrl "$CATALOG" --overwrite >/dev/null
APP_ID="$(m365 spo app get --name "$PKG_NAME" --appCatalogScope tenant --appCatalogUrl "$CATALOG" --output json | jget ID)"
[ -n "$APP_ID" ] || { echo "Could not resolve app ID after upload" >&2; exit 1; }

deploy_args=(spo app deploy --id "$APP_ID" --appCatalogScope tenant --appCatalogUrl "$CATALOG")
[ "$SKIP_FEATURE" = "true" ] && deploy_args+=(--skipFeatureDeployment)
m365 "${deploy_args[@]}" >/dev/null
echo "Deployed (tenant-wide: ${SKIP_FEATURE:-false}) — app id $APP_ID"

# Install on the target site, or upgrade if already installed.
if m365 spo app install --id "$APP_ID" --siteUrl "$SPO_TARGET_SITE_URL" --appCatalogScope tenant >/dev/null 2>/tmp/spfx-install.err; then
  echo "Installed on $SPO_TARGET_SITE_URL"
else
  if grep -qiE "already|exist|installed" /tmp/spfx-install.err; then
    m365 spo app upgrade --id "$APP_ID" --siteUrl "$SPO_TARGET_SITE_URL" --appCatalogScope tenant >/dev/null
    echo "Upgraded on $SPO_TARGET_SITE_URL"
  else
    cat /tmp/spfx-install.err >&2; exit 1
  fi
fi

# Optional: sync to Teams (for Teams-enabled web parts). Best effort; verify on first project.
if [ "${TEAMS_SYNC:-false}" = "true" ]; then
  ITEM_ID="$(m365 spo listitem list --webUrl "$CATALOG" --listTitle "Apps for SharePoint" --filter "UniqueId eq guid'$APP_ID'" --fields Id --output json | jget 0.Id || true)"
  if [ -n "$ITEM_ID" ] && m365 request --method post --url "$CATALOG/_api/web/tenantappcatalog/SyncSolutionToTeams(id=$ITEM_ID)" >/dev/null 2>&1; then
    echo "Synced to Teams"
  else
    echo "WARN: Teams sync failed — record in docs/OPEN_QUESTIONS.md (may require Teams admin)" >&2
  fi
fi

# Report pending API permission requests (approval needs SharePoint admin rights).
PENDING="$(m365 spo serviceprincipal permissionrequest list --output json 2>/dev/null || echo '[]')"
COUNT="$(printf '%s' "$PENDING" | node -e 'let s="";process.stdin.on("data",d=>s+=d).on("end",()=>{try{console.log(JSON.parse(s).length)}catch{console.log(0)}})')"
[ "$COUNT" != "0" ] && echo "NOTE: $COUNT pending API permission request(s) — see CLAUDE.md §8"

echo "DEPLOY OK: $PKG_NAME v$VERSION ${ROLLBACK:+(rollback)}"
