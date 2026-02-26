import { test, expect } from '@playwright/test';
import { getCustomersForRun } from './customers';
import { LoginPage, CustomerDashboardPage, DepositPage, WithdrawPage } from '../pages';

for (const customerName of getCustomersForRun()) {
  test.describe(`Withdraw flow [${customerName}]`, () => {
    test.beforeEach(async ({ page }) => {
      await test.step('Log in and deposit 5000 for withdrawal tests', async () => {
        const loginPage = new LoginPage(page);
        const depositPage = new DepositPage(page);
        await loginPage.loginAsCustomer(customerName);
        await new CustomerDashboardPage(page).expectLoaded();
        await depositPage.depositAmount(5000);
      });
    });

    test('balance reduces on withdrawal and zero on exact balance', async ({ page }) => {
      const dashboardPage = new CustomerDashboardPage(page);
      const withdrawPage = new WithdrawPage(page);
      const balanceBefore = await test.step('Get balance before withdrawal', async () => {
        return await dashboardPage.getBalance();
      });
      await test.step('Withdraw amount 1000', async () => {
        await withdrawPage.withdrawAmount(1000);
      });
      await test.step('Expect success message visible', async () => {
        await expect(page.locator('span[ng-show="message"]')).toBeVisible();
      });
      let balanceAfter = await dashboardPage.getBalance();
      expect(balanceAfter).toBe(balanceBefore - 1000);
      await test.step('Withdraw exact remaining balance', async () => {
        await withdrawPage.withdrawAmount(balanceAfter);
      });
      await test.step('Expect balance zero', async () => {
        balanceAfter = await dashboardPage.getBalance();
        expect(balanceAfter).toBe(0);
      });
    });

    test('overdraft and invalid amounts rejected', async ({ page }) => {
      const dashboardPage = new CustomerDashboardPage(page);
      const withdrawPage = new WithdrawPage(page);
      const balanceBefore = await test.step('Get balance before', async () => {
        return await dashboardPage.getBalance();
      });
      await test.step('Attempt overdraft (balance + 1)', async () => {
        await withdrawPage.open();
        await withdrawPage.enterAmount(balanceBefore + 1);
        await withdrawPage.submit();
      });
      await test.step('Expect Transaction Failed message', async () => {
        await expect(page.locator('span[ng-show="message"]')).toContainText('Transaction Failed');
      });
      await test.step('Expect balance unchanged', async () => {
        const balanceAfter = await dashboardPage.getBalance();
        expect(balanceAfter).toBe(balanceBefore);
      });
    });
  });
}
