"""Shared dataclasses mirroring src/core/types.ts field-for-field. Keep these two
files in sync by hand -- a schema field added to one language without the other
is a shippable bug, not a documentation footnote (see repo CLAUDE.md).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class SuccessCriterion:
    type: str  # "element_exists" | "element_not_exists" | "url_contains" | "text_contains"
    selector: Optional[str] = None
    value: Optional[str] = None


@dataclass
class AgentAction:
    type: str  # "click" | "fill" | "navigate" | "read" | "finish"
    name: Optional[str] = None
    selector: Optional[str] = None
    value: Optional[str] = None
    url: Optional[str] = None


@dataclass
class TaskDefinition:
    id: str
    goal: str
    target_url: str
    allowed_actions: List[str]
    forbidden_actions: List[str]
    success_criteria: List[SuccessCriterion]
    max_steps: int
    reference_actions: List[AgentAction] = field(default_factory=list)


@dataclass
class SuiteConfig:
    version: int
    tasks: List[TaskDefinition]
    pass_threshold: Optional[float] = None
    forbidden_action_weight: Optional[float] = None


@dataclass
class AgentObservation:
    goal: str
    target_url: str
    allowed_actions: List[str]
    forbidden_actions: List[str]
    step_index: int
    max_steps: int
    screenshot_base64: str
    ax_tree: str
    url: str


class AgentAdapter(ABC):
    """The contract every agent integration implements: given the current
    observation, return the next action. DeskCert never calls a model API
    directly -- this is the one interface a caller wraps around Claude
    computer-use, LangGraph, CrewAI, or an in-house agent loop.
    """

    name: str = "adapter"

    @abstractmethod
    async def next_action(self, observation: AgentObservation) -> AgentAction: ...


@dataclass
class ForbiddenActionViolation:
    task_id: str
    action: str
    step: int


@dataclass
class TaskResult:
    task_id: str
    goal: str
    completed: bool
    steps_used: int
    max_steps: int
    forbidden_violations: List[ForbiddenActionViolation]
    failed_criteria: List[str]
    error: Optional[str] = None


@dataclass
class ScoreReport:
    suite_score: float
    task_completion_rate: float
    forbidden_violation_count: int
    pass_threshold: float
    gate_passed: bool
    task_results: List[TaskResult]
    generated_at: str
