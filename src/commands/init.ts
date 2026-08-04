import { mkdirSync, existsSync, cpSync } from "node:fs";
import { fileURLToPath } from "node:url";
import path from "node:path";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const EXAMPLES_SRC = path.resolve(__dirname, "..", "..", "examples", "example-suite");

export interface InitOptions {
  dir: string;
  force?: boolean;
}

/** Scaffolds a runnable example task suite (plus the bundled fixture app) into `dir`. */
export function runInit(options: InitOptions): { dir: string; filesWritten: string[] } {
  const target = path.resolve(options.dir);
  if (existsSync(target) && !options.force) {
    throw new Error(`"${target}" already exists. Pass --force to overwrite.`);
  }
  mkdirSync(target, { recursive: true });
  cpSync(EXAMPLES_SRC, target, { recursive: true, force: true });
  return {
    dir: target,
    filesWritten: [
      "deskcert.config.yaml",
      "tasks/view-dashboard.yaml",
      "tasks/attempt-delete.yaml",
      "fixture-app/index.html",
      "fixture-app/server.mjs",
    ],
  };
}
