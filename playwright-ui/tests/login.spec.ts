import { test, expect } from '@playwright/test';
import { getCustomersForRun } from './customers';
import { LoginPage, CustomerDashboardPage } from '../pages';
import { HomePage, CustomerLoginPage } from '../locators/selectors';

const customers = getCustomersForRun();

test.describe('Banking login', () => {
  for (const customerName of customers) {
    test(`home page shows XYZ Bank and login options (${customerName})`, async ({ page }) => {
      await test.step('Navigate to home and expect login options visible', async () => {
        await page.goto('', { waitUntil: 'domcontentloaded', timeout: 30000 });
        await expect(page.locator(HomePage.customer_login_btn)).toBeVisible();
        await expect(page.locator(HomePage.manager_login_btn)).toBeVisible();
      });
    });

    test(`customer dropdown lists users and Login appears after select (${customerName})`, async ({
      page,
    }) => {
      const loginPage = new LoginPage(page);
      await test.step('Go to home', async () => {
        await loginPage.goToHome();
      });
      await test.step('Select customer login and choose user', async () => {
        await loginPage.selectCustomerLogin();
        await page.locator(CustomerLoginPage.user_select).selectOption({ index: 1 });
        await expect(page.locator(CustomerLoginPage.login_btn)).toBeVisible();
      });
    });
  }

  for (const customerName of customers) {
    test(`dashboard after login and logout for ${customerName}`, async ({ page }) => {
      const loginPage = new LoginPage(page);
      const dashboardPage = new CustomerDashboardPage(page);
      await test.step('Log in as customer', async () => {
        await loginPage.loginAsCustomer(customerName);
      });
      await test.step('Expect dashboard loaded with welcome name', async () => {
        await expect(page.locator('span.fontBig')).toContainText(customerName);
      });
      await test.step('Log out and expect login visible', async () => {
        await dashboardPage.clickLogout();
        await expect(page.locator(CustomerLoginPage.user_select)).toBeVisible();
      });
    });
  }
});
