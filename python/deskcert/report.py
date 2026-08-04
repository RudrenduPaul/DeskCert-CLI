"""Human-readable and JSON report formatting. Mirrors src/core/report.ts,
including the anti-sycophancy scope-limitation footer required by this repo's
CLAUDE.md: a passing score means the agent passed this task suite and these
guardrails, not that it is "safe" in general.
"""

from __future__ import annotations

import dataclasses
import json

from .types import ScoreReport


def format_report_human(report: ScoreReport) -> str:
    gate = "PASS" if report.gate_passed else "FAIL"
    lines = [
        f"DeskCert run — {gate}",
        f"Suite score:        {report.suite_score:.2f} / 100 (threshold {report.pass_threshold})",
        f"Task completion:    {report.task_completion_rate * 100:.1f}%",
        f"Forbidden actions:  {report.forbidden_violation_count} violation(s)",
        "",
    ]
    for task in report.task_results:
        status = "completed" if task.completed else "incomplete"
        lines.append(f"  [{task.task_id}] {status} in {task.steps_used}/{task.max_steps} steps")
        for v in task.forbidden_violations:
            lines.append(f'    ! FORBIDDEN ACTION: "{v.action}" at step {v.step}')
        for c in task.failed_criteria:
            lines.append(f"    x failed criterion: {c}")
        if task.error:
            lines.append(f"    ! error: {task.error}")
    lines.append("")
    if report.forbidden_violation_count > 0:
        lines.append(
            "GATE FAILED: at least one forbidden-action violation. A violation fails the gate "
            "regardless of the numeric score."
        )
    elif not report.gate_passed:
        lines.append(
            f"GATE FAILED: suite score {report.suite_score:.2f} is below threshold {report.pass_threshold}."
        )
    lines.append(
        "Note: this score reflects only the task suite and guardrails it was run against. "
        "It is not a general safety certification for this agent."
    )
    return "\n".join(lines)


def format_report_json(report: ScoreReport) -> str:
    return json.dumps(_to_camel_case_dict(report), indent=2)


def _to_camel_case_dict(obj):
    if dataclasses.is_dataclass(obj):
        return {_camel(k): _to_camel_case_dict(v) for k, v in dataclasses.asdict(obj).items()}
    if isinstance(obj, list):
        return [_to_camel_case_dict(v) for v in obj]
    if isinstance(obj, dict):
        return {_camel(k): _to_camel_case_dict(v) for k, v in obj.items()}
    return obj


def _camel(snake: str) -> str:
    head, *tail = snake.split("_")
    return head + "".join(w.capitalize() for w in tail)
