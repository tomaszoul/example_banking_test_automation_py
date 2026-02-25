import os
import time

from playwright.sync_api import Page

BANK_BASE_URL = os.environ.get(
    "BANK_BASE_URL",
    "https://www.globalsqa.com/angularJs-protractor/BankingProject/#/login",
)


def _is_ci() -> bool:
    """True when running in CI/CD (GitHub Actions, GitLab CI, etc.)."""
    return os.environ.get("CI") == "true" or os.environ.get("GITHUB_ACTIONS") == "true"


def _micro_delay_for_ci(seconds: float = 0.1) -> None:
    """
    Small delay to reduce flakiness in CI/CD.
    CI runners typically have slower I/O and CPU than local dev machines;
    a brief buffer after navigation or DOM updates helps assertions pass.
    Only runs when CI=true or GITHUB_ACTIONS=true; skipped locally.
    """
    if _is_ci():
        time.sleep(seconds)


def navigate_to_bank(page: Page) -> None:
    """Navigate to the banking app base URL and wait for Angular to settle."""
    page.goto(BANK_BASE_URL, wait_until="domcontentloaded", timeout=60000)
    wait_for_angular(page)
    _micro_delay_for_ci(0.1)  # CI/CD: runners are slower; buffer before first interaction


def wait_for_angular(page: Page) -> None:
    """Wait for AngularJS digest cycle to settle.

    Uses $browser.notifyWhenNoOutstandingRequests when available.
    """
    try:
        page.wait_for_function(
            """
            () => {
                const ng = window.angular;
                if (!ng) return true;
                const el = document.querySelector('[ng-app]') || document.body;
                const ngEl = ng.element(el);
                if (!ngEl || typeof ngEl.injector !== 'function') return true;
                const injector = ngEl.injector();
                if (!injector) return true;
                try {
                    const $browser = injector.get('$browser');
                    return new Promise(resolve => {
                        $browser.notifyWhenNoOutstandingRequests(() => resolve(true));
                        setTimeout(() => resolve(true), 250);
                    });
                } catch { return true; }
            }
        """,
            timeout=3000,
        )
    except Exception:
        pass  # app ready enough
    _micro_delay_for_ci(0.05)  # CI/CD: slight buffer after Angular digest; runners are slower
