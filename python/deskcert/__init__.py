"""DeskCert: certify whether an AI agent is safe to operate your internal web
application before production rollout.

This package is a real, independent Python/Playwright implementation of the
task-runner and scorer -- not a subprocess wrapper around the TypeScript CLI.
Its scorer produces identical scores to the TypeScript package for the same
fixture run; see tests/test_parity.py.
"""

from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as _pkg_version

from .adapter import ScriptedAdapter, load_adapter_module
from .loader import load_suite
from .report import format_report_human, format_report_json
from .schema import SchemaValidationError, parse_suite, validate_suite_object
from .scorer import DEFAULT_FORBIDDEN_ACTION_WEIGHT, DEFAULT_PASS_THRESHOLD, score_suite
from .types import (
    AgentAction,
    AgentAdapter,
    AgentObservation,
    ForbiddenActionViolation,
    ScoreReport,
    SuccessCriterion,
    SuiteConfig,
    TaskDefinition,
    TaskResult,
)

try:
    # Single source of truth: read the version from the installed distribution's
    # own metadata (built from pyproject.toml's `version` field) instead of a
    # hardcoded string here. A hardcoded copy previously drifted out of sync
    # with the version actually published to PyPI, so `deskcert --version`
    # reported a stale, incorrect version on live installs.
    __version__ = _pkg_version("deskcert-cli")
except PackageNotFoundError:  # pragma: no cover - local checkout without installed metadata
    __version__ = "0.0.0-dev"

__all__ = [
    "DEFAULT_FORBIDDEN_ACTION_WEIGHT",
    "DEFAULT_PASS_THRESHOLD",
    "AgentAction",
    "AgentAdapter",
    "AgentObservation",
    "ForbiddenActionViolation",
    "SchemaValidationError",
    "ScoreReport",
    "ScriptedAdapter",
    "SuccessCriterion",
    "SuiteConfig",
    "TaskDefinition",
    "TaskResult",
    "__version__",
    "format_report_human",
    "format_report_json",
    "load_adapter_module",
    "load_suite",
    "parse_suite",
    "score_suite",
    "validate_suite_object",
]
