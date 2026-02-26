/**
 * Login page object for XYZ Banking Project.
 * Mirrors src/banking/pages/login_page.py.
 */
import type { Page } from '@playwright/test';
import { applyCiBuffer, waitForAngular } from './helpers';
import { CustomerLoginPage, HomePage } from '../locators/selectors';

/** Timeout for user select after "Customer Login" click; Angular may be slow to render. */
const USER_SELECT_TIMEOUT = 25_000;

export class LoginPage {
  constructor(private readonly page: Page) {}

  async goToHome(): Promise<void> {
    await this.page.goto('', { waitUntil: 'domcontentloaded', timeout: 30000 });
    await this.page.waitForSelector(HomePage.customer_login_btn, { state: 'visible', timeout: 15000 });
  }

  async selectCustomerLogin(): Promise<void> {
    await this.page.locator(HomePage.customer_login_btn).click();
    await waitForAngular(this.page);
    await this.page.waitForSelector(CustomerLoginPage.user_select, { state: 'visible', timeout: USER_SELECT_TIMEOUT });
  }

  async selectManagerLogin(): Promise<void> {
    await this.page.locator(HomePage.manager_login_btn).click();
    await waitForAngular(this.page);
  }

  async selectUser(name: string): Promise<void> {
    await this.page.locator(CustomerLoginPage.user_select).selectOption({ label: name });
    await this.page.waitForSelector(CustomerLoginPage.login_btn, { state: 'visible', timeout: 5000 });
  }

  async clickLogin(): Promise<void> {
    await this.page.locator(CustomerLoginPage.login_btn).click();
    await waitForAngular(this.page);
    await applyCiBuffer(0.25);
  }

  /** Full flow: goToHome → selectCustomerLogin → selectUser → clickLogin. Retries once on timeout. */
  async loginAsCustomer(name: string): Promise<void> {
    const maxAttempts = 2;
    let lastError: Error | undefined;
    for (let attempt = 1; attempt <= maxAttempts; attempt++) {
      try {
        await this.goToHome();
        await this.selectCustomerLogin();
        await this.selectUser(name);
        await this.clickLogin();
        return;
      } catch (e) {
        lastError = e instanceof Error ? e : new Error(String(e));
        if (attempt < maxAttempts) {
          await new Promise((r) => setTimeout(r, 2000));
        }
      }
    }
    throw lastError;
  }
}
