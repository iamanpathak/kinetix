# Kinetix: Vision-Based Zero-Touch OS Controller

[![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python&logoColor=white)](https://python.org/)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.x-green?logo=opencv&logoColor=white)](https://opencv.org/)
[![MediaPipe](https://img.shields.io/badge/MediaPipe-Google-orange?logo=google&logoColor=white)](https://mediapipe.dev/)
[![PyAutoGUI](https://img.shields.io/badge/Automation-PyAutoGUI-red?logo=windows&logoColor=white&v=1)](https://pyautogui.readthedocs.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow)](https://opensource.org/licenses/MIT)

Hey! I'm Aman. I built **Kinetix** to reduce the friction in human-computer interaction. Controlling an OS through standard webcams usually involves high latency, jittery cursors, and accidental clicks. I engineered Kinetix as a lightweight, context-aware gesture routing engine that translates structural hand gestures into real-time system actions for touchless navigation and productivity control.

---

## 🎯 Engineering Objective

**The Problem:** Controlling a PC via webcam usually involves mapping your index finger to the mouse cursor. This relies heavily on perfect lighting, high-end cameras, and holding your hand perfectly still in the air - which causes massive arm fatigue and results in constant misclicks.

**The Solution:** Kinetix reduces dependence on traditional cursor-tracking. Instead, it acts as a background spatial-recognition engine that interprets structural hand gestures and translates them into real-time system-level actions for navigation, media control, scrolling, zooming, and productivity workflows. It features a “Typing Shield” that dynamically ignores your hands when they rest near your keyboard, ensuring minimal accidental interference while you work. The system is designed with an extensible gesture-routing architecture, allowing additional gestures, action mappings, and context-aware workflows to be integrated without modifying the core vision pipeline.

---

## 🏗️ System Architecture & Execution Flow

I designed the engine to be as lightweight as possible. It captures frames, processes spatial data locally through a pre-trained vision model, applies debounce algorithms to filter out camera blur, and routes the validated gesture to the OS.

```text
[Webcam Feed] ──(Raw Frames @ 30FPS)──> [OpenCV Frame Buffer]
                                                 │
                                                 ▼
                                   [MediaPipe Vision Task Model]
                                     (gesture_recognizer.task)
                                                 │
                      ┌──────────────────────────┴──────────────────────────┐
                      ▼                                                     ▼
             [Spatial Validation]                                    [Context Router]
             ├─ 1. Typing Shield Check                        ├─ 1. Detect Active Window
             │     (Y-Axis)                                   │     (Browser, IDE, Spotify)
             ├─ 2. Ghost Hand Filter                          └─ 2. Assign Hotkey Protocol
             │     (Wrist Distance)                                         │
             └─ 3. Frame Debounce                                           │
                   (Micro-stutter fix)                                      │
                      │                                                     │
                      └──────────────────────────┬──────────────────────────┘
                                                 ▼
                                     [ActionController Engine]
                                    (Translates Math to Hotkeys)
                                                 │
                      ┌──────────────────────────┴──────────────────────────┐
                      ▼                                                     ▼
             [Continuous Actions]                                  [Instant Triggers]
             (Scroll, Zoom, Volume)                                (Minimize, Escape)
                      │                                                     │
                      └──────────────────────────┬──────────────────────────┘
                                                 ▼
                                       [PyAutoGUI Interface]
                                   (Executes Native OS Commands)
```

---

## ⚡ Platform Features & Gesture Dictionary

Kinetix relies on a highly reliable vocabulary of physical gestures to ensure maximum accuracy and zero misfires. 

### 🔄 Continuous Action Gestures
Hold the pose and move your hand to trigger these actions dynamically:

*   **✌️ Victory (Peace Sign): The Scroll Engine**
    *   *Action:* Move hand Up/Down to scroll web pages and documents effortlessly.
*   **🤟 Spiderman (Rock On): The Audio Mixer**
    *   *Action:* Move hand Up/Down to adjust your system master volume.
*   **✋ Open Palm: The Media & Tab Engine**
    *   *Hover Still (0.6s):* Action: Play/Pause active media. The engine dynamically adapts actions based on the active application context, including browsers, IDEs, and media applications.
    *   *Swipe Right/Left:* Action: Switch to Next/Previous Tab (Browser/VS Code) or Next/Previous Track (Spotify).
*   **👐 Two Hands: The Zoom Engine**
    *   *Action:* Bring both hands closer together or further apart to trigger precise, atomic zooming in documents or browsers.

### ⚡ Instant Triggers
Fire instantly the moment the camera detects the pose (no holding required):

*   **👎 Thumbs Down: The Boss Key**
    *   *Action:* Instantly minimizes all windows and displays the desktop (`Win + D`). *Pro-Tip: Tilt your hand slightly sideways so the camera sees the profile of your thumb!*
*   **✊ Closed Fist: The Escape Hatch**
    *   *Action:* Presses the `Esc` key to exit full-screen videos, close popups, or drop active contexts.

### 👻 Ghost Mode
By default, Kinetix runs with a visual HUD window so you can see what the AI sees. If you want it to run completely invisibly in the background without taking up screen space, simply open `config.py` and change `GHOST_MODE = False` to `True`.

---

## 📁 Codebase Architecture

```text
kinetix/
├── actions.py               # Core OS routing, macro logic, and failsafes
├── config.py                # Global settings (FPS, Ghost Mode, Thresholds)
├── main.py                  # Computer Vision loop and MediaPipe integration
├── gesture_recognizer.task  # The compiled Neural Network AI model (Required)
├── .gitignore               # Repository hygiene protocol
├── README.md                # Project documentation
└── LICENSE                  # MIT License
```

---

## 🛠️ Technical Decisions & Trade-offs

* **Atomic Hotkeys vs. Held Keys:** In earlier versions, gestures simulated physically holding down keys (like `Ctrl` for zooming). *Tradeoff:* Camera stutters occasionally caused release commands to fail, resulting in stuck modifier keys. I refactored the engine to use atomic keystrokes (e.g., pulsing `Ctrl + =`) instead, eliminating the risk of stuck modifier states during gesture interruptions.

* **Frame Validation vs. Time-Based Triggers:** Instead of relying entirely on Python timing intervals for critical system actions, Kinetix validates gestures across consecutive frame states. *Tradeoff:* This improves consistency during rapid hand movement and reduces accidental trigger execution caused by motion blur or unstable frame timing.

* **Local Processing vs. Cloud APIs:** The entire processing pipeline runs locally on the CPU. *Tradeoff:* Requires shipping the `.task` model with the application, but guarantees low latency, offline functionality, and complete webcam privacy without transmitting visual data externally.

* **Gesture Cooldowns vs. Instant Responsiveness:** Critical actions use cooldown windows and micro-validation delays to prevent repeated accidental execution during unstable gesture transitions. *Tradeoff:* Introduces a slight delay before activation, but significantly improves interaction reliability and usability.

---

## 🚀 Local Development & Setup

### 1. Clone & Setup

```bash
git clone https://github.com/iamanpathak/kinetix.git
cd kinetix
```

### 2. Install Dependencies

```bash
pip install opencv-python mediapipe pyautogui pygetwindow numpy
```

### 3. Launch the Engine

Ensure your webcam is connected, then run:

```bash
python main.py
```

---

## 📦 Building a Standalone Executable (`.exe`)

You don't need Python installed to share Kinetix with your friends. You can compile the entire project into a single, click-to-run `.exe` file.

1. Open your terminal in the project folder and install PyInstaller:

```bash
pip install pyinstaller
```

2. Run this exact build command to bundle the app, hide the background console, and seamlessly attach the AI model:

```bash
pyinstaller --onefile --noconsole --add-data "gesture_recognizer.task;." main.py
```

3. Once finished, navigate to the newly created `dist/` folder. You will find your `.exe` inside. Move it anywhere and double-click to run!

---

## 🔒 Privacy & Security

Kinetix is designed with privacy in mind. All gesture processing runs locally in volatile memory (RAM) without storing photos, recording video, or transmitting webcam data to external servers.

---

## 📄 License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.

<p align="center">
  Made with ❤️ by <a href="https://github.com/iamanpathak">Aman Pathak</a>
</p>