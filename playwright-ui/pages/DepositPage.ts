/**
 * Deposit page object for XYZ Banking Project.
 * Mirrors src/banking/pages/deposit_page.py.
 */
import type { Page } from '@playwright/test';
import { applyCiBuffer, waitForAngular } from './helpers';
import { CustomerDashboard, DepositPageSelectors } from '../locators/selectors';

export class DepositPage {
  constructor(private readonly page: Page) {}

  async open(): Promise<void> {
    await this.page.locator(CustomerDashboard.deposit_btn).click();
    await waitForAngular(this.page);
    await this.page.waitForSelector('form[ng-submit="deposit()"]', { state: 'visible', timeout: 5000 });
  }

  async enterAmount(amount: number): Promise<void> {
    const loc = this.page.locator(DepositPageSelectors.amount_input);
    await loc.waitFor({ state: 'visible', timeout: 5000 });
    await loc.fill(String(amount));
  }

  async submit(): Promise<void> {
    const btn = this.page.locator(DepositPageSelectors.submit_btn);
    await btn.waitFor({ state: 'visible', timeout: 5000 });
    await btn.click();
    await waitForAngular(this.page);
    await applyCiBuffer(0.25);
  }

  async expectSuccess(): Promise<void> {
    const msg = (await this.page.locator(DepositPageSelectors.success_message).textContent()) ?? '';
    if (!msg.includes('Deposit Successful')) {
      throw new Error(`Expected deposit success message, got: ${msg}`);
    }
  }

  /** open → enterAmount → submit → expectSuccess */
  async depositAmount(amount: number): Promise<void> {
    await this.open();
    await this.enterAmount(amount);
    await this.submit();
    await this.expectSuccess();
  }
}
