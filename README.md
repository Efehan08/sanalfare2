# 🖐️ Dual-Hand Virtual Mouse - Advanced Gesture Control

An advanced, two-handed virtual mouse application built with Python, OpenCV, and MediaPipe. This system completely decouples cursor movement from clicking actions by assigning independent tasks to each hand, resulting in zero cursor drift during clicks.

## 🏗️ System Architecture & Prompt Engineering

This project demonstrates modern AI-assisted software development. I acted as the **System Architect and Logic Designer**, utilizing generative AI to write the boilerplate code based on my structural constraints.

My core architectural designs in this V2 iteration include:
* **Task Decoupling (Two-Handed Logic):** Solved the classic "cursor drift" problem by assigning the non-dominant hand solely to cursor navigation, while the dominant hand handles execution (clicks, drags).
* **Mutex Lock & Gesture Priority:** Designed a priority-based locking mechanism (`sol_tik_aktif` boolean logic). If the ring finger is active (Drag & Drop), it locks out the index finger (Left Click) to prevent conflicting OS commands.
* **Anchor-Based Stabilization (Zero-Jitter):** Engineered a velocity-based lock (`is_locked`). When hand movement drops below a threshold, the cursor anchors its coordinates, eliminating the micro-jitters common in computer vision applications.

## ✨ Key Features

* **Dual-Hand Operation:** * **Left Hand (Navigation):** Controls the mouse cursor.
  * **Right Hand (Action):** Executes clicks based on distance ratios between the thumb and other fingertips.
* **Multi-Finger Gestures:**
  * **Index Finger + Thumb:** Left Click
  * **Middle Finger + Thumb:** Right Click
  * **Ring Finger + Thumb:** Hold to Drag & Drop
* **Distance-Agnostic Clicks:** Uses the palm size (wrist to middle-finger base) as a dynamic reference ratio, meaning gestures work perfectly whether your hand is 10 cm or 1 meter away from the webcam.

## 🛠️ Installation & Setup

This version runs entirely locally using your built-in webcam.

1. Clone this repository to your local machine.
2. Install the required Python dependencies:
   ```bash
   pip install opencv-python mediapipe pyautogui

The pyautogui.FAILSAFE mechanism is intentionally disabled to provide a seamless edge-to-edge screen experience. To forcefully stop the application if needed, ensure your terminal window is accessible to press q or CTRL+C

How to Use (Gestures)
Move Cursor: Move your index and thumb fingers together around the screen.

Left Click / Drag: Pinch your Index Finger and Thumb together. Hold to drag.

Right Click: Pinch your Middle Finger and Thumb together.

Exit: Press the q key on your physical keyboard to terminate the program.
