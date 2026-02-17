import { test, expect } from '@playwright/test';
import { asyncWrapProviders } from 'async_hooks';

test.describe('sign-in', () => {
    test.describe('validation', () => {
        test('If select plan type and fill name, submit enabled', async ({ 
            page,
        }) => {
            const startURL = 'https://vercel.com/signup';

            await page.goto(startURL);


            await expect(
                page.getByRole('button', {name: 'Continue'})
            ).toBeDisabled();

            await page.getByText("I'm working on personal projects").click();

            await page.getByLabel('Your name').fill('a');

            await expect(
                page.getByRole('button', {name: 'Continue'})
            ).toBeEnabled();
        });
    })
})