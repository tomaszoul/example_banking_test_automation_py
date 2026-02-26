/**
 * Intentionally failing spec — mirrors Python test_failing_deposit.py.
 * Used to validate failure reporting and trace generation. Do not fix.
 */
import { test, expect } from '@playwright/test';
import { DEFAULT_CUSTOMER } from './customers';
import { LoginPage, CustomerDashboardPage, DepositPage } from '../pages';

test.describe('Failing deposit (expected to fail)', () => {
  test.beforeEach(async ({ page }) => {
    await test.step('Log in as customer', async () => {
      const loginPage = new LoginPage(page);
      await loginPage.loginAsCustomer(DEFAULT_CUSTOMER);
    });
  });

  test.fail('this test will fail — wrong expected balance for report validation', async ({ page }) => {
    const dashboardPage = new CustomerDashboardPage(page);
    const depositPage = new DepositPage(page);
    const balanceBefore = await test.step('Get balance before deposit', async () => {
      return await dashboardPage.getBalance();
    });
    await test.step('Deposit amount 10000', async () => {
      await depositPage.depositAmount(10000);
    });
    await test.step('Assert wrong expected balance (for report validation)', async () => {
      const balanceAfter = await dashboardPage.getBalance();
      const wrongExpected = balanceBefore + 1234567890;
      expect(balanceAfter).toBe(wrongExpected);
    });
  });
});
