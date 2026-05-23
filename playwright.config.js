const { defineConfig } = require('@playwright/test');

const ADMIN_EMAIL = process.env.E2E_ADMIN_EMAIL || 'admin@uni.edu';
const ADMIN_PASSWORD = process.env.E2E_ADMIN_PASSWORD || 'Admin123!'; // NOSONAR
const DOCENTE_EMAIL = process.env.E2E_DOCENTE_EMAIL || 'docente@uni.edu';
const DOCENTE_PASSWORD = process.env.E2E_DOCENTE_PASSWORD || 'Docente123!'; // NOSONAR

module.exports = defineConfig({
  testDir: './tests/e2e/specs',
  timeout: 30_000,
  retries: 1,
  workers: 1,
  use: {
    baseURL: 'http://localhost:5173',
    headless: true,
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
    trace: 'retain-on-failure',
  },
  env: {
    ADMIN_EMAIL,
    ADMIN_PASSWORD,
    DOCENTE_EMAIL,
    DOCENTE_PASSWORD,
    BACKEND_URL: process.env.BACKEND_URL || 'http://localhost:8000',
  },
});
