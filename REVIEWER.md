# Banking E2E Test Suite (Python) — Reviewer Guide

## How to Run

### Prerequisites

1. **Python 3.10+** — install via [python.org](https://www.python.org/downloads/) or your OS package manager.
2. **Install dependencies:**
   ```bash
   python -m pip install -r requirements.txt
   ```
3. **Install Playwright browsers (Chromium only):**
   ```bash
   playwright install chromium
   ```

### Run Modes: Smoke vs Full Run

| Mode | Command | Tests | Use when |
|------|---------|-------|----------|
| **Smoke tests** | `python run_tests.py` or `pytest` | ~18 | Fast feedback, CI, daily development |
| **Full run** | `python run_tests.py --full` | ~75 | Every scenario × every user; pre-release, thorough validation |

- **Smoke tests** run all scenarios once with a single customer (Harry Potter). Fast, minimal.
- **Full run** runs the same scenarios across all 5 customers (Hermoine, Harry, Ron, Albus, Neville). Each scenario executes 5×; total runtime is higher but every user is exercised in every flow.

Both modes can target the live site or a local app. Combine with `--local` to use the bundled banking app in `banking-app/`.

### Against the Live Site (default)

```bash
python run_tests.py                 # headless, smoke tests (single user)
python run_tests.py --full          # headless, full run (all 5 users)
python run_tests.py --headed        # smoke + visible browser
python run_tests.py --full --headed # full run + visible browser
python run_tests.py --headed        # visible browser
python run_tests.py --debug         # step-through debug (Playwright Inspector)
```

### Against the Local App (offline)

```bash
python run_tests.py --local                 # headless, smoke tests, auto-starts local server
python run_tests.py --local --full         # headless, full run, auto-starts local server
python run_tests.py --local --headed       # smoke + local + visible browser
python run_tests.py --local --full --headed  # full run + local + visible browser
python run_tests.py --local --headed       # visible browser
python run_tests.py --local --debug         # step-through debug
```

### Configuration Commands (Parity with TypeScript package.json)

| TypeScript (pnpm) | Python | Description |
|-------------------|--------|--------------|
| `test` / `test:smoke` | `python run_tests.py` or `run-tests` | Smoke tests, headless, live site |
| `test:full` | `python run_tests.py --full` | Full run (all 5 customers), headless |
| `test:local` / `test:local:smoke` | `python run_tests.py --local` | Smoke, headless, local app |
| `test:local:full` | `python run_tests.py --local --full` | Full run, headless, local app |
| `test:headed` | `python run_tests.py --headed` | Visible browser |
| `test:ui` | `python run_tests.py --headed` | Headed (visible browser; full Playwright UI is TS-only) |
| `test:ui:full` | `python run_tests.py --full --headed` | Full run + headed |
| `test:local:ui` | `python run_tests.py --local --headed` | Smoke + local + headed |
| `test:local:ui:full` | `python run_tests.py --local --full --headed` | Full run + local + headed |
| `test:debug` | `python run_tests.py --debug` | Playwright Inspector (PWDEBUG=1) |
| `test:report:open` | `python run_tests.py --open` | Run tests, then open HTML report |
| — | `python run_tests.py --open-trace-failed` | After run: open traces from failed tests (works with `--local` or live) |
| — | `python run_tests.py --open-trace-all` | After run: record + open all traces (works with `--local` or live) |

### Quick Reference Table

| Command | Description |
|---------|-------------|
| `python run_tests.py` | Smoke tests, headless, live site |
| `python run_tests.py --full` | Full run (all 5 users), headless |
| `python run_tests.py --headed` | Smoke + visible browser |
| `python run_tests.py --full --headed` | Full run + visible browser |
| `python run_tests.py --headed` | Visible browser window |
| `python run_tests.py --debug` | Debug with Playwright Inspector |
| `python run_tests.py --local` | Smoke + local app (auto-starts server on :8081) |
| `python run_tests.py --local --full` | Full run + local app |
| `python run_tests.py --local --headed` | Smoke + local + visible browser |
| `python run_tests.py --local --full --headed` | Full run + local + visible browser |
| `python run_tests.py --open-trace-failed` | Open traces from failed tests (standalone or after run) |
| `python run_tests.py --open-trace-all` | Record + open all traces in viewer |
| `python run_tests.py --local --open-trace-failed` | Run local, then open failed traces |
| `python run_tests.py --local --open-trace-all` | Run local, then record + open all traces |

Flags can be combined: `python run_tests.py --local --full --headed`, etc.

### Exclude the Intentionally Failing Test (for CI)

The suite includes one test that fails on purpose for report validation. Exclude it in CI:

```bash
pytest -k "not test_this_test_will_fail"
# or
python run_tests.py -k "not test_this_test_will_fail"
```

### Targeting a Specific Spec

```bash
python run_tests.py src/banking/specs/test_deposit.py
python run_tests.py -k "deposit"
```

### Custom Target URL (staging, Docker, etc.)

```bash
# bash / zsh
export BANK_BASE_URL='http://my-staging-host:3000/#/login'
python run_tests.py

# PowerShell
$env:BANK_BASE_URL='http://my-staging-host:3000/#/login'
python run_tests.py
```

---

## Local App Setup

The `--local` flag auto-starts a static server on port 8081 from `banking-app/`. On first use:

```bash
python download_app.py   # downloads the app from the live site
python run_tests.py --local
```

If `banking-app/index.html` does not exist, `run_tests.py --local` will warn and exit. Copy `banking-app/` from the TypeScript repo or run `download_app.py`.

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `BANK_BASE_URL` | globalsqa.com live URL | Override to test against localhost or staging. Prefer `--local` for localhost. |
| `BANK_LOCAL` | (unset) | Set to `1` by `run_tests.py --local`; enables auto-start of local server |
| `BANK_FULL_RUN` | (unset) | Set to `1` by `run_tests.py --full`; runs each scenario for all 5 customers |
| `PW_REPORT_KEEP_COUNT` | `3` | Max report directories to retain on disk (pruned before each run) |
| `PW_REPORT_AUTO_OPEN` | `false` | Open HTML report in browser after post-run |
| `PW_REPORT_PORTAL` | `false` | Post results to Report Portal (requires RP_* vars; see REPORTING.md) |

**Report automation:** Every run generates a versioned HTML report under `test-reports/<runId>/report.html`. Only the latest 3 reports are kept. See [REPORTING.md](REPORTING.md).

---

## Test Coverage (18 tests)

| Spec File | Tests | What it covers |
|-----------|-------|----------------|
| test_customer_login | 2 | Home page options, dropdown users, login/logout flow |
| test_account_switching | 5 | Welcome name, account dropdown, currency switching, deposit isolation |
| test_deposit | 2 | Deposit + balance update, empty/zero submit |
| test_withdraw | 2 | Successful withdrawal, overdraft/empty/zero/negative rejection |
| test_transactions_list | 2 | Deposit in list, reset clears list and back navigation |
| test_failing_deposit | 1 | Intentional failure for report/trace validation |
| test_manager_crud | 4 | Add customer, open account, list/filter, full CRUD flow |

---

## Playwright UI parity

The TypeScript repo runs `playwright test --ui`, which opens Playwright's native interactive UI (test picker, time-travel debugging, watch mode). **pytest-playwright has no equivalent** — the Playwright Test UI is part of the Node.js runner. In Python, use `--headed` (visible browser) as the best available substitute. For full Playwright UI, use the TypeScript suite. See [PLAYWRIGHT_ALTERNATIVES.md](PLAYWRIGHT_ALTERNATIVES.md) for feature comparison and trace visualization.

---

## Architecture

```
utils/reporting/           # Report config, retention, post-run (mirrors TS repo)
├── report_config.py
├── retention.py
└── post_run.py

src/banking/
├── data/customers.py        # Customer fixtures (Harry, Hermoine, etc.)
├── locators/selectors.py    # Centralized CSS selectors
├── pages/                   # Page Object classes
│   ├── login_page.py
│   ├── customer_dashboard_page.py
│   ├── deposit_page.py
│   ├── withdraw_page.py
│   └── manager_page.py
├── helpers/
│   ├── browser_helpers.py   # wait_for_angular
│   └── assert_helpers.py   # expect_balance_change
└── specs/                   # Test specs
```

---

See [README.md](README.md) for setup steps and structure overview.
