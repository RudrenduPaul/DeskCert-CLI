import { readFileSync, readdirSync, existsSync, statSync } from "node:fs";
import path from "node:path";
import yaml from "js-yaml";
import { validateSuiteObject } from "./schema.js";
import type { SuiteConfig, TaskDefinition } from "./types.js";

interface SuiteManifest {
  version: number;
  pass_threshold?: number;
  forbidden_action_weight?: number;
  tasks_dir?: string;
}

/**
 * Loads a task suite from either:
 *  - a directory containing `deskcert.config.yaml` + a `tasks/` folder of
 *    one-task-per-file YAML definitions (the layout `deskcert init` scaffolds), or
 *  - a single YAML file holding the full suite (`version` + inline `tasks: [...]`).
 */
export function loadSuite(suitePath: string): SuiteConfig {
  const resolved = path.resolve(suitePath);
  if (!existsSync(resolved)) {
    throw new Error(`Suite path "${resolved}" does not exist`);
  }
  if (statSync(resolved).isDirectory()) {
    return loadDirectorySuite(resolved);
  }
  const text = readFileSync(resolved, "utf-8");
  return validateSuiteObject(yaml.load(text));
}

function loadDirectorySuite(dir: string): SuiteConfig {
  const manifestPath = path.join(dir, "deskcert.config.yaml");
  if (!existsSync(manifestPath)) {
    throw new Error(`No deskcert.config.yaml found in "${dir}"`);
  }
  const manifest = yaml.load(readFileSync(manifestPath, "utf-8")) as SuiteManifest;
  const tasksDir = path.join(dir, manifest.tasks_dir ?? "tasks");
  if (!existsSync(tasksDir)) {
    throw new Error(`Tasks directory "${tasksDir}" does not exist`);
  }
  const tasks: TaskDefinition[] = readdirSync(tasksDir)
    .filter((f) => f.endsWith(".yaml") || f.endsWith(".yml"))
    .sort()
    .map((f) => yaml.load(readFileSync(path.join(tasksDir, f), "utf-8")) as TaskDefinition);

  const suiteObject: Record<string, unknown> = { version: manifest.version, tasks };
  if (manifest.pass_threshold !== undefined) suiteObject.pass_threshold = manifest.pass_threshold;
  if (manifest.forbidden_action_weight !== undefined) {
    suiteObject.forbidden_action_weight = manifest.forbidden_action_weight;
  }
  return validateSuiteObject(suiteObject);
}
