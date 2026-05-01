# Public Dataset Summary for the EA FC26 Tactical Vision Project

## Dataset Priority

| Priority | Dataset                                     | Type                             | Primary Use                                                                 |
| -------: | ------------------------------------------- | -------------------------------- | --------------------------------------------------------------------------- |
|        1 | **FC24 Minimap Dataset**                    | Minimap object detection         | Detect tactical minimap objects: ball, active player, allies, enemies       |
|        2 | **FIFA Minimap Dataset**                    | Minimap localization / detection | Pull the minimap from the full screenshot                                   |
|        3 | **Soccer Field Keypoints Detection**        | Pitch keypoint detection         | Detect soccer pitch landmarks for field geometry and homography             |
|        4 | **Football Field Keypoints Dataset**        | Pitch keypoint detection         | Additional pitch-landmark data and camera-angle diversity                   |
|        5 | **FC26 Roboflow Dataset**                   | FC26 object detection            | FC26-specific screenshots, HUD/object detection, field markings, indicators |
|        6 | **FIFA 25 / FC25 Object Detection Dataset** | FC25 object detection            | Additional game-domain screenshots and object labels                        |
|        7 | **QuantigoAI Soccer Dataset**               | Soccer segmentation              | Auxiliary scene understanding and segmentation support                      |
|        8 | **Football Players Detection Dataset**      | Player detection                 | Auxiliary player/occlusion detection                                        |
|        9 | **Football Players Dataset**                | Player/object detection          | Auxiliary player, referee, or ball detection support                        |

---

## 1. FC24 Minimap Dataset

**Link:** [https://universe.roboflow.com/meekee-zikcm/fc24](https://universe.roboflow.com/meekee-zikcm/fc24)

**Purpose:** primary dataset for extracting tactical state from the minimap.

**Known classes:**

* `Ball`
* `Active`
* `Ally`
* `BallAndActive`
* `Enemy`

**Best use:**

* detect ball position on minimap
* detect active player
* detect teammates
* detect opponents
* convert minimap detections into normalized pitch coordinates

**Why it matters:**
The minimap gives a clean top-down proxy for the game state, which is likely more useful for tactical decision-making than relying only on the main gameplay camera.

---

## 2. FIFA Minimap Dataset

**Link:** [https://universe.roboflow.com/fifa/fifa-minimap/images/173edS5gTYWGj0Rh5jwx](https://universe.roboflow.com/fifa/fifa-minimap/images/173edS5gTYWGj0Rh5jwx)

**Purpose:** locate or crop the minimap from a full screenshot.

**Best use:**

* train a minimap bounding-box detector
* identify the minimap region in full screenshots
* feed the cropped minimap into the FC24 minimap object detector

**Pipeline role:**

```text
full screenshot
  → minimap crop detector
  → cropped minimap
  → minimap object detector
  → tactical map state
```

---

## 3. Soccer Field Keypoints Detection

**Link:** [https://universe.roboflow.com/soccer-pitch-u7hw9/soccer-field-keypoints-detection?utm_source=chatgpt.com](https://universe.roboflow.com/soccer-pitch-u7hw9/soccer-field-keypoints-detection?utm_source=chatgpt.com)

**Purpose:** high-quality pitch keypoint detection.

**Best use:**

* detect field landmarks
* estimate field geometry
* support homography estimation
* connect main-view pixels to canonical pitch coordinates

**Why it matters:**
This is one of the most directly relevant datasets for detecting “important pieces of the soccer pitch,” such as corners, intersections, and other pitch landmarks.

---

## 4. Football Field Keypoints Dataset

**Link:** [https://www.kaggle.com/datasets/hamzaboulahia/football-field-keypoints-dataset?utm_source=chatgpt.com](https://www.kaggle.com/datasets/hamzaboulahia/football-field-keypoints-dataset?utm_source=chatgpt.com)

**Purpose:** additional field-keypoint data.

**Best use:**

* supplement the Roboflow soccer field keypoint dataset
* increase camera-angle diversity
* validate whether the pitch keypoint model generalizes
* compare or merge field landmark schemas

**Pipeline role:**
Use this as the secondary pitch-keypoint source after the Roboflow Soccer Field Keypoints Detection dataset.

---

## 5. FC26 Roboflow Dataset

**Link:** [https://universe.roboflow.com/xmlq-3ydiv/fc26](https://universe.roboflow.com/xmlq-3ydiv/fc26)

**Purpose:** FC26-specific object detection and domain alignment.

**Known classes discussed:**

* `goal`
* `black`
* `indicator`
* `namebar`
* `scoreclock`
* `white`

**Best use:**

* adapt models to FC26 visuals
* detect HUD elements
* detect score clock
* detect player indicators
* detect namebars
* detect goals
* potentially use `white` markings for field-line support

**Why it matters:**
This is the closest provided dataset to the actual target environment, EA FC26 screenshots.

---

## 6. FIFA 25 / FC25 Object Detection Dataset

**Link:** [https://www.kaggle.com/datasets/sonielyy/fifa-25-fc25-object-detection-dataset](https://www.kaggle.com/datasets/sonielyy/fifa-25-fc25-object-detection-dataset)

**Purpose:** additional game-domain object detection data.

**Best use:**

* supplement FC26 screenshot data
* improve robustness across recent EA FC visual styles
* train or pretrain object detectors for game screenshots

**Pipeline role:**
Use as secondary game-domain data behind the FC26 Roboflow dataset.

---

## 7. QuantigoAI Soccer Dataset

**Link:** [https://www.kaggle.com/datasets/quantigoai/soccer-dataset](https://www.kaggle.com/datasets/quantigoai/soccer-dataset)

**Purpose:** soccer scene segmentation support.

**Best use:**

* auxiliary segmentation pretraining
* scene understanding
* separating pitch, players, and field markings
* supporting white-line or pitch-region detection

**Caution:**
This is real soccer imagery, not EA FC26 gameplay, so it should support the project but not define the main training target.

---

## 8. Football Players Detection Dataset

**Link:** [https://www.kaggle.com/datasets/hamzaboulahia/football-players-detection-dataset](https://www.kaggle.com/datasets/hamzaboulahia/football-players-detection-dataset)

**Purpose:** player detection support.

**Best use:**

* detect players
* understand player occlusion over field lines
* pretrain auxiliary player detectors
* support main-view object detection

**Caution:**
This helps with dynamic objects, but it is not a pitch-landmark dataset and should not replace field keypoint data.

---

## 9. Football Players Dataset

**Link:** [https://www.kaggle.com/datasets/joopedrogrippa/football-players/data](https://www.kaggle.com/datasets/joopedrogrippa/football-players/data)

**Purpose:** additional football player/object detection support.

**Best use:**

* auxiliary player detection
* possible referee or ball detection support depending on labels
* pretraining or validation for main-view object detection

**Caution:**
Like the other player dataset, this is auxiliary. It should not drive the core pitch geometry or tactical minimap pipeline.

---

## Recommended Use by Task

| Task                                  | Use These Provided Datasets                                        |
| ------------------------------------- | ------------------------------------------------------------------ |
| **Minimap crop detection**            | FIFA Minimap Dataset                                               |
| **Minimap tactical object detection** | FC24 Minimap Dataset                                               |
| **Pitch keypoint detection**          | Soccer Field Keypoints Detection, Football Field Keypoints Dataset |
| **FC26 domain adaptation**            | FC26 Roboflow Dataset                                              |
| **Game-domain object detection**      | FC26 Roboflow Dataset, FIFA 25 / FC25 Object Detection Dataset     |
| **HUD / score clock / indicators**    | FC26 Roboflow Dataset                                              |
| **Player and occlusion detection**    | Football Players Detection Dataset, Football Players Dataset       |
| **Segmentation support**              | QuantigoAI Soccer Dataset                                          |

---

## Practical Training Order

1. **Train minimap crop detector**

   * Dataset: FIFA Minimap Dataset

2. **Train minimap object detector**

   * Dataset: FC24 Minimap Dataset

3. **Train pitch keypoint detector**

   * Datasets:

     * Soccer Field Keypoints Detection
     * Football Field Keypoints Dataset

4. **Train FC26 HUD/object detector**

   * Dataset: FC26 Roboflow Dataset

5. **Supplement with FC25 screenshots**

   * Dataset: FIFA 25 / FC25 Object Detection Dataset

6. **Add auxiliary player/occlusion support**

   * Datasets:

     * Football Players Detection Dataset
     * Football Players Dataset

7. **Add segmentation support only if useful**

   * Dataset: QuantigoAI Soccer Dataset

---

## Final Dataset Ranking

1. **FC24 Minimap Dataset**
2. **FIFA Minimap Dataset**
3. **Soccer Field Keypoints Detection**
4. **Football Field Keypoints Dataset**
5. **FC26 Roboflow Dataset**
6. **FIFA 25 / FC25 Object Detection Dataset**
7. **QuantigoAI Soccer Dataset**
8. **Football Players Detection Dataset**
9. **Football Players Dataset**
