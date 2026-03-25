import { test, expect } from '@playwright/test';

test('login -> add cart -> checkout -> success', async ({ page }) => {
  await page.goto('https://www.saucedemo.com/');

  //login
  await page.getByPlaceholder('Username').fill('standard_user');
  await page.getByPlaceholder('Password').fill('secret_sauce');

  // list 표시되는지 확인
  await Promise.all([
    page.waitForURL(/inventory\.html/),
    page.getByRole('button', { name: 'Login' }).click(),
  ]);
  
  await expect(page.locator('[data-test="add-to-cart-sauce-labs-backpack"]')).toBeVisible();
  await page.locator('[data-test="add-to-cart-sauce-labs-backpack"]').click();
  await expect(page.locator('[data-test="shopping-cart-badge"]')).toHaveText('1');
  
  // 장바구니에 상품 넣고 장바구니 확인
  await Promise.all([
    page.waitForURL(/\/cart\.html$/),
    page.locator('[data-test="shopping-cart-link"]').click(),
  ])
  
  await expect(page.locator('[data-test="title"]')).toHaveText('Your Cart');

  // 결제 화면 이동
  await Promise.all([
    page.waitForURL(/\/checkout-step-one\.html$/),
    page.getByRole('button', {name: 'Checkout'}).click()
  ])
  
  await expect(page.locator('[data-test="title"]')).toHaveText('Checkout: Your Information');

  // 결제 정보 입력 및 cart 화면 이동
  await page.getByPlaceholder('First Name').fill('test');
  await page.getByPlaceholder('Last Name').fill('123');
  await page.getByPlaceholder('Zip/Postal Code').fill('01000');

  await Promise.all([
    page.waitForURL(/\/checkout-step-two\.html$/),
    page.getByRole('button', {name: 'Continue'}).click(),
  ])

  await expect(page.locator('[data-test="title"]')).toHaveText('Checkout: Overview');

  await 


  await Promise.all([
    page.waitForURL(/\/checkout-complete\.html$/),
    page.getByRole('button', {name: 'Finish'}).click()
  ])
  await expect(page.locator('[data-test="complete-header"]')).toHaveText('Thank you for your order!');
});