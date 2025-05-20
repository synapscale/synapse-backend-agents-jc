import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './tests/playwright-tests',
  use: {
    baseURL: 'http://localhost:3000',
  },
  projects: [
    {
      name: 'chromium',
      use: { browserName: 'chromium' },
    },
  ],
});