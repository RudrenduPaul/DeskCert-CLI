// Library entry point -- import DeskCert's core pieces directly instead of
// shelling out to the CLI, e.g. to embed the scorer in a custom test harness.
export * from "./core/types.js";
export { parseSuite, validateSuiteObject, getSchemaJson, SchemaValidationError } from "./core/schema.js";
export { loadSuite } from "./core/loader.js";
export { runSuite } from "./core/runner.js";
export { scoreSuite, DEFAULT_PASS_THRESHOLD, DEFAULT_FORBIDDEN_ACTION_WEIGHT } from "./core/scorer.js";
export { ScriptedAdapter, loadAdapterModule } from "./core/adapter.js";
export { formatReportHuman, formatReportJson } from "./core/report.js";
export { runCommand, exitCodeFor, EXIT_PASS, EXIT_BELOW_THRESHOLD, EXIT_FORBIDDEN_VIOLATION } from "./commands/run.js";
export { ciCommand } from "./commands/ci.js";
