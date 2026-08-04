# Security Policy

## Reporting a vulnerability

Please open a GitHub issue at [RudrenduPaul/DeskCert-CLI/issues](https://github.com/RudrenduPaul/DeskCert-CLI/issues).

If the report involves a way to bypass the forbidden-action gate undetected, say so explicitly
in the title -- that is the class of bug this project treats as highest severity, since it
defeats the safety guarantee the whole tool exists to provide.

## Supported versions

Only the latest published release on npm (`deskcert-cli`) and PyPI (`deskcert-cli`) is
supported. Fixes land on `main` and ship in the next release; there is no backport policy for
older versions yet.

## Scope

In scope: the task-runner, the scorer (especially forbidden-action detection), the
task-definition schema validator, and the MCP server. Out of scope: vulnerabilities in the
target web application under test, or in an agent adapter you wrote yourself.
