import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';
import { writeFileSync, mkdirSync } from 'node:fs';
import { config, openPage, tag } from './helpers';

// WCAG 2.1 AA scan scoped to the app root (SharePoint's own chrome is out of scope).
mkdirSync('artifacts/a11y', { recursive: true });

for (const spec of config.pages) {
  test(`${tag(spec)} a11y`, async ({ page }) => {
    await page.setViewportSize(config.viewports.desktop);
    await openPage(page, spec);
    const results = await new AxeBuilder({ page })
      .include(spec.root)
      .withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa'])
      .analyze();
    writeFileSync(`artifacts/a11y/${spec.name}.json`, JSON.stringify(results.violations, null, 2));
    const blocking = results.violations.filter((v) => v.impact === 'serious' || v.impact === 'critical');
    expect(blocking.map((v) => `${v.id} (${v.impact}): ${v.nodes.length} node(s) — ${v.help}`)).toEqual([]);
  });
}
