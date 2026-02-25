"""Banking-scoped fixtures: page objects for login, dashboard, deposit, withdraw."""
import pytest

from src.banking.pages.customer_dashboard_page import CustomerDashboardPage
from src.banking.pages.deposit_page import DepositPage
from src.banking.pages.login_page import LoginPage
from src.banking.pages.withdraw_page import WithdrawPage


@pytest.fixture
def login_page(page):
    """Login page object."""
    return LoginPage(page)


@pytest.fixture
def dashboard_page(page):
    """Customer dashboard page object."""
    return CustomerDashboardPage(page)


@pytest.fixture
def deposit_page(page):
    """Deposit page object."""
    return DepositPage(page)


@pytest.fixture
def withdraw_page(page):
    """Withdraw page object."""
    return WithdrawPage(page)
