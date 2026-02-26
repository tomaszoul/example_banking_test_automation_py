# XYZ Banking E2E Tests (Python + Playwright)

Python Playwright E2E test suite for the XYZ Banking Project demo app (AngularJS).

**App under test:** [GlobalSQA Banking Project](https://www.globalsqa.com/angularJs-protractor/BankingProject/#/login) or a local copy in `banking-app/`.

## Prerequisites

- Python 3.10+
- Dependencies: `playwright`, `pytest`, `pytest-playwright`

## Setup

### 1. Install Python (if not already installed)

**Windows (winget):**
```powershell
winget install --id=Python.Python.3.13 -e --scope machine
```
Close and reopen your terminal. If `python` opens the Microsoft Store, disable the `python.exe` and `python3.exe` aliases in **Settings → Apps → Advanced app settings → App execution aliases**.

**macOS (Homebrew):**
```bash
brew install python@3.13
```
Add to PATH if needed: `echo 'export PATH="$(brew --prefix python@3.13)/bin:$PATH"' >> ~/.zshrc`

**Linux (Ubuntu/Debian):**
```bash
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update && sudo apt install python3.13
```

**Linux (Fedora/RHEL):**
```bash
sudo dnf install python3.13
```

**Other / manual:** Download from [python.org](https://www.python.org/downloads/).

### 2. Install Python dependencies

```bash
python -m pip install -r requirements.txt
```
*Or `pip install` / `pip3 install` if available in PATH.*

### 3. Install Playwright browsers (required before running tests)

```bash
playwright install chromium
```

## Run Tests

*Ensure steps 1–3 above are complete (Python, pip packages, `playwright install chromium`).*

| Mode | Command | Description |
|------|---------|-------------|
| **Smoke tests** | `python run_tests.py` or `run-tests` (after `pip install -e .`) | Fast feedback — all scenarios with one customer |
| **Full run** | `python run_tests.py --full` | Every scenario × all 5 customers |
| **Headed (visible browser)** | `python run_tests.py --headed` or `python run_tests.py --full --headed` | See the browser during the test run. |
| **Playwright Test UI** | `python run_tests.py --ui` and/or `--local` and/or `--full` | TS Playwright Test UI in `playwright-ui/`: test picker, watch, time-travel. **All 4 combinations:** `--ui` (live, smoke), `--ui --full` (live, all tests), `--ui --local` (local, smoke), `--ui --local --full` (local, all tests). First time: `cd playwright-ui && npm install`. |
| **Debug** | `python run_tests.py --debug` | Playwright Inspector; test pauses before each action—use Inspector to step or resume |
| **Local app** | `python run_tests.py --local` | Auto-starts banking-app on :8081 |
| **Open report** | `python run_tests.py --open` | Open HTML report in browser after run |
| **Open failed traces** | `python run_tests.py --open-trace-failed` | After run: open traces from failed tests (works with `--local` or live) |
| **Open all traces** | `python run_tests.py --open-trace-all` | After run: record + open all traces (works with `--local` or live) |

Every test run generates a versioned HTML report under `test-reports/<runId>/report.html`. Only the latest **3 reports** are kept; older runs are pruned before each run.

**Command matrix (all combinations):**  
*Flags: `--full` = all 5 customers; `--local` = local app (else live); `--ui` = TS Playwright Test UI (else Python pytest).*

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

For reviewers: full command reference, env vars, and architecture are in [REVIEWER.md](REVIEWER.md).

```bash
# Headless
python run_tests.py                  # smoke tests
python run_tests.py --full           # full run (all 5 users)

# Headed (visible browser)
python run_tests.py --headed         # smoke + visible browser
python run_tests.py --full --headed  # full run + visible browser

# Playwright Test UI (TS runner in playwright-ui/; all combos of --full and --local)
cd playwright-ui && npm install     # first time only
python run_tests.py --ui            # live app, smoke tests
python run_tests.py --ui --full     # live app, all tests
python run_tests.py --ui --local    # local app, smoke tests
python run_tests.py --ui --local --full   # local app, all tests

# Local app (download_app.py fetches index.html + Angular templates)
python download_app.py              # first time: download app to banking-app/
python run_tests.py --local          # smoke + local
python run_tests.py --local --full   # full run + local
python run_tests.py --local --headed # smoke + local + visible browser

# Report + traces
python run_tests.py --open                 # smoke + open report after run
python run_tests.py --open-trace-failed    # smoke + open failed traces (or standalone to view last run)
python run_tests.py --open-trace-all       # smoke + record + open all traces
python run_tests.py --local --open-trace-failed  # local + open failed traces

# Other
python run_tests.py --debug         # step-through debug
```

The suite includes one deliberately failing test to demonstrate how the HTML report captures screenshots and failure traces—intended for showcase only. Exclude it for CI or when you need all-green runs:

**Exclude failing test (for CI):**
```bash
python run_tests.py -k "not test_this_test_will_fail"
```

**Detailed reviewer guide:** See [REVIEWER.md](REVIEWER.md) for all run variants, environment variables, and architecture notes. For Python vs Node.js Playwright and trace visualization, see [PLAYWRIGHT_ALTERNATIVES.md](PLAYWRIGHT_ALTERNATIVES.md).

## Avoiding long freezes

If a run appears to hang for minutes (e.g. at manager CRUD tests), it is usually due to the **live site** (globalsqa.com) being slow or unresponsive. Navigation uses a **30s timeout** so a single slow load will fail fast; use **`--local`** for stable, fast runs and CI:

```bash
python download_app.py              # once: fetch app into banking-app/
python run_tests.py --local --full  # full run against local app
```

## Test Stability (No Flakiness)

Tests are designed to be deterministic. **No retries** (MAX_RETRIES=0); failures indicate real issues. Strategy:

- **Deterministic setup:** Fixed test data from [customers.py](src/banking/data/customers.py); manager CRUD uses time-based postcodes only for isolation.
- **Robust waits:** `wait_for_angular`, explicit `wait_for(state="visible")`, Playwright auto-waiting.
- **Micro delays for CI/CD:** Brief buffers (50–150 ms) after navigation and form submissions when `CI=true` or `GITHUB_ACTIONS=true`. Skipped locally; CI runners are typically slower. See [browser_helpers.py](src/banking/helpers/browser_helpers.py).
- **Stable selectors:** Centralized in [selectors.py](src/banking/locators/selectors.py).
- **Local-first for CI:** Prefer `--local` to reduce network flakiness; live site may have CDN latency.

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| BANK_BASE_URL | globalsqa live URL | Override for local/staging |
| BANK_LOCAL | (unset) | 1 = start local server on 8081 |
| BANK_FULL_RUN | (unset) | 1 = parametrize over all 5 customers |
| PW_REPORT_KEEP_COUNT | 3 | Max report dirs to retain (pruned before each run) |
| PW_REPORT_AUTO_OPEN | false | Open HTML report in browser after run |
| PW_REPORT_PORTAL | false | Post results to Report Portal (set RP_* vars) |
| MAX_RETRIES | 0 | No retries; fix root cause instead of masking flakiness |

## Structure

```
banking-e2e-tests-python/
├── banking-app/                 # Local copy (run download_app.py)
├── conftest.py
├── run_tests.py
├── download_app.py
├── REPORTING.md                 # Report generation, retention, env vars
├── PLAYWRIGHT_ALTERNATIVES.md   # Python vs Node.js Playwright, trace visualization
├── src/banking/
│   ├── data/customers.py
│   ├── locators/selectors.py
│   ├── helpers/
│   ├── pages/
│   └── specs/
└── utils/reporting/             # Report config, retention, post-run (mirrors TS)
    ├── report_config.py
    ├── retention.py
    └── post_run.py
```
