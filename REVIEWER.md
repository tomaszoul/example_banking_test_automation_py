# Banking E2E Test Suite — Reviewer Guide

**For reviewers:** This doc is the single reference. Start with **Flags** and the **Command matrix** below; then use **How to Run** for copy-paste commands. **Architecture** and **Test coverage** are at the end.

---

## Flags (what they do)

| Flag | Effect |
|------|--------|
| *(none)* | **Python pytest** runner, **smoke** tests (1 customer), **live** app (globalsqa.com) |
| `--full` | **Full** test set: same scenarios × **all 5 customers** (Hermoine, Harry, Ron, Albus, Neville) |
| `--local` | **Local** app: auto-starts server on **:8081** from `banking-app/` (run `download_app.py` once first) |
| `--ui` | **TS Playwright Test UI** (Node in `playwright-ui/`): interactive picker, watch, time-travel. Requires `cd playwright-ui && npm install` once. |

Flags combine in all ways. **Without `--ui`** = Python tests; **with `--ui`** = TypeScript Playwright tests in the official UI.

---

## Command matrix (all combinations)

| Command | Runner | Tests | App |
|---------|--------|-------|-----|
| `python run_tests.py` | Python | smoke | live |
| `python run_tests.py --full` | Python | full | live |
| `python run_tests.py --local` | Python | smoke | local |
| `python run_tests.py --local --full` | Python | full | local |
| `python run_tests.py --ui` | TS Playwright UI | smoke | live |
| `python run_tests.py --ui --full` | TS Playwright UI | full | live |
| `python run_tests.py --ui --local` | TS Playwright UI | smoke | local |
| `python run_tests.py --ui --local --full` | TS Playwright UI | full | local |

- **Smoke** ≈ 18–20 tests (one customer). **Full** ≈ 66–75 (same scenarios × 5 customers).
- **Live** = [GlobalSQA Banking Project](https://www.globalsqa.com/angularJs-protractor/BankingProject/#/login). **Local** = `http://127.0.0.1:8081/#/login`.

---

## How to Run

### Prerequisites

1. **Python 3.10+** — install via [python.org](https://www.python.org/downloads/) or your OS package manager.
2. **Install dependencies:**
   ```bash
   python -m pip install -r requirements.txt
   ```
3. **Playwright browser (Chromium):**
   ```bash
   playwright install chromium
   ```
4. **For `--ui` only:** Node in `playwright-ui/`: run `cd playwright-ui && npm install` once.

*The **Command matrix** above lists all eight main combinations (Python vs TS UI × smoke vs full × live vs local).*

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
python run_tests.py --debug         # step-through debug (Playwright Inspector)
```

### Against the Local App (offline)

```bash
python run_tests.py --local                 # headless, smoke tests, auto-starts local server
python run_tests.py --local --full         # headless, full run, auto-starts local server
python run_tests.py --local --headed       # smoke + local + visible browser
python run_tests.py --local --full --headed  # full run + local + visible browser
python run_tests.py --local --debug        # step-through debug
```

### Configuration Commands (Parity with TypeScript package.json)

| TypeScript (pnpm) | Python | Description |
|-------------------|--------|--------------|
| `test` / `test:smoke` | `python run_tests.py` or `run-tests` | Smoke tests, headless, live site |
| `test:full` | `python run_tests.py --full` | Full run (all 5 customers), headless |
| `test:local` / `test:local:smoke` | `python run_tests.py --local` | Smoke, headless, local app |
| `test:local:full` | `python run_tests.py --local --full` | Full run, headless, local app |
| `test:headed` | `python run_tests.py --headed` | Visible browser |
| `test:ui` | `python run_tests.py --ui` | TS Playwright Test UI (live, smoke) |
| `test:ui:full` | `python run_tests.py --ui --full` | TS Playwright Test UI (live, full) |
| `test:local:ui` | `python run_tests.py --ui --local` | TS Playwright Test UI (local, smoke) |
| `test:local:ui:full` | `python run_tests.py --ui --local --full` | TS Playwright Test UI (local, full) |
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
| `python run_tests.py --debug` | Debug with Playwright Inspector |
| `python run_tests.py --local` | Smoke + local app (auto-starts server on :8081) |
| `python run_tests.py --local --full` | Full run + local app |
| `python run_tests.py --local --headed` | Smoke + local + visible browser |
| `python run_tests.py --local --full --headed` | Full run + local + visible browser |
| `python run_tests.py --ui` | Playwright Test UI (live, smoke); full traces, screenshots, network |
| `python run_tests.py --ui --local` | Playwright Test UI (local app, smoke) |
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

## Test coverage

**Smoke** (one customer): ~18 test nodes. **Full** (all 5 customers): ~66 test nodes (same scenarios × 5).

| Spec file | Tests (smoke) | What it covers |
|-----------|---------------|----------------|
| test_customer_login | 2 | Home page options, dropdown users, login/logout flow |
| test_account_switching | 5 | Welcome name, account dropdown, currency switching, deposit isolation, rapid switch |
| test_deposit | 2 | Deposit + balance update, empty/zero submit |
| test_withdraw | 2 | Successful withdrawal, overdraft/empty/zero/negative rejection |
| test_transactions_list | 2 | Deposit in list, reset clears list and back navigation |
| test_failing_deposit | 1 | Intentional failure for report/trace validation |
| test_manager_crud | 4 | Add customer, open account, list/filter, full CRUD flow |

---

## Playwright Test UI (`--ui`)

`python run_tests.py --ui` (and `--ui --full`, `--ui --local`, `--ui --local --full`) launches the **TypeScript** Playwright Test UI from `playwright-ui/`: interactive test picker, watch mode, time-travel. The same scenarios run as in Python; test set (smoke vs full) and app (live vs local) follow the **Command matrix** above. For Python vs Node runner and trace visualization, see [PLAYWRIGHT_ALTERNATIVES.md](PLAYWRIGHT_ALTERNATIVES.md).

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

See [README.md](README.md) for setup and structure. **Quick recap:** use the **Command matrix** at the top of this guide for the eight main combinations (Python vs TS UI × smoke vs full × live vs local).
