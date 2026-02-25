"""
Customer Login — verifies home page options, customer list, login flow, and logout.
"""
import pytest

from src.banking.data.customers import Customers
from src.banking.locators.selectors import CustomerLoginPage, HomePage


def test_should_show_login_options_and_list_all_customers_in_dropdown(login_page):
    """
    Verifies home page offers customer and manager login, lists known customers,
    and hides the Login button until a customer is selected from the dropdown.
    """
    login_page.go_to_home()
    login_page.page.locator(HomePage.customer_login_btn).wait_for(state="visible", timeout=5000)
    login_page.page.locator(HomePage.manager_login_btn).wait_for(state="visible", timeout=5000)
    heading = login_page.page.locator(HomePage.heading).text_content() or ""
    assert "XYZ Bank" in heading

    login_page.select_customer_login()
    options = login_page.page.locator(f"{CustomerLoginPage.user_select} option").all_text_contents()
    option_texts = [o.strip() for o in options if o.strip()]
    all_names = [c.name for c in Customers.ALL.values()]
    for name in all_names:
        assert name in option_texts

    # Login button should not be visible until a user is selected
    login_page.page.locator(CustomerLoginPage.login_btn).wait_for(state="hidden", timeout=3000)


def test_should_show_dashboard_after_login_and_return_to_login_page_on_logout(
    login_page, dashboard_page,     bank_user
):
    """
    Verifies dashboard loads after login (welcome contains name), and logout
    returns to login page with user select visible.
    """
    login_page.login_as_customer(bank_user.name)
    dashboard_page.expect_loaded()
    welcome = dashboard_page.get_welcome_text()
    assert bank_user.name in welcome

    dashboard_page.click_logout()
    login_page.page.locator(CustomerLoginPage.user_select).wait_for(state="visible", timeout=5000)
    login_page.page.locator(CustomerLoginPage.login_btn).wait_for(state="hidden", timeout=3000)
