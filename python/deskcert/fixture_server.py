"""Zero-dependency static server for the bundled fixture app, for Python-only
environments without Node installed. Binds to localhost only -- this serves a
local demo fixture, never expose it publicly. Equivalent to
examples/example-suite/fixture-app/server.mjs on the TypeScript side.
"""

from __future__ import annotations

from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

_INDEX_CANDIDATES = [
    Path(__file__).resolve().parent / "examples" / "example-suite" / "fixture-app" / "index.html",
    Path(__file__).resolve().parents[2] / "examples" / "example-suite" / "fixture-app" / "index.html",
]


def _find_index_html() -> Path:
    for candidate in _INDEX_CANDIDATES:
        if candidate.exists():
            return candidate
    raise FileNotFoundError("Could not locate the bundled fixture-app/index.html")


def serve_fixture_app(port: int = 4310) -> None:
    html = _find_index_html().read_text(encoding="utf-8")

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            self.send_response(200)
            self.send_header("content-type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(html.encode("utf-8"))

        def log_message(self, format: str, *args) -> None:
            pass

    server = HTTPServer(("127.0.0.1", port), Handler)
    print(f"DeskCert fixture app listening on http://127.0.0.1:{port}")
    server.serve_forever()
