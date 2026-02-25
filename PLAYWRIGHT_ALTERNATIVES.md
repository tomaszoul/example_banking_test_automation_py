# Python Playwright as Alternative to Node.js

This document describes the Python + pytest-playwright setup as an alternative to the Node.js `@playwright/test` runner. Use it when the team prefers Python, has existing Python tooling, or needs to integrate with Python-based CI or reporting.

Both stacks use the same Playwright browser automation; they differ in test runner and ecosystem features.

## Feature Comparison

| Capability | Node.js (@playwright/test) | Python (pytest-playwright) |
|------------|---------------------------|----------------------------|
| Test execution | Yes | Yes |
| Trace recording | Yes | Yes |
| Trace viewer | Yes | Yes (same format) |
| Live UI mode (`--ui`) | Yes | No |
| Headed / visible browser | Yes | Yes (`--headed`) |
| Step debug (Inspector) | Yes | Yes (`PWDEBUG=1`) |
| Screenshot on failure | Yes | Yes |
| Cross-browser (chromium, firefox, webkit) | Yes | Yes |

## Trace Visualization

Traces are recorded and can be viewed with the same Trace Viewer as in the Node.js setup.

### Where Traces Live

With the default `--tracing=retain-on-failure`, traces are saved only for failed tests:

```
test-reports/<runId>/artifacts/<test-folder>/trace.zip
```

Example: `test-reports/20260225-221435/artifacts/src-banking-specs-test-withdraw-py-test-should-reduce-balance-...-chromium/trace.zip`

### How to Open Traces

| Method | Command / action |
|--------|------------------|
| **CLI** | `playwright show-trace path/to/trace.zip` |
| **Web** | [trace.playwright.dev](https://trace.playwright.dev/) — drag-and-drop or "Select file" (works on all platforms) |
| **VS Code** | Playwright Test extension → Open Trace |

The Trace Viewer shows the same UI in all cases: timeline, actions list, Before/After tabs, source code, and DOM snapshots.

## Node.js-Only Features

**UI Mode** (`npx playwright test --ui`) is available only in the Node.js runner. It provides:

- Interactive test picker
- Live timeline during test runs
- Watch mode for automatic re-runs
- Time-travel debugging in real time

**Python equivalent:** Use `--headed` to see the browser during runs, and open traces in the Trace Viewer after completion for step-by-step inspection.

## References

- [Playwright Python Trace Viewer](https://playwright.dev/python/docs/trace-viewer)
- [trace.playwright.dev](https://trace.playwright.dev/)
