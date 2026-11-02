import { test, expect } from '@playwright/test';
import { mkdirSync } from 'node:fs';
import { config, openPage, tag } from './helpers';

// For every page x viewport:
//  1. capture the app root to artifacts/screenshots/<page>-<viewport>.png (Claude compares these with the design files)
//  2. compare to the approved baseline in baselines/ (regression). First run: create baselines with --update-snapshots.
mkdirSync('artifacts/screenshots', { recursive: true });

for (const spec of config.pages) {
  for (const [vpName, vp] of Object.entries(config.viewports)) {
    test(`${tag(spec)} visual ${vpName}`, async ({ page }) => {
      await page.setViewportSize(vp);
      await openPage(page, spec);
      const root = page.locator(spec.root).first();
      await root.screenshot({ path: `artifacts/screenshots/${spec.name}-${vpName}.png`, animations: 'disabled' });
      await expect(root).toHaveScreenshot(`${spec.name}-${vpName}.png`);
    });
  }
}
