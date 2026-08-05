"""DeskCert: certify whether an AI agent is safe to operate your internal web
application before production rollout.

This package is a real, independent Python/Playwright implementation of the
task-runner and scorer -- not a subprocess wrapper around the TypeScript CLI.
Its scorer produces identical scores to the TypeScript package for the same
fixture run; see tests/test_parity.py.
"""

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

__version__ = "0.1.2"

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
