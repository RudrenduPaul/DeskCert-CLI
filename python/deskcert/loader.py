"""Loads a task suite from either a directory (deskcert.config.yaml + tasks/*.yaml,
the layout `deskcert init` scaffolds) or a single YAML file holding the full
suite inline. Mirrors src/core/loader.ts.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import yaml

from .schema import validate_suite_object
from .types import SuiteConfig


def load_suite(suite_path: str) -> SuiteConfig:
    resolved = Path(suite_path).resolve()
    if not resolved.exists():
        raise FileNotFoundError(f'Suite path "{resolved}" does not exist')
    if resolved.is_dir():
        return _load_directory_suite(resolved)
    text = resolved.read_text(encoding="utf-8")
    return validate_suite_object(yaml.safe_load(text))


def _load_directory_suite(directory: Path) -> SuiteConfig:
    manifest_path = directory / "deskcert.config.yaml"
    if not manifest_path.exists():
        raise FileNotFoundError(f'No deskcert.config.yaml found in "{directory}"')
    manifest: Dict[str, Any] = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))

    tasks_dir = directory / manifest.get("tasks_dir", "tasks")
    if not tasks_dir.exists():
        raise FileNotFoundError(f'Tasks directory "{tasks_dir}" does not exist')

    tasks = [
        yaml.safe_load(p.read_text(encoding="utf-8"))
        for p in sorted(tasks_dir.glob("*.yaml")) + sorted(tasks_dir.glob("*.yml"))
    ]

    suite_object: Dict[str, Any] = {"version": manifest["version"], "tasks": tasks}
    if manifest.get("pass_threshold") is not None:
        suite_object["pass_threshold"] = manifest["pass_threshold"]
    if manifest.get("forbidden_action_weight") is not None:
        suite_object["forbidden_action_weight"] = manifest["forbidden_action_weight"]

    return validate_suite_object(suite_object)
