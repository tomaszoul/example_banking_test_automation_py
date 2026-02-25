"""
Intentionally failing spec used to validate failure reporting and trace generation.
Do not fix — failures are expected.
"""
import pytest

from src.banking.data.customers import Customers


@pytest.fixture(autouse=True)
def _before_each(login_page, dashboard_page, bank_user):
    login_page.login_as_customer(bank_user.name)
    dashboard_page.expect_loaded()


@pytest.mark.parametrize("bank_user", [Customers.HARRY_POTTER], indirect=True)
def test_this_test_will_fail(dashboard_page, deposit_page):
    """
    Expects balance + 5000 but deposit adds 10000 — assertion fails for report validation.
    """
    balance_before = dashboard_page.get_balance()
    deposit_page.deposit_amount(10000)
    balance_after = dashboard_page.get_balance()
    # wrong - should be +10000 (following assert fails to demonstrate report generation)
    expected = balance_before + 1234567890
    assert balance_after == expected
