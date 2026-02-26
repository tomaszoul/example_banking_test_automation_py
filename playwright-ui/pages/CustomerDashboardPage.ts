/**
 * Customer dashboard page object for XYZ Banking Project.
 * Mirrors src/banking/pages/customer_dashboard_page.py.
 */
import type { Page } from '@playwright/test';
import { waitForAngular } from './helpers';
import { CustomerDashboard } from '../locators/selectors';

export class CustomerDashboardPage {
  constructor(private readonly page: Page) {}

  async getWelcomeText(): Promise<string> {
    return (await this.page.locator(CustomerDashboard.welcome_name).textContent())?.trim() ?? '';
  }

  async getBalance(): Promise<number> {
    const text = (await this.page.locator(CustomerDashboard.balance).textContent()) ?? '0';
    const digits = text.replace(/[^0-9.-]/g, '') || '0';
    return parseInt(digits, 10);
  }

  async getAccountOptions(): Promise<string[]> {
    const raw = await this.page.locator(`${CustomerDashboard.account_select} option`).allTextContents();
    return raw.map((s) => s.trim()).filter(Boolean);
  }

  /** Wait for dropdown to be ready. */
  private static readonly WAIT_TIMEOUT = 10_000;
  /** Per-attempt timeout: keep total under test timeout so we don't get "page closed". */
  private static readonly SELECT_ATTEMPT_TIMEOUT = 6_000;

  async selectAccount(accountNumberOrLabel: string): Promise<void> {
    const loc = this.page.locator(CustomerDashboard.account_select);
    await loc.waitFor({ state: 'visible', timeout: CustomerDashboardPage.WAIT_TIMEOUT });
    const opts = { timeout: CustomerDashboardPage.SELECT_ATTEMPT_TIMEOUT };
    const attempts = [
      () => loc.selectOption({ value: accountNumberOrLabel }, opts),
      () => loc.selectOption({ value: `number:${accountNumberOrLabel}` }, opts),
      () => loc.selectOption({ label: accountNumberOrLabel }, opts),
      () => this.selectAccountByMatchingOption(loc, accountNumberOrLabel, opts),
    ];
    for (const attempt of attempts) {
      try {
        await attempt();
        await waitForAngular(this.page);
        return;
      } catch {
        // try next
      }
    }
    await loc.selectOption({ label: accountNumberOrLabel }, opts);
    await waitForAngular(this.page);
  }

  /** Fallback: select option whose value or text contains the account number. */
  private async selectAccountByMatchingOption(
    selectLoc: ReturnType<Page['locator']>,
    accountNumber: string,
    opts: { timeout: number }
  ): Promise<void> {
    const options = await selectLoc.locator('option').all();
    for (const opt of options) {
      const value = (await opt.getAttribute('value')) ?? '';
      const text = (await opt.textContent()) ?? '';
      if (value.includes(accountNumber) || text.includes(accountNumber)) {
        await selectLoc.selectOption({ value }, opts);
        return;
      }
    }
    throw new Error(`No option found for account ${accountNumber}`);
  }

  async clickLogout(): Promise<void> {
    await this.page.locator(CustomerDashboard.logout_btn).click();
    await waitForAngular(this.page);
  }

  async expectLoaded(): Promise<void> {
    await this.page.locator(CustomerDashboard.welcome_name).waitFor({ state: 'visible', timeout: 15000 });
  }
}
