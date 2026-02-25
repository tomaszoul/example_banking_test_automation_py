"""
Manager CRUD — add customer, open account, list/search customers, delete customer.
"""
import time

import pytest

from src.banking.pages.login_page import LoginPage
from src.banking.pages.manager_page import ManagerPage


@pytest.fixture
def login_page(page):
    return LoginPage(page)


@pytest.fixture
def manager_page(page):
    return ManagerPage(page)


@pytest.fixture(autouse=True)
def _before_each(login_page, manager_page):
    login_page.go_to_home()
    login_page.select_manager_login()
    manager_page.go_to_manager()


def test_should_show_success_alert_with_customer_id_when_adding_customer(manager_page):
    """
    Verifies adding a customer returns a success alert with positive customer_id.
    """
    manager_page.open_add_customer_tab()
    result = manager_page.add_customer("Test", "CRUDUser", "E99999")
    assert result["customer_id"] > 0


def test_should_show_success_alert_with_account_number_when_opening_account(manager_page):
    """
    Opens a Dollar account for Harry Potter and verifies a non-empty account number is returned.
    """
    manager_page.open_open_account_tab()
    result = manager_page.open_account("Harry Potter", "Dollar")
    assert result["account_number"]


def test_should_list_customers_and_filter_them_by_search(manager_page):
    """
    Verifies customers tab lists all customers and search filters rows correctly.
    """
    manager_page.open_customers_tab()
    assert manager_page.has_customer_in_list("Harry", "Potter")

    manager_page.search_customer("Harry")
    rows = manager_page.get_customer_rows()
    for first, last, _ in rows:
        assert "Harry" in first or "Harry" in last


def test_should_add_customer_open_accounts_search_and_delete_customer(manager_page):
    """
    Full CRUD lifecycle: add customer with unique postcode, open Dollar/Pound/Rupee accounts,
    search to locate them, delete customer, then verify they no longer appear in search.
    """
    unique_postcode = f"E{int(time.time()) % 10**6:06d}"
    manager_page.open_add_customer_tab()
    manager_page.add_customer("Delete", "MeUser", unique_postcode)

    manager_page.open_open_account_tab()
    manager_page.open_account("Delete MeUser", "Dollar")
    manager_page.open_open_account_tab()
    manager_page.open_account("Delete MeUser", "Pound")
    manager_page.open_open_account_tab()
    manager_page.open_account("Delete MeUser", "Rupee")

    manager_page.open_customers_tab()
    # Search to locate the new customer
    manager_page.search_customer("Delete")
    rows = manager_page.get_customer_rows()
    assert any("Delete" in f and "MeUser" in l for f, l, _ in rows)

    manager_page.delete_customer("Delete", "MeUser")
    manager_page.search_customer("Delete")
    rows = manager_page.get_customer_rows()
    assert not any("Delete" in f and "MeUser" in l for f, l, _ in rows)
