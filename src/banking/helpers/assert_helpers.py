"""Assertion helpers for banking E2E tests."""


def expect_balance_change(balance_before: int, balance_after: int, delta: int) -> None:
    """Assert balance changed by the expected delta.

    Args:
        balance_before: Balance before the transaction.
        balance_after: Balance after the transaction.
        delta: Expected change (positive for deposit, negative for withdrawal).
    """
    assert balance_after == balance_before + delta
