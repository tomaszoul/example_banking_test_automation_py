/**
 * Withdraw page object for XYZ Banking Project.
 * Mirrors src/banking/pages/withdraw_page.py.
 */
import type { Page } from '@playwright/test';
import { applyCiBuffer, waitForAngular } from './helpers';
import { CustomerDashboard, WithdrawPageSelectors } from '../locators/selectors';

export class WithdrawPage {
  constructor(private readonly page: Page) {}

  async open(): Promise<void> {
    await this.page.locator(CustomerDashboard.withdraw_btn).click();
    await waitForAngular(this.page);
    await this.page.waitForSelector('form[ng-submit="withdrawl()"]', { state: 'visible', timeout: 5000 });
  }

  async enterAmount(amount: number): Promise<void> {
    const loc = this.page.locator(WithdrawPageSelectors.amount_input);
    await loc.waitFor({ state: 'visible', timeout: 5000 });
    await loc.fill(String(amount));
  }

  async submit(): Promise<void> {
    const btn = this.page.locator(WithdrawPageSelectors.submit_btn);
    await btn.waitFor({ state: 'visible', timeout: 5000 });
    await btn.click();
    await waitForAngular(this.page);
    await applyCiBuffer(0.25);
  }

  async getMessage(): Promise<string> {
    return (await this.page.locator(WithdrawPageSelectors.message).textContent())?.trim() ?? '';
  }

  async expectSuccess(): Promise<void> {
    const msg = await this.getMessage();
    if (!msg.includes('Transaction successful')) {
      throw new Error(`Expected withdrawal success message, got: ${msg}`);
    }
  }

  /** open → enterAmount → submit (no assertion) */
  async withdrawAmount(amount: number): Promise<void> {
    await this.open();
    await this.enterAmount(amount);
    await this.submit();
  }
}
