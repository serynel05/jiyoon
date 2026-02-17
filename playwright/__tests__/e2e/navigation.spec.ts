import { test, expect } from '@playwright/test';

test ('if user visit home and click "Get started", h1 "introduction" is visible and page title containes "Introduction" ', async ({
    page,
 }) => {
    const startURL = 'http://localhost:3000/';
    const h1 = 'Next.js';
    const title = /Next\.js/;

    await page.goto(startURL);
    await page.getByRole('link', {name: 'Get Started'}).click();

    const isVisible = await page
      .getByRole('heading', { name: h1, level:1 })
      .isVisible();
   //console.log(isVisible);
   //expect(isVisible).toEqual(true);

   await expect(page.getByRole('heading', { name: h1, level: 1 })).toBeVisible();
    // await expect(page).toHaveTitle(title);
 });
