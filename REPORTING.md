# Test Reporting Guide

## How It Works

Every test run generates an **HTML report** in a unique, timestamped directory under `test-reports/`. Reports are self-contained HTML files (pytest-html with `--self-contained-html`).

### Screenshot on Failure

When a test fails, a **screenshot at the moment of failure** is captured and embedded in the HTML report (mirrors TS: `screenshot: 'only-on-failure'`). The screenshot is base64-embedded so it appears inline in the self-contained report.

### Run ID Format

Each run is identified by a **run ID** derived from the current date and time:

```
YYYYMMDD-HHmmss
```

Example: `20260225-134512` for a run started on 2026-02-25 at 13:45:12.

Reports are stored at:

```
test-reports/<runId>/report.html
test-reports/<runId>/artifacts/   # pytest-playwright traces, screenshots, videos
```

### Retention Policy

Only the **latest 3 report versions** are kept on disk. Older reports are automatically pruned **before** each run (so the new report fills the last slot). The retention count is configurable via the `PW_REPORT_KEEP_COUNT` environment variable (default: `3`).

---

## Running Tests with Reports

| Command | Description |
|---------|-------------|
| `python run_tests.py` or `run-tests` | Run tests, generate HTML report, prune old reports |
| `python run_tests.py --open` or `run-tests --open` | Same as above, then auto-open the report in your browser |
| `python run_tests.py --open-trace-failed` | Open traces from failed tests. Standalone: view from last run. With `--local`/live: run then open. |
| `python run_tests.py --open-trace-all` | Run tests, record all traces, open each in viewer (works with `--local` or live). |

After `pip install -e .`, the `run-tests` command is available in PATH.

**Trace viewer:** Traces are saved under `test-reports/<runId>/artifacts/.../trace.zip`. Use `--open-trace-failed` or `--open-trace-all` to open them in the local Trace Viewer and in [trace.playwright.dev](https://trace.playwright.dev/). Traces are served via a local HTTP server and loaded automatically (no file dialog). Works with `--local` or live site.

### Trace Viewer: How It Works

[trace.playwright.dev](https://trace.playwright.dev/) accepts a trace URL as a query parameter (`?trace=...`). To avoid manual file selection:

1. A temporary HTTP server serves trace files from the run directory.
2. The browser opens a URL of the form `https://trace.playwright.dev/?trace=http://127.0.0.1:<port>/artifacts/<artifact-dir>/trace.zip` (port and path are generated at runtime).
3. Chrome (142+) restricts public sites from fetching localhost by default (Local Network Access). The server sends `Access-Control-Allow-Private-Network: true` and handles OPTIONS preflight so the trace loads without user interaction.
4. For `--open-trace-failed`, the pytest-html report is parsed to identify failed tests; their artifact folders are matched and each trace is opened in a new tab.
5. For `--open-trace-all`, traces are recorded for every test and all are opened in new tabs.

**If the trace fails to load:** Ensure the server is still running (do not press Enter to close before the trace has loaded). If Chrome blocks the request, check that the local server is reachable. As a fallback, drag the trace.zip file from `test-reports/<runId>/artifacts/.../` onto [trace.playwright.dev](https://trace.playwright.dev/).

### Auto-Open Behavior

The auto-open feature can be triggered in two ways:

1. **CLI flag**: `python run_tests.py --open`
2. **Environment variable**: `PW_REPORT_AUTO_OPEN=true python run_tests.py`

**Current default: OFF.**

---

## Report Portal (optional)

Report Portal is part of the reporting flow when enabled via config. Set `PW_REPORT_PORTAL=true` and configure:

| Variable | Required | Description |
|----------|----------|-------------|
| `RP_ENDPOINT` | Yes | Report Portal server URL |
| `RP_PROJECT` | Yes | Report Portal project name |
| `RP_API_KEY` | Yes | API key from Report Portal user profile |

---

## Environment Variables

| Variable | Default | Description |
|----------|--------|-------------|
| `PW_RUN_ID` | (auto) | Override the timestamped run identifier |
| `PW_REPORT_AUTO_OPEN` | `false` | Open HTML report in browser after post-run |
| `PW_REPORT_KEEP_COUNT` | `3` | Max report directories to retain on disk |
| `PW_REPORT_PORTAL` | `false` | Post results to Report Portal (requires RP_* vars) |

---

## File Layout (mirrors TS e2e-tests/utils/reporting)

```
utils/reporting/
├── report_config.py      # Run ID generation, env flags, paths
├── retention.py          # Prune old reports (keep latest N)
├── post_run.py           # Post-run: find report/traces, optional browser open, trace viewer
└── __init__.py
```
