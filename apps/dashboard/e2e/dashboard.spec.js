import { test, expect } from '@playwright/test';
import { makeForecast } from '../src/test/fixtures';

test('navegación de tarjetas con teclado y diseño móvil sin desbordamiento', async ({ page }) => {
  if (!process.env.E2E_REAL_API) await page.route('**/api/v1/forecast/**', (route) => route.fulfill({ json: makeForecast() }));
  await page.goto('/');
  const cards = page.getByRole('group', { name: 'Selecciona un día de los próximos siete días' }).getByRole('button');
  await expect(cards).toHaveCount(7);
  await expect(cards.first()).toHaveAttribute('aria-pressed', 'true');
  await cards.nth(1).focus();
  await page.keyboard.press('Enter');
  await expect(cards.nth(1)).toHaveAttribute('aria-pressed', 'true');
  await expect(cards.first()).toHaveAttribute('aria-pressed', 'false');
  await page.screenshot({ path: 'test-results/dashboard-desktop.png', fullPage: true });
  await page.setViewportSize({ width: 375, height: 812 });
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);
  const box = await cards.first().boundingBox();
  expect(box.width).toBeGreaterThanOrEqual(44);
  expect(box.height).toBeGreaterThanOrEqual(44);
  await page.screenshot({ path: 'test-results/dashboard-mobile.png', fullPage: true });
});
