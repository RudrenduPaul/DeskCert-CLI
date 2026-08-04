"""`deskcert run` / `deskcert ci` shared execution logic. Mirrors
src/commands/run.ts and src/commands/ci.ts, including the exit-code contract:
0 pass, 1 below threshold, 2 forbidden-action violation.
"""

from __future__ import annotations

from typing import Optional

from .adapter import ScriptedAdapter, load_adapter_module
from .loader import load_suite
from .runner import run_suite
from .scorer import score_suite
from .types import ScoreReport, TaskDefinition

EXIT_PASS = 0
EXIT_BELOW_THRESHOLD = 1
EXIT_FORBIDDEN_VIOLATION = 2


def exit_code_for(report: ScoreReport) -> int:
    if report.forbidden_violation_count > 0:
        return EXIT_FORBIDDEN_VIOLATION
    if not report.gate_passed:
        return EXIT_BELOW_THRESHOLD
    return EXIT_PASS


async def run_command(
    suite_path: str, agent: str, adapter_module: Optional[str] = None, headless: bool = True
) -> ScoreReport:
    suite = load_suite(suite_path)

    custom_adapter = None
    if agent == "scripted":
        pass
    elif adapter_module:
        custom_adapter = load_adapter_module(adapter_module)
    else:
        raise ValueError(
            f'Unknown agent "{agent}". Use --agent scripted for the bundled reference adapter, '
            f"or --agent <name> --adapter-module <path> to wire up a real agent."
        )

    def adapter_factory(task: TaskDefinition):
        return custom_adapter if custom_adapter is not None else ScriptedAdapter.for_task(task)

    results = await run_suite(suite, adapter_factory, headless=headless)
    return score_suite(
        results,
        pass_threshold=suite.pass_threshold,
        forbidden_action_weight=suite.forbidden_action_weight,
    )
