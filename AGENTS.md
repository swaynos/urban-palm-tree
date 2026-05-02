# Project Instructions

## Purpose

`urban-palm-tree` is an EA FC gameplay automation and computer-vision research repo. It captures gameplay frames, runs inference/model steps to estimate game state, and drives controller actions through strategy handlers. Current near-term focus is notebook-first model/data work (`PROJECT.md`, `SPEC.md`) rather than expanding runtime logic in `src/`. Do not break the async runtime loop in `src/start.py`, controller IO safety behavior, or existing game-state/strategy contracts used by tests.

## Stack

- Language: Python
- Runtime: CPython (3.10 in `pyproject.toml`; local model build has also used 3.11 via pyenv)
- Framework: Asyncio-based custom app architecture; Ultralytics/PyTorch/TensorFlow used for ML work
- Package manager: Poetry (current repo default; may be migrated later)
- Database: None
- Test framework: Pytest

## Commands

- Install: `poetry install`
- Dev server: `poetry run python src/start.py`
- Focused test: `poetry run pytest tests/test_game_control_handler.py -q`
- All tests: `poetry run pytest`
- Typecheck: `poetry run python -m py_compile src/**/*.py` (no dedicated typechecker configured)
- Lint: `poetry run pylint src` (pylint is included in dependencies)
- Build: `poetry run python -m compileall src`

## Repo map

- `src/`: runtime application code (capture, inference handlers, strategy/controllers, game-state, IO utilities)
- `notebooks/`: model/data experimentation pipeline for first buildout (active `01_...08_...` flow + `old/` legacy notebooks)
- `tests/`: pytest suite for core runtime behaviors and utility modules
- `PROJECT.md`: long-range project plan and architecture direction
- `SPEC.md`: first-buildout execution spec (notebook-first training/inference/validation workflow)
- `DATA.md`: public dataset inventory and priority ordering
- `artifacts/` (ignored): local training outputs, reports, predictions, and dataset extracts

## Architecture invariants

- Keep runtime orchestration asynchronous and non-blocking: `capture_image_handler`, `infer_image_handler`, and `controller_input_handler` run together via `asyncio.gather` in `src/start.py`.
- Preserve controller safety on shutdown: exit handling presses specific keys and sets `shared_data.exit_event`; do not remove this behavior without a safer replacement.
- Maintain modular game-flow boundaries: controllers decide flow/strategy; handlers execute loop work; inference steps should remain composable and not hardwire unrelated concerns.
- For current phase, prefer notebook/data/model work over invasive `src/` changes unless explicitly requested.

## Testing rules

- Tests live in `tests/`.
- Test files use `tests/test_*.py`.
- Use existing patterns/helpers from current tests (e.g., `tests/test_inference_step.py`, `tests/test_shared_object.py`) before introducing new scaffolding.
- For bug fixes, add a regression test when practical.

## High-risk areas

Be conservative when touching:

- controller IO and key-press behavior (`src/utilities/playstation_io.py`, `src/handlers/game_control_handler.py`)
- runtime shutdown/signal handling (`src/start.py`)
- shared concurrency/state primitives (`src/utilities/shared_thread_resources.py`)
- inference step chaining and decision order (`src/inference/inference_step.py`, pipeline modules)
- config/env loading used across runtime (`src/utilities/config.py`)

## Extra references

Read these only when relevant:

- `README.md`: project overview, current setup, and contributor guidance
- `PROJECT.md`: end-to-end tactical CV/control roadmap
- `SPEC.md`: first buildout scope and acceptance criteria
- `DATA.md`: public dataset links and intended task mapping
