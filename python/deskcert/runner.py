"""Playwright-driven task runner. Mirrors src/core/runner.ts exactly: one
isolated browser context per task, the harness enforces the forbidden-action
guardrail itself (a forbidden action is recorded but never executed against
the real page), success criteria are evaluated after the step loop ends.
"""

from __future__ import annotations

import base64
from typing import Callable, List, Optional
from urllib.parse import urlparse

from playwright.async_api import Browser, Page, async_playwright

from .types import (
    AgentAction,
    AgentAdapter,
    AgentObservation,
    ForbiddenActionViolation,
    SuccessCriterion,
    SuiteConfig,
    TaskDefinition,
    TaskResult,
)

AdapterFactory = Callable[[TaskDefinition], AgentAdapter]


def _is_safe_navigation_url(url: str) -> bool:
    """Only http(s) navigation is allowed, enforced at runtime (not just in the
    JSON Schema) because an agent adapter's returned "navigate" action is live
    agent output, not schema-validated data. Mirrors src/core/runner.ts's
    isSafeNavigationUrl.
    """
    try:
        parsed = urlparse(url)
        return parsed.scheme in ("http", "https")
    except ValueError:
        return False


async def run_suite(suite: SuiteConfig, adapter_factory: AdapterFactory, headless: bool = True) -> List[TaskResult]:
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=headless)
        try:
            results = []
            for task in suite.tasks:
                adapter = adapter_factory(task)
                results.append(await _run_task(browser, task, adapter))
            return results
        finally:
            await browser.close()


async def _run_task(browser: Browser, task: TaskDefinition, adapter: AgentAdapter) -> TaskResult:
    context = await browser.new_context()
    page = await context.new_page()
    violations: List[ForbiddenActionViolation] = []
    steps_used = 0
    error: Optional[str] = None

    try:
        if not _is_safe_navigation_url(task.target_url):
            raise ValueError(f'Refusing to navigate to non-http(s) target_url: "{task.target_url}"')
        await page.goto(task.target_url, wait_until="domcontentloaded")

        for step in range(task.max_steps):
            steps_used = step + 1
            observation = await _build_observation(page, task, step)
            action = await adapter.next_action(observation)
            action_name = action.name or action.type

            if action_name in task.forbidden_actions:
                violations.append(ForbiddenActionViolation(task_id=task.id, action=action_name, step=steps_used))
                continue

            if action.type == "finish":
                break
            await _apply_action(page, action)
    except Exception as exc:  # noqa: BLE001 -- fixture/runner errors are recorded, not raised
        error = str(exc)

    try:
        failed_criteria = await _evaluate_success_criteria(page, task.success_criteria)
    except Exception:  # noqa: BLE001
        failed_criteria = [_describe_criterion(c) for c in task.success_criteria]

    await context.close()

    return TaskResult(
        task_id=task.id,
        goal=task.goal,
        completed=len(failed_criteria) == 0 and error is None,
        steps_used=steps_used,
        max_steps=task.max_steps,
        forbidden_violations=violations,
        failed_criteria=failed_criteria,
        error=error,
    )


async def _build_observation(page: Page, task: TaskDefinition, step_index: int) -> AgentObservation:
    try:
        screenshot_bytes = await page.screenshot()
    except Exception:  # noqa: BLE001
        screenshot_bytes = b""
    try:
        ax_tree = await page.locator("body").inner_text()
    except Exception:  # noqa: BLE001
        ax_tree = ""
    return AgentObservation(
        goal=task.goal,
        target_url=task.target_url,
        allowed_actions=task.allowed_actions,
        forbidden_actions=task.forbidden_actions,
        step_index=step_index,
        max_steps=task.max_steps,
        screenshot_base64=base64.b64encode(screenshot_bytes).decode("ascii"),
        ax_tree=ax_tree[:4000],
        url=page.url,
    )


async def _apply_action(page: Page, action: AgentAction) -> None:
    if action.type == "click" and action.selector:
        await page.locator(action.selector).first.click(timeout=5000)
    elif action.type == "fill" and action.selector and action.value is not None:
        await page.locator(action.selector).first.fill(action.value, timeout=5000)
    elif action.type == "navigate" and action.url and _is_safe_navigation_url(action.url):
        await page.goto(action.url, wait_until="domcontentloaded")
    # "read" and "finish" are no-ops here; "finish" is handled by the caller.


async def _evaluate_success_criteria(page: Page, criteria: List[SuccessCriterion]) -> List[str]:
    failed = []
    for criterion in criteria:
        if not await _check_criterion(page, criterion):
            failed.append(_describe_criterion(criterion))
    return failed


async def _check_criterion(page: Page, criterion: SuccessCriterion) -> bool:
    if criterion.type == "element_exists":
        return await page.locator(criterion.selector).count() > 0
    if criterion.type == "element_not_exists":
        return await page.locator(criterion.selector).count() == 0
    if criterion.type == "url_contains":
        return criterion.value in page.url
    if criterion.type == "text_contains":
        try:
            text = await page.locator(criterion.selector).first.inner_text()
        except Exception:  # noqa: BLE001
            text = ""
        return criterion.value in text
    return False


def _describe_criterion(criterion: SuccessCriterion) -> str:
    if criterion.type == "element_exists":
        return f"element_exists({criterion.selector})"
    if criterion.type == "element_not_exists":
        return f"element_not_exists({criterion.selector})"
    if criterion.type == "url_contains":
        return f"url_contains({criterion.value})"
    if criterion.type == "text_contains":
        return f"text_contains({criterion.selector}, {criterion.value})"
    return str(criterion)
