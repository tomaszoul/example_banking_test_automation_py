#!/usr/bin/env python3
"""
CLI to run banking E2E tests.

Flow (mirrors TS e2e-tests/utils/reporting/run-tests.ts):
1. With --local: prepare local banking-app (utils.local_banking_app), serve and wait until healthy, then point tests at it.
2. Prune old reports (keep N-1 so new report fills last slot).
3. Run pytest or Playwright UI with HTML report + artifacts.
4. Post-run: optionally open report and/or traces in browser.
"""
import argparse
import os
import subprocess
import sys
from pathlib import Path

from utils.reporting import (
    build_run_id,
    open_trace,
    post_run,
    prune_reports,
    report_dir,
    report_html_path,
)
from utils.reporting.report_config import KEEP_COUNT, REPORT_PORTAL
from utils.local_banking_app import (
    LOCAL_LOGIN_URL,
    prepare_and_serve_local,
)

REPO_ROOT = Path(__file__).resolve().parent
PLAYWRIGHT_UI_DIR = REPO_ROOT / "playwright-ui"


def _run_playwright_ui(env: dict, *, local: bool) -> None:
    """Prepare local app if requested (build-up + healthy), then run `npx playwright test --ui`."""
    if local:
        prepare_and_serve_local(REPO_ROOT)
        env["BANK_BASE_URL"] = LOCAL_LOGIN_URL
    if not (PLAYWRIGHT_UI_DIR / "package.json").exists():
        print("WARNING: playwright-ui/package.json not found. Run: cd playwright-ui && npm install")
        sys.exit(1)
    cmd = ["npx", "playwright", "test", "--ui"]
    result = subprocess.run(cmd, env=env, cwd=PLAYWRIGHT_UI_DIR)
    sys.exit(result.returncode)


def main() -> None:
    """Parse args, set env, prune reports, run pytest, optionally open report and traces."""
    parser = argparse.ArgumentParser(description="Run banking E2E tests")
    parser.add_argument(
        "--local",
        action="store_true",
        help="Prepare, serve and health-check local banking-app (port 8081), then run tests against it. Run download_app.py once first.",
    )
    parser.add_argument("--full", action="store_true", help="Run with all 5 customers")
    parser.add_argument(
        "--ui",
        action="store_true",
        help="Run in TS Playwright Test UI (playwright-ui/). Combines with --full (smoke vs all tests) and --local (live vs local app).",
    )
    parser.add_argument("--open", action="store_true", help="Open HTML report in browser after run")
    parser.add_argument(
        "--headed",
        action="store_true",
        help="Visible browser during test run (Playwright Test UI is TypeScript-only)",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Playwright Inspector: PWDEBUG=1, step-through debug",
    )
    parser.add_argument(
        "--open-trace-failed",
        action="store_true",
        help="After run: open traces from failed tests (works with --local or live)",
    )
    parser.add_argument(
        "--open-trace-all",
        action="store_true",
        help="After run: record + open all traces (works with --local or live)",
    )
    args, pytest_args = parser.parse_known_args()

    env = os.environ.copy()
    if args.local:
        env["BANK_LOCAL"] = "1"
        env["BANK_BASE_URL"] = LOCAL_LOGIN_URL
    if args.full:
        env["BANK_FULL_RUN"] = "1"
    if args.debug:
        env["PWDEBUG"] = "1"

    # --ui: launch Node Playwright Test UI (TS runner in playwright-ui/).
    # Respects --full (smoke vs full test set) and --local (live vs local app); all 4 combinations supported.
    if args.ui:
        _run_playwright_ui(env, local=args.local)
        return

    # Standalone: open failed traces without running (only --open-trace-failed)
    # --open-trace-all always runs tests first to record traces
    trace_flags = args.open_trace_failed or args.open_trace_all
    if args.open_trace_failed and not args.open_trace_all and len(pytest_args) == 0 and not (args.local or args.full):
        try:
            open_trace(scope="failed", local_viewer=True, online_viewer=True)
        except Exception:
            pass
        sys.exit(0)

    run_id = build_run_id()
    env["PW_RUN_ID"] = run_id

    # Prune before run so the new report fills the last slot (keep N-1 before adding 4th).
    removed = prune_reports(KEEP_COUNT - 1)
    if removed:
        print(f"Pruned {len(removed)} old report(s): {', '.join(removed)}")

    report_dir_path = report_dir()
    report_dir_path.mkdir(parents=True, exist_ok=True)
    report_html = report_html_path()

    if args.local:
        prepare_and_serve_local(REPO_ROOT)

    html_report_args = [
        f"--html={report_html}",
        "--self-contained-html",
    ]
    # Use subdir for playwright so its session cleanup does not delete the report dir
    artifacts_dir = report_dir_path / "artifacts"
    # Trace only when requested: on=all (--open-trace-all), retain-on-failure=failed only (--open-trace-failed)
    if args.open_trace_all:
        tracing = "on"
    elif args.open_trace_failed:
        tracing = "retain-on-failure"
    else:
        tracing = "off"
    output_args = [
        f"--output={artifacts_dir}",
        "--screenshot=only-on-failure",  # Capture screenshot at moment of failure (TS: screenshot: 'only-on-failure')
        f"--tracing={tracing}",
    ]
    play_opts = []
    if args.headed:
        play_opts.append("--headed")
    if REPORT_PORTAL:
        play_opts.append("--reportportal")
    if args.debug:
        play_opts.extend(["-s"])  # no capture, so Inspector output is visible
    cmd = (
        [sys.executable, "-m", "pytest"]
        + html_report_args
        + output_args
        + play_opts
        + pytest_args
    )
    result = subprocess.run(cmd, env=env, cwd=REPO_ROOT)

    # Post-run: open report if requested (failures swallowed to not mask test exit code)
    try:
        post_run(should_open=args.open)
    except Exception:
        pass
    if trace_flags:
        scope = "all" if args.open_trace_all else "failed"
        try:
            open_trace(scope=scope, local_viewer=True, online_viewer=True)
        except Exception:
            pass

    sys.exit(result.returncode)


if __name__ == "__main__":
    main()

# "In the Kamigata area, they have a sort of tiered lunchbox
#  they use for a single day when flower viewing. Upon returning,
#  they throw them away, trampling them underfoot.
#  The end is important in all things."
#
#  — Hagakure, Yamamoto Tsunetomo
