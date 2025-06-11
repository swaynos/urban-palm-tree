# Project Refactoring Idea
## Goal
Develop an intelligent, AI-assisted system for automating and guiding user interactions in FC 25, with distinct strategies for in-match, fallout (such as pause, or half-time), and menu-based navigation states. The project aims to emphasize real-time speed, context awareness, and robust decision-making through a combination of fast vision models and GPT-4 reasoning.

## High-Level Architecture
### 1. Fast Path – In-Gameplay Detection & Action

#### Assumption
The user is actively engaged in a live match. Speed and low latency are critical.

#### Strategy
Instead of using MLLMs here (which would be too slow), this phase relies on a two-stage inference pipeline designed for real-time responsiveness:
##### Stage 1: High-Speed Visual Detection
- Run fast YOLO models on every frame to extract structured information about the gameplay.
- Example detections:
- player: (x1, y1, x2, y2)
- ball: (x3, y3, x4, y4)
- These detections form a **real-time, lightweight representation of the game state**.
##### Stage 2: Tactical Inference Model
- Feed the YOLO outputs into a **secondary model** (rule-based, shallow ML, or tiny neural net).secondary model (rule-based, shallow ML, or tiny neural net).
- This model maps simplified game state => action, such as:
```
INPUT:
  player = (x1, y1, x2, y2)
  ball = (x3, y3, x4, y4)

OUTPUT:
  action = "move toward 130 degrees and press [X]"
  ```
- This system ensures **minimal latency** and **rapid responsiveness** in gameplay without human intervention.

#### Fallback Trigger
To detect a “fallout” (i.e., user no longer in a match):
- Monitor YOLO confidence levels and consistency.
- If several consecutive frames return **unknown**, **empty**, or **ambiguous** detections.
  - Assume gameplay has ended or paused.
  - Transition to **Fallback Path** for recovery or reclassification.

---

## 2. Fallback Path – Post-Gameplay Handling ("Fallout")

- **Goal:** Rapidly assess whether gameplay can be resumed, and if so, how.

- **Action Flow:**
  - Run existing suite of image classification models.
  - Aggregate their outputs and pass context to MLLM (multi-modal).
  - MLLM infers current state and provides a tactical, short-term goal to return to gameplay (e.g., resume, exit cutscene, handle dialog).

- **Priority:** Minimize delay before re-entering gameplay and resuming fast model usage.

---

## 3. Turn-Based Goal Reasoning – Menu Navigation

- **Trigger:** Confirmed non-gameplay state (main menu, squad management, settings, etc.).

- **Action Flow:**
  - MLLM is provided with current visual state and a high-level user goal (e.g., "Handle injured player" or "Claim Squad Battles rewards").
  - The model acts as a turn-based planner, suggesting the next UI step or action.
  - System takes action → re-evaluates visual state → MLLM refines goal or next step.

---
