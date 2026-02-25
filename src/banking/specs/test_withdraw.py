"""
Withdrawal Flow — verifies balance reduction, exact-balance withdrawal, and validation (overdraft, empty, zero, negative).
"""
import pytest

@pytest.fixture(autouse=True)
def _before_each(login_page, dashboard_page, deposit_page, bank_user):
    login_page.login_as_customer(bank_user.name)
    dashboard_page.expect_loaded()
    deposit_page.deposit_amount(5000)


def test_should_reduce_balance_on_withdrawal_and_zero_out_on_exact_balance_withdrawal(
    dashboard_page, withdraw_page
):
    """
    Verifies balance decreases by withdrawal amount and that withdrawing the exact
    remaining balance succeeds, leaving balance at zero.
    """
    balance_before = dashboard_page.get_balance()
    withdraw_page.withdraw_amount(1000)
    withdraw_page.expect_success()
    balance_after_first = dashboard_page.get_balance()
    assert balance_after_first == balance_before - 1000

    # Withdraw exact remaining balance — should succeed and hit zero
    withdraw_page.withdraw_amount(balance_after_first)
    withdraw_page.expect_success()
    assert dashboard_page.get_balance() == 0


def test_should_reject_overdraft_empty_zero_and_negative_amounts(dashboard_page, withdraw_page):
    """
    Verifies withdrawal validation: overdraft rejected with "Transaction Failed",
    empty/zero/negative amounts leave balance unchanged (HTML5 required blocks empty).
    """
    balance_before = dashboard_page.get_balance()

    # Overdraft — one dollar more than balance
    withdraw_page.open()
    withdraw_page.enter_amount(balance_before + 1)
    withdraw_page.submit()
    msg = withdraw_page.get_message()
    assert "Transaction Failed" in msg
    balance_after = dashboard_page.get_balance()
    assert balance_after == balance_before

    # Empty submit — HTML5 required attribute blocks form submission
    withdraw_page.open()
    withdraw_page.submit()
    balance_after = dashboard_page.get_balance()
    assert balance_after == balance_before

    # Zero amount
    withdraw_page.open()
    withdraw_page.enter_amount(0)
    withdraw_page.submit()
    balance_after = dashboard_page.get_balance()
    assert balance_after == balance_before

    # Negative amount
    withdraw_page.open()
    withdraw_page.enter_amount(-100)
    withdraw_page.submit()
    balance_after = dashboard_page.get_balance()
    assert balance_after == balance_before
