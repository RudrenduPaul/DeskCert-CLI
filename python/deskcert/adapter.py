"""Reference agent adapter and the custom-adapter-module loading extension
point. Mirrors src/core/adapter.ts.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import List

from .types import AgentAction, AgentAdapter, AgentObservation, TaskDefinition


class ScriptedAdapter(AgentAdapter):
    """Replays a task's `reference_actions` list verbatim, one per step. Used by
    `deskcert run --agent scripted` -- this is what makes the bundled example
    suite (and every fixture test / CI run of this repo) work with zero
    external agent or API key. It is NOT an AI agent: it never reads the
    screenshot or accessibility tree, it just plays back a fixed script.

    A real agent integration implements the same AgentAdapter interface and
    reads observation.screenshot_base64 / observation.ax_tree to decide the
    next action -- see docs/agent-adapter.md for a worked example.
    """

    name = "scripted"

    def __init__(self, actions: List[AgentAction]):
        self._actions = actions
        self._cursor = 0

    @classmethod
    def for_task(cls, task: TaskDefinition) -> ScriptedAdapter:
        return cls(list(task.reference_actions))

    async def next_action(self, observation: AgentObservation) -> AgentAction:
        if self._cursor >= len(self._actions):
            return AgentAction(type="finish")
        action = self._actions[self._cursor]
        self._cursor += 1
        return action


def load_adapter_module(module_path: str) -> AgentAdapter:
    """Loads a user-supplied adapter module by file path. The module must define
    an `Adapter` class implementing AgentAdapter -- the extension point for a
    real agent: Claude computer-use, LangGraph, CrewAI, or an in-house loop.
    """
    resolved = Path(module_path).resolve()
    if not resolved.exists():
        raise FileNotFoundError(f'Adapter module "{module_path}" does not exist')

    spec = importlib.util.spec_from_file_location(f"deskcert_adapter_{resolved.stem}", resolved)
    if spec is None or spec.loader is None:
        raise ImportError(f'Could not load adapter module "{module_path}"')
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)

    adapter_class = getattr(module, "Adapter", None)
    if adapter_class is None:
        raise ImportError(f'Adapter module "{module_path}" must define an `Adapter` class implementing AgentAdapter')
    instance = adapter_class()
    if not hasattr(instance, "next_action"):
        raise TypeError(f'Adapter module "{module_path}" Adapter class does not implement next_action()')
    return instance
