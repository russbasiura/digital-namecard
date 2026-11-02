#!/usr/bin/env bash
# Build the SPFx solution. Auto-detects Heft (SPFx 1.22+) vs gulp toolchains.
#   scripts/build.sh          -> clean, lint, test, production bundle, package (.sppkg)
#   scripts/build.sh --quick  -> lint, test, debug build (fast inner loop)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SPFX_DIR="${SPFX_DIR:-$ROOT/spfx}"
MODE="${1:-full}"

export NVM_DIR="$HOME/.nvm"
# shellcheck disable=SC1091
[ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh" >/dev/null 2>&1
cd "$SPFX_DIR"
[ -f .nvmrc ] && nvm use >/dev/null 2>&1 || true

[ -d node_modules ] || { if [ -f package-lock.json ]; then npm ci; else npm install; fi; }

if grep -q 'heft' package.json; then
  TOOL=heft
else
  TOOL=gulp
fi
echo "== build ($TOOL, $MODE) =="

run_lint() {
  if npm run | grep -qE '^\s+lint$'; then npm run lint; else npx eslint "src/**/*.{ts,tsx}"; fi
}

if [ "$MODE" = "--quick" ]; then
  run_lint
  if [ "$TOOL" = heft ]; then npx heft test; else npx gulp build && { npm test --if-present; }; fi
  exit 0
fi

run_lint
if [ "$TOOL" = heft ]; then
  npx heft test --clean --production
  npx heft package-solution --production
else
  npx gulp clean
  npm test --if-present
  npx gulp bundle --ship
  npx gulp package-solution --ship
fi

PKG="$(ls -t sharepoint/solution/*.sppkg 2>/dev/null | head -1 || true)"
[ -n "$PKG" ] || { echo "No .sppkg produced" >&2; exit 1; }
echo "Package: $PKG ($(du -h "$PKG" | cut -f1))"
