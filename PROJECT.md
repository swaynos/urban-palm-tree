# EA FC26 Computer Vision and Controller-Learning Project Plan

## 1. End Goal

Build a system that can read EA FC26 gameplay screenshots or video frames, understand the tactical game state, infer a strong tactical approach, and eventually output a sequence of controller commands.

Target pipeline:

```text
screenshot / frame sequence
  → perception outputs
  → structured game state
  → temporal tactical state
  → tactical decision
  → controller command sequence
```

The project should not start by learning controller inputs directly from pixels. The first milestone is to extract as much useful information as possible from screenshots and represent it in a clean, structured format.

---

## 2. Core Strategy

Use a layered perception system:

```text
Full EA FC26 screenshot
  ├─ Main gameplay view
  │   ├─ pitch keypoints
  │   ├─ field geometry
  │   ├─ visible players
  │   ├─ ball
  │   ├─ active-player indicator
  │   └─ local control context
  │
  ├─ Minimap region
  │   ├─ ball icon
  │   ├─ active player
  │   ├─ allies
  │   ├─ enemies
  │   └─ top-down tactical state
  │
  └─ HUD / overlay
      ├─ score
      ├─ clock
      ├─ namebar
      ├─ player indicator
      ├─ stamina / power bars
      └─ distracting occluders
```

Then combine these into a frame-level game-state representation.

---

## 3. Why the Minimap Is Central

The minimap is likely the strongest source of tactical information because it provides a simplified top-down representation of:

* player positions
* ball position
* active player
* teammates
* opponents
* team shape
* available space
* defensive pressure
* attacking direction

This is more stable and less occluded than the main camera view.

Recommended minimap pipeline:

```text
Full screenshot
  → detect or crop minimap
  → run minimap object detector
  → detect Ball / Active / Ally / Enemy
  → convert minimap pixels to normalized pitch coordinates
  → build tactical state
```

For EA FC26, start with a deterministic minimap crop if resolution and HUD settings are stable. Add a minimap detector if the crop location varies.

---

## 4. Pitch Keypoint Detection Purpose

Pitch keypoints are still important, but their purpose is different from the minimap.

They help with:

* camera pose estimation
* homography estimation
* mapping main-view pixels to field coordinates
* identifying field zones
* interpreting local player and ball positions in the main camera
* connecting the gameplay camera to canonical pitch space

Pitch keypoints should represent stable field landmarks, not players or the ball.

---

## 5. Dataset Priority

### Priority 1: Minimap Crop and Minimap Icon Datasets

Use these to extract tactical state from the minimap.

Important datasets:

1. **FIFA minimap crop dataset**

   * Used to locate the minimap inside full screenshots.
   * Useful for training a `minimap` bounding box detector.

2. **Roboflow FC24 minimap dataset**

   * Classes:

     * `Ball`
     * `Active`
     * `Ally`
     * `BallAndActive`
     * `Enemy`
   * Useful for detecting player and ball icons on the minimap.
   * Even though it is FC24, the minimap format should transfer well to FC26.

### Priority 2: Soccer Pitch Keypoint Datasets

Use these to train field landmark detection.

Important datasets:

1. **Roboflow Soccer Field Keypoints Detection**

   * Very high priority.
   * High-quality field keypoint dataset.
   * Best candidate for defining the canonical pitch landmark schema.

2. **Kaggle Football Field Keypoints Dataset**

   * Also highly relevant.
   * Use for diversity, cross-validation, and additional camera views.

Other likely relevant pitch-keypoint candidates:

* Football Pitch Keypoints Detection by Daniel Machniak
* Keypoints on soccer pitch
* Soccer Field Keypoints Detection
* soccernet-pitch-keypoints
* Keypoints Field Detection
* Soccer Field Detection

### Priority 3: FC26 and FC25 Game-Domain Datasets

Use these for domain alignment with EA FC screenshots.

Important datasets:

1. **Roboflow FC26 dataset**

   * Direct FC26 visual domain.
   * Classes include:

     * `goal`
     * `black`
     * `indicator`
     * `namebar`
     * `scoreclock`
     * `white`
   * Useful for HUD elements, player indicators, score clock, goal, and potentially white field markings.

2. **Kaggle FIFA 25 / FC25 object detection dataset**

   * Useful as a secondary game-domain source.
   * Good for visual similarity to FC26.

### Priority 4: Player, Referee, Ball, and Segmentation Datasets

Use these only as auxiliary support.

Datasets:

* Kaggle football players dataset
* Kaggle football players detection dataset by Hamza Boulahia
* QuantigoAI soccer panoptic segmentation dataset

Use cases:

* player detection pretraining
* ball detection pretraining
* occlusion detection
* segmentation pretraining
* learning pitch/player/line separation

These should not define the main schema because the end goal is tactical FC26 gameplay interpretation, not general football video understanding.

---

## 6. Master Annotation Schema

Use one unified frame-level record.

```json
{
  "frame_id": "match001_frame000123",
  "timestamp_ms": 4100,
  "image": "match001/frame000123.png",
  "width": 1920,
  "height": 1080,

  "field": {
    "keypoints": {},
    "homography": null,
    "camera_side": null,
    "attacking_direction": null
  },

  "minimap": {
    "bbox": [x, y, w, h],
    "objects": []
  },

  "main_view": {
    "objects": [],
    "active_player": null,
    "ball": null
  },

  "hud": {
    "score": null,
    "clock": null,
    "namebars": [],
    "indicators": [],
    "overlays": []
  },

  "derived_pitch_state": {
    "ball": null,
    "active_player": null,
    "allies": [],
    "enemies": [],
    "team_shape": null,
    "phase": null,
    "pressure": null,
    "open_space": null
  },

  "controller": {
    "current_input": null,
    "future_sequence": []
  }
}
```

At the beginning, the `controller` section can remain empty. Later it will be filled using aligned key sequence data.

---

## 7. Field Keypoint Schema

Use a fixed canonical list of landmarks. Keep the order stable across all datasets.

Recommended starting keypoints:

### Core Pitch Landmarks

1. `top_left_pitch_corner`
2. `top_right_pitch_corner`
3. `bottom_left_pitch_corner`
4. `bottom_right_pitch_corner`
5. `center_spot`
6. `center_circle_top`
7. `center_circle_bottom`
8. `center_circle_left`
9. `center_circle_right`

### Halfway Line

10. `halfway_line_top_touchline_intersection`
11. `halfway_line_bottom_touchline_intersection`

### Left Penalty Area

12. `left_penalty_spot`
13. `left_penalty_area_top_corner`
14. `left_penalty_area_bottom_corner`
15. `left_goal_area_top_corner`
16. `left_goal_area_bottom_corner`
17. `left_goal_center`

### Right Penalty Area

18. `right_penalty_spot`
19. `right_penalty_area_top_corner`
20. `right_penalty_area_bottom_corner`
21. `right_goal_area_top_corner`
22. `right_goal_area_bottom_corner`
23. `right_goal_center`

Optional later expansion:

* penalty arc intersections
* goal line intersections
* corner arc points
* additional line intersections
* visible line endpoints

Each keypoint should have:

```json
{
  "x": 960,
  "y": 540,
  "visible": true,
  "occluded": false,
  "source_dataset": "custom_fc26",
  "confidence": 1.0
}
```

Rules:

* Do not guess off-screen landmarks.
* Mark cropped or invisible landmarks as `visible: false`.
* Use `occluded: true` when the point is geometrically in-frame but covered by a player, HUD element, minimap, or overlay.
* Prefer meaningful pitch landmarks over arbitrary visible line endpoints.

---

## 8. Minimap Annotation Schema

### Minimap Crop

```json
{
  "class": "minimap",
  "bbox": [x, y, width, height]
}
```

### Minimap Objects

Use center-point or bounding-box annotations.

Classes:

```text
Ball
Active
BallAndActive
Ally
Enemy
Goalkeeper
Unknown
```

Example:

```json
{
  "minimap": {
    "bbox": [680, 890, 690, 230],
    "objects": [
      {"class": "Ball", "x": 326, "y": 989},
      {"class": "Active", "x": 351, "y": 1002},
      {"class": "Ally", "x": 287, "y": 1015},
      {"class": "Enemy", "x": 419, "y": 973}
    ]
  }
}
```

Derived pitch coordinates:

```json
{
  "pitch_objects": [
    {"class": "Ball", "pitch_x": 0.54, "pitch_y": 0.48},
    {"class": "Active", "pitch_x": 0.51, "pitch_y": 0.52}
  ]
}
```

Normalize coordinates to a canonical pitch:

```text
pitch_x ∈ [0, 1]
pitch_y ∈ [0, 1]
```

or use real-world pitch units:

```text
x ∈ [0, 105]
y ∈ [0, 68]
```

---

## 9. Main-View Object Schema

Detect the main-view elements that help with local control:

Classes:

* `player`
* `goalkeeper`
* `referee`
* `ball`
* `active_player`
* `selected_indicator`
* `namebar`
* `stamina_bar`
* `power_bar`
* `scoreclock`
* `goal`
* `white_field_marking`
* `black_overlay`
* `hud_overlay`

Main-view detection helps with:

* dribbling
* shielding
* shot timing
* tackle timing
* loose balls
* nearby defenders
* active player context
* local passing lanes

---

## 10. Derived Tactical Features

Once detections exist, compute tactical features.

Per frame:

```json
{
  "phase": "buildup",
  "field_zone": "middle_third",
  "possession": "user",
  "attacking_direction": "left_to_right",
  "ball_velocity": [0.01, -0.02],
  "active_player_velocity": [0.03, 0.00],
  "nearest_defender_distance": 0.08,
  "nearest_teammate_distance": 0.12,
  "passing_options": [],
  "open_space_regions": [],
  "defensive_pressure": "medium"
}
```

Useful tactical labels:

* buildup
* counterattack
* final third
* defending
* pressing
* transition
* set piece
* possession recycle
* through-ball opportunity
* crossing opportunity
* shooting opportunity
* danger under pressure

---

## 11. Controller Sequence Learning

Do not start with pixel-to-controller learning. Use a hierarchy.

Recommended final architecture:

```text
Perception model:
image / frame → structured game state

Tracking model:
game-state sequence → temporal tactical state

Tactical model:
temporal tactical state → intent

Control model:
intent + state → controller command sequence
```

Example:

```text
state sequence + tactical intent
  → left stick direction
  → sprint modifier
  → pass / through ball / shoot / tackle
  → timing and duration
```

Possible tactical intents:

* keep possession
* short pass
* through ball
* switch play
* dribble forward
* sprint into space
* shield ball
* cross
* shoot
* jockey
* press ball carrier
* cut passing lane
* clear ball

Controller sequence format:

```json
{
  "start_timestamp_ms": 4100,
  "end_timestamp_ms": 4700,
  "inputs": [
    {
      "timestamp_ms": 4100,
      "left_stick": [0.7, -0.2],
      "right_stick": [0.0, 0.0],
      "buttons": ["sprint"]
    },
    {
      "timestamp_ms": 4300,
      "left_stick": [0.8, -0.1],
      "buttons": ["pass"]
    }
  ]
}
```

---

## 12. Training Plan

### Phase 1: Perception Dataset

Build or convert datasets for:

1. minimap crop
2. minimap icons
3. pitch keypoints
4. main-view players and ball
5. HUD elements

Output:

* clean unified labels
* one frame-level JSON record per image
* consistent coordinate system

### Phase 2: Minimap State Extraction

Train:

* minimap crop detector
* minimap icon detector

Then convert icon positions into pitch coordinates.

Deliverable:

```text
screenshot → top-down tactical player/ball state
```

### Phase 3: Pitch Geometry and Homography

Train:

* pitch keypoint model
* optional field-line segmentation model

Use keypoints to estimate:

* homography
* camera direction
* field zone
* main-view coordinate mapping

Deliverable:

```text
main camera view → registered pitch geometry
```

### Phase 4: Main-View Local Context

Train:

* player detector
* ball detector
* active-player detector
* HUD detector

Deliverable:

```text
main view → local control and occlusion context
```

### Phase 5: Temporal Tracking

Track across frames:

* ball movement
* active player movement
* teammate and opponent movement
* shape changes
* defensive pressure
* passing lanes
* open space

Deliverable:

```text
frame sequence → tactical state sequence
```

### Phase 6: Tactical Intent Learning

Train a model to infer high-level tactical actions:

* pass
* dribble
* shoot
* defend
* press
* switch
* hold
* clear

Deliverable:

```text
state sequence → tactical intent
```

### Phase 7: Controller Sequence Learning

Align frame sequences with controller inputs.

Train:

```text
state sequence + intent → controller command sequence
```

Deliverable:

```text
screenshot sequence → executable controller commands
```

---

## 13. Model Choices

### Object Detection

Use YOLO-style models for:

* minimap crop
* minimap icons
* players
* ball
* HUD elements

### Keypoint Detection

Use keypoint-style model for:

* pitch landmarks
* field registration points

Possible approaches:

* YOLO pose/keypoint model
* heatmap-based CNN
* HRNet-style keypoint model
* custom U-Net/heatmap model

### Segmentation

Use segmentation for:

* white pitch markings
* pitch area
* players
* HUD occlusions

Possible use:

```text
segmentation → line extraction → geometry fitting → keypoint refinement
```

### Temporal Modeling

Use:

* Kalman filters or SORT/DeepSORT for early tracking
* temporal transformer, GRU, LSTM, or 1D temporal CNN later
* hierarchical policy model for controller commands

---

## 14. Data Conversion Plan

Convert all datasets into the same internal structure.

For each source dataset:

1. Inspect classes and annotation format.
2. Map labels to internal schema.
3. Drop unusable labels.
4. Mark unavailable keypoints as invisible.
5. Preserve `source_dataset`.
6. Preserve original image dimensions.
7. Normalize coordinates.
8. Create one JSON record per frame.

Example conversion target:

```json
{
  "frame_id": "source_dataset_image_000001",
  "source_dataset": "roboflow_soccer_field_keypoints",
  "image": "images/image_000001.jpg",
  "width": 1920,
  "height": 1080,
  "field": {
    "keypoints": {
      "center_spot": {
        "x": 960,
        "y": 540,
        "visible": true,
        "occluded": false
      }
    }
  },
  "minimap": null,
  "main_view": null,
  "hud": null,
  "controller": null
}
```

---

## 15. Labeling Guide Principles

Use consistent landmark definitions.

For each point, define:

* exact soccer-field meaning
* whether the point is allowed to be inferred
* how to handle crop boundaries
* how to handle occlusion
* how to handle line thickness
* whether to label center of line intersection or edge

Recommended rules:

* Label the geometric center of field-line intersections.
* For thick lines, click the midpoint of the white line.
* If a point is outside the image, mark invisible.
* If a point is hidden by a player or HUD element, mark occluded.
* If a point is visible but slightly blurred, label it and set lower confidence if needed.
* Do not label arbitrary endpoints unless they are part of the schema.

---

## 16. Immediate Next Steps

### Step 1: Define the Final Unified Schema

Create the first version of:

* pitch keypoints
* minimap objects
* HUD objects
* main-view objects
* derived tactical fields
* controller sequence format

### Step 2: Inspect and Convert Highest-Priority Datasets

Start with:

1. Roboflow FC24 minimap object dataset
2. FIFA minimap crop dataset
3. Roboflow Soccer Field Keypoints Detection
4. Kaggle Football Field Keypoints Dataset
5. Roboflow FC26 dataset

### Step 3: Label a Small FC26 Test Set

Create 20 to 50 manually labeled FC26 screenshots.

Include:

* different camera angles
* different field zones
* possession and non-possession
* HUD overlays
* minimap visibility
* crowded and uncrowded frames

### Step 4: Train First Detectors

Train in this order:

1. minimap crop detector
2. minimap icon detector
3. pitch keypoint detector
4. HUD detector
5. main-view player/ball detector

### Step 5: Build State Extractor

Create a script that takes one screenshot and outputs:

```json
{
  "field": {},
  "minimap": {},
  "main_view": {},
  "hud": {},
  "derived_pitch_state": {}
}
```

### Step 6: Move From Single Frames to Sequences

Once single-frame extraction works, process short clips.

Compute:

* velocity
* movement direction
* pressure
* passing options
* team shape
* open space

### Step 7: Add Controller Data

Record or import aligned gameplay:

* video frames
* timestamps
* controller states
* button presses
* stick positions

Then train tactical and control models.

---

## 17. Current Project Ranking

1. **Minimap icon detection**

   * Highest tactical value.
   * Gives player and ball positions.

2. **Minimap crop detection**

   * Needed to reliably extract minimap from screenshots.

3. **Pitch keypoint detection**

   * Needed for field geometry and main-view registration.

4. **FC26 domain-specific detection**

   * Needed for real EA FC26 screenshot robustness.

5. **HUD detection**

   * Needed to remove distractions and extract context.

6. **Main-view player and ball detection**

   * Needed for local control details.

7. **Temporal tactical modeling**

   * Needed for tactical interpretation.

8. **Controller sequence learning**

   * Final stage, only after strong perception exists.

---

## 18. Key Design Decision

The system should learn from a structured intermediate game state rather than raw pixels alone.

Preferred final design:

```text
images → structured state → tactical intent → controller commands
```

Not:

```text
images → controller commands
```

This makes the system:

* easier to debug
* easier to improve
* easier to train with limited data
* better at combining datasets
* more robust across camera views and game versions
