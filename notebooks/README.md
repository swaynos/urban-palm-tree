# Notebook Execution Plan

This directory is the primary workspace for the current buildout phase.

Current focus: **data audit, SAM 3 feasibility spike, and auto-labeling pipeline** for `ball`, `player`, and `user-controlled-player` detection.

See `SPEC.md` for full spec and acceptance criteria. Dataset working artifacts go to `/Volumes/X9 Pro/Dev` — not in this repo.

---

## Active Notebook Order

1. `01_dataset_inventory.ipynb`: Inventories public datasets and aligns annotation schemas. Reference only for future phases.
2. `02_collate_tactical_dataset.ipynb`: **Primary active notebook.** SAM 3 auto-labeling pipeline — audit, feasibility spike, SAM 3 vs. manual labels comparison, and YOLO dataset construction. See SPEC.md §2–4 for deliverables.

---

## Deferred Notebooks (TacticalVisionNet)

Notebooks `03–06` implement the TacticalVisionNet multi-task network. They are **parked** until a real labeled dataset exists from the pipeline above. Do not execute them in the current phase.

- `03_train_tactical_vision.ipynb`: TVN training loop (deferred)
- `04_eval_tactical_vision.ipynb`: TVN evaluation (deferred)
- `05_realtime_inference_gating.ipynb`: Fast-path gameplay gating (deferred)
- `06_derived_tactical_features.ipynb`: Derived temporal features (deferred)

---

## Legacy Notebooks (`old/`)

Notebooks in `old/` are legacy/experimental. They can be referenced but do not define the current pipeline.

Particularly useful legacy notebooks for the current phase:
- `old/rush-detection-model-infer-to-label-studio.ipynb` — prior YOLO-assisted labeling loop (Label Studio)
- `old/crop-screenshots.ipynb` — 1920×1080 normalization utilities
- `old/screenshot-to-jpg.ipynb` — PNG→JPEG conversion

---

## Coordination Notes

- Spec and schema decisions live in `SPEC.md` and `PROJECT.md`.
- Dataset artifacts live on `/Volumes/X9 Pro/Dev` — never in the repo.
- `src/` expansion is deferred during this phase.
