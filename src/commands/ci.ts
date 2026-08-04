import { runCommand, exitCodeFor, type RunCommandOptions } from "./run.js";
import { formatReportHuman, formatReportJson } from "../core/report.js";

export interface CiCommandOptions extends RunCommandOptions {
  json?: boolean;
}

/**
 * Same execution as `run`, packaged for CI: prints a single report and returns
 * the exit code the caller's shell should use (0 pass, 1 below threshold,
 * 2 forbidden-action violation) -- see docs/ci.md and the bundled GitHub Action.
 */
export async function ciCommand(options: CiCommandOptions): Promise<{ report: string; exitCode: number }> {
  const report = await runCommand(options);
  const exitCode = exitCodeFor(report);
  const text = options.json ? formatReportJson(report) : formatReportHuman(report);
  return { report: text, exitCode };
}
