import { test, expect } from '@playwright/test';
import { LoginPage, ManagerPage } from '../pages';

test.describe('Manager CRUD', () => {
  test.beforeEach(async ({ page }) => {
    await test.step('Go to home and open manager', async () => {
      const loginPage = new LoginPage(page);
      await loginPage.goToHome();
      await loginPage.selectManagerLogin();
      await page.waitForURL(/.*#\/manager.*/);
    });
    await test.step('Expect manager page loaded', async () => {
      const managerPage = new ManagerPage(page);
      await managerPage.goToManager();
    });
  });

  test('add customer shows success alert with customer id', async ({ page }) => {
    const managerPage = new ManagerPage(page);
    await test.step('Open add customer tab', async () => {
      await managerPage.openAddCustomerTab();
    });
    const result = await test.step('Add customer Test CRUDUser E99999', async () => {
      return await managerPage.addCustomer('Test', 'CRUDUser', 'E99999');
    });
    await test.step('Expect customer id in result', async () => {
      expect(result.customer_id).toBeGreaterThan(0);
    });
  });

  test('open account shows success with account number', async ({ page }) => {
    const managerPage = new ManagerPage(page);
    await test.step('Open open account tab', async () => {
      await managerPage.openOpenAccountTab();
    });
    const result = await test.step('Open Dollar account for Harry Potter', async () => {
      return await managerPage.openAccount('Harry Potter', 'Dollar');
    });
    await test.step('Expect account number in result', async () => {
      expect(result.account_number).toBeTruthy();
    });
  });

  test('customers tab lists and search filters', async ({ page }) => {
    const managerPage = new ManagerPage(page);
    await test.step('Open customers tab', async () => {
      await managerPage.openCustomersTab();
    });
    await test.step('Expect table visible with Harry Potter', async () => {
      await expect(page.locator('table.table-bordered')).toBeVisible();
      const tableText = await page.locator('table.table-bordered').textContent();
      expect(tableText).toContain('Harry');
      expect(tableText).toContain('Potter');
    });
    await test.step('Search customer Harry', async () => {
      await managerPage.searchCustomer('Harry');
    });
    await test.step('Expect filtered rows visible', async () => {
      const rows = page.locator('table.table-bordered tbody tr');
      await expect(rows.first()).toBeVisible();
    });
  });

  test('full CRUD: add, open accounts, search, delete', async ({ page }) => {
    const managerPage = new ManagerPage(page);
    const uniquePostcode = `E${Date.now() % 1000000}`.padStart(6, '0').slice(-6);
    await test.step('Add customer Delete MeUser', async () => {
      await managerPage.openAddCustomerTab();
      await managerPage.addCustomer('Delete', 'MeUser', uniquePostcode);
    });
    await test.step('Open Dollar account for Delete MeUser', async () => {
      await managerPage.openOpenAccountTab();
      await managerPage.openAccount('Delete MeUser', 'Dollar');
    });
    await test.step('Open customers tab and search Delete', async () => {
      await managerPage.openCustomersTab();
      await managerPage.searchCustomer('Delete');
    });
    await test.step('Expect customer in table', async () => {
      await expect(page.locator('table.table-bordered')).toContainText('Delete');
      await expect(page.locator('table.table-bordered')).toContainText('MeUser');
    });
    await test.step('Delete customer', async () => {
      const row = page
        .locator('table.table-bordered tbody tr')
        .filter({ hasText: 'Delete' })
        .filter({ hasText: 'MeUser' });
      await row.locator('button[ng-click="deleteCust(cust)"]').click();
    });
    await test.step('Clear search and search again, expect customer gone', async () => {
      await managerPage.searchCustomer('');
      await managerPage.searchCustomer('Delete');
      await expect(page.locator('table.table-bordered')).not.toContainText('MeUser');
    });
  });
});
