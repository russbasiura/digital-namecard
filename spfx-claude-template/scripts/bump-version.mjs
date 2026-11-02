#!/usr/bin/env node
// Bump version in spfx/package.json and spfx/config/package-solution.json (+ feature versions) in sync.
// Usage: node scripts/bump-version.mjs <patch|minor|major|x.y.z>
import { readFileSync, writeFileSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const spfx = process.env.SPFX_DIR || join(root, 'spfx');
const pkgPath = join(spfx, 'package.json');
const psPath = join(spfx, 'config', 'package-solution.json');
const kind = process.argv[2] || 'patch';

const pkg = JSON.parse(readFileSync(pkgPath, 'utf8'));
const ps = JSON.parse(readFileSync(psPath, 'utf8'));

const current = (ps.solution.version || pkg.version || '0.0.1.0').split('.').slice(0, 3).map(Number);
let [maj, min, pat] = current;
if (/^\d+\.\d+\.\d+$/.test(kind)) [maj, min, pat] = kind.split('.').map(Number);
else if (kind === 'major') { maj++; min = 0; pat = 0; }
else if (kind === 'minor') { min++; pat = 0; }
else if (kind === 'patch') { pat++; }
else { console.error(`Unknown bump: ${kind}`); process.exit(1); }

const semver = `${maj}.${min}.${pat}`;
pkg.version = semver;
ps.solution.version = `${semver}.0`;
for (const f of ps.solution.features || []) f.version = `${semver}.0`;

writeFileSync(pkgPath, JSON.stringify(pkg, null, 2) + '\n');
writeFileSync(psPath, JSON.stringify(ps, null, 2) + '\n');
console.log(semver);
