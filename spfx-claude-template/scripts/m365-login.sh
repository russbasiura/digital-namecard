#!/usr/bin/env bash
# Idempotent app-only certificate login for CLI for Microsoft 365. Never prints secrets.
set -euo pipefail
: "${M365_TENANT_ID:?M365_TENANT_ID is not set}"
: "${M365_APP_ID:?M365_APP_ID is not set}"
: "${M365_CERT_BASE64:?M365_CERT_BASE64 is not set}"

m365 cli config set --key output --value json >/dev/null 2>&1 || true
m365 cli config set --key prompt --value false >/dev/null 2>&1 || true

if m365 status --output json 2>/dev/null | grep -q "\"$M365_APP_ID\"" ; then
  echo "m365: already logged in"
  exit 0
fi

args=(login --authType certificate --appId "$M365_APP_ID" --tenant "$M365_TENANT_ID"
      --certificateBase64Encoded "$M365_CERT_BASE64")
[ -n "${M365_CERT_PASSWORD:-}" ] && args+=(--password "$M365_CERT_PASSWORD")

for attempt in 1 2; do
  if m365 "${args[@]}" >/dev/null 2>&1; then
    echo "m365: logged in (app-only, certificate)"
    exit 0
  fi
  echo "m365: login attempt $attempt failed" >&2
  sleep 3
done
echo "m365: certificate login failed twice — Hard Stop (check app registration, cert, consent)" >&2
exit 1
