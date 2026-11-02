import { readFileSync } from 'node:fs';
import type { Page } from '@playwright/test';

export interface PageSpec {
  name: string;
  url: string;
  root: string;
  design?: Record<string, string>;
  requirements?: string[];
  smoke?: boolean;
  waitFor?: string;
}
export interface PagesFile { viewports: Record<string, { width: number; height: number }>; pages: PageSpec[] }

export const config: PagesFile = JSON.parse(readFileSync(new URL('./pages.json', import.meta.url), 'utf8'));

/** Navigate and wait until SharePoint + the app have settled. */
export async function openPage(page: Page, spec: PageSpec) {
  await page.goto(spec.url, { waitUntil: 'domcontentloaded' });
  await page.locator(spec.root).first().waitFor({ state: 'visible', timeout: 60_000 });
  if (spec.waitFor) await page.locator(spec.waitFor).first().waitFor({ state: 'visible' });
  await page.waitForLoadState('networkidle').catch(() => undefined);
  // Hide volatile SharePoint chrome (suite bar notifications, feedback buttons) for stable captures.
  await page.addStyleTag({ content: '#O365_NavHeader [role="status"], .feedback-button { visibility: hidden !important; }' });
}

export const tag = (spec: PageSpec) =>
  `${(spec.requirements || []).length ? `[${spec.requirements!.join(', ')}] ` : ''}${spec.name}`;
