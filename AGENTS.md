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
- `notebooks/`: active notebook pipeline (current: `01_dataset_inventory`, `02_collate_tactical_dataset` for SAM3 auto-labeling; `03–06` deferred TVN work; `old/` legacy notebooks)
- `tests/`: pytest suite for core runtime behaviors and utility modules
- `PROJECT.md`: long-range project plan and architecture direction
- `SPEC.md`: current buildout spec — audit + SAM 3 auto-labeling → YOLO distillation (TacticalVisionNet deferred)
- `DATA.md`: public dataset inventory and priority ordering (reserved for future phases)
- `artifacts/` (ignored): local training outputs, reports, predictions, and dataset extracts
- `/Volumes/X9 Pro/Dev` (external, gitignored): ALL dataset working artifacts (frames, labels, YOLO datasets, audit reports, SAM 3 outputs)

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

## NotebookLM (data-scientist workspace)

The primary NotebookLM for this project is registered in the local library as **"urban-palm-tree Data Science Notebook"**:

- URL: `https://notebooklm.google.com/notebook/de8dcffd-3940-4e36-9e59-5f3d2a30ff23`
- Library ID: `urban-palm-tree-data-science-n`

Use this notebook when working on: TacticalVisionNet architecture decisions, dataset curation and label schema questions, training pipeline design, tactical feature extraction approaches, and SAM 3 auto-labeling design. Query it via the `notebooklm_ask_question` tool before making significant model or data decisions.

## Extra references

Read these only when relevant:

- `README.md`: project overview, current setup, and contributor guidance
- `PROJECT.md`: end-to-end tactical CV/control roadmap
- `SPEC.md`: current buildout scope and acceptance criteria
- `DATA.md`: public dataset links and intended task mapping
