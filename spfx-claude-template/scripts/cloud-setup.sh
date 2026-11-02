#!/usr/bin/env bash
# Paste this into the Claude Code cloud environment's "Setup script" field.
# It installs tools only — setup scripts cannot read environment variables/secrets.
set -euo pipefail

NODE_VERSION="${NODE_VERSION:-22}"   # SPFx 1.21+ supports Node 22 LTS. CLAUDE.md re-checks per project.

# --- Node via nvm ---
export NVM_DIR="$HOME/.nvm"
if [ ! -s "$NVM_DIR/nvm.sh" ]; then
  curl -fsSL https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash
fi
# shellcheck disable=SC1091
. "$NVM_DIR/nvm.sh"
nvm install "$NODE_VERSION"
nvm alias default "$NODE_VERSION"

# --- SPFx + M365 tooling ---
npm install -g yo @microsoft/generator-sharepoint @pnp/cli-microsoft365 gulp-cli @rushstack/heft

# CLI for Microsoft 365: non-interactive defaults
m365 cli config set --key output --value json
m365 cli config set --key autoOpenLinksInBrowser --value false
m365 cli config set --key prompt --value false
m365 cli config set --key printErrorsAsPlainText --value true

# --- Python for BRD parsing ---
python3 -m pip install --quiet --upgrade openpyxl || pip3 install --quiet openpyxl

# --- Playwright browser ---
# Cloud images ship Chromium at /opt/pw-browsers; only install if it is missing.
if [ ! -e /opt/pw-browsers/chromium ] && [ -z "${PLAYWRIGHT_BROWSERS_PATH:-}" ]; then
  npx -y playwright@latest install --with-deps chromium
fi

echo "SPFx cloud setup complete: node $(node -v), m365 $(m365 version 2>/dev/null || echo '?')"
