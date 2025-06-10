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
# Reducing Delay Between Screenshot Capture and Action Execution

There is currently a delay between when a screenshot is captured and when actions are executed. This delay is suspected to be caused by a bug, but it may also be due to architectural issues. If it is architecture-related, re-architecting thread execution may help minimize the delay. However, optimizing this may be challenging if the underlying design is flawed.

---

## Existing Architecture (Threads)

- **Thread 1: Capture Screenshots**
    - Continuously loops to capture screenshots as quickly as possible.
    - Has a configurable delay between each loop.

- **Thread 2: Inference Images**
    - Loops and runs inference on the latest screenshot.
    - Has a configurable delay between each loop.

- **Thread 3: Execute Actions**
    - Loops and builds actions based on the strategy in `GameStrategyController`.
    - Has a configurable delay between each loop.

> `GameStrategyController` is shared between the Inference and Execute Actions threads.
>
> The aspiration is for the Execute Actions thread to execute as soon as inference is completed, but delays are currently preventing this.

---

## Proposed Architecture (Threads)

- **Thread 1: Capture Screenshots**
    - Loops and captures screenshots as quickly as possible, outputting each screenshot to a single-dimension queue.
    - Configurable delay between each loop, which could be optimized automatically.

- **Thread 2: Inference Images**
    - Long-polls the queue for new screenshots.
    - Runs inference only when a new screenshot is available, outputting inference results to a separate single-dimension queue.
    - No delay is needed between loops, as processing is triggered by the arrival of new screenshots.
    - _Optional:_ Consider using a more efficient event mechanism in Python to react to new screenshots, rather than polling.

- **Thread 3: Execute Actions**
    - Long-polls the queue for new inference results.
    - Executes actions as soon as new inference results are available.
    - No delay is needed between loops, as processing is triggered by the arrival of new inference results.
    - _Optional:_ Explore better event mechanisms in Python to react to new inference results, instead of polling.

---

## Goals and Open Questions

- **Goal:**  
    - Minimize the delay between inference completion and action execution.

- **Open Questions:**  
    - Can Python’s event-driven primitives (such as `queue.Queue` with blocking `get()`, `threading.Event`, or async libraries) improve responsiveness?
    - Are there recommended patterns or libraries for real-time, event-driven thread communication in Python?


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