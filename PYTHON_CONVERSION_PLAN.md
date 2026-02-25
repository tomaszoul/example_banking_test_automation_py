# Python Conversion Plan — Copy-Paste for New Repo

**Use this plan when you open the new Python repository workspace.** Paste it (or link this file) and ask the AI to execute it step by step.

---

## Context

You are creating a **Python Playwright E2E test suite** that replicates an existing TypeScript suite for the XYZ Banking Project demo app (AngularJS). The app under test is the same: `https://www.globalsqa.com/angularJs-protractor/BankingProject/#/login` or a local copy in `banking-app/`.

**Source reference:** If possible, have the TypeScript repo open in a sibling folder or multi-root workspace at `example_banking_test_automation` for reference. Otherwise, follow this plan exactly—all selectors and logic are embedded below.

---

## Prerequisites in New Repo

1. **Copy `banking-app/`** from the TypeScript repo into the Python repo root (or add as submodule).
2. **Python 3.10+**
3. **Dependencies:** `playwright`, `pytest`, `pytest-playwright`

---

## Target Directory Layout

```
banking-e2e-tests-python/
├── banking-app/                 # Copied from TS repo
├── requirements.txt
├── pyproject.toml
├── conftest.py                  # Root: Playwright fixtures, bank_user, config
├── run_tests.py                # CLI: --local, --full, report pruning
├── download_app.py             # Optional: re-download app from live site
├── src/
│   └── banking/
│       ├── conftest.py         # Optional: banking-scoped fixtures
│       ├── data/
│       │   └── customers.py
│       ├── locators/
│       │   └── selectors.py
│       ├── pages/
│       │   ├── login_page.py
│       │   ├── customer_dashboard_page.py
│       │   ├── deposit_page.py
│       │   ├── withdraw_page.py
│       │   └── manager_page.py
│       ├── helpers/
│       │   ├── browser_helpers.py
│       │   └── assert_helpers.py
│       └── specs/
│           ├── test_customer_login.py
│           ├── test_deposit.py
│           ├── test_withdraw.py
│           ├── test_transactions_list.py
│           ├── test_account_switching.py
│           ├── test_manager_crud.py
│           └── test_failing_deposit.py
└── utils/
    └── reporting/              # Optional: can add later
```

---

## Phase 1: Project Setup

### 1.1 `requirements.txt`

```
playwright>=1.56.0
pytest>=8.0
pytest-playwright>=0.5.0
```

### 1.2 `pyproject.toml`

```toml
[tool.pytest.ini_options]
testpaths = ["src"]
asyncio_mode = "auto"
addopts = "-v --tb=short"
markers = [
    "smoke: smoke tests (default, single user)",
    "full: full run (parametrized over all customers)",
    "manager: manager CRUD tests",
]
```

### 1.3 `conftest.py` (root)

- Use `pytest-playwright` `page` fixture.
- Add `bank_user` fixture that returns a `Customer` (default: Harry Potter). Use `pytest.mark.parametrize` when `BANK_FULL_RUN=1` to run with all 5 customers.
- Set `base_url` from `BANK_BASE_URL` env (default: `https://www.globalsqa.com/angularJs-protractor/BankingProject/#/login`).
- When `BANK_LOCAL=1`, configure `pytest-playwright` to start `serve banking-app -l 8081` (or use `run_tests.py` to wrap and pass env).
- `bank_user` fixture: return `Customers.HARRY_POTTER` by default; when `BANK_FULL_RUN=1`, parametrize over `list(Customers.ALL.values())`.

---

## Phase 2: Data & Selectors

### 2.1 `src/banking/data/customers.py`

```python
from dataclasses import dataclass
from typing import TypedDict

Currency = str  # "Dollar" | "Pound" | "Rupee"
CURRENCIES = ["Dollar", "Pound", "Rupee"]

@dataclass
class Customer:
    name: str
    accounts: dict[str, str]

def all_account_numbers(customer: Customer) -> list[str]:
    return [customer.accounts[c] for c in CURRENCIES]

class Customers:
    HERMOINE_GRANGER = Customer("Hermoine Granger", {"Dollar": "1001", "Pound": "1002", "Rupee": "1003"})
    HARRY_POTTER = Customer("Harry Potter", {"Dollar": "1004", "Pound": "1005", "Rupee": "1006"})
    RON_WEASLY = Customer("Ron Weasly", {"Dollar": "1007", "Pound": "1008", "Rupee": "1009"})
    ALBUS_DUMBLEDORE = Customer("Albus Dumbledore", {"Dollar": "1010", "Pound": "1011", "Rupee": "1012"})
    NEVILLE_LONGBOTTOM = Customer("Neville Longbottom", {"Dollar": "1013", "Pound": "1014", "Rupee": "1015"})
    ALL = {
        "hermoine-granger": HERMOINE_GRANGER,
        "harry-potter": HARRY_POTTER,
        "ron-weasly": RON_WEASLY,
        "albus-dumbledore": ALBUS_DUMBLEDORE,
        "neville-longbottom": NEVILLE_LONGBOTTOM,
    }
```

### 2.2 `src/banking/locators/selectors.py`

Exact selectors (copy-paste):

```python
"""Central selector registry for XYZ Banking Project demo app."""

class HomePage:
    heading = 'strong.mainHeading'
    customer_login_btn = 'button[ng-click="customer()"]'
    manager_login_btn = 'button[ng-click="manager()"]'

class CustomerLoginPage:
    user_select = '#userSelect'
    login_btn = 'button[type="submit"]'

class CustomerDashboard:
    welcome_name = 'span.fontBig'
    account_number = 'div.center[ng-hide="noAccount"] strong:nth-of-type(1)'
    balance = 'div.center[ng-hide="noAccount"] strong:nth-of-type(2)'
    currency = 'div.center[ng-hide="noAccount"] strong:nth-of-type(3)'
    account_select = '#accountSelect'
    transactions_btn = 'button[ng-click="transactions()"]'
    deposit_btn = 'button[ng-click="deposit()"]'
    withdraw_btn = 'button[ng-click="withdrawl()"]'
    logout_btn = 'button[ng-click="byebye()"]'

class DepositPageSelectors:
    amount_input = 'input[ng-model="amount"]'
    submit_btn = 'form button[type="submit"]'
    success_message = 'span[ng-show="message"]'

class WithdrawPageSelectors:
    amount_input = 'input[ng-model="amount"]'
    submit_btn = 'form button[type="submit"]'
    message = 'span[ng-show="message"]'

class TransactionsPage:
    table = 'table.table-bordered'
    start_date_input = '#start'
    end_date_input = '#end'
    table_rows = 'tbody tr'
    reset_btn = 'button[ng-click="reset()"]'
    back_btn = 'button[ng-click="back()"]'

class ManagerPageSelectors:
    add_customer_tab = 'button[ng-click="addCust()"]'
    open_account_tab = 'button[ng-click="openAccount()"]'
    customers_tab = 'button[ng-click="showCust()"]'
    first_name_input = 'input[ng-model="fName"]'
    last_name_input = 'input[ng-model="lName"]'
    post_code_input = 'input[ng-model="postCd"]'
    add_customer_btn = 'button[ng-click="addCustomer()"]'
    customer_select = '#userSelect'
    currency_select = '#currency'
    process_btn = 'button[ng-click="process()"]'
    search_input = 'input[ng-model="searchCustomer"]'
    customers_table = 'table.table-bordered'
    delete_btn = 'button[ng-click="deleteCust(cust)"]'
```

---

## Phase 3: Helpers

### 3.1 `src/banking/helpers/browser_helpers.py`

**Critical:** AngularJS app needs `wait_for_angular` to settle digest cycles.

```python
import os
from playwright.sync_api import Page

BANK_BASE_URL = os.environ.get(
    "BANK_BASE_URL",
    "https://www.globalsqa.com/angularJs-protractor/BankingProject/#/login"
)

def navigate_to_bank(page: Page) -> None:
    page.goto(BANK_BASE_URL, wait_until="domcontentloaded")
    wait_for_angular(page)

def wait_for_angular(page: Page) -> None:
    """Waits for AngularJS to settle. Uses $browser.notifyWhenNoOutstandingRequests."""
    try:
        page.wait_for_function("""
            () => {
                const ng = window.angular;
                if (!ng) return true;
                const el = document.querySelector('[ng-app]') || document.body;
                const ngEl = ng.element(el);
                if (!ngEl || typeof ngEl.injector !== 'function') return true;
                const injector = ngEl.injector();
                if (!injector) return true;
                try {
                    const $browser = injector.get('$browser');
                    return new Promise(resolve => {
                        $browser.notifyWhenNoOutstandingRequests(() => resolve(true));
                        setTimeout(() => resolve(true), 250);
                    });
                } catch { return true; }
            }
        """, timeout=3000)
    except Exception:
        pass  # app ready enough
```

### 3.2 `src/banking/helpers/assert_helpers.py`

```python
def expect_visible(locator, timeout: int = 5000) -> None:
    locator.wait_for(state="visible", timeout=timeout)

def expect_balance_change(balance_before: int, balance_after: int, delta: int) -> None:
    assert balance_after == balance_before + delta
```

---

## Phase 4: Page Objects

All page classes take `page: Page` in `__init__`. Use Playwright **sync API** (not async) for simplicity with pytest.

### 4.1 `LoginPage`

- `go_to_home()`: navigate + wait for `HomePage.heading`
- `select_customer_login()`: click customer btn, expect `CustomerLoginPage.user_select` visible
- `select_manager_login()`: click manager btn, `wait_for_angular`
- `select_user(name)`: `select_option(label=name)` on user select, expect login btn visible
- `click_login()`: click login btn, `wait_for_angular`
- `login_as_customer(name)`: full flow — go_to_home → select_customer_login → select_user → click_login

### 4.2 `CustomerDashboardPage`

- `get_welcome_text()`, `get_account_number()`, `get_balance()`, `get_currency()` — read from locators
- `get_balance()`: parse text, strip non-digits: `int(re.sub(r'[^0-9.-]', '', text) or '0')`
- `get_account_options()`: `locator.all_text_contents()`, trim, filter blank
- `get_selected_account()`: `locator.input_value()`, strip AngularJS prefix `re.sub(r'^[a-z]+:', '', raw, flags=re.I)`
- `select_account(account_number)`: `select_option(account_number)`, `wait_for_angular`
- `click_logout()`: click logout, `wait_for_angular`
- `expect_loaded()`: expect `CustomerDashboard.welcome_name` visible

### 4.3 `DepositPage`

- `open()`: click `CustomerDashboard.deposit_btn`, wait_for_angular, wait for `form[ng-submit="deposit()"]`
- `enter_amount(amount)`: fill amount input
- `submit()`: click submit btn, wait_for_angular
- `expect_success()`: expect success message contains "Deposit Successful"
- `deposit_amount(amount)`: open → enter_amount → submit → expect_success

### 4.4 `WithdrawPage`

- `open()`, `enter_amount()`, `submit()` — same pattern as Deposit
- `get_message()`: text_content of message span
- `expect_success()`: expect message contains "Transaction successful"
- `withdraw_amount(amount)`: open → enter_amount → submit (no assertion)

### 4.5 `ManagerPage`

- Handle **JavaScript dialogs**: use `page.on("dialog", lambda d: (capture_message(d.message()), d.accept()))` before form submit. Python: `with page.expect_dialog() as dialog_info:` then `dialog = dialog_info.value; msg = dialog.message; dialog.accept()`.
- `go_to_manager()`: wait for add_customer_tab visible
- `open_add_customer_tab()`, `open_open_account_tab()`, `open_customers_tab()`: click tab, wait_for_angular
- `add_customer(first, last, post_code)`: set dialog listener, fill form, submit via `form.evaluate("el => el.requestSubmit()")`, parse alert for `customer id :(\d+)`, return `{customer_id: int}`
- `open_account(customer_name, currency)`: same pattern, parse `account Number :(\d+)`, return `{account_number: str}`
- `search_customer(query)`: fill search, wait_for_angular
- `get_customer_rows()`: iterate `tbody tr`, read cells 0,1,2 → firstName, lastName, postCode
- `delete_customer(first, last)`: find row with matching name, click delete btn in that row

**Note:** In TS, `openAccount` is called with "Delete MeUser" (first+last concatenated with space) because the dropdown shows it that way. Match that behavior.

---

## Phase 5: Test Specs

Use `@pytest.fixture(autouse=True)` or explicit fixture for `beforeEach`-style setup. All specs use `page` and `bank_user` fixtures.

### 5.1 `test_customer_login.py`

1. **test_should_show_login_options_and_list_all_customers_in_dropdown**: go_to_home → expect customer + manager btns visible, heading contains "XYZ Bank" → select_customer_login → assert dropdown options contain all 5 names → expect login_btn hidden
2. **test_should_show_dashboard_after_login_and_return_to_login_page_on_logout**: login_as_customer(bank_user.name) → expect_loaded → welcome contains bank_user.name → click_logout → expect user_select visible, login_btn hidden

### 5.2 `test_deposit.py`

`beforeEach`: login, expect_loaded

1. **test_should_show_deposit_button_and_update_balance_when_depositing_money**: expect deposit btn visible, contains "Deposit" → get_balance → deposit_amount(10000) → expect_balance_change(before, after, 10000)
2. **test_should_not_change_balance_when_submitting_empty_or_zero_amounts**: before = get_balance → open, submit (empty) → balance unchanged → enter 0, submit → unchanged → fill -500, submit → unchanged

### 5.3 `test_withdraw.py`

`beforeEach`: login, expect_loaded, deposit_amount(5000)

1. **test_should_reduce_balance_on_withdrawal_and_zero_out_on_exact_balance_withdrawal**: withdraw 1000, expect_success, assert balance reduced → withdraw remaining, expect_success, assert balance 0
2. **test_should_reject_overdraft_empty_zero_and_negative_amounts**: overdraft (balance+1) → message contains "Transaction Failed", balance unchanged → open, fill "", submit → unchanged → enter 0, submit → unchanged → fill -100, submit → unchanged

### 5.4 `test_transactions_list.py`

`beforeEach`: login, expect_loaded, deposit_amount(500)

**Helper** `go_to_transactions(page)`: click transactions btn, wait_for_url listTx, wait_for_angular, expect table visible. Then run JS to fix date filter:
```python
page.evaluate("""
  () => {
    const ng = window.angular;
    if (!ng) return;
    const el = document.querySelector('table.table-bordered') || document.querySelector('tbody');
    if (!el) return;
    let scope = ng.element(el).scope();
    while (scope && !scope.transactions) scope = scope.$parent;
    if (scope?.transactions?.length > 0 && !scope.startDate) {
      scope.startDate = new Date(0);
      scope.end = new Date();
      scope.$apply();
    }
  }
""")
```
Then `page.wait_for_selector("tbody tr", timeout=5000)` (catch if fails).

1. **test_should_show_deposit_entry_on_transactions_page**: Skip if bank_user.name == "Hermoine Granger". go_to_transactions → table text contains "500"
2. **test_should_clear_transactions_on_reset_and_return_to_dashboard_on_back**: go_to_transactions → click reset → expect table_rows count 0 → click back → wait_for_url account → expect deposit_btn visible

### 5.5 `test_account_switching.py`

`beforeEach`: login, expect_loaded. Uses `bank_user` and `CURRENCIES`, `all_account_numbers`.

1. **test_should_show_correct_welcome_name_default_account_and_dropdown_options**: welcome contains name, get_selected_account == bank_user.accounts.Dollar, get_account_number contains Dollar, get_currency == "Dollar", options == all_account_numbers(bank_user)
2. **test_should_show_correct_account_info_when_switching_currencies**: for each currency, select_account → assert account_number contains it, currency matches, balance >= 0
3. **test_should_isolate_deposits_between_accounts**: select Dollar, deposit 2500, assert balance increased → select Pound, assert 0 → select Rupee, assert 0 → select Dollar, assert 2500 preserved
4. **test_should_accumulate_deposits_correctly_across_multiple_accounts**: record balances before for each currency → deposit Dollar 1000, Pound 2000, Rupee 3000 → verify each balance increased correctly → deposit Rupee 500 twice, verify total
5. **test_should_keep_ui_in_sync_during_rapid_account_switching**: loop 3× over CURRENCIES, select each, assert currency and account_number match

### 5.6 `test_manager_crud.py`

`beforeEach`: go_to_home, select_manager_login, go_to_manager

1. **test_should_show_success_alert_with_customer_id_when_adding_customer**: open_add_customer_tab → add_customer("Test","CRUDUser","E99999") → customer_id > 0
2. **test_should_show_success_alert_with_account_number_when_opening_account**: open_open_account_tab → open_account("Harry Potter","Dollar") → account_number non-empty
3. **test_should_list_customers_and_filter_them_by_search**: open_customers_tab → get_customer_rows, assert Harry Potter in list → search_customer("Harry") → filtered rows all contain "Harry"
4. **test_should_add_customer_open_accounts_search_and_delete_customer**: unique_postcode = f"E{int(time.time()) % 10**6:06d}" → add "Delete","MeUser",postcode → open Dollar/Pound/Rupee for "Delete MeUser" → search "Delete", assert found → delete_customer("Delete","MeUser") → search again, assert not found

### 5.7 `test_failing_deposit.py`

**Intentionally fails** — for report validation.

`beforeEach`: login, expect_loaded

**test_this_test_will_fail**: deposit 10000 → expected = balance_before + 5000 (wrong!) → assert balance_after == expected → WILL FAIL

---

## Phase 6: CLI & Scripts

### 6.1 `run_tests.py`

- Parse `--local`, `--full` from argv
- If `--local`: set `BANK_LOCAL=1`, `BANK_BASE_URL=http://localhost:8081/#/login`
- If `--full`: set `BANK_FULL_RUN=1`
- Prune old reports: keep last 3 in `test-reports/` (same logic as TS)
- Run: `pytest` with env. Forward remaining args to pytest.
- Use pytest-playwright's `--headed`, `--ui` etc. if supported, or document in README

### 6.2 `download_app.py` (optional)

Replicate Node logic: launch chromium, goto app URL, capture HTML and resources, save to `banking-app/`. CDN map for local filenames. Graceful failure if local copy exists.

---

## Phase 7: Execution Order

1. Create `requirements.txt`, `pyproject.toml`
2. Create `src/banking/data/customers.py`
3. Create `src/banking/locators/selectors.py`
4. Create `src/banking/helpers/browser_helpers.py`, `assert_helpers.py`
5. Create `conftest.py` with `page` and `bank_user`
6. Create page objects (Login, CustomerDashboard, Deposit, Withdraw, Manager)
7. Create test specs in order: customer_login → deposit → withdraw → transactions_list → account_switching → manager_crud → failing_deposit
8. Create `run_tests.py`
9. Create `README.md` with: `pip install -r requirements.txt`, `playwright install chromium`, `pytest` (or `python run_tests.py`)

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|--------------|
| BANK_BASE_URL | globalsqa live URL | Override for local/staging |
| BANK_LOCAL | (unset) | 1 = start local server on 8081 |
| BANK_FULL_RUN | (unset) | 1 = parametrize over all 5 customers |
| PW_REPORT_KEEP_COUNT | 3 | Max report dirs to retain |

---

## Playwright Python API Mapping

| TypeScript | Python (sync) |
|------------|---------------|
| page.goto(url, { waitUntil }) | page.goto(url, wait_until="domcontentloaded") |
| page.locator(sel).click() | page.locator(sel).click() |
| locator.selectOption({ label: x }) | locator.select_option(label=x) |
| locator.selectOption(value) | locator.select_option(value) |
| locator.fill(str) | locator.fill(str) |
| locator.textContent() | locator.text_content() |
| locator.inputValue() | locator.input_value() |
| locator.allTextContents() | locator.all_text_contents() |
| expect(loc).toBeVisible() | locator.wait_for(state="visible") or expect(locator).to_be_visible() |
| expect(loc).toContainText(x) | expect(locator).to_contain_text(x) |
| expect(loc).toBeHidden() | expect(locator).to_be_hidden() |
| page.waitForEvent('dialog') | with page.expect_dialog() as di: d = di.value |
| form.evaluate(fn) | form.evaluate("el => el.requestSubmit()") |
| page.waitForURL(regex) | page.wait_for_url(regex) |
| page.waitForSelector(sel) | page.wait_for_selector(sel) |

---

## Done

After implementation, run:

```bash
pip install -r requirements.txt
playwright install chromium
python run_tests.py          # smoke, live site
python run_tests.py --local  # smoke, local app
python run_tests.py --full   # all customers
```

Exclude or skip `test_failing_deposit` in CI if desired.
