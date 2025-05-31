# Project Refactoring Idea
## Goal
Develop an intelligent, AI-assisted system for automating and guiding user interactions in FC 25, with distinct strategies for in-match, fallout (such as pause, or half-time), and menu-based navigation states. The project aims to emphasize real-time speed, context awareness, and robust decision-making through a combination of fast vision models and GPT-4 reasoning.

## High-Level Architecture
### 1. Fast Path – In-Gameplay Detection & Action

#### Assumption
The user is actively engaged in a live match. Speed and low latency are critical.

#### Strategy
Instead of using GPT-4 here (which would be too slow), this phase relies on a two-stage inference pipeline designed for real-time responsiveness:
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
  - Aggregate their outputs and pass context to GPT-4 (multi-modal).
  - GPT-4 infers current state and provides a tactical, short-term goal to return to gameplay (e.g., resume, exit cutscene, handle dialog).

- **Priority:** Minimize delay before re-entering gameplay and resuming fast model usage.

---

## 3. Turn-Based Goal Reasoning – Menu Navigation

- **Trigger:** Confirmed non-gameplay state (main menu, squad management, settings, etc.).

- **Action Flow:**
  - GPT-4 is provided with current visual state and a high-level user goal (e.g., "Handle injured player" or "Claim Squad Battles rewards").
  - The model acts as a turn-based planner, suggesting the next UI step or action.
  - System takes action → re-evaluates visual state → GPT-4 refines goal or next step.

---

## 4. Threaded Execution Architecture
There is a delay that exists between when the screenshot is captured to when actions are executed. It is believed that this delay is due to a bug. However, if the bug is architecture related, we could re-architect the thread execution to minimize this delay.

Existing Architecture | Threads:
Thread 1. Capture Screenshots - Will loop and capture screenshots as fast as possible. There is a configurable delay between each loop.
Thread 2. Inference Images - Loops and runs inference on the latest screenshot. There is a configurable delay between each loop.
Thread 3. Execute Actions - Loops and builds actions based on the strategy built in GameStrategyController.  There is a configurable delay between each loop.

GameStrategyController is shared between the Inference and Execute Actions threads.

The aspiration is that the Execute Actions thread will execute as soon as inference is completed.

*Existing Performance*
| Action                       | Time Elapsed (seconds)  |
|------------------------------|-------------------------|
| Time elapsed from screenshot:| 0.6129|
| Time elapsed from screenshot:| 2.3702|
| Time elapsed from screenshot:| 4.0333|
| Time elapsed from screenshot:| 0.5419|
| Time elapsed from screenshot:| 2.2480|
| Time elapsed from screenshot:| 4.0895|
| Time elapsed from screenshot:| 0.5110|
| Time elapsed from screenshot:| 2.0662|
| Time elapsed from screenshot:| 3.6719|
| Time elapsed from screenshot:| 0.5006|
| Time elapsed from screenshot:| 2.1289|
| Time elapsed from screenshot:| 3.7140|
| Time elapsed from screenshot:| 0.5033|
| Time elapsed from screenshot:| 2.2351|
| Time elapsed from screenshot:| 4.0609|
| Time elapsed from screenshot:| 0.5243|