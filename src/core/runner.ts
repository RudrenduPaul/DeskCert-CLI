import { chromium, type Browser, type Page } from "playwright";
import type {
  AgentAction,
  AgentAdapter,
  ForbiddenActionViolation,
  SuccessCriterion,
  SuiteConfig,
  TaskDefinition,
  TaskResult,
} from "./types.js";

export interface RunOptions {
  headless?: boolean;
  adapterFactory: (task: TaskDefinition) => AgentAdapter;
}

/**
 * Only http(s) navigation is allowed. This is enforced here at runtime, not just
 * in the JSON Schema, because an agent adapter's returned "navigate" action is
 * live agent output -- not schema-validated data -- and a buggy or malicious
 * adapter could otherwise send Playwright to file:// (local file disclosure via
 * the screenshot observation) or javascript: (arbitrary script execution in the
 * page context).
 */
function isSafeNavigationUrl(url: string): boolean {
  try {
    const parsed = new URL(url);
    return parsed.protocol === "http:" || parsed.protocol === "https:";
  } catch {
    return false;
  }
}

/** Runs every task in a suite sequentially, each in its own isolated browser context. */
export async function runSuite(suite: SuiteConfig, options: RunOptions): Promise<TaskResult[]> {
  const browser = await chromium.launch({ headless: options.headless ?? true });
  try {
    const results: TaskResult[] = [];
    for (const task of suite.tasks) {
      const adapter = options.adapterFactory(task);
      results.push(await runTask(browser, task, adapter));
    }
    return results;
  } finally {
    await browser.close();
  }
}

async function runTask(browser: Browser, task: TaskDefinition, adapter: AgentAdapter): Promise<TaskResult> {
  const context = await browser.newContext();
  const page = await context.newPage();
  const violations: ForbiddenActionViolation[] = [];
  let stepsUsed = 0;
  let error: string | undefined;

  try {
    if (!isSafeNavigationUrl(task.target_url)) {
      throw new Error(`Refusing to navigate to non-http(s) target_url: "${task.target_url}"`);
    }
    await page.goto(task.target_url, { waitUntil: "domcontentloaded" });

    for (let step = 0; step < task.max_steps; step += 1) {
      stepsUsed = step + 1;
      const observation = await buildObservation(page, task, step);
      const action = await adapter.nextAction(observation);
      const actionName = action.name ?? action.type;

      if (task.forbidden_actions.includes(actionName)) {
        violations.push({ taskId: task.id, action: actionName, step: stepsUsed });
        // The harness enforces the guardrail itself: a forbidden action is
        // recorded but never executed against the real page.
        continue;
      }

      if (action.type === "finish") break;
      await applyAction(page, action);
    }
  } catch (err) {
    error = err instanceof Error ? err.message : String(err);
  }

  const failedCriteria = await evaluateSuccessCriteria(page, task.success_criteria).catch(
    () => task.success_criteria.map((c) => JSON.stringify(c))
  );

  await context.close();

  return {
    taskId: task.id,
    goal: task.goal,
    completed: failedCriteria.length === 0 && !error,
    stepsUsed,
    maxSteps: task.max_steps,
    forbiddenViolations: violations,
    failedCriteria,
    error,
  };
}

async function buildObservation(page: Page, task: TaskDefinition, stepIndex: number) {
  const screenshotBuffer = await page.screenshot().catch(() => Buffer.alloc(0));
  const axTree = await page
    .locator("body")
    .innerText()
    .catch(() => "");
  return {
    goal: task.goal,
    targetUrl: task.target_url,
    allowedActions: task.allowed_actions,
    forbiddenActions: task.forbidden_actions,
    stepIndex,
    maxSteps: task.max_steps,
    screenshotBase64: screenshotBuffer.toString("base64"),
    axTree: axTree.slice(0, 4000),
    url: page.url(),
  };
}

async function applyAction(page: Page, action: AgentAction): Promise<void> {
  switch (action.type) {
    case "click":
      if (action.selector) await page.locator(action.selector).first().click({ timeout: 5000 });
      return;
    case "fill":
      if (action.selector && action.value !== undefined) {
        await page.locator(action.selector).first().fill(action.value, { timeout: 5000 });
      }
      return;
    case "navigate":
      if (action.url && isSafeNavigationUrl(action.url)) {
        await page.goto(action.url, { waitUntil: "domcontentloaded" });
      }
      return;
    case "read":
    case "finish":
      return;
    default:
      return;
  }
}

async function evaluateSuccessCriteria(
  page: Page,
  criteria: SuccessCriterion[]
): Promise<string[]> {
  const failed: string[] = [];
  for (const criterion of criteria) {
    const ok = await checkCriterion(page, criterion);
    if (!ok) failed.push(describeCriterion(criterion));
  }
  return failed;
}

async function checkCriterion(page: Page, criterion: SuccessCriterion): Promise<boolean> {
  switch (criterion.type) {
    case "element_exists":
      return (await page.locator(criterion.selector).count()) > 0;
    case "element_not_exists":
      return (await page.locator(criterion.selector).count()) === 0;
    case "url_contains":
      return page.url().includes(criterion.value);
    case "text_contains": {
      const text = await page.locator(criterion.selector).first().innerText().catch(() => "");
      return text.includes(criterion.value);
    }
    default:
      return false;
  }
}

function describeCriterion(criterion: SuccessCriterion): string {
  switch (criterion.type) {
    case "element_exists":
      return `element_exists(${criterion.selector})`;
    case "element_not_exists":
      return `element_not_exists(${criterion.selector})`;
    case "url_contains":
      return `url_contains(${criterion.value})`;
    case "text_contains":
      return `text_contains(${criterion.selector}, ${criterion.value})`;
  }
}
