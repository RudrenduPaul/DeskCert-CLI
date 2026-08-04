# Contributing to DeskCert

Issues and pull requests are welcome.

## Development setup

TypeScript package:

```
npm install
npm run build
npx playwright install chromium
npm test
npm run lint
```

Python package:

```
cd python
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
playwright install chromium
pytest
ruff check deskcert tests
```

## Before opening a pull request

- `npm test` and `npm run lint` pass for the TypeScript package.
- `pytest` and `ruff check` pass for the Python package.
- If you change the task-definition schema, update
  [`schema/task-suite.schema.json`](schema/task-suite.schema.json) once (both languages read
  the same file) and update both `src/core/schema.ts` and `python/deskcert/schema.py` if the
  validation logic itself, not just the schema, needs to change.
- If you change the scoring formula, update both `src/core/scorer.ts` and
  `python/deskcert/scorer.py`, and confirm `python/tests/test_parity.py` still passes against
  a fresh `npm run build`. A score that diverges between the two packages is a bug, not a
  documentation footnote.
- Add a test for any bug fix. `test/*.test.mjs` for TypeScript, `python/tests/test_*.py` for
  Python.

## Reporting a security issue

Please open a GitHub issue. If the report involves a way to bypass the forbidden-action gate
undetected, say so explicitly in the title -- that's the class of bug this project treats as
highest severity.
