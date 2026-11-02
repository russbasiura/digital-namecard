import { test, expect } from '@playwright/test';
import { config, openPage, tag } from './helpers';

// Post-deploy smoke: app renders without console errors on each smoke page.
for (const spec of config.pages.filter((p) => p.smoke)) {
  test(`${tag(spec)} renders @smoke`, async ({ page }) => {
    const errors: string[] = [];
    page.on('pageerror', (e) => errors.push(e.message));
    page.on('console', (m) => { if (m.type() === 'error' && /spfx|sp-|webpart|extension/i.test(m.text())) errors.push(m.text()); });
    await openPage(page, spec);
    await expect(page.locator(spec.root).first()).toBeVisible();
    await expect(page.locator(spec.root).first().getByText(/something went wrong|error loading/i)).toHaveCount(0);
    expect(errors).toEqual([]);
  });
}
