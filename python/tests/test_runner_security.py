"""Regression test for the CSO-flagged finding: a library caller can construct a
SuiteConfig directly (bypassing schema.validate_suite_object entirely), so the
runtime navigation guard in runner.py must reject unsafe schemes on its own.
Mirrors test/runner.security.test.mjs.
"""

import asyncio

from deskcert.adapter import ScriptedAdapter
from deskcert.runner import run_suite
from deskcert.types import AgentAction, SuccessCriterion, SuiteConfig, TaskDefinition


def test_run_suite_refuses_non_http_target_url_even_when_schema_is_bypassed():
    task = TaskDefinition(
        id="evil",
        goal="read a local file",
        target_url="file:///etc/passwd",
        allowed_actions=["read"],
        forbidden_actions=[],
        success_criteria=[SuccessCriterion(type="url_contains", value="x")],
        max_steps=1,
        reference_actions=[AgentAction(type="finish")],
    )
    suite = SuiteConfig(version=1, tasks=[task])

    results = asyncio.run(run_suite(suite, lambda t: ScriptedAdapter.for_task(t), headless=True))

    assert len(results) == 1
    assert results[0].completed is False
    assert "non-http(s)" in (results[0].error or "")
