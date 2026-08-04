"""Task-suite JSON Schema validation. Loads and validates against the exact
same schema/task-suite.schema.json the TypeScript package ships -- there is
only one schema file, shared by both languages, so a new field can never be
added to one validator without the other seeing it.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

import jsonschema
import yaml

from .types import AgentAction, SuccessCriterion, SuiteConfig, TaskDefinition

_SCHEMA_CANDIDATES = [
    Path(__file__).resolve().parent / "schema" / "task-suite.schema.json",  # packaged wheel
    Path(__file__).resolve().parents[2] / "schema" / "task-suite.schema.json",  # repo checkout
]


def _load_schema() -> Dict[str, Any]:
    for candidate in _SCHEMA_CANDIDATES:
        if candidate.exists():
            return json.loads(candidate.read_text(encoding="utf-8"))
    raise FileNotFoundError(
        "Could not locate task-suite.schema.json in any known location: "
        + ", ".join(str(c) for c in _SCHEMA_CANDIDATES)
    )


_SCHEMA = _load_schema()
_VALIDATOR = jsonschema.Draft7Validator(_SCHEMA)


class SchemaValidationError(Exception):
    def __init__(self, errors: List[str]):
        self.errors = errors
        super().__init__("Task suite failed schema validation:\n" + "\n".join(f"  - {e}" for e in errors))


def validate_suite_object(raw: Dict[str, Any]) -> SuiteConfig:
    errors = sorted(_VALIDATOR.iter_errors(raw), key=lambda e: list(e.path))
    if errors:
        raise SchemaValidationError([f"{'/'.join(str(p) for p in e.path) or '(root)'} {e.message}" for e in errors])

    seen_ids = set()
    for task in raw.get("tasks", []):
        if task["id"] in seen_ids:
            raise SchemaValidationError([f'/tasks duplicate task id "{task["id"]}"'])
        seen_ids.add(task["id"])

    tasks = [_to_task_definition(t) for t in raw["tasks"]]
    return SuiteConfig(
        version=raw["version"],
        tasks=tasks,
        pass_threshold=raw.get("pass_threshold"),
        forbidden_action_weight=raw.get("forbidden_action_weight"),
    )


def parse_suite(yaml_text: str) -> SuiteConfig:
    return validate_suite_object(yaml.safe_load(yaml_text))


def get_schema_json() -> Dict[str, Any]:
    return _SCHEMA


def _to_task_definition(raw: Dict[str, Any]) -> TaskDefinition:
    return TaskDefinition(
        id=raw["id"],
        goal=raw["goal"],
        target_url=raw["target_url"],
        allowed_actions=list(raw.get("allowed_actions", [])),
        forbidden_actions=list(raw.get("forbidden_actions", [])),
        success_criteria=[SuccessCriterion(**c) for c in raw["success_criteria"]],
        max_steps=raw["max_steps"],
        reference_actions=[AgentAction(**a) for a in raw.get("reference_actions", [])],
    )
