import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";
import { runCommand, exitCodeFor } from "../commands/run.js";
import { formatReportJson } from "../core/report.js";

/**
 * DeskCert MCP server: exposes the same run/score capability the CLI has, so an
 * orchestrating agent (a deployment pipeline, another agent) can invoke DeskCert
 * programmatically instead of shelling out to `deskcert run`. Agent-native
 * surface required by this repo's Agent-Native Packaging Standard.
 */
export function createServer(): McpServer {
  const server = new McpServer({
    name: "deskcert",
    version: "0.1.0",
  });

  server.registerTool(
    "run_suite",
    {
      title: "Run a DeskCert task suite",
      description:
        "Runs every task in a DeskCert task suite against a target web application using the " +
        "bundled scripted reference adapter, and returns the Capability & Safety Score report " +
        "as JSON. A passing result means the agent (or, for the scripted adapter, the recorded " +
        "reference script) passed this specific task suite and its forbidden-action guardrails " +
        "-- it is not a general safety certification.",
      inputSchema: {
        suite: z.string().describe("Path to a task-suite directory or single suite YAML file"),
        agent: z.string().default("scripted").describe("Adapter name: 'scripted' for the bundled reference adapter"),
        adapterModule: z.string().optional().describe("Path to a custom AgentAdapter module (required unless agent is 'scripted')"),
      },
    },
    async ({ suite, agent, adapterModule }) => {
      const report = await runCommand({ suite, agent, adapterModule, headless: true });
      const exitCode = exitCodeFor(report);
      return {
        content: [{ type: "text", text: formatReportJson(report) }],
        isError: exitCode !== 0,
      };
    }
  );

  return server;
}

export async function startStdioServer(): Promise<void> {
  const server = createServer();
  const transport = new StdioServerTransport();
  await server.connect(transport);
}
