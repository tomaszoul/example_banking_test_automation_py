import { test, expect } from '@playwright/test';
import { getCustomersForRun } from './customers';
import { LoginPage, CustomerDashboardPage, DepositPage } from '../pages';
import { CustomerDashboard, TransactionsPage } from '../locators/selectors';

for (const customerName of getCustomersForRun()) {
  test.describe(`Transactions list [${customerName}]`, () => {
    test.beforeEach(async ({ page }) => {
      await test.step('Log in and deposit 500', async () => {
        const loginPage = new LoginPage(page);
        const depositPage = new DepositPage(page);
        await loginPage.loginAsCustomer(customerName);
        await new CustomerDashboardPage(page).expectLoaded();
        await depositPage.depositAmount(500);
      });
    });

    test('deposit entry appears in transactions table', async ({ page }) => {
      await test.step('Open transactions list', async () => {
        await page.locator(CustomerDashboard.transactions_btn).click();
        await page.waitForURL(/.*#\/listTx.*/);
      });
      await test.step('Expect table visible with 500', async () => {
        await expect(page.locator(TransactionsPage.table)).toBeVisible();
        await expect(page.locator(TransactionsPage.table)).toContainText('500', { timeout: 15_000 });
      });
    });

    test('reset clears table and back returns to dashboard', async ({ page }) => {
      await test.step('Open transactions list', async () => {
        await page.locator(CustomerDashboard.transactions_btn).click();
        await page.waitForURL(/.*#\/listTx.*/);
      });
      await test.step('Reset and expect empty table', async () => {
        await page.locator(TransactionsPage.reset_btn).click();
        await expect(page.locator(TransactionsPage.table + ' tbody tr')).toHaveCount(0);
      });
      await test.step('Click Back and expect dashboard', async () => {
        await page.locator(TransactionsPage.back_btn).click();
        await page.waitForURL(/.*#\/account.*/);
        await expect(page.locator(CustomerDashboard.deposit_btn)).toBeVisible();
      });
    });
  });
}
