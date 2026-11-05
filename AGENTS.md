# AGENTS.md

This file provides guidance to agents when working with code in this repository.

## Project Overview

MCP-server for TM4J (Zephyr Scale) API built with FastMCP (stdio transport), Python 3.11+, `uv` package manager.

## Commands

```bash
# Install deps and run server
uv run tm4j-mcp

# Run tests (full suite / single file / single test)
uv run pytest
uv run pytest tests/test_config.py
uv run pytest tests/test_config.py::test_config_bearer_auth

# Lint / format / type-check
uv run ruff check .
uv run ruff format .
uv run mypy src/
```

## Code Style

- `from __future__ import annotations` on every file, full type hints, `strict = true` mypy
- Line length 120, Ruff lint/format, Python 3.11 target
- Intentional ignores: `BLE001` (broad Exception catch), `S110` (try/except/pass)
- Russian-language docstrings/comments throughout the project — preserve this convention

## Architecture (Non-Obvious)

- Single `AuthHandler` shared by `TM4JClient` and `JiraClient` — same credentials for both APIs
- Jira host defaults to `tm4j_host` unless `JIRA_HOST` env var overrides
- All tools extend `BaseTool` ([`src/tm4j_mcp/tools/base.py`](src/tm4j_mcp/tools/base.py)) which provides `response_wrapper()`, `resolve_owner()`, `_execute_with_steps()`
- Responses always include `step_status` via `StepTracker` ([`src/tm4j_mcp/utils/step_tracker.py`](src/tm4j_mcp/utils/step_tracker.py)) — check this field for progress
- `convert_to_markdown=true` param on tools triggers `MarkdownConverter` ([`src/tm4j_mcp/converters/markdown.py`](src/tm4j_mcp/converters/markdown.py))
- Retry via `tenacity` on `TM4JAPIError` only (not all HTTP errors) in `TM4JClient._request()`
- Config from `.env` file via `pydantic-settings`, case-insensitive env var matching

## Testing

- `pytest` + `pytest-asyncio` with `asyncio_mode = "auto"`, fixture loop scope = `"function"`
- Tests use `patch.dict(os.environ, ..., clear=True)` to isolate env vars
- Import path in tests: `from src.tm4j_mcp...` (not `from tm4j_mcp...`)
- `python_classes = ["test_*"]` — test classes must match this pattern (NOT default `Test*`)
