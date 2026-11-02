#!/usr/bin/env node
// Idempotent, ADDITIVE provisioning of SharePoint lists/libraries/fields/views from /provisioning/*.json.
// Never deletes or changes the type of existing artifacts — differences are reported as warnings.
//
// Usage: node scripts/provision.mjs [--dry-run] [--site <url>]
// Schema: see provisioning/schema.example.json
import { execFileSync } from 'node:child_process';
import { readdirSync, readFileSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const args = process.argv.slice(2);
const dryRun = args.includes('--dry-run');
const siteIdx = args.indexOf('--site');
const webUrl = siteIdx >= 0 ? args[siteIdx + 1] : process.env.SPO_TARGET_SITE_URL;
if (!webUrl) { console.error('SPO_TARGET_SITE_URL is not set'); process.exit(1); }

const changes = [];
const warnings = [];

function m365(cmdArgs, { allowFail = false } = {}) {
  try {
    const out = execFileSync('m365', [...cmdArgs, '--output', 'json'], { encoding: 'utf8', stdio: ['ignore', 'pipe', 'pipe'] });
    return out.trim() ? JSON.parse(out) : null;
  } catch (e) {
    if (allowFail) return undefined;
    throw new Error(`m365 ${cmdArgs.slice(0, 3).join(' ')} failed: ${e.stderr || e.message}`);
  }
}

const esc = (s) => String(s).replace(/&/g, '&amp;').replace(/"/g, '&quot;').replace(/</g, '&lt;');

function fieldXml(f) {
  const attrs = {
    Type: f.type, Name: f.internalName, StaticName: f.internalName, DisplayName: f.displayName || f.internalName,
    Required: f.required ? 'TRUE' : 'FALSE', ...(f.indexed ? { Indexed: 'TRUE' } : {}),
    ...(f.type === 'Note' ? { NumLines: f.numLines || 6, RichText: f.richText ? 'TRUE' : 'FALSE' } : {}),
    ...(f.type === 'DateTime' ? { Format: f.format || 'DateOnly' } : {}),
    ...(f.type === 'UserMulti' || f.type === 'LookupMulti' ? { Mult: 'TRUE' } : {}),
    ...(f.type === 'Lookup' || f.type === 'LookupMulti' ? { ShowField: f.showField || 'Title', List: `{LIST:${f.lookupList}}` } : {}),
    ...(f.attributes || {}),
  };
  const attrStr = Object.entries(attrs).map(([k, v]) => `${k}="${esc(v)}"`).join(' ');
  let inner = '';
  if (f.choices?.length) inner += `<CHOICES>${f.choices.map((c) => `<CHOICE>${esc(c)}</CHOICE>`).join('')}</CHOICES>`;
  if (f.default != null) inner += `<Default>${esc(f.default)}</Default>`;
  return `<Field ${attrStr}>${inner}</Field>`;
}

function resolveLookupIds(f, listIds) {
  if (!f.lookupList) return f;
  const id = listIds[f.lookupList] ?? m365(['spo', 'list', 'get', '--webUrl', webUrl, '--title', f.lookupList], { allowFail: true })?.Id;
  if (!id) throw new Error(`Lookup list "${f.lookupList}" not found for field ${f.internalName}`);
  return { ...f, attributes: { ...(f.attributes || {}), List: `{${id}}` } };
}

const dir = join(root, 'provisioning');
const files = readdirSync(dir).filter((f) => f.endsWith('.json') && !f.includes('example')).sort();
if (!files.length) { console.log('No provisioning files — nothing to do.'); process.exit(0); }

if (!dryRun) execFileSync('bash', [join(root, 'scripts', 'm365-login.sh')], { stdio: 'inherit' });

const listIds = {};
for (const file of files) {
  const spec = JSON.parse(readFileSync(join(dir, file), 'utf8'));
  for (const list of spec.lists || []) {
    let existing = dryRun ? undefined : m365(['spo', 'list', 'get', '--webUrl', webUrl, '--title', list.title], { allowFail: true });
    if (!existing) {
      changes.push(`create list "${list.title}"`);
      if (!dryRun) {
        existing = m365(['spo', 'list', 'add', '--webUrl', webUrl, '--title', list.title, '--baseTemplate',
          list.template || 'GenericList', ...(list.description ? ['--description', list.description] : []),
          ...(list.enableVersioning !== false ? ['--enableVersioning', 'true'] : [])]);
      }
    }
    if (existing?.Id) listIds[list.title] = existing.Id;

    for (const raw of list.fields || []) {
      const field = dryRun ? raw : resolveLookupIds(raw, listIds);
      const current = dryRun ? undefined : m365(['spo', 'field', 'get', '--webUrl', webUrl, '--listTitle', list.title,
        '--internalName', field.internalName], { allowFail: true });
      if (!current) {
        changes.push(`add field ${list.title}.${field.internalName} (${field.type})`);
        if (!dryRun) {
          m365(['spo', 'field', 'add', '--webUrl', webUrl, '--listTitle', list.title, '--xml', fieldXml(field),
            ...(field.addToDefaultView !== false ? ['--addToDefaultView'] : [])]);
        }
      } else if (current.TypeAsString && current.TypeAsString !== field.type) {
        warnings.push(`${list.title}.${field.internalName}: exists as ${current.TypeAsString}, spec says ${field.type} — NOT changed (destructive)`);
      }
    }

    for (const view of list.views || []) {
      const current = dryRun ? undefined : m365(['spo', 'list', 'view', 'get', '--webUrl', webUrl, '--listTitle', list.title,
        '--title', view.title], { allowFail: true });
      if (!current) {
        changes.push(`add view ${list.title}/${view.title}`);
        if (!dryRun) {
          m365(['spo', 'list', 'view', 'add', '--webUrl', webUrl, '--listTitle', list.title, '--title', view.title,
            '--fields', view.fields.join(','), ...(view.query ? ['--viewQuery', view.query] : []),
            ...(view.default ? ['--default'] : []), ...(view.rowLimit ? ['--rowLimit', String(view.rowLimit)] : [])]);
        }
      }
    }
  }
}

console.log(changes.length ? `${dryRun ? 'Would apply' : 'Applied'}:\n  - ${changes.join('\n  - ')}` : 'Provisioning up to date (no changes).');
if (warnings.length) console.warn(`Warnings (log in docs/OPEN_QUESTIONS.md):\n  - ${warnings.join('\n  - ')}`);
