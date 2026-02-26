import { test, expect } from '@playwright/test';
import { getCustomersForRun, CUSTOMER_ACCOUNTS } from './customers';
import { LoginPage, CustomerDashboardPage, DepositPage } from '../pages';
import { CustomerDashboard } from '../locators/selectors';

const CURRENCIES = ['Dollar', 'Pound', 'Rupee'] as const;

for (const customerName of getCustomersForRun()) {
  test.describe(`Account switching [${customerName}]`, () => {
    test.setTimeout(90_000);

    test.beforeEach(async ({ page }) => {
      await test.step('Log in as customer', async () => {
        const loginPage = new LoginPage(page);
        await loginPage.loginAsCustomer(customerName);
      });
      await test.step('Wait for dashboard', async () => {
        const dashboardPage = new CustomerDashboardPage(page);
        await dashboardPage.expectLoaded();
      });
    });

    test('welcome, default account and dropdown options', async ({ page }) => {
      const dashboardPage = new CustomerDashboardPage(page);
      await test.step('Expect welcome name', async () => {
        await expect(page.locator(CustomerDashboard.welcome_name)).toContainText(customerName);
      });
      await test.step('Expect account select visible with options', async () => {
        const accountSelect = page.locator(CustomerDashboard.account_select);
        await expect(accountSelect).toBeVisible();
        const options = await accountSelect.locator('option').allTextContents();
        expect(options.length).toBeGreaterThanOrEqual(3);
      });
    });

    test('account info updates when switching currency', async ({ page }) => {
      const dashboardPage = new CustomerDashboardPage(page);
      const accountSelect = page.locator(CustomerDashboard.account_select);
      const accounts = CUSTOMER_ACCOUNTS[customerName];
      for (const currency of CURRENCIES) {
        await test.step(`Select account for ${currency}`, async () => {
          await dashboardPage.selectAccount(accounts[currency]);
        });
        await test.step(`Expect center text contains ${currency}`, async () => {
          const centerText = await page.locator('div.center[ng-hide="noAccount"]').first().textContent();
          expect(centerText).toContain(currency);
        });
      }
    });

    test('deposits isolated between accounts', async ({ page }) => {
      const dashboardPage = new CustomerDashboardPage(page);
      const depositPage = new DepositPage(page);
      const accounts = CUSTOMER_ACCOUNTS[customerName];
      await test.step('Select Dollar account and deposit 2500', async () => {
        await dashboardPage.selectAccount(accounts.Dollar);
        await depositPage.depositAmount(2500);
      });
      const balanceDollar = await test.step('Get Dollar balance', async () => {
        return await dashboardPage.getBalance();
      });
      expect(balanceDollar).toBeGreaterThanOrEqual(2500);
      await test.step('Switch to Pound account, expect zero balance', async () => {
        await dashboardPage.selectAccount(accounts.Pound);
        const balancePound = await dashboardPage.getBalance();
        expect(balancePound).toBe(0);
      });
      await test.step('Switch back to Dollar account, expect balance unchanged', async () => {
        await dashboardPage.selectAccount(accounts.Dollar);
        const balanceDollarAfter = await dashboardPage.getBalance();
        expect(balanceDollarAfter).toBe(balanceDollar);
      });
    });

    test('accumulate deposits correctly across multiple accounts', async ({ page }) => {
      const dashboardPage = new CustomerDashboardPage(page);
      const depositPage = new DepositPage(page);
      const accounts = CUSTOMER_ACCOUNTS[customerName];
      const balancesBefore: Record<string, number> = {};
      await test.step('Record balances for each currency', async () => {
        for (const currency of CURRENCIES) {
          await dashboardPage.selectAccount(accounts[currency]);
          balancesBefore[currency] = await dashboardPage.getBalance();
        }
      });
      await test.step('Deposit 1000 on Dollar account', async () => {
        await dashboardPage.selectAccount(accounts.Dollar);
        await depositPage.depositAmount(1000);
      });
      expect(await dashboardPage.getBalance()).toBe(balancesBefore['Dollar'] + 1000);
      await test.step('Deposit 2000 on Pound account', async () => {
        await dashboardPage.selectAccount(accounts.Pound);
        await depositPage.depositAmount(2000);
      });
      expect(await dashboardPage.getBalance()).toBe(balancesBefore['Pound'] + 2000);
      await test.step('Deposit 3000 + 500 + 500 on Rupee account', async () => {
        await dashboardPage.selectAccount(accounts.Rupee);
        await depositPage.depositAmount(3000);
        await depositPage.open();
        await depositPage.enterAmount(500);
        await depositPage.submit();
        await depositPage.open();
        await depositPage.enterAmount(500);
        await depositPage.submit();
      });
      const expectedRupee = balancesBefore['Rupee'] + 3000 + 500 + 500;
      expect(await dashboardPage.getBalance()).toBe(expectedRupee);
    });

    test('UI in sync during rapid account switching', async ({ page }) => {
      const dashboardPage = new CustomerDashboardPage(page);
      const centerLoc = page.locator('div.center[ng-hide="noAccount"]').first();
      const accounts = CUSTOMER_ACCOUNTS[customerName];
      for (let cycle = 0; cycle < 3; cycle++) {
        for (const currency of CURRENCIES) {
          await test.step(`Switch to ${currency}`, async () => {
            await dashboardPage.selectAccount(accounts[currency]);
          });
          const centerText = await centerLoc.textContent();
          expect(centerText).toContain(currency);
        }
      }
    });
  });
}
