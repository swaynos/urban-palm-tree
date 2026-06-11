# SPEC.md — First Buildout (Notebook-First Data + Transfer Learning Pipeline)

## Development Environment & Poetry Migration

### Current State
This project is paused. It currently uses Poetry via `pyproject.toml` and `poetry.lock`, with a large ML-heavy Poetry-managed virtualenv cached outside the repository.

### Resume Direction
When work resumes, migrate the project away from Poetry and use a raw Python `venv` plus `pip` workflow instead.

### Migration Requirements
- Preserve the dependency intent from `pyproject.toml` and `poetry.lock` before removing Poetry-specific configuration.
- Create a local virtual environment with Python `>=3.10,<3.11` unless the runtime target is deliberately changed.
- Replace Poetry install/run instructions with direct `python -m venv`, `python -m pip install`, and plain Python command usage.
- Prefer a `requirements.txt` or split `requirements*.txt` files if pinned dependencies are still needed.
- Review heavy ML dependencies such as TensorFlow, Torch, Ultralytics, OpenCV, and related scientific packages before reinstalling them.
- Do not recreate or depend on Poetry-managed virtualenvs under `~/Library/Caches/pypoetry`.

### Cleanup Note
The old Poetry cache and virtualenv are disposable and may be deleted. They should be recreated only through the new `venv` + `pip` workflow.

---

## Problem Statement

The project has a large local corpus of EA FC gameplay screenshots (`screenshots/`) and a set of public labeled datasets (`DATA.md`), but no first-buildout execution contract for producing a high-accuracy, reusable combined recordset.

The immediate need is to stand up a notebook-first pipeline that transfers learning from public datasets into FC-domain predictions on local screenshots, validates those predictions automatically, and outputs a merged canonical dataset for downstream tactical modeling.

## Goals

1. Establish a reproducible notebook execution flow for first-buildout dataset production.
2. Train task-specific teacher models from public datasets (minimap crop, minimap objects, pitch keypoints, FC26 HUD/objects).
3. Generate pseudo-label predictions for local screenshots without requiring human tagging at scale.
4. Add an automated validation layer (including optional OpenAI validation) to increase precision before promotion.
5. Export one combined canonical recordset with provenance and confidence metadata.

## Non-Goals

1. Expanding runtime/game-loop behavior in `src/` for this phase.
2. Building final temporal tactical models or controller sequence learning.
3. Requiring exhaustive manual annotation of local screenshots.
4. Finalizing long-term production infrastructure (deployment/serving/CI pipelines).

## Constraints

### Technical

- Work is notebook-first in `./notebooks/`.
- Existing package workflow currently uses Poetry; commands below use Poetry until migration occurs.
- `screenshots/` is treated as local working data and is not required to be committed.

### Data/Quality

- Project must not depend on human tagging for scaling.
- Transfer from public datasets must be explicit and measurable.
- Each promoted label must retain provenance: source model, confidence, and validation status.

### Compatibility

- Must align with roadmap and schema direction in `PROJECT.md`.
- Must align dataset priorities in `DATA.md`.

### Timeline (First Buildout)

- Deliverables in this spec are scoped to first-buildout only: teacher training, screenshot inference, validation, and combined recordset creation.

## Functional Requirements

### FR-1: Notebook orchestration and ordering

The active notebook flow must follow the numbered execution plan documented in `notebooks/README.md`.

**Acceptance Criteria**

1. `notebooks/README.md` lists the active ordered notebook sequence from `01_...` through `08_...`.
2. New first-buildout work is added to the numbered sequence, not legacy notebooks.

---

### FR-2: Public dataset inventory + class mapping

A notebook stage must produce a machine-readable inventory of datasets and class mappings used for teacher training.

**Acceptance Criteria**

1. A file exists at `artifacts/reports/dataset_inventory.json`.
2. Inventory includes, at minimum, entries for:
   - FC24 Minimap Dataset
   - FIFA Minimap Dataset
   - Soccer Field Keypoints Detection
   - Football Field Keypoints Dataset
   - FC26 Roboflow Dataset
3. Inventory records normalized internal target labels for each relevant class set.

---

### FR-3: Teacher model training outputs

Notebook stages must train (or load/fine-tune) teacher models and persist model artifacts and training summaries.

**Acceptance Criteria**

1. Model artifact directories exist:
   - `artifacts/models/minimap_crop/`
   - `artifacts/models/minimap_objects/`
   - `artifacts/models/pitch_keypoints/`
   - `artifacts/models/fc26_hud_objects/`
2. Each model directory contains a run summary JSON with:
   - model identifier/version
   - source datasets used
   - date/time
   - key validation metrics (at least one metric per model)

---

### FR-4: Screenshot inference without manual-tag dependency

Notebook inference stage must run teacher models on local screenshots and generate structured prediction records.

**Acceptance Criteria**

1. Predictions file exists at `artifacts/predictions/screenshot_predictions.jsonl`.
2. Each record contains at minimum:
   - `frame_id`
   - `image`
   - `width`, `height`
   - task predictions (where available)
   - per-prediction `confidence`
   - `model_name` (or equivalent provenance field)
3. The stage runs without requiring a human-labeled local screenshot set.

---

### FR-5: Automated validation + promotion gating

Notebook validation stage must score and gate predictions for promotion into the combined recordset.

**Acceptance Criteria**

1. Validation report exists at `artifacts/validation/validation_report.json`.
2. Report includes:
   - total predictions evaluated
   - accepted vs rejected counts
   - rejection reasons (e.g., low confidence, structural inconsistency)
3. If OpenAI validation is enabled, report includes an `openai_validation` summary section.

---

### FR-6: Combined canonical recordset export

Notebook merge stage must output a unified canonical dataset for downstream use.

**Acceptance Criteria**

1. Combined recordset exists at `artifacts/combined/combined_recordset.jsonl`.
2. Every record includes:
   - core frame metadata (`frame_id`, `image`, dimensions)
   - available perception sections (`minimap`, `field`, `hud`, `main_view`) with `null` allowed where unavailable
   - provenance/quality metadata (`source_model`, `confidence`, `validation_status`)
3. A merge summary exists at `artifacts/reports/merge_summary.json` with total merged records and section completeness stats.

## Verification Plan

Run these commands from repo root.

1. Verify required planning/docs files:

```bash
ls PROJECT.md DATA.md SPEC.md notebooks/README.md
```

2. Execute dataset inventory notebook:

```bash
poetry run jupyter nbconvert --to notebook --execute "notebooks/01_dataset_inventory.ipynb" --output "01_dataset_inventory.executed.ipynb" --output-dir "artifacts/reports"
```

3. Execute teacher training notebooks:

```bash
poetry run jupyter nbconvert --to notebook --execute "notebooks/02_train_minimap_crop_teacher.ipynb" --output "02_train_minimap_crop_teacher.executed.ipynb" --output-dir "artifacts/reports"
poetry run jupyter nbconvert --to notebook --execute "notebooks/03_train_minimap_objects_teacher.ipynb" --output "03_train_minimap_objects_teacher.executed.ipynb" --output-dir "artifacts/reports"
poetry run jupyter nbconvert --to notebook --execute "notebooks/04_train_pitch_keypoints_teacher.ipynb" --output "04_train_pitch_keypoints_teacher.executed.ipynb" --output-dir "artifacts/reports"
poetry run jupyter nbconvert --to notebook --execute "notebooks/05_train_fc26_hud_objects_teacher.ipynb" --output "05_train_fc26_hud_objects_teacher.executed.ipynb" --output-dir "artifacts/reports"
```

4. Execute inference, validation, and merge notebooks:

```bash
poetry run jupyter nbconvert --to notebook --execute "notebooks/06_infer_screenshots.ipynb" --output "06_infer_screenshots.executed.ipynb" --output-dir "artifacts/reports"
poetry run jupyter nbconvert --to notebook --execute "notebooks/07_validate_predictions.ipynb" --output "07_validate_predictions.executed.ipynb" --output-dir "artifacts/reports"
poetry run jupyter nbconvert --to notebook --execute "notebooks/08_build_combined_recordset.ipynb" --output "08_build_combined_recordset.executed.ipynb" --output-dir "artifacts/reports"
```

5. Verify expected artifacts exist:

```bash
ls artifacts/reports/dataset_inventory.json artifacts/validation/validation_report.json artifacts/combined/combined_recordset.jsonl artifacts/reports/merge_summary.json
ls artifacts/models/minimap_crop artifacts/models/minimap_objects artifacts/models/pitch_keypoints artifacts/models/fc26_hud_objects
```

## Detailed Implementation Plan (Checklist)

### A. Spec + notebook coordination

- [ ] Confirm `SPEC.md` and `PROJECT.md` are aligned on first-buildout scope.
- [ ] Keep active execution order in `notebooks/README.md` as the coordination source.

### B. Notebook scaffolding and shared conventions

- [ ] Add a standard config cell in each active notebook (paths, run_id, seed, thresholds).
- [ ] Standardize artifact output paths under `artifacts/models`, `artifacts/predictions`, `artifacts/validation`, `artifacts/combined`, and `artifacts/reports`.
- [ ] Add end-of-notebook run summary output (JSON) for each stage.

### C. Dataset inventory + mapping

- [ ] Implement dataset inventory notebook to produce `artifacts/reports/dataset_inventory.json`.
- [ ] Define normalized label mappings from public datasets to canonical internal labels.

### D. Teacher training stages

- [ ] Implement minimap crop teacher training notebook output + metrics summary.
- [ ] Implement minimap object teacher training notebook output + metrics summary.
- [ ] Implement pitch keypoint teacher training notebook output + metrics summary.
- [ ] Implement FC26 HUD/object teacher training notebook output + metrics summary.

### E. Screenshot inference stage

- [ ] Implement screenshot inference notebook to read local `screenshots/*.jpg` and emit `artifacts/predictions/screenshot_predictions.jsonl`.
- [ ] Include per-prediction provenance + confidence metadata.

### F. Validation + gating

- [ ] Implement deterministic validation checks (schema, geometry, threshold gates).
- [ ] Implement optional OpenAI validation pass for uncertain/ambiguous predictions.
- [ ] Emit `artifacts/validation/validation_report.json` with acceptance/rejection accounting.

### G. Combined recordset build

- [ ] Merge validated outputs into canonical records with nullable sections.
- [ ] Emit `artifacts/combined/combined_recordset.jsonl`.
- [ ] Emit `artifacts/reports/merge_summary.json` with completeness and provenance stats.

### H. Final review for first buildout

- [ ] Confirm all acceptance criteria are met via verification commands.
- [ ] Document first-buildout quality baseline metrics and next-iteration priorities.

## Key Assumptions

1. Local `screenshots/` contains sufficient FC gameplay diversity for domain adaptation.
2. Public dataset labels are reliable enough to bootstrap strong teacher models.
3. Notebook execution is the intended delivery mechanism for first buildout.
4. Poetry remains the temporary command runner until migration.

## Open Risks

1. Domain shift between public datasets and local FC screenshots may reduce early precision.
2. OpenAI validation can improve quality but may add cost/latency and requires careful prompting/guardrails.
3. Inconsistent label semantics across source datasets can introduce merge noise if mappings are not strict.
4. Notebook drift (ad hoc edits) can hurt reproducibility unless output conventions are enforced.
