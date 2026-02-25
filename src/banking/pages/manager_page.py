"""Manager page object for XYZ Banking Project."""
import re

from playwright.sync_api import Page

from src.banking.helpers.browser_helpers import wait_for_angular
from src.banking.locators.selectors import ManagerPageSelectors


class ManagerPage:
    def __init__(self, page: Page):
        self.page = page

    def go_to_manager(self) -> None:
        """Wait for add_customer_tab visible (implies we're on manager page)."""
        self.page.wait_for_selector(
            ManagerPageSelectors.add_customer_tab, state="visible", timeout=10000
        )

    def open_add_customer_tab(self) -> None:
        self.page.locator(ManagerPageSelectors.add_customer_tab).click()
        wait_for_angular(self.page)

    def open_open_account_tab(self) -> None:
        self.page.locator(ManagerPageSelectors.open_account_tab).click()
        wait_for_angular(self.page)

    def open_customers_tab(self) -> None:
        self.page.locator(ManagerPageSelectors.customers_tab).click()
        wait_for_angular(self.page)

    def add_customer(self, first: str, last: str, post_code: str) -> dict:
        """Fill form, submit, parse alert for customer id. Returns {customer_id: int}."""
        dialog_messages: list[str] = []

        def handle_dialog(dialog):
            dialog_messages.append(dialog.message)
            dialog.accept()

        self.page.once("dialog", handle_dialog)
        self.page.locator(ManagerPageSelectors.first_name_input).fill(first)
        self.page.locator(ManagerPageSelectors.last_name_input).fill(last)
        self.page.locator(ManagerPageSelectors.post_code_input).fill(post_code)
        form = self.page.locator('form[ng-submit="addCustomer()"]').first
        form.evaluate("el => el.requestSubmit()")
        msg = dialog_messages[0] if dialog_messages else ""
        m = re.search(r"customer id\s*:\s*(\d+)", msg, re.I)
        return {"customer_id": int(m.group(1))} if m else {"customer_id": 0}

    def open_account(self, customer_name: str, currency: str) -> dict:
        """Open account for customer, parse alert for account number. Returns {account_number: str}."""
        dialog_messages: list[str] = []

        def handle_dialog(dialog):
            dialog_messages.append(dialog.message)
            dialog.accept()

        self.page.once("dialog", handle_dialog)
        self.page.locator(ManagerPageSelectors.customer_select).select_option(
            label=customer_name
        )
        wait_for_angular(self.page)
        self.page.locator(ManagerPageSelectors.currency_select).select_option(
            label=currency
        )
        wait_for_angular(self.page)
        btn = self.page.locator(ManagerPageSelectors.process_btn)
        try:
            btn.click(timeout=5000)
        except Exception:
            self.page.get_by_role("button", name="Process").click(timeout=5000)
        msg = dialog_messages[0] if dialog_messages else ""
        m = re.search(r"account (?:Number|number)\s*:\s*(\d+)", msg, re.I)
        return {"account_number": m.group(1)} if m else {"account_number": ""}

    def search_customer(self, query: str) -> None:
        self.page.locator(ManagerPageSelectors.search_input).fill(query)
        wait_for_angular(self.page)

    def get_customer_rows(self) -> list[tuple[str, str, str]]:
        """Iterate tbody tr, return list of (firstName, lastName, postCode). Columns may vary."""
        rows = self.page.locator(f"{ManagerPageSelectors.customers_table} tbody tr")
        result = []
        for i in range(rows.count()):
            cells = rows.nth(i).locator("td")
            count = cells.count()
            first = (cells.nth(0).text_content() or "").strip() if count > 0 else ""
            last = (cells.nth(1).text_content() or "").strip() if count > 1 else ""
            post = (cells.nth(2).text_content() or "").strip() if count > 2 else ""
            result.append((first, last, post))
        return result

    def has_customer_in_list(self, first: str, last: str) -> bool:
        """Check if any row contains both first and last name (any column order)."""
        self.page.wait_for_selector(f"{ManagerPageSelectors.customers_table} tbody tr", timeout=5000)
        wait_for_angular(self.page)
        table_text = self.page.locator(ManagerPageSelectors.customers_table).text_content() or ""
        return first in table_text and last in table_text

    def delete_customer(self, first: str, last: str) -> None:
        """Find row with matching name, click delete btn in that row."""
        rows = self.page.locator(f"{ManagerPageSelectors.customers_table} tbody tr")
        for i in range(rows.count()):
            cells = rows.nth(i).locator("td")
            f = (cells.nth(0).text_content() or "").strip()
            l = (cells.nth(1).text_content() or "").strip()
            if f == first and l == last:
                rows.nth(i).locator(ManagerPageSelectors.delete_btn).click()
                wait_for_angular(self.page)
                return
        raise ValueError(f"Customer not found: {first} {last}")
