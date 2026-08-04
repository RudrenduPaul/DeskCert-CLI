import { test } from "node:test";
import assert from "node:assert/strict";
import { runSuite, ScriptedAdapter } from "../dist/index.js";

// Regression test for the CSO-flagged finding: a library caller can construct a
// SuiteConfig object directly (bypassing parseSuite/loadSuite's schema check
// entirely), so the runtime navigation guard in runner.ts must reject unsafe
// schemes on its own, not rely on schema validation as the only gate.

test("runSuite refuses to navigate to a non-http(s) target_url even when schema validation is bypassed", async () => {
  const suite = {
    version: 1,
    tasks: [
      {
        id: "evil",
        goal: "read a local file",
        target_url: "file:///etc/passwd",
        allowed_actions: ["read"],
        forbidden_actions: [],
        max_steps: 1,
        success_criteria: [{ type: "url_contains", value: "x" }],
        reference_actions: [{ type: "finish" }],
      },
    ],
  };

  const results = await runSuite(suite, {
    headless: true,
    adapterFactory: (task) => ScriptedAdapter.forTask(task),
  });

  assert.equal(results.length, 1);
  assert.equal(results[0].completed, false);
  assert.match(results[0].error ?? "", /non-http\(s\)/);
});
