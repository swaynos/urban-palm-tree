# urban-palm-tree

`urban-palm-tree` is an EA FC automation and research project that captures gameplay frames, infers game state, and issues controller actions.

The long-term direction is documented in `PROJECT.md`: move from frame perception to a structured tactical state, then to higher-level action selection and controller sequencing.

## Project Scope

- Current codebase: runtime frame capture, inference pipelines, game-state tracking, and controller/action orchestration.
- Long-term plan: `images -> structured state -> tactical intent -> controller commands`.
- Primary planning source: `PROJECT.md` (dataset strategy, schema direction, and phased milestones).

## Repository Layout

- `PROJECT.md` - project plan, milestones, schema direction, and model roadmap.
- `src/` - main application code.
  - `src/start.py` - async runtime entrypoint.
  - `src/inference/` - image and game-state inference steps.
  - `src/controllers/` - game flow and strategy controllers.
  - `src/handlers/` - capture, inference, and control loop handlers.
  - `src/game_state/` - game-state models and trackers.
  - `src/game_action/` - action definitions.
  - `src/utilities/` - platform, IO, config, and helper utilities.
- `tests/` - unit tests.
- `notebooks/` - training and data preparation experiments.

## Getting Started

Note: the project currently uses Poetry for dependency management and run commands. I plan to migrate away from Poetry in a future update; until that change lands, use the Poetry commands below.

1. Clone the repository:

```bash
git clone git@github.com:swaynos/urban-palm-tree.git
cd urban-palm-tree
```

2. Install dependencies (Python 3.10 required):

```bash
poetry install
```

3. Run the app runtime:

```bash
poetry run python src/start.py
```

4. Run tests:

```bash
poetry run pytest
```

## Contributor Guide

- Read `PROJECT.md` first to align contributions with the roadmap.
- Prefer focused pull requests tied to one phase or milestone.
- Add or update tests for behavior changes when practical.
- If you add new inference outputs, keep naming and structure consistent with existing game-state and inference modules.

Good first contribution areas:

- Inference pipeline quality and robustness improvements.
- Test coverage fixes and reliability updates.
- Dataset conversion and tooling that aligns with `PROJECT.md` phase priorities.
- Platform/runtime ergonomics in capture and control handlers.

## License

This project is licensed under the GNU General Public License v3.0.
