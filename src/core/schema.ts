import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import path from "node:path";
import Ajv, { type ErrorObject } from "ajv";
import addFormats from "ajv-formats";
import yaml from "js-yaml";
import type { SuiteConfig } from "./types.js";

const __dirname = path.dirname(fileURLToPath(import.meta.url));

// Packaged location (dist/core -> ../../schema) and source location
// (src/core -> ../../schema) resolve to the same schema file either way.
const SCHEMA_PATH = path.resolve(__dirname, "..", "..", "schema", "task-suite.schema.json");

const ajv = new Ajv({ allErrors: true, strict: false });
addFormats(ajv);
const schemaJson = JSON.parse(readFileSync(SCHEMA_PATH, "utf-8"));
const validateFn = ajv.compile(schemaJson);

export class SchemaValidationError extends Error {
  constructor(public readonly errors: ErrorObject[]) {
    super(
      `Task suite failed schema validation:\n${errors
        .map((e) => `  - ${e.instancePath || "(root)"} ${e.message}`)
        .join("\n")}`
    );
    this.name = "SchemaValidationError";
  }
}

/** Validate an already-parsed suite object (used by the directory loader). Throws on any violation. */
export function validateSuiteObject(raw: unknown): SuiteConfig {
  if (!validateFn(raw)) {
    throw new SchemaValidationError(validateFn.errors ?? []);
  }
  const suite = raw as SuiteConfig;
  const ids = new Set<string>();
  for (const task of suite.tasks) {
    if (ids.has(task.id)) {
      throw new SchemaValidationError([
        {
          instancePath: `/tasks`,
          message: `duplicate task id "${task.id}"`,
        } as ErrorObject,
      ]);
    }
    ids.add(task.id);
  }
  return suite;
}

/** Parse and validate a single-file task-suite YAML string. Throws SchemaValidationError on any violation. */
export function parseSuite(yamlText: string): SuiteConfig {
  return validateSuiteObject(yaml.load(yamlText));
}

export function getSchemaJson(): unknown {
  return schemaJson;
}
