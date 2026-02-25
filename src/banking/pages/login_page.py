"""Login page object for XYZ Banking Project."""
from playwright.sync_api import Page

from src.banking.helpers.browser_helpers import (
    navigate_to_bank,
    wait_for_angular,
    _micro_delay_for_ci,
)
from src.banking.locators.selectors import (
    CustomerLoginPage,
    HomePage,
)


class LoginPage:
    def __init__(self, page: Page):
        self.page = page

    def go_to_home(self) -> None:
        """Navigate to home + wait for heading."""
        navigate_to_bank(self.page)
        self.page.wait_for_selector(HomePage.heading, state="visible", timeout=10000)

    def select_customer_login(self) -> None:
        """Click customer btn, expect user select visible."""
        self.page.locator(HomePage.customer_login_btn).click()
        wait_for_angular(self.page)
        self.page.wait_for_selector(CustomerLoginPage.user_select, state="visible", timeout=15000)

    def select_manager_login(self) -> None:
        """Click manager btn, wait for angular."""
        self.page.locator(HomePage.manager_login_btn).click()
        wait_for_angular(self.page)

    def select_user(self, name: str) -> None:
        """Select user from dropdown by label, expect login btn visible."""
        self.page.locator(CustomerLoginPage.user_select).select_option(label=name)
        self.page.wait_for_selector(CustomerLoginPage.login_btn, state="visible", timeout=5000)

    def click_login(self) -> None:
        """Click login btn, wait for angular."""
        self.page.locator(CustomerLoginPage.login_btn).click()
        wait_for_angular(self.page)
        _micro_delay_for_ci(0.15)  # CI/CD: login triggers navigation; runners need extra buffer

    def login_as_customer(self, name: str) -> None:
        """Full flow: go_to_home → select_customer_login → select_user → click_login."""
        self.go_to_home()
        self.select_customer_login()
        self.select_user(name)
        self.click_login()
