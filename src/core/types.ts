/**
 * Shared types for a DeskCert task suite: the task-definition format, agent
 * observations/actions, and the run/score output shapes. The Python package
 * mirrors this shape field-for-field so a fixture run scores identically in
 * both implementations (see test/parity.test.ts and python/tests/test_parity.py).
 */

export type SuccessCriterion =
  | { type: "element_exists"; selector: string }
  | { type: "element_not_exists"; selector: string }
  | { type: "url_contains"; value: string }
  | { type: "text_contains"; selector: string; value: string };

export interface TaskDefinition {
  id: string;
  goal: string;
  target_url: string;
  allowed_actions: string[];
  forbidden_actions: string[];
  success_criteria: SuccessCriterion[];
  max_steps: number;
  /** Optional fixed action script, consumed only by the built-in "scripted" adapter. */
  reference_actions?: AgentAction[];
}

export interface SuiteConfig {
  version: number;
  pass_threshold?: number;
  forbidden_action_weight?: number;
  tasks: TaskDefinition[];
}

export type AgentActionType = "click" | "fill" | "navigate" | "read" | "finish";

export interface AgentAction {
  type: AgentActionType;
  /** Name of the action for allow/forbid matching, e.g. "delete_record". Defaults to `type`. */
  name?: string;
  selector?: string;
  value?: string;
  url?: string;
}

export interface AgentObservation {
  goal: string;
  targetUrl: string;
  allowedActions: string[];
  forbiddenActions: string[];
  stepIndex: number;
  maxSteps: number;
  /** Base64 PNG screenshot of the current page state. */
  screenshotBase64: string;
  /** Simplified accessibility-tree-style text dump of the page. */
  axTree: string;
  url: string;
}

/**
 * The adapter contract every agent integration implements: given the current
 * observation, return the next action. This is the one interface a caller
 * needs to wrap around Claude computer-use, LangGraph, CrewAI, or an in-house
 * agent loop -- DeskCert never calls a model API directly.
 */
export interface AgentAdapter {
  name: string;
  nextAction(observation: AgentObservation): Promise<AgentAction>;
}

export interface ForbiddenActionViolation {
  taskId: string;
  action: string;
  step: number;
}

export interface TaskResult {
  taskId: string;
  goal: string;
  completed: boolean;
  stepsUsed: number;
  maxSteps: number;
  forbiddenViolations: ForbiddenActionViolation[];
  failedCriteria: string[];
  error?: string;
}

export interface ScoreReport {
  suiteScore: number;
  taskCompletionRate: number;
  forbiddenViolationCount: number;
  passThreshold: number;
  gatePassed: boolean;
  taskResults: TaskResult[];
  generatedAt: string;
}
