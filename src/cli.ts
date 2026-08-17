#!/usr/bin/env node
import { Command } from "commander";
import { runInit } from "./commands/init.js";
import { runCommand, exitCodeFor } from "./commands/run.js";
import { ciCommand } from "./commands/ci.js";
import { formatReportHuman, formatReportJson } from "./core/report.js";
import { startStdioServer } from "./mcp/server.js";
import { VERSION } from "./version.js";

const program = new Command();

program
  .name("deskcert")
  .description(
    "Certify whether an AI agent is safe to operate your internal web application " +
      "before production rollout. Author a task suite in YAML against your own app, " +
      "run it with Playwright, and gate CI/CD on a forbidden-action safety score."
  )
  .version(VERSION);

program
  .command("init")
  .description("Scaffold a runnable example task suite and fixture app into a directory")
  .option("-d, --dir <path>", "target directory", "./deskcert-suite")
  .option("-f, --force", "overwrite the target directory if it already exists", false)
  .action((opts: { dir: string; force: boolean }) => {
    try {
      const { dir, filesWritten } = runInit({ dir: opts.dir, force: opts.force });
      console.log(`Scaffolded a DeskCert task suite in ${dir}`);
      for (const f of filesWritten) console.log(`  ${f}`);
      console.log("\nNext steps:");
      console.log(`  node ${dir}/fixture-app/server.mjs &`);
      console.log(`  deskcert run --agent scripted --suite ${dir}`);
    } catch (err) {
      console.error(`Error: ${(err as Error).message}`);
      process.exitCode = 1;
    }
  });

program
  .command("run")
  .description("Run a task suite against a target application and print a Capability & Safety Score")
  .requiredOption("-s, --suite <path>", "path to a task-suite directory or a single suite YAML file")
  .option("-a, --agent <name>", "adapter name: 'scripted' for the bundled reference adapter", "scripted")
  .option("--adapter-module <path>", "path to a custom AgentAdapter module (required unless --agent scripted)")
  .option("--json", "print the report as structured JSON instead of human-readable text", false)
  .option("--headless <bool>", "run the browser headless (true/false)", "true")
  .action(async (opts: { suite: string; agent: string; adapterModule?: string; json: boolean; headless: string }) => {
    try {
      const report = await runCommand({
        suite: opts.suite,
        agent: opts.agent,
        adapterModule: opts.adapterModule,
        headless: opts.headless !== "false",
      });
      console.log(opts.json ? formatReportJson(report) : formatReportHuman(report));
      process.exitCode = exitCodeFor(report);
    } catch (err) {
      console.error(`Error: ${(err as Error).message}`);
      process.exitCode = 1;
    }
  });

program
  .command("ci")
  .description("Run a task suite in CI mode: exit 0 pass / 1 below threshold / 2 forbidden-action violation")
  .requiredOption("-s, --suite <path>", "path to a task-suite directory or a single suite YAML file")
  .option("-a, --agent <name>", "adapter name: 'scripted' for the bundled reference adapter", "scripted")
  .option("--adapter-module <path>", "path to a custom AgentAdapter module (required unless --agent scripted)")
  .option("--json", "print the report as structured JSON instead of human-readable text", false)
  .action(async (opts: { suite: string; agent: string; adapterModule?: string; json: boolean }) => {
    try {
      const { report, exitCode } = await ciCommand({
        suite: opts.suite,
        agent: opts.agent,
        adapterModule: opts.adapterModule,
        json: opts.json,
        headless: true,
      });
      console.log(report);
      process.exitCode = exitCode;
    } catch (err) {
      console.error(`Error: ${(err as Error).message}`);
      process.exitCode = 1;
    }
  });

program
  .command("mcp")
  .description("Start the DeskCert MCP server over stdio, exposing run_suite for agent-native invocation")
  .action(async () => {
    await startStdioServer();
  });

program.parseAsync(process.argv);
