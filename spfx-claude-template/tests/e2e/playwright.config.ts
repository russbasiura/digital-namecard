import { defineConfig, devices } from '@playwright/test';
import { existsSync } from 'node:fs';

// Cloud images ship Chromium here; use it if present so no browser download is needed.
const chromiumPath = process.env.CHROMIUM_PATH || (existsSync('/opt/pw-browsers/chromium') ? '/opt/pw-browsers/chromium' : undefined);
const launchOptions = chromiumPath ? { executablePath: chromiumPath } : {};

export default defineConfig({
  testDir: '.',
  timeout: 90_000,
  expect: { timeout: 20_000, toHaveScreenshot: { maxDiffPixelRatio: 0.02, animations: 'disabled' } },
  retries: 1,
  workers: 2,
  reporter: [['list'], ['html', { open: 'never', outputFolder: 'artifacts/report' }]],
  outputDir: 'artifacts/results',
  snapshotPathTemplate: '{testDir}/baselines/{arg}{ext}',
  use: {
    baseURL: process.env.SPO_TARGET_SITE_URL,
    trace: 'retain-on-failure',
    screenshot: 'only-on-failure',
    launchOptions,
  },
  projects: [
    { name: 'setup', testMatch: /auth\.setup\.ts/, use: { launchOptions } },
    {
      name: 'chromium',
      dependencies: ['setup'],
      testIgnore: /auth\.setup\.ts/,
      use: { ...devices['Desktop Chrome'], storageState: '.auth/user.json', launchOptions },
    },
  ],
});
