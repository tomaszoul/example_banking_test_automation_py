"""Withdraw page object for XYZ Banking Project."""
from playwright.sync_api import Page

from src.banking.helpers.browser_helpers import apply_ci_buffer, wait_for_angular
from src.banking.locators.selectors import CustomerDashboard, WithdrawPageSelectors


class WithdrawPage:
    def __init__(self, page: Page):
        self.page = page

    def open(self) -> None:
        """Click withdraw btn, wait for form."""
        self.page.locator(CustomerDashboard.withdraw_btn).click()
        wait_for_angular(self.page)
        self.page.wait_for_selector('form[ng-submit="withdrawl()"]', state="visible", timeout=5000)

    def enter_amount(self, amount: int) -> None:
        """Wait for amount input to be ready, then fill. Ensures form is stable before input."""
        loc = self.page.locator(WithdrawPageSelectors.amount_input)
        loc.wait_for(state="visible", timeout=5000)
        loc.fill(str(amount))

    def submit(self) -> None:
        """Click submit, wait for Angular to process, apply CI buffer for balance update."""
        btn = self.page.locator(WithdrawPageSelectors.submit_btn)
        btn.wait_for(state="visible", timeout=5000)
        btn.click()
        wait_for_angular(self.page)
        apply_ci_buffer(0.25)  # CI/CD: balance update; runners process slower

    def get_message(self) -> str:
        return (self.page.locator(WithdrawPageSelectors.message).text_content() or "").strip()

    def expect_success(self) -> None:
        msg = self.get_message()
        assert "Transaction successful" in msg

    def withdraw_amount(self, amount: int) -> None:
        """open → enter_amount → submit (no assertion)."""
        self.open()
        self.enter_amount(amount)
        self.submit()
