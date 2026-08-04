import { test } from "node:test";
import assert from "node:assert/strict";
import { createServer } from "node:http";
import { readFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { loadSuite, runSuite, scoreSuite, ScriptedAdapter } from "../dist/index.js";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const FIXTURE_HTML = path.resolve(__dirname, "..", "examples", "example-suite", "fixture-app", "index.html");
const SUITE_DIR = path.resolve(__dirname, "..", "examples", "example-suite");

async function withFixtureServer(fn) {
  const html = await readFile(FIXTURE_HTML, "utf-8");
  const server = createServer((_req, res) => {
    res.writeHead(200, { "content-type": "text/html" });
    res.end(html);
  });
  await new Promise((resolve) => server.listen(4310, "127.0.0.1", resolve));
  try {
    await fn();
  } finally {
    await new Promise((resolve) => server.close(resolve));
  }
}

test(
  "end-to-end fixture run: forbidden-action detection has no false negative and tanks the score",
  { timeout: 30000 },
  async () => {
    await withFixtureServer(async () => {
      const suite = loadSuite(SUITE_DIR);
      const results = await runSuite(suite, {
        headless: true,
        adapterFactory: (task) => ScriptedAdapter.forTask(task),
      });

      const deleteTask = results.find((r) => r.taskId === "attempt-delete");
      assert.ok(deleteTask, "attempt-delete task result must be present");
      assert.equal(
        deleteTask.forbiddenViolations.length,
        1,
        "the scripted click on the forbidden delete_record action must be caught -- zero false negatives"
      );
      assert.equal(deleteTask.forbiddenViolations[0].action, "delete_record");
      assert.equal(deleteTask.forbiddenViolations[0].step, 1);

      // The harness must have blocked the action, not merely logged it --
      // the fixture page never renders its "deleted" banner.
      assert.deepEqual(deleteTask.failedCriteria, []);

      const report = scoreSuite(results, {
        passThreshold: suite.pass_threshold,
        forbiddenActionWeight: suite.forbidden_action_weight,
      });
      assert.equal(report.gatePassed, false, "gate must fail whenever any forbidden-action violation occurred");
      assert.equal(report.forbiddenViolationCount, 1);
    });
  }
);

test("view-dashboard task completes cleanly with zero violations", { timeout: 30000 }, async () => {
  await withFixtureServer(async () => {
    const suite = loadSuite(SUITE_DIR);
    const results = await runSuite(suite, {
      headless: true,
      adapterFactory: (task) => ScriptedAdapter.forTask(task),
    });
    const dashboardTask = results.find((r) => r.taskId === "view-dashboard");
    assert.ok(dashboardTask);
    assert.equal(dashboardTask.completed, true);
    assert.equal(dashboardTask.forbiddenViolations.length, 0);
  });
});
