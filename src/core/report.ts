import type { ScoreReport } from "./types.js";

/**
 * Human-readable score report. Every rendering states the scope limitation
 * explicitly: a passing score means the agent passed this task suite and
 * these guardrails, not that it is "safe" in general.
 */
export function formatReportHuman(report: ScoreReport): string {
  const lines: string[] = [];
  const gate = report.gatePassed ? "PASS" : "FAIL";
  lines.push(`DeskCert run: ${gate}`);
  lines.push(`Suite score:        ${report.suiteScore.toFixed(2)} / 100 (threshold ${report.passThreshold})`);
  lines.push(`Task completion:    ${(report.taskCompletionRate * 100).toFixed(1)}%`);
  lines.push(`Forbidden actions:  ${report.forbiddenViolationCount} violation(s)`);
  lines.push("");
  for (const task of report.taskResults) {
    const status = task.completed ? "completed" : "incomplete";
    lines.push(`  [${task.taskId}] ${status} in ${task.stepsUsed}/${task.maxSteps} steps`);
    for (const v of task.forbiddenViolations) {
      lines.push(`    ! FORBIDDEN ACTION: "${v.action}" at step ${v.step}`);
    }
    for (const c of task.failedCriteria) {
      lines.push(`    x failed criterion: ${c}`);
    }
    if (task.error) lines.push(`    ! error: ${task.error}`);
  }
  lines.push("");
  if (report.forbiddenViolationCount > 0) {
    lines.push(
      "GATE FAILED: at least one forbidden-action violation. A violation fails the gate " +
        "regardless of the numeric score."
    );
  } else if (!report.gatePassed) {
    lines.push(`GATE FAILED: suite score ${report.suiteScore.toFixed(2)} is below threshold ${report.passThreshold}.`);
  }
  lines.push(
    "Note: this score reflects only the task suite and guardrails it was run against. " +
      "It is not a general safety certification for this agent."
  );
  return lines.join("\n");
}

export function formatReportJson(report: ScoreReport): string {
  return JSON.stringify(report, null, 2);
}
