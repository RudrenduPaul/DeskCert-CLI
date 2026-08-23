# Changelog

All notable changes to this project are documented in this file.

## [0.1.5] - 2026-08-10

### Added

- **MCP registry ownership proof**: added `<!-- mcp-name: io.github.RudrenduPaul/deskcert -->`
  to the top of `README.md` and `python/README.md`, and a `mcpName` field to
  `package.json`, so the [MCP Registry](https://github.com/modelcontextprotocol/registry)
  can verify this repository's ownership of the `io.github.RudrenduPaul/deskcert`
  server name.
- **`python/server.json`**: new MCP registry server manifest describing the
  `deskcert mcp` entry point (PyPI package `deskcert-cli`, invoked via `uvx`
  with a `stdio` transport), so the server can be published to the MCP
  Registry.

Note: this version bump was made in the source repository but has not yet
been published to npm as of this changelog entry (PyPI has since caught up
to 0.1.5). Published-package versions can lag the repository; always check
the registries for the actual live version.

## [0.1.4] - 2026-08-08

### Fixed

- **npm package**: `deskcert --version` and the MCP server's reported version
  were hardcoded to `"0.1.0"` in `src/cli.ts` and `src/mcp/server.ts`, so a
  clean `npm install -g deskcert-cli@latest` (actual published version 0.1.3)
  reported the wrong version. Both now read the version from `package.json`
  at runtime via a shared `src/version.ts` helper, so the reported version can
  no longer drift from the published package version.
- **PyPI package**: `deskcert --version` was hardcoded as `__version__ = "0.1.2"`
  in `python/deskcert/__init__.py`, independently of `pyproject.toml`'s
  `version` field. The version actually published to PyPI as 0.1.3 shipped
  with a stale `__version__` of `0.1.1`. `__version__` is now read from the
  installed distribution's own metadata via `importlib.metadata.version()`,
  with a `"0.0.0-dev"` fallback for an uninstalled local checkout, so it can
  no longer diverge from the version PyPI actually published.

All other documented functionality (`init`, `run`, `ci`, `mcp`,
`serve-fixture`) was verified working correctly on a clean install from both
registries before and after this fix; only the `--version` output was wrong.
