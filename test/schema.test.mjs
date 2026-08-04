import { test } from "node:test";
import assert from "node:assert/strict";
import { parseSuite, SchemaValidationError } from "../dist/index.js";

const VALID_SUITE = `
version: 1
pass_threshold: 70
tasks:
  - id: task-one
    goal: "Do a benign thing"
    target_url: "http://localhost:4310/"
    allowed_actions: [read]
    forbidden_actions: [delete_record]
    max_steps: 5
    success_criteria:
      - type: element_exists
        selector: "#widget"
`;

test("a valid suite parses without throwing", () => {
  const suite = parseSuite(VALID_SUITE);
  assert.equal(suite.tasks.length, 1);
  assert.equal(suite.tasks[0].id, "task-one");
});

test("missing required field (max_steps) is rejected", () => {
  const bad = VALID_SUITE.replace("    max_steps: 5\n", "");
  assert.throws(() => parseSuite(bad), SchemaValidationError);
});

test("an unknown top-level field is rejected (additionalProperties: false)", () => {
  const bad = VALID_SUITE + "\nnot_a_real_field: true\n";
  assert.throws(() => parseSuite(bad), SchemaValidationError);
});

test("duplicate task ids across the suite are rejected", () => {
  const dup = `
version: 1
tasks:
  - id: same-id
    goal: "a"
    target_url: "http://localhost:4310/"
    allowed_actions: []
    forbidden_actions: []
    max_steps: 1
    success_criteria: [{ type: url_contains, value: "x" }]
  - id: same-id
    goal: "b"
    target_url: "http://localhost:4310/"
    allowed_actions: []
    forbidden_actions: []
    max_steps: 1
    success_criteria: [{ type: url_contains, value: "x" }]
`;
  assert.throws(() => parseSuite(dup), SchemaValidationError);
});

test("an invalid success_criteria type is rejected", () => {
  const bad = VALID_SUITE.replace("type: element_exists", "type: not_a_real_type");
  assert.throws(() => parseSuite(bad), SchemaValidationError);
});
