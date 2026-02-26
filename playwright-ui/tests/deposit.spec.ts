import { test, expect } from '@playwright/test';
import { getCustomersForRun } from './customers';
import { LoginPage, CustomerDashboardPage, DepositPage } from '../pages';

for (const customerName of getCustomersForRun()) {
  test.describe(`Deposit flow [${customerName}]`, () => {
    test.beforeEach(async ({ page }) => {
      await test.step('Log in as customer', async () => {
        const loginPage = new LoginPage(page);
        await loginPage.loginAsCustomer(customerName);
      });
    });

    test('deposit button visible and balance updates on deposit', async ({ page }) => {
      const dashboardPage = new CustomerDashboardPage(page);
      const depositPage = new DepositPage(page);
      await test.step('Expect deposit button visible', async () => {
        await expect(page.locator('button[ng-click="deposit()"]')).toBeVisible();
      });
      const balanceBefore = await test.step('Get balance before deposit', async () => {
        return await dashboardPage.getBalance();
      });
      await test.step('Deposit amount 10000', async () => {
        await depositPage.depositAmount(10000);
      });
      await test.step('Expect balance increased by 10000', async () => {
        const balanceAfter = await dashboardPage.getBalance();
        expect(balanceAfter).toBe(balanceBefore + 10000);
      });
    });

    test('empty or zero amount does not change balance', async ({ page }) => {
      const dashboardPage = new CustomerDashboardPage(page);
      const depositPage = new DepositPage(page);
      const balanceBefore = await test.step('Get balance before', async () => {
        return await dashboardPage.getBalance();
      });
      await test.step('Open deposit and submit without amount', async () => {
        await depositPage.open();
        await depositPage.submit();
      });
      await test.step('Expect balance unchanged', async () => {
        const balanceAfter = await dashboardPage.getBalance();
        expect(balanceAfter).toBe(balanceBefore);
      });
    });
  });
}
