"""`deskcert init` -- scaffold a runnable example task suite + fixture app.
Mirrors src/commands/init.ts.
"""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import List

_EXAMPLES_CANDIDATES = [
    Path(__file__).resolve().parent / "examples" / "example-suite",  # packaged wheel
    Path(__file__).resolve().parents[2] / "examples" / "example-suite",  # repo checkout
]


def _find_examples_dir() -> Path:
    for candidate in _EXAMPLES_CANDIDATES:
        if candidate.exists():
            return candidate
    raise FileNotFoundError("Could not locate the bundled example-suite directory")


def run_init(target_dir: str, force: bool = False) -> List[str]:
    target = Path(target_dir).resolve()
    if target.exists() and not force:
        raise FileExistsError(f'"{target}" already exists. Pass --force to overwrite.')
    source = _find_examples_dir()
    shutil.copytree(source, target, dirs_exist_ok=True)
    return [
        "deskcert.config.yaml",
        "tasks/view-dashboard.yaml",
        "tasks/attempt-delete.yaml",
        "fixture-app/index.html",
        "fixture-app/server.mjs",
    ]
