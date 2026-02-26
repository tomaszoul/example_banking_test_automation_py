/**
 * Manager page object for XYZ Banking Project.
 * Mirrors src/banking/pages/manager_page.py.
 */
import type { Page } from '@playwright/test';
import { waitForAngular } from './helpers';
import { ManagerPageSelectors } from '../locators/selectors';

export interface AddCustomerResult {
  customer_id: number;
}

export interface OpenAccountResult {
  account_number: string;
}

export class ManagerPage {
  constructor(private readonly page: Page) {}

  async goToManager(): Promise<void> {
    await this.page.waitForSelector(ManagerPageSelectors.add_customer_tab, { state: 'visible', timeout: 10000 });
  }

  async openAddCustomerTab(): Promise<void> {
    await this.page.locator(ManagerPageSelectors.add_customer_tab).click();
    await waitForAngular(this.page);
  }

  async openOpenAccountTab(): Promise<void> {
    await this.page.locator(ManagerPageSelectors.open_account_tab).click();
    await waitForAngular(this.page);
  }

  async openCustomersTab(): Promise<void> {
    await this.page.locator(ManagerPageSelectors.customers_tab).click();
    await waitForAngular(this.page);
  }

  async addCustomer(first: string, last: string, postCode: string): Promise<AddCustomerResult> {
    const dialogPromise = new Promise<string>((resolve) => {
      this.page.once('dialog', (d) => {
        const msg = d.message();
        d.accept();
        resolve(msg);
      });
    });
    await this.page.locator(ManagerPageSelectors.first_name_input).fill(first);
    await this.page.locator(ManagerPageSelectors.last_name_input).fill(last);
    await this.page.locator(ManagerPageSelectors.post_code_input).fill(postCode);
    await this.page.locator(ManagerPageSelectors.add_customer_btn).click();
    const msg = await dialogPromise;
    const m = msg.match(/customer id\s*:\s*(\d+)/i);
    return { customer_id: m ? parseInt(m[1], 10) : 0 };
  }

  async openAccount(customerName: string, currency: string): Promise<OpenAccountResult> {
    const dialogPromise = new Promise<string>((resolve) => {
      this.page.once('dialog', (d) => {
        const msg = d.message();
        d.accept();
        resolve(msg);
      });
    });
    await this.page.locator(ManagerPageSelectors.customer_select).selectOption({ label: customerName });
    await waitForAngular(this.page);
    await this.page.locator(ManagerPageSelectors.currency_select).selectOption({ label: currency });
    await waitForAngular(this.page);
    await this.page.locator(ManagerPageSelectors.process_btn).click({ timeout: 5000 }).catch(() =>
      this.page.getByRole('button', { name: 'Process' }).click({ timeout: 5000 })
    );
    const msg = await dialogPromise;
    const m = msg.match(/account (?:Number|number)\s*:\s*(\d+)/i);
    return { account_number: m ? m[1] : '' };
  }

  async searchCustomer(query: string): Promise<void> {
    await this.page.locator(ManagerPageSelectors.search_input).fill(query);
    await waitForAngular(this.page);
  }

  async getCustomerRows(): Promise<[string, string, string][]> {
    const rows = this.page.locator(`${ManagerPageSelectors.customers_table} tbody tr`);
    const count = await rows.count();
    const result: [string, string, string][] = [];
    for (let i = 0; i < count; i++) {
      const cells = rows.nth(i).locator('td');
      const cellCount = await cells.count();
      const first = (cellCount > 0 ? (await cells.nth(0).textContent())?.trim() ?? '' : '');
      const last = (cellCount > 1 ? (await cells.nth(1).textContent())?.trim() ?? '' : '');
      const post = (cellCount > 2 ? (await cells.nth(2).textContent())?.trim() ?? '' : '');
      result.push([first, last, post]);
    }
    return result;
  }

  async hasCustomerInList(first: string, last: string): Promise<boolean> {
    await this.page.waitForSelector(`${ManagerPageSelectors.customers_table} tbody tr`, { timeout: 5000 });
    await waitForAngular(this.page);
    const tableText = (await this.page.locator(ManagerPageSelectors.customers_table).textContent()) ?? '';
    return tableText.includes(first) && tableText.includes(last);
  }

  async deleteCustomer(first: string, last: string): Promise<void> {
    const rows = this.page.locator(`${ManagerPageSelectors.customers_table} tbody tr`);
    const count = await rows.count();
    for (let i = 0; i < count; i++) {
      const cells = rows.nth(i).locator('td');
      const f = (await cells.nth(0).textContent())?.trim() ?? '';
      const l = (await cells.nth(1).textContent())?.trim() ?? '';
      if (f === first && l === last) {
        await rows.nth(i).locator(ManagerPageSelectors.delete_btn).click();
        await waitForAngular(this.page);
        return;
      }
    }
    throw new Error(`Customer not found: ${first} ${last}`);
  }
}
