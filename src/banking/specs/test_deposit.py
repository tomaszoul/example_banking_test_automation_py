"""
Deposit Flow — verifies deposit button visibility, balance updates, and invalid input handling.
"""
import pytest

from src.banking.helpers.assert_helpers import expect_balance_change
from src.banking.locators.selectors import CustomerDashboard


@pytest.fixture(autouse=True)
def _before_each(login_page, dashboard_page, bank_user):
    login_page.login_as_customer(bank_user.name)
    dashboard_page.expect_loaded()


def test_should_show_deposit_button_and_update_balance_when_depositing_money(
    dashboard_page, deposit_page
):
    """
    Verifies deposit button is visible and depositing money updates balance correctly.
    """
    dashboard_page.page.locator(CustomerDashboard.deposit_btn).wait_for(
        state="visible", timeout=5000
    )
    btn_text = dashboard_page.page.locator(CustomerDashboard.deposit_btn).text_content() or ""
    assert "Deposit" in btn_text

    balance_before = dashboard_page.get_balance()
    deposit_page.deposit_amount(10000)
    balance_after = dashboard_page.get_balance()
    expect_balance_change(balance_before, balance_after, 10000)


def test_should_not_change_balance_when_submitting_empty_or_zero_amounts(
    dashboard_page, deposit_page
):
    """
    Verifies that invalid deposit inputs leave the balance unchanged.
    Covers: empty submit (HTML5 required blocks form), zero amount (form submits but no change),
    and negative amount (number input rejects, balance unchanged).
    """
    balance_before = dashboard_page.get_balance()

    # Empty submit — HTML5 required attribute prevents form submission
    deposit_page.open()
    deposit_page.submit()
    balance_after = dashboard_page.get_balance()
    assert balance_after == balance_before

    # Zero amount — form submits but balance should not change
    deposit_page.enter_amount(0)
    deposit_page.submit()
    balance_after = dashboard_page.get_balance()
    assert balance_after == balance_before

    # Negative amount — HTML number input rejects it, balance unchanged
    deposit_page.enter_amount(-500)
    deposit_page.submit()
    balance_after = dashboard_page.get_balance()
    assert balance_after == balance_before
