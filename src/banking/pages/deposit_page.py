"""Deposit page object for XYZ Banking Project."""
from playwright.sync_api import Page

from src.banking.helpers.browser_helpers import apply_ci_buffer, wait_for_angular
from src.banking.locators.selectors import CustomerDashboard, DepositPageSelectors


class DepositPage:
    def __init__(self, page: Page):
        self.page = page

    def open(self) -> None:
        """Click deposit btn, wait for angular, wait for form."""
        self.page.locator(CustomerDashboard.deposit_btn).click()
        wait_for_angular(self.page)
        self.page.wait_for_selector('form[ng-submit="deposit()"]', state="visible", timeout=5000)

    def enter_amount(self, amount: int) -> None:
        """Wait for amount input to be ready, then fill. Ensures form is stable before input."""
        loc = self.page.locator(DepositPageSelectors.amount_input)
        loc.wait_for(state="visible", timeout=5000)
        loc.fill(str(amount))

    def submit(self) -> None:
        """Click submit, wait for Angular to process, apply CI buffer for balance update."""
        btn = self.page.locator(DepositPageSelectors.submit_btn)
        btn.wait_for(state="visible", timeout=5000)
        btn.click()
        wait_for_angular(self.page)
        apply_ci_buffer(0.25)  # CI/CD: balance update; runners process slower

    def expect_success(self) -> None:
        msg = self.page.locator(DepositPageSelectors.success_message).text_content() or ""
        assert "Deposit Successful" in msg

    def deposit_amount(self, amount: int) -> None:
        """open → enter_amount → submit → expect_success."""
        self.open()
        self.enter_amount(amount)
        self.submit()
        self.expect_success()
