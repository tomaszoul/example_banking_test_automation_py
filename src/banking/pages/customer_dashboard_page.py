"""Customer dashboard page object for XYZ Banking Project."""
import re

from playwright.sync_api import Page

from src.banking.helpers.browser_helpers import wait_for_angular
from src.banking.locators.selectors import CustomerDashboard


class CustomerDashboardPage:
    def __init__(self, page: Page):
        self.page = page

    def get_welcome_text(self) -> str:
        return (self.page.locator(CustomerDashboard.welcome_name).text_content() or "").strip()

    def get_account_number(self) -> str:
        return (self.page.locator(CustomerDashboard.account_number).text_content() or "").strip()

    def get_balance(self) -> int:
        text = self.page.locator(CustomerDashboard.balance).text_content() or "0"
        return int(re.sub(r"[^0-9.-]", "", text) or "0")

    def get_currency(self) -> str:
        return (self.page.locator(CustomerDashboard.currency).text_content() or "").strip()

    def get_account_options(self) -> list[str]:
        raw = self.page.locator(f"{CustomerDashboard.account_select} option").all_text_contents()
        return [s.strip() for s in raw if s and s.strip()]

    def get_selected_account(self) -> str:
        """Get selected account, stripping AngularJS prefix like 'number:1004' or '1004 : 1001'."""
        raw = self.page.locator(CustomerDashboard.account_select).input_value()
        cleaned = re.sub(r"^[a-z]+:", "", raw, flags=re.I).strip()
        if " : " in cleaned:
            return cleaned.split(" : ")[0].strip()
        return cleaned or raw

    def select_account(self, account_number: str) -> None:
        loc = self.page.locator(CustomerDashboard.account_select)
        try:
            loc.select_option(value=account_number)
        except Exception:
            loc.select_option(label=account_number)
        wait_for_angular(self.page)

    def click_logout(self) -> None:
        self.page.locator(CustomerDashboard.logout_btn).click()
        wait_for_angular(self.page)

    def expect_loaded(self) -> None:
        self.page.locator(CustomerDashboard.welcome_name).wait_for(state="visible", timeout=15000)
