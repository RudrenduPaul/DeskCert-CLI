"""DeskCert MCP server (Python): exposes the same run/score capability the CLI
has, over stdio, so an orchestrating agent can invoke DeskCert programmatically.
Mirrors src/mcp/server.ts.
"""

from __future__ import annotations

from typing import Optional

from mcp.server.fastmcp import FastMCP

from .report import format_report_json
from .run_cmd import exit_code_for, run_command

mcp = FastMCP("deskcert")


@mcp.tool()
async def run_suite(suite: str, agent: str = "scripted", adapter_module: Optional[str] = None) -> str:
    """Run every task in a DeskCert task suite against a target web application
    and return the Capability & Safety Score report as JSON. A passing result
    means the agent (or, for the scripted adapter, the recorded reference
    script) passed this specific task suite and its forbidden-action
    guardrails -- it is not a general safety certification.
    """
    report = await run_command(suite, agent, adapter_module, headless=True)
    exit_code_for(report)  # computed for parity with the CLI; report carries gate_passed already
    return format_report_json(report)


def main() -> None:
    mcp.run(transport="stdio")
