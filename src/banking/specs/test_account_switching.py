"""
Account Dashboard & Switching — welcome, default account, dropdown, currency switching, deposit isolation.
"""
import time

import pytest

from src.banking.data.customers import CURRENCIES, all_account_numbers

_SETUP_RETRIES = 3
_SETUP_RETRY_DELAY = 1.0


@pytest.fixture(autouse=True)
def _before_each(login_page, dashboard_page, bank_user):
    """Robust setup: retry login + dashboard load to handle slow network / Angular flakiness."""
    last_error = None
    for attempt in range(_SETUP_RETRIES):
        try:
            login_page.login_as_customer(bank_user.name)
            dashboard_page.expect_loaded()
            return
        except Exception as e:
            last_error = e
            if attempt < _SETUP_RETRIES - 1:
                time.sleep(_SETUP_RETRY_DELAY)
    raise last_error


def test_should_show_correct_welcome_name_default_account_and_dropdown_options(
    dashboard_page, bank_user
):
    """
    Verifies welcome shows user name, default account is Dollar, and dropdown lists all account numbers.
    """
    welcome = dashboard_page.get_welcome_text()
    assert bank_user.name in welcome

    selected = dashboard_page.get_selected_account()
    assert selected == bank_user.accounts["Dollar"]

    account_number_text = dashboard_page.get_account_number()
    assert "Dollar" in account_number_text or bank_user.accounts["Dollar"] in account_number_text

    currency = dashboard_page.get_currency()
    assert currency == "Dollar"

    options = dashboard_page.get_account_options()
    expected = all_account_numbers(bank_user)
    for opt in expected:
        assert opt in options or any(opt in o for o in options)


def test_should_show_correct_account_info_when_switching_currencies(
    dashboard_page, bank_user
):
    """
    Verifies account number, currency label, and balance update correctly when switching accounts.
    """
    for currency in CURRENCIES:
        acc = bank_user.accounts[currency]
        dashboard_page.select_account(acc)
        account_num = dashboard_page.get_account_number()
        curr = dashboard_page.get_currency()
        balance = dashboard_page.get_balance()
        assert currency in account_num or acc in account_num
        assert curr == currency
        assert balance >= 0


def test_should_isolate_deposits_between_accounts(dashboard_page, bank_user):
    """
    Deposits on Dollar account; verifies Pound and Rupee stay at 0. Switches back to Dollar
    to confirm the deposit is persisted and not lost during account switching.
    """
    from src.banking.pages.deposit_page import DepositPage

    deposit_page = DepositPage(dashboard_page.page)
    dashboard_page.select_account(bank_user.accounts["Dollar"])
    deposit_page.deposit_amount(2500)
    balance_dollar = dashboard_page.get_balance()
    assert balance_dollar >= 2500

    dashboard_page.select_account(bank_user.accounts["Pound"])
    balance_pound = dashboard_page.get_balance()
    assert balance_pound == 0

    dashboard_page.select_account(bank_user.accounts["Rupee"])
    balance_rupee = dashboard_page.get_balance()
    assert balance_rupee == 0

    # Switch back — balance preserved
    dashboard_page.select_account(bank_user.accounts["Dollar"])
    balance_dollar_after = dashboard_page.get_balance()
    assert balance_dollar_after == balance_dollar


def test_should_accumulate_deposits_correctly_across_multiple_accounts(
    dashboard_page, bank_user
):
    """
    Records baseline balances for all currencies, deposits per-currency amounts,
    then verifies each account reflects its own deposit. Also checks multiple
    sequential deposits on one account accumulate correctly.
    """
    from src.banking.pages.deposit_page import DepositPage

    deposit_page = DepositPage(dashboard_page.page)
    balances_before = {}
    for c in CURRENCIES:
        dashboard_page.select_account(bank_user.accounts[c])
        balances_before[c] = dashboard_page.get_balance()

    dashboard_page.select_account(bank_user.accounts["Dollar"])
    deposit_page.deposit_amount(1000)
    assert dashboard_page.get_balance() == balances_before["Dollar"] + 1000

    dashboard_page.select_account(bank_user.accounts["Pound"])
    deposit_page.deposit_amount(2000)
    assert dashboard_page.get_balance() == balances_before["Pound"] + 2000

    dashboard_page.select_account(bank_user.accounts["Rupee"])
    deposit_page.deposit_amount(3000)
    assert dashboard_page.get_balance() == balances_before["Rupee"] + 3000

    # Multiple deposits on one account
    deposit_page.deposit_amount(500)
    deposit_page.deposit_amount(500)
    expected_rupee = balances_before["Rupee"] + 3000 + 500 + 500
    assert dashboard_page.get_balance() == expected_rupee


def test_should_keep_ui_in_sync_during_rapid_account_switching(dashboard_page, bank_user):
    """
    Rapidly cycles through account dropdown 3 times. Ensures dropdown state,
    currency label, and account number stay in sync with selected account.
    """
    for _ in range(3):
        for currency in CURRENCIES:
            dashboard_page.select_account(bank_user.accounts[currency])
            curr = dashboard_page.get_currency()
            account_num = dashboard_page.get_account_number()
            assert curr == currency
            assert currency in account_num or bank_user.accounts[currency] in account_num
