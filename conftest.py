"""Root conftest: Playwright fixtures, bank_user, config. Screenshot-on-failure for HTML report."""
import base64
import os

import pytest

from src.banking.data.customers import Customer, Customers


def _get_page_from_item(item: pytest.Item):
    """Extract Playwright Page from test fixtures (page, or page objects with .page)."""
    funcargs = getattr(item, "funcargs", {})
    if "page" in funcargs:
        return funcargs["page"]
    for val in funcargs.values():
        if hasattr(val, "page"):
            return val.page
    return None


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    On test failure, capture Playwright screenshot and embed in pytest-html report.
    Mirrors TS playwright.config.ts: screenshot: 'only-on-failure'.
    """
    outcome = yield
    report = outcome.get_result()
    extras = getattr(report, "extras", [])

    if report.when == "call" and report.failed:
        page = _get_page_from_item(item)
        if page:
            try:
                # Base64 for self-contained HTML (pytest-html embeds only base64 in --self-contained-html)
                screenshot_bytes = page.screenshot(type="png")
                b64 = base64.b64encode(screenshot_bytes).decode("ascii")
                pytest_html = item.config.pluginmanager.getplugin("html")
                if pytest_html:
                    extras.append(pytest_html.extras.png(b64, name="Screenshot at failure"))
            except Exception:
                pass
        report.extras = extras


def pytest_metadata(metadata: dict) -> None:
    """
    Sanitize metadata so reports are platform-agnostic for review on any OS (macOS, Linux, etc.).
    Removes Platform and any Python executable path to avoid leaking local paths.
    """
    metadata.pop("Platform", None)
    metadata.pop("Executable", None)
    metadata.pop("sys.executable", None)


def _get_bank_user_params():
    """Return customers to parametrize over: single user (smoke) or all (full run)."""
    if os.environ.get("BANK_FULL_RUN") == "1":
        return list(Customers.ALL.values())
    return [Customers.HARRY_POTTER]


@pytest.fixture(params=_get_bank_user_params())
def bank_user(request: pytest.FixtureRequest) -> Customer:
    """Fixture providing the current customer. Harry Potter by default; all 5 when BANK_FULL_RUN=1."""
    return request.param
