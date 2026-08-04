import type { AgentAction, AgentAdapter, AgentObservation, TaskDefinition } from "./types.js";

/**
 * Reference adapter: replays a task's `reference_actions` list verbatim, one per
 * step. This is what `deskcert run --agent scripted` uses -- it exists so the
 * bundled example suite (and every fixture test / CI run of this repo) works with
 * zero external agent or API key. It is NOT an AI agent: it does not look at the
 * screenshot or accessibility tree, it just plays back a fixed script.
 *
 * A real agent integration implements the same `AgentAdapter` interface and reads
 * `observation.screenshotBase64` / `observation.axTree` to decide the next action
 * -- see docs/agent-adapter.md for a worked example wiring this up to an LLM.
 */
export class ScriptedAdapter implements AgentAdapter {
  name = "scripted";
  private cursor = 0;

  constructor(private readonly actions: AgentAction[]) {}

  static forTask(task: TaskDefinition): ScriptedAdapter {
    return new ScriptedAdapter(task.reference_actions ?? []);
  }

  async nextAction(_observation: AgentObservation): Promise<AgentAction> {
    if (this.cursor >= this.actions.length) {
      return { type: "finish" };
    }
    const action = this.actions[this.cursor];
    this.cursor += 1;
    return action;
  }
}

/**
 * Loads a user-supplied adapter module by path. The module's default export must
 * be a class implementing AgentAdapter (constructor takes no required args, or the
 * caller wires its own construction) -- this is the extension point for a real
 * agent: Claude computer-use, LangGraph, CrewAI, or an in-house loop.
 */
export async function loadAdapterModule(modulePath: string): Promise<AgentAdapter> {
  const resolved = modulePath.startsWith(".") || modulePath.startsWith("/")
    ? modulePath
    : `./${modulePath}`;
  const mod = await import(resolved);
  const AdapterClass = mod.default ?? mod.Adapter;
  if (!AdapterClass) {
    throw new Error(
      `Adapter module "${modulePath}" must have a default export implementing AgentAdapter`
    );
  }
  const instance = new AdapterClass();
  if (typeof instance.nextAction !== "function") {
    throw new Error(`Adapter module "${modulePath}" default export does not implement nextAction()`);
  }
  return instance as AgentAdapter;
}
