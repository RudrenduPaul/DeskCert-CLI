"""DeskCert command-line entry point (Python implementation). Real subcommands
mirroring the TypeScript CLI: init, run, ci, mcp, plus a Python-only
serve-fixture helper for environments without Node installed.
"""

from __future__ import annotations

import asyncio
import sys

import click

from . import __version__
from .init_cmd import run_init
from .report import format_report_human, format_report_json
from .run_cmd import exit_code_for, run_command


@click.group()
@click.version_option(version=__version__, prog_name="deskcert")
def cli() -> None:
    """Certify whether an AI agent is safe to operate your internal web application
    before production rollout. Author a task suite in YAML against your own app,
    run it with Playwright, and gate CI/CD on a forbidden-action safety score.
    """


@cli.command()
@click.option("-d", "--dir", "target_dir", default="./deskcert-suite", help="target directory")
@click.option("-f", "--force", is_flag=True, default=False, help="overwrite the target directory if it already exists")
def init(target_dir: str, force: bool) -> None:
    """Scaffold a runnable example task suite and fixture app into a directory."""
    try:
        files = run_init(target_dir, force=force)
    except FileExistsError as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)
    click.echo(f"Scaffolded a DeskCert task suite in {target_dir}")
    for f in files:
        click.echo(f"  {f}")
    click.echo("\nNext steps:")
    click.echo(f"  deskcert serve-fixture --dir {target_dir}/fixture-app &")
    click.echo(f"  deskcert run --agent scripted --suite {target_dir}")


def _run_options(fn):
    suite_help = "path to a task-suite directory or a single suite YAML file"
    agent_help = "adapter name: 'scripted' for the bundled reference adapter"
    adapter_module_help = "path to a custom AgentAdapter module (required unless --agent scripted)"
    json_help = "print the report as structured JSON instead of human-readable text"
    fn = click.option("-s", "--suite", required=True, help=suite_help)(fn)
    fn = click.option("-a", "--agent", default="scripted", help=agent_help)(fn)
    fn = click.option("--adapter-module", default=None, help=adapter_module_help)(fn)
    fn = click.option("--json", "as_json", is_flag=True, default=False, help=json_help)(fn)
    return fn


@cli.command()
@_run_options
@click.option("--headless/--headed", default=True, help="run the browser headless")
def run(suite: str, agent: str, adapter_module: str, as_json: bool, headless: bool) -> None:
    """Run a task suite against a target application and print a Capability & Safety Score."""
    try:
        report = asyncio.run(run_command(suite, agent, adapter_module, headless=headless))
    except Exception as exc:  # noqa: BLE001 -- surfaced to the user as a CLI error, not a traceback
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)
    click.echo(format_report_json(report) if as_json else format_report_human(report))
    sys.exit(exit_code_for(report))


@cli.command()
@_run_options
def ci(suite: str, agent: str, adapter_module: str, as_json: bool) -> None:
    """Run a task suite in CI mode: exit 0 pass / 1 below threshold / 2 forbidden-action violation."""
    try:
        report = asyncio.run(run_command(suite, agent, adapter_module, headless=True))
    except Exception as exc:  # noqa: BLE001
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)
    click.echo(format_report_json(report) if as_json else format_report_human(report))
    sys.exit(exit_code_for(report))


@cli.command()
def mcp() -> None:
    """Start the DeskCert MCP server over stdio, exposing run_suite for agent-native invocation."""
    from .mcp_server import main as mcp_main

    mcp_main()


@cli.command(name="serve-fixture")
@click.option("--port", default=4310, help="port to serve the bundled fixture app on")
@click.option("--dir", "_dir", default=None, help="unused, kept for CLI symmetry with the Node fixture server")
def serve_fixture(port: int, _dir: str) -> None:
    """Serve the bundled fixture app locally (Python-only, no Node required)."""
    from .fixture_server import serve_fixture_app

    serve_fixture_app(port=port)


def main() -> None:
    cli()


if __name__ == "__main__":
    main()
