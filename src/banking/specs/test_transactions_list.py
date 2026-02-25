"""
Transactions List — verifies deposit entry visibility in table, reset clears list, back returns to dashboard.
"""
import re

import pytest

from src.banking.helpers.browser_helpers import wait_for_angular
from src.banking.locators.selectors import CustomerDashboard, TransactionsPage


def _go_to_transactions(page):
    """
    Navigates to the transactions list and ensures the AngularJS date filter
    is wide enough to show all transactions. On fast connections (localhost),
    the datetime-local input binding can nullify the filter dates before
    Angular finishes its digest, hiding rows that actually exist.
    """
    page.locator(CustomerDashboard.transactions_btn).click()
    page.wait_for_url(re.compile(r".*#/listTx.*"), timeout=5000)
    wait_for_angular(page)
    page.wait_for_selector(TransactionsPage.table, state="visible", timeout=5000)

    page.evaluate(
        """
        () => {
            const ng = window.angular;
            if (!ng) return;
            const el = document.querySelector('table.table-bordered') || document.querySelector('tbody');
            if (!el) return;
            let scope = ng.element(el).scope();
            while (scope && !scope.transactions) scope = scope.$parent;
            if (scope?.transactions?.length > 0) {
              scope.startDate = new Date(0);
              scope.end = new Date();
              scope.$apply();
            }
        }
    """
    )
    page.wait_for_selector("tbody tr", timeout=5000)


@pytest.fixture(autouse=True)
def _before_each(login_page, dashboard_page, deposit_page, bank_user):
    login_page.login_as_customer(bank_user.name)
    dashboard_page.expect_loaded()
    deposit_page.deposit_amount(500)


def test_should_show_deposit_entry_on_transactions_page(page, dashboard_page):
    """
    Verifies the pre-deposit amount (500) appears in the transactions table.
    """
    _go_to_transactions(page)
    table_text = page.locator(TransactionsPage.table).text_content() or ""
    assert "500" in table_text


def test_should_clear_transactions_on_reset_and_return_to_dashboard_on_back(page):
    """
    Clears transaction list via Reset, verifies table empties, then Back returns to account dashboard.
    """
    _go_to_transactions(page)

    page.locator(TransactionsPage.reset_btn).click()
    wait_for_angular(page)
    rows = page.locator(TransactionsPage.table_rows)
    assert rows.count() == 0

    page.locator(TransactionsPage.back_btn).click()
    page.wait_for_url(re.compile(r".*#/account.*"), timeout=5000)
    page.locator(CustomerDashboard.deposit_btn).wait_for(state="visible", timeout=5000)
