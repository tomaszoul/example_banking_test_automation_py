"""Customer data and account fixtures for XYZ Banking Project tests."""
from dataclasses import dataclass

Currency = str  # "Dollar" | "Pound" | "Rupee"
CURRENCIES = ["Dollar", "Pound", "Rupee"]


@dataclass
class Customer:
    """A bank customer with name and accounts per currency."""

    name: str
    accounts: dict[str, str]


def all_account_numbers(customer: Customer) -> list[str]:
    """Return account numbers for all supported currencies.

    Args:
        customer: Customer whose accounts to enumerate.

    Returns:
        List of account number strings for Dollar, Pound, Rupee.
    """
    return [customer.accounts[c] for c in CURRENCIES]


class Customers:
    """Static customer fixtures for the XYZ Banking demo app."""

    HERMOINE_GRANGER = Customer(
        "Hermoine Granger", {"Dollar": "1001", "Pound": "1002", "Rupee": "1003"}
    )
    HARRY_POTTER = Customer(
        "Harry Potter", {"Dollar": "1004", "Pound": "1005", "Rupee": "1006"}
    )
    RON_WEASLY = Customer(
        "Ron Weasly", {"Dollar": "1007", "Pound": "1008", "Rupee": "1009"}
    )
    ALBUS_DUMBLEDORE = Customer(
        "Albus Dumbledore", {"Dollar": "1010", "Pound": "1011", "Rupee": "1012"}
    )
    NEVILLE_LONGBOTTOM = Customer(
        "Neville Longbottom", {"Dollar": "1013", "Pound": "1014", "Rupee": "1015"}
    )
    ALL = {
        "hermoine-granger": HERMOINE_GRANGER,
        "harry-potter": HARRY_POTTER,
        "ron-weasly": RON_WEASLY,
        "albus-dumbledore": ALBUS_DUMBLEDORE,
        "neville-longbottom": NEVILLE_LONGBOTTOM,
    }
