# SPEC.md — Dataset Bootstrap: Audit, SAM 3 Feasibility, and Auto-Labeling Pipeline

This specification defines the first executable buildout for EA FC in-match perception: **audit existing data and models**, **run feasibility spikes** (notably SAM 3 vs. existing manual labels), and from those findings produce a **truly meaningful labeled dataset** plus a **repeatable approach for adding new classes** (e.g. referee) in future iterations.

**TacticalVisionNet is explicitly deferred.** The previous spec (dual-branch ResNet multi-task network) is parked until a real labeled dataset exists. Its notebooks (`03–06`) are left untouched.

---

## 0. Operating Constraints (Read First)

### Storage — space is precious
- **All dataset working artifacts** (extracted frames, normalized images, SAM 3 labels, YOLO datasets, model outputs, reports) MUST be written under: **`/Volumes/X9 Pro/Dev`**.
- Do NOT write dataset artifacts into the repo or the system disk. The repo holds only notebooks, specs, and small reports/manifests.

### Source data — read-only
- **callisto** (`sftp://callisto/media/jpswaynos/HDD1/Shared/Documents/Projects/FC24` and `.../FC26`) and **OneDrive** (`.../FC-Project`) are **audit-only**: read and inventory, never write, move, or delete.
- The user intends to clean these repositories one day. Record observations (duplicates, junk, reorganization candidates) in a **Cleanup Notes** report — but take no destructive action.

### Ignore list
- `'/Users/jpswaynos/Library/CloudStorage/OneDrive-Personal/Dev/Projects/FC-Project/squad-battles detection'` — UI-element detection; noise for the early object-detection approach. Skip entirely.

---

## 1. Data & Artifact Sources to Audit

| # | Source | Location | Expected content | Access |
|---|---|---|---|---|
| 1 | Rush screenshots | `/Users/jpswaynos/Documents/Rush/2025-02-15` | Rush playthrough stills — good for player, ball, goal/goalie | Local |
| 2 | Rush model | `/Users/jpswaynos/Documents/Rush/fc25-rush.mk1.pt` | Trained YOLO; **classes unknown — must enumerate** | Local |
| 3 | FC-Project archive | `/Users/jpswaynos/Library/CloudStorage/OneDrive-Personal/Dev/Projects/FC-Project` | Many screenshots + prior models WITH manual labels | OneDrive (read-only) |
| 4 | FC-Project screenshots | `.../FC-Project/screenshots` | Bulk raw screenshots | OneDrive (read-only) |
| 5 | Rush video | `/Volumes/X9 Pro/PS5/CREATE/Video Clips/EA SPORTS FC 25/EA SPORTS FC 25_20250222040256.mp4` | Realtime Rush playthrough — sequential frames for SAM 3 video tracking | External drive |
| 6 | callisto FC24 | `sftp://callisto/media/jpswaynos/HDD1/Shared/Documents/Projects/FC24` | More screenshots (possibly duplicate sets) | SSH/SFTP (read-only) |
| 7 | callisto FC26 | `sftp://callisto/media/jpswaynos/HDD1/Shared/Documents/Projects/FC26` | More screenshots (possibly duplicate sets) | SSH/SFTP (read-only) |
| — | squad-battles detection | `.../FC-Project/squad-battles detection` | UI elements | **IGNORE** |

The audit run is expected to reach callisto via `ssh callisto` / sftp (assumes non-interactive auth works; if it does not, document as a blocker and continue with reachable sources).

---

## 2. First @autonomous Run — Deliverables

This run is **audit + feasibility + minimal proof-of-concept**. It does NOT build the full production dataset yet. Concrete deliverables, all written under `/Volumes/X9 Pro/Dev` (with small summary copies referenced from the repo):

1. **Data Inventory Report** (`audit/data_inventory.json` + readable `.md`):
   - Per source: path, reachable (y/n), file counts by type, resolution(s), rough size, sequential-vs-stills, duplicate-set observations.
2. **Model Inventory Report** (`audit/model_inventory.json`):
   - For `fc25-rush.mk1.pt` and any FC-Project models: enumerate **actual class names**, base architecture, input size, and any accompanying `dataset.yaml`/label files.
3. **Existing-Labels Inventory**:
   - Where manual labels exist, in what format (YOLO/COCO/VOC/Label Studio), which classes, approximate instance counts per class.
4. **SAM 3 Feasibility Spike Report** (`audit/sam3_spike.json` + `.md`):
   - SAM 3 installability/runnability finding (deps, weights, GPU/host; SAM 3.1 considered).
   - SAM 3 vs. existing manual labels comparison (see §4) on a sampled set.
   - Per-class verdict: adopt SAM 3 / keep manual / hybrid / needs fine-tuning.
5. **Minimal SAM 3 PoC**: SAM 3 run end-to-end on a small audited frame set producing YOLO-format labels for the reliable classes, saved to `/Volumes/X9 Pro/Dev/poc/`.
6. **Cleanup Notes** (`audit/cleanup_notes.md`): observations on callisto/OneDrive for future (non-destructive) cleanup.
7. **Proposed Class Schema** (`audit/proposed_schema.md`): the class list to commit to, derived from audit findings (see §3).
8. **Knowledge Gaps memo** (`audit/knowledge_gaps.md`): what we still need to learn after the audit (per Goal: "what knowledge do we still need").

---

## 3. Class Schema — Audit-Driven

The committed class list is **decided after the audit**, not pre-fixed. The audit enumerates which classes existing data/models already cover and where gaps are.

- **Likely core** (from Rush + FC-Project): `ball`, `player`, `user-controlled-player`, `goal`, `goalkeeper`. To be confirmed by what `fc25-rush.mk1.pt` and the manual labels actually contain.
- **Future-add test case:** `referee`. The schema and pipeline MUST be designed so a new class can be added quickly in a later iteration (Goal 2). The `proposed_schema.md` must include an explicit "how to add a new class" procedure validated conceptually against `referee`.
- **Label format:** YOLO normalized boxes (`class_id cx cy w h`).

---

## 4. SAM 3 vs. Existing Labels — Comparison Protocol

When existing manual labels are available for audited frames, SAM 3 is compared against them quantitatively (grounded in the SAM 3 paper's own methodology; data scientist consult 2026-06-11).

### 4.1 Metrics
- **Primary: classification-gated F1 (cgF1)** = `100 × pmF1 × IL_MCC`:
  - **pmF1** (positive micro F1): localization quality via optimal bipartite matching between SAM 3 and manual boxes, averaged over **IoU thresholds 0.50→0.95 (step 0.05)**.
  - **IL_MCC** (image-level Matthews Correlation Coefficient): binary "is the class present in this frame" capability; robust to class imbalance.
- **Nested boxes** (e.g. active-player marker inside a player box): use **Intersection-over-Minimum (IoM)**, threshold 0.5, for NMS instead of IoU.
- SAM 3 predictions gated at **confidence > 0.5** to mimic downstream use.

### 4.2 Interpreting disagreements fairly
- Manual labels are imperfect. A high-confidence SAM 3 detection that the human missed is a **candidate for manual review**, NOT an automatic false positive.
- Isolate all high-confidence disagreements (SAM FP and FN vs. manual) and produce a small visual audit set so the human can judge whether SAM 3 caught a labeling error.

### 4.3 Spike sample size
- Sample enough frames to capture **≥150–200 instances of the rarest class (ball)** for statistical significance. (50–100 frames is noise for the ball.)
- Random sampling across sources/scenes (both teams, pitch zones, crowded/sparse).

### 4.4 Decision thresholds
- Estimate a human baseline (annotator agreement) where possible.
- **Adopt SAM 3 for a class** if its audited cgF1 reaches **~75–80% of the human baseline** for that class.
- Otherwise: keep manual / specialized YOLO for that class, or fine-tune SAM 3 on a small annotated set for that fine-grained concept.

### 4.5 Per-class breakdown (decoupled adoption)
- Evaluate strictly **per class**. Expected pattern: SAM 3 strong on `player`/`goalkeeper`; weaker zero-shot on `ball` (small) and `user-controlled-player` (UI-indicator, fine-grained).
- `user-controlled-player` evaluated via **visual exemplar prompting** (exemplar crop of the active-player indicator), not text.
- Outcome is a **hybrid adoption map**: SAM 3 for classes where cgF1 clears threshold; manual/YOLO/fine-tune for the rest.

---

## 5. Pipeline Design (Post-Audit, Forward-Looking)

The production pipeline is shaped by audit findings; this is the intended design.

1. **SAM 3 PCS** as primary labeler for adopted classes: text prompts for base classes, visual exemplar for `user-controlled-player`.
2. **SAM 3 video tracking** (memory bank, masklet propagation + suppression) on sequential sources (Rush video #5) for temporal consistency and missed-object recovery. No separate ByteTrack needed.
3. **Existing manual labels reused** for classes where they beat SAM 3.
4. **VLM fallback only** (SAM 3 Agent, Set-of-Marks on full uncropped image — never crops) for fine-grained classes SAM 3 can't isolate.
5. **YOLO student distillation** (`yolo11m`, reuse `src/inference/yolo_object_detector.py` + `parse_rush_model_results`) trained on the combined label set.
6. **Extensibility:** adding a class = define prompt/exemplar (or small fine-tune set) + extend schema + re-run labeling for that class. Documented procedure validated against `referee`.

---

## 6. Eval & Quality

- **Eval set:** small, hand-verified, **rotated** each cycle to avoid eval-set overfitting/leakage. Sized to capture ≥150 ball instances for meaningful ball metrics.
- **Metrics:** mAP@0.5 overall + per-class AP/recall; ball recall tracked as a trend (high variance at small N).
- **Provenance:** every training label carries source (`sam3_pcs` / `manual` / `fine_tuned` / `yolo`). No human relabeling at scale; manual labels are reused-as-found, not regenerated.

---

## 7. Verification (First Run)

```bash
# All artifacts land on the external drive
test -d "/Volumes/X9 Pro/Dev"

# Audit outputs exist
ls "/Volumes/X9 Pro/Dev/audit/data_inventory.json"
ls "/Volumes/X9 Pro/Dev/audit/model_inventory.json"
ls "/Volumes/X9 Pro/Dev/audit/sam3_spike.json"
ls "/Volumes/X9 Pro/Dev/audit/proposed_schema.md"
ls "/Volumes/X9 Pro/Dev/audit/knowledge_gaps.md"
ls "/Volumes/X9 Pro/Dev/audit/cleanup_notes.md"

# fc25-rush model class list was enumerated (non-empty)
test -s "/Volumes/X9 Pro/Dev/audit/model_inventory.json"

# Minimal SAM 3 PoC produced YOLO labels
ls "/Volumes/X9 Pro/Dev/poc/"
```

---

## 8. Acceptance Criteria (First Run)

### AC-1: Audit completeness
- Every source in §1 is either inventoried or explicitly recorded as unreachable with reason. The ignore-listed path is skipped.

### AC-2: Model class enumeration
- `fc25-rush.mk1.pt` actual class names are listed. Any FC-Project model's classes and label formats are listed.

### AC-3: SAM 3 feasibility verdict
- A clear installable/runnable finding for SAM 3 (or SAM 3.1) on this hardware.
- Per-class cgF1 comparison against existing manual labels (where labels exist), using §4 metrics, with a per-class adoption verdict.

### AC-4: Minimal PoC
- SAM 3 runs end-to-end on ≥1 audited sequence/frame set and emits YOLO-format labels for at least the reliable base classes, saved under `/Volumes/X9 Pro/Dev/poc/`.

### AC-5: Decisions enabled
- `proposed_schema.md` commits a class list with rationale.
- `knowledge_gaps.md` states what remains unknown and what the next run should do.
- Extensibility procedure ("add a class like referee") is documented.

### AC-6: Constraints honored
- No writes outside `/Volumes/X9 Pro/Dev` for dataset artifacts (repo gets only small summaries/manifests).
- No writes/moves/deletes on callisto or OneDrive. Cleanup observations captured as notes only.

---

## 9. Open Dependencies & Risks

| Item | Status | Notes |
|---|---|---|
| SAM 3 / SAM 3.1 install | Unverified | Weights, deps, GPU/host. Resolve in spike. Repo: `facebookresearch/sam3` (inference + finetune + checkpoints). |
| `ssh callisto` non-interactive | Unverified | If auth blocks, document and proceed with reachable sources. |
| External drive mounted | Required | `/Volumes/X9 Pro` must be mounted for both source #5 and all output. |
| `fc25-rush.mk1.pt` classes | Unknown | Core reason for the model audit. |
| Manual label formats vary | Likely | FC-Project may mix YOLO/COCO/Label Studio; inventory must normalize understanding before comparison. |
| Domain gap (SAM 3 real→rendered game) | Medium | Measured by the spike; fine-tune on small annotated set if a class underperforms. |
| `user-controlled-player` via exemplar | Medium-High | Make-or-break for that class; VLM Set-of-Marks fallback or small fine-tune if exemplar fails. |
| Duplicate sets across callisto/OneDrive | Likely | Note for dedup during dataset assembly + future cleanup. |

---

## 10. Change Log
- 2026-06-11 — Rewrote spec around audit + SAM 3 feasibility as the first @autonomous run. Added data/model source inventory, `/Volumes/X9 Pro/Dev` storage constraint, read-only callisto/OneDrive policy, cgF1-based SAM3-vs-manual comparison protocol, audit-driven schema, and class-extensibility goal (referee). Superseded the TacticalVisionNet-first spec (deferred).
