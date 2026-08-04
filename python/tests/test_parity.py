"""Cross-language parity: the Python scorer must produce the same score for the
same fixture run as the TypeScript scorer (repo CLAUDE.md engineering standard
4). Runs the bundled example suite through the Python CLI and, if a built
`dist/cli.js` is present (built by `npm run build` in CI and dev), through the
Node CLI too, then asserts the two JSON reports agree on every score field.
Skips the cross-language half gracefully when the Node build isn't present
locally, so `pytest` still runs standalone for a Python-only contributor.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

import pytest

from deskcert.adapter import ScriptedAdapter
from deskcert.loader import load_suite
from deskcert.report import format_report_json
from deskcert.runner import run_suite
from deskcert.scorer import score_suite

REPO_ROOT = Path(__file__).resolve().parents[2]
FIXTURE_HTML = REPO_ROOT / "examples" / "example-suite" / "fixture-app" / "index.html"
SUITE_DIR = REPO_ROOT / "examples" / "example-suite"
NODE_CLI = REPO_ROOT / "dist" / "cli.js"

SCORE_FIELDS = ("suiteScore", "taskCompletionRate", "forbiddenViolationCount", "gatePassed")


class _FixtureServer:
    def __enter__(self):
        html = FIXTURE_HTML.read_text(encoding="utf-8")

        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                self.send_response(200)
                self.send_header("content-type", "text/html")
                self.end_headers()
                self.wfile.write(html.encode("utf-8"))

            def log_message(self, *args):
                pass

        self.server = HTTPServer(("127.0.0.1", 4310), Handler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        return self

    def __exit__(self, *exc):
        self.server.shutdown()
        self.thread.join(timeout=5)


def _run_python_report() -> dict:
    import asyncio

    suite = load_suite(str(SUITE_DIR))
    results = asyncio.run(run_suite(suite, lambda task: ScriptedAdapter.for_task(task), headless=True))
    report = score_suite(
        results,
        pass_threshold=suite.pass_threshold,
        forbidden_action_weight=suite.forbidden_action_weight,
    )
    return json.loads(format_report_json(report))


_NODE_BUILD_MISSING = not NODE_CLI.exists() or shutil.which("node") is None


@pytest.mark.skipif(_NODE_BUILD_MISSING, reason="Node build (dist/cli.js) not present -- run `npm run build` first")
def test_python_and_typescript_scores_match_on_the_same_fixture():
    with _FixtureServer():
        python_report = _run_python_report()
        node_result = subprocess.run(
            ["node", str(NODE_CLI), "run", "--agent", "scripted", "--suite", str(SUITE_DIR), "--json"],
            capture_output=True,
            text=True,
            check=False,
        )
        # exit codes 0/1/2 are all "successful" CLI runs (score outcomes), not crashes
        assert node_result.returncode in (0, 1, 2), node_result.stderr
        node_report = json.loads(node_result.stdout)

    for field in SCORE_FIELDS:
        assert python_report[field] == node_report[field], (
            f"parity mismatch on {field}: python={python_report[field]!r} node={node_report[field]!r}"
        )
