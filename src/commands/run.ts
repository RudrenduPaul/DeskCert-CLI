import { loadSuite } from "../core/loader.js";
import { runSuite } from "../core/runner.js";
import { scoreSuite } from "../core/scorer.js";
import { ScriptedAdapter, loadAdapterModule } from "../core/adapter.js";
import type { AgentAdapter, ScoreReport, TaskDefinition } from "../core/types.js";

export interface RunCommandOptions {
  suite: string;
  agent: string;
  adapterModule?: string;
  headless?: boolean;
}

/** Exit code contract shared by `run` and `ci`: 0 pass, 1 below threshold, 2 forbidden-action violation. */
export const EXIT_PASS = 0;
export const EXIT_BELOW_THRESHOLD = 1;
export const EXIT_FORBIDDEN_VIOLATION = 2;

export function exitCodeFor(report: ScoreReport): number {
  if (report.forbiddenViolationCount > 0) return EXIT_FORBIDDEN_VIOLATION;
  if (!report.gatePassed) return EXIT_BELOW_THRESHOLD;
  return EXIT_PASS;
}

export async function runCommand(options: RunCommandOptions): Promise<ScoreReport> {
  const suite = loadSuite(options.suite);

  let customAdapter: AgentAdapter | undefined;
  if (options.agent === "scripted") {
    // built-in, constructed per task below
  } else if (options.adapterModule) {
    customAdapter = await loadAdapterModule(options.adapterModule);
  } else {
    throw new Error(
      `Unknown agent "${options.agent}". Use --agent scripted for the bundled reference ` +
        `adapter, or --agent <name> --adapter-module <path> to wire up a real agent.`
    );
  }

  const adapterFactory = (task: TaskDefinition): AgentAdapter =>
    customAdapter ?? ScriptedAdapter.forTask(task);

  const results = await runSuite(suite, {
    headless: options.headless ?? true,
    adapterFactory,
  });

  return scoreSuite(results, {
    passThreshold: suite.pass_threshold,
    forbiddenActionWeight: suite.forbidden_action_weight,
  });
}
