# Model Build Summary - 2026-05-01

## Completed Work

- Created and used project-local Python environment via pyenv: `urban-palm-tree-311` (Python 3.11.10).
- Verified GPU acceleration on local hardware:
  - GPU: `NVIDIA GeForce RTX 4050 Laptop GPU`
  - CUDA available in PyTorch: `True`
- Downloaded available Kaggle datasets and extracted into `artifacts/datasets/`.
- Prepared YOLO training configs and dataset YAML files.
- Trained first-buildout detection models on local GPU.

## Model Outputs (Local Paths)

- Minimap crop model:
  - `/home/bendy/.pyenv/runs/detect/artifacts/models/minimap_crop`
  - Best weights: `/home/bendy/.pyenv/runs/detect/artifacts/models/minimap_crop/weights/best.pt`

- Pitch keypoints proxy model:
  - `/home/bendy/.pyenv/runs/detect/artifacts/models/pitch_keypoints`
  - Best weights: `/home/bendy/.pyenv/runs/detect/artifacts/models/pitch_keypoints/weights/best.pt`

- FC26 HUD/object proxy model (trained from FC25 object dataset):
  - `/home/bendy/.pyenv/runs/detect/artifacts/models/fc26_hud_objects_proxy`
  - Best weights: `/home/bendy/.pyenv/runs/detect/artifacts/models/fc26_hud_objects_proxy/weights/best.pt`

- Minimap objects proxy model (trained from player/object dataset):
  - `/home/bendy/.pyenv/runs/detect/artifacts/models/minimap_objects_proxy-3`
  - Best weights: `/home/bendy/.pyenv/runs/detect/artifacts/models/minimap_objects_proxy-3/weights/best.pt`

## Dataset/Config Artifacts Used

- Synthetic minimap crop dataset config:
  - `/home/bendy/Git/urban-palm-tree/artifacts/datasets/minimap_crop_synth/data.yaml`

- Field keypoint dataset config:
  - `/home/bendy/Git/urban-palm-tree/artifacts/datasets/football-field-keypoints/field_yolo/data.yaml`

- FC25 object dataset config:
  - `/home/bendy/Git/urban-palm-tree/artifacts/datasets/fc25-objects/data.yaml`

- Player/object dataset config:
  - `/home/bendy/Git/urban-palm-tree/artifacts/datasets/football-players/football-players-detection/data.yaml`

## Notes

- A direct Roboflow dataset pull for FC24 minimap required a valid API key in this environment, so those specific downloads were blocked.
- Model build-out proceeded using available datasets and completed successfully for all planned first-pass proxy/teacher runs.
- Detailed command history and outcomes are tracked in:
  - `/home/bendy/Git/urban-palm-tree/progress.txt`

## Screenshot Policy (Agreed)

- `./screenshots/` is raw gameplay data and should be treated as an inference/evaluation target early on.
- Early-stage training should prioritize labeled public datasets (Kaggle/Roboflow) to establish stronger base models.
- The correct sequence is:
  - train on labeled public datasets,
  - validate on held-out public data,
  - run inference on `./screenshots/` samples to measure transfer quality.
- Direct early training on raw `./screenshots/` is considered a strategy mistake and should be avoided until baseline transfer performance is acceptable.
