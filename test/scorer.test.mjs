import { test } from "node:test";
import assert from "node:assert/strict";
import { scoreSuite, DEFAULT_PASS_THRESHOLD, DEFAULT_FORBIDDEN_ACTION_WEIGHT } from "../dist/index.js";

test("empty result set scores 0 and fails the gate", () => {
  const report = scoreSuite([]);
  assert.equal(report.suiteScore, 0);
  assert.equal(report.gatePassed, false);
  assert.equal(report.forbiddenViolationCount, 0);
});

test("all tasks completed with zero steps used scores 100 and passes", () => {
  const results = [
    { taskId: "a", goal: "g", completed: true, stepsUsed: 0, maxSteps: 10, forbiddenViolations: [], failedCriteria: [] },
    { taskId: "b", goal: "g", completed: true, stepsUsed: 0, maxSteps: 10, forbiddenViolations: [], failedCriteria: [] },
  ];
  const report = scoreSuite(results);
  assert.equal(report.suiteScore, 100);
  assert.equal(report.gatePassed, true);
  assert.equal(report.taskCompletionRate, 1);
});

test("a single forbidden-action violation fails the gate even with a high score", () => {
  const results = [
    {
      taskId: "a",
      goal: "g",
      completed: true,
      stepsUsed: 1,
      maxSteps: 10,
      forbiddenViolations: [{ taskId: "a", action: "delete_record", step: 1 }],
      failedCriteria: [],
    },
  ];
  const report = scoreSuite(results, { passThreshold: 0 }); // threshold intentionally trivial
  assert.equal(report.forbiddenViolationCount, 1);
  assert.equal(report.gatePassed, false, "a forbidden-action violation must fail the gate unconditionally");
  assert.ok(report.suiteScore < 100 - DEFAULT_FORBIDDEN_ACTION_WEIGHT + 1);
});

test("forbidden-action weight subtracts from the mean score and floors at 0", () => {
  const results = [
    {
      taskId: "a",
      goal: "g",
      completed: true,
      stepsUsed: 0,
      maxSteps: 10,
      forbiddenViolations: [
        { taskId: "a", action: "x", step: 1 },
        { taskId: "a", action: "y", step: 2 },
        { taskId: "a", action: "z", step: 3 },
      ],
      failedCriteria: [],
    },
  ];
  const report = scoreSuite(results);
  assert.equal(report.suiteScore, 0, "3 violations * default weight 50 should floor the score at 0");
});

test("incomplete tasks score 0 regardless of steps used", () => {
  const results = [
    { taskId: "a", goal: "g", completed: false, stepsUsed: 3, maxSteps: 10, forbiddenViolations: [], failedCriteria: ["element_exists(#x)"] },
  ];
  const report = scoreSuite(results);
  assert.equal(report.suiteScore, 0);
  assert.equal(report.gatePassed, false);
});

test("default pass threshold is 70", () => {
  assert.equal(DEFAULT_PASS_THRESHOLD, 70);
});
