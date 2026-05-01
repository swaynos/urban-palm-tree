# Notebook Execution Plan (First Buildout)

This directory is the primary workspace for the first buildout.

For now, we are prioritizing:

1. transfer learning from public datasets,
2. inference over local `screenshots/` gameplay data,
3. automated validation and confidence filtering,
4. merged combined recordset generation.

`src/` expansion is intentionally deferred during this phase.

---

## Active Notebook Order

Use (or create/rename to) the following execution order for current work:

1. `01_dataset_inventory.ipynb`
2. `02_train_minimap_crop_teacher.ipynb`
3. `03_train_minimap_objects_teacher.ipynb`
4. `04_train_pitch_keypoints_teacher.ipynb`
5. `05_train_fc26_hud_objects_teacher.ipynb`
6. `06_infer_screenshots.ipynb`
7. `07_validate_predictions.ipynb`
8. `08_build_combined_recordset.ipynb`

If notebook names differ while work is in progress, keep this numbered flow as the source of truth.

---

## Legacy Notebooks

Existing notebooks in this folder that do not match the active numbered sequence are considered **legacy/experimental** for this phase.

- They can still be referenced when useful.
- They should not define the first-buildout pipeline.
- Prefer adding new work in the numbered sequence above.

---

## Coordination Notes

- Keep roadmap and schema decisions in `PROJECT.md` and `SPEC.md`.
- Keep notebook outputs focused on measurable model quality and dataset merge quality.
- Favor small, comparable experiments over broad refactors.
