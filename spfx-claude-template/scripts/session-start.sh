#!/usr/bin/env bash
# SessionStart hook: verifies tools and required env vars WITHOUT printing secret values.
set -uo pipefail
export NVM_DIR="$HOME/.nvm"
# shellcheck disable=SC1091
[ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh" >/dev/null 2>&1
cd "${CLAUDE_PROJECT_DIR:-.}" || exit 0
[ -f .nvmrc ] && nvm use >/dev/null 2>&1

echo "== SPFx environment check =="
for t in node npm yo m365 python3 git; do
  if command -v "$t" >/dev/null 2>&1; then echo "  ok   $t"; else echo "  MISSING $t (fix the environment setup script)"; fi
done
python3 -c "import openpyxl" 2>/dev/null && echo "  ok   openpyxl" || echo "  MISSING python openpyxl"

missing=()
for v in M365_TENANT_ID M365_APP_ID M365_CERT_BASE64 SPO_TENANT_URL SPO_TARGET_SITE_URL SPO_TEST_USER SPO_TEST_PASSWORD; do
  [ -n "${!v:-}" ] || missing+=("$v")
done
if [ ${#missing[@]} -eq 0 ]; then
  echo "  ok   all required environment variables are set (values hidden)"
else
  echo "  MISSING env vars: ${missing[*]} — deployment and live-tenant tests will be blocked"
fi

ls requirements/*.xlsx >/dev/null 2>&1 && echo "  ok   BRD found" || echo "  NOTE no BRD .xlsx in requirements/ yet"
[ -n "$(ls -A requirements/design 2>/dev/null | grep -v README)" ] && echo "  ok   design package found" || echo "  NOTE requirements/design/ is empty"
exit 0
