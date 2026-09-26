import { chromium } from 'playwright';
import fs from 'node:fs/promises';
import path from 'node:path';

const baseURL = process.env.SCREENSHOT_BASE_URL || 'http://127.0.0.1:3000';
const outDir = path.resolve(process.cwd(), '../../docs/screenshots');
await fs.mkdir(outDir, { recursive: true });

const browser = await chromium.launch({ headless: true });

async function capture({ name, url, viewport, fullPage = true }) {
  const page = await browser.newPage({
    viewport,
    deviceScaleFactor: 1,
  });
  await page.goto(baseURL + url, { waitUntil: 'domcontentloaded', timeout: 45_000 });
  await page.waitForTimeout(3_000);
  await page.screenshot({
    path: path.join(outDir, name),
    type: 'jpeg',
    quality: 88,
    fullPage,
  });
  await page.close();
}

await capture({
  name: 'operations-dashboard-desktop.jpg',
  url: '/',
  viewport: { width: 1440, height: 1100 },
});

await capture({
  name: 'analyst-event-detail.jpg',
  url: '/events/demo-003',
  viewport: { width: 1440, height: 1100 },
});

await capture({
  name: 'methodology-and-ethics.jpg',
  url: '/methodology',
  viewport: { width: 1440, height: 1100 },
});

await capture({
  name: 'operations-dashboard-mobile.jpg',
  url: '/',
  viewport: { width: 430, height: 932 },
});

await browser.close();
console.log(`Captured SentinelOSINT UI screenshots in ${outDir}`);
