/**
 * Browser helpers mirroring src/banking/helpers/browser_helpers.py.
 */
import type { Page } from '@playwright/test';

function isCi(): boolean {
  return process.env.CI === 'true' || process.env.GITHUB_ACTIONS === 'true';
}

export async function applyCiBuffer(seconds: number = 0.25): Promise<void> {
  if (isCi()) {
    await new Promise((r) => setTimeout(r, seconds * 1000));
  }
}

export async function waitForAngular(page: Page): Promise<void> {
  try {
    await page.waitForFunction(
      `
      () => {
        const ng = (window as unknown as { angular?: unknown }).angular;
        if (!ng) return true;
        const el = document.querySelector('[ng-app]') || document.body;
        const ngEl = (ng as (el: Element) => { injector?: () => unknown })(el);
        if (!ngEl || typeof ngEl.injector !== 'function') return true;
        const injector = ngEl.injector();
        if (!injector) return true;
        try {
          const get = (injector as { get: (name: string) => unknown }).get;
          const $browser = get.call(injector, '$browser');
          return new Promise((resolve: (v: boolean) => void) => {
            ($browser as { notifyWhenNoOutstandingRequests: (cb: () => void) => void }).notifyWhenNoOutstandingRequests(() => resolve(true));
            setTimeout(() => resolve(true), 250);
          });
        } catch { return true; }
      }
    `,
      { timeout: 3000 }
    );
  } catch {
    // app ready enough
  }
  await applyCiBuffer(0.25);
}
