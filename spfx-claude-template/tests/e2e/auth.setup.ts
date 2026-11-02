import { test as setup, expect } from '@playwright/test';
import { existsSync, statSync, mkdirSync } from 'node:fs';

const STATE = '.auth/user.json';

// Signs in the MFA-excluded test account and stores the session for the other tests.
setup('authenticate', async ({ page }) => {
  const site = process.env.SPO_TARGET_SITE_URL;
  const user = process.env.SPO_TEST_USER;
  const pass = process.env.SPO_TEST_PASSWORD;
  if (!site || !user || !pass) throw new Error('SPO_TARGET_SITE_URL / SPO_TEST_USER / SPO_TEST_PASSWORD must be set');

  // Reuse a session younger than 8 hours.
  if (existsSync(STATE) && Date.now() - statSync(STATE).mtimeMs < 8 * 3600_000) return;
  mkdirSync('.auth', { recursive: true });

  await page.goto(site);
  await page.locator('input[name="loginfmt"]').fill(user);
  await page.locator('input[type="submit"]').click();
  await page.locator('input[name="passwd"]').fill(pass);
  await page.locator('input[type="submit"]').click();

  // "Stay signed in?" prompt (KMSI) — answer Yes if it appears.
  const kmsi = page.locator('#idSIButton9, input[value="Yes"]');
  if (await kmsi.isVisible({ timeout: 10_000 }).catch(() => false)) await kmsi.click();

  await page.waitForURL((url) => url.href.startsWith(site), { timeout: 60_000 });
  await expect(page.locator('body')).toBeVisible();
  await page.context().storageState({ path: STATE });
});
