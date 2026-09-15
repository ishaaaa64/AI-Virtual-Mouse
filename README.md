# 🖱️ AI Virtual Mouse

An AI-powered virtual mouse that allows users to control computer actions using **hand gestures captured through a webcam**.

The project combines **Computer Vision, MediaPipe Hand Landmarks, Machine Learning, and PyAutoGUI** to translate real-time hand gestures into mouse actions.

---

## ✨ Features

* 🖱️ Cursor movement using hand movement
* 👆 Left click using hand gesture
* 👉 Right click using hand gesture
* 🔄 Scroll control using hand gesture
* ✊ Pause gesture
* 🤏 Drag-and-drop using left-click hold
* 🎯 Real-time gesture classification
* 🤖 Random Forest machine learning model
* 📷 Webcam-based hand tracking
* ⚡ Real-time prediction with confidence score
* 🧩 Normalized hand landmark features for better generalization

---

## 🧠 How It Works

The system follows this pipeline:

```text
Webcam
   ↓
OpenCV
   ↓
MediaPipe Hand Landmarker
   ↓
21 Hand Landmarks
   ↓
Landmark Normalization
   ↓
Machine Learning Model
   ↓
Gesture Prediction
   ↓
PyAutoGUI
   ↓
Computer Mouse Action
```

### 1. Hand Detection

The webcam captures the user's hand and MediaPipe detects **21 hand landmarks**.

### 2. Feature Extraction

The `(x, y)` coordinates of the 21 landmarks are extracted.

This produces:

```text
21 landmarks × 2 coordinates = 42 features
```

### 3. Feature Normalization

The landmarks are normalized relative to the wrist.

This helps the model become less dependent on the absolute position and size of the hand in the camera frame.

### 4. Gesture Classification

A trained **Random Forest classifier** predicts the user's gesture.

Supported gestures:

| Gesture     | Action      |
| ----------- | ----------- |
| MOVE        | Move cursor |
| LEFT_CLICK  | Left click  |
| RIGHT_CLICK | Right click |
| SCROLL      | Scroll      |
| PAUSE       | Pause       |

### 5. Mouse Control

The predicted gesture is converted into an actual computer action using PyAutoGUI.

---

## 🎮 Gesture Controls

| Hand Gesture               | Mouse Action |
| -------------------------- | ------------ |
| ☝️ Index finger            | Move cursor  |
| 🤏 Thumb + index           | Left click   |
| 🤏 Thumb + middle finger   | Right click  |
| ✌️ Index + middle          | Scroll       |
| ✊ Closed fist              | Pause        |
| 🤏 Hold left-click gesture | Drag         |
| Release after drag         | Drop         |

---

## 🛠️ Tech Stack

### Programming Language

* Python

### Computer Vision

* OpenCV
* MediaPipe

### Machine Learning

* Scikit-learn
* Random Forest Classifier

### Mouse Automation

* PyAutoGUI

### Model Serialization

* Joblib

### Development Tools

* Visual Studio Code
* Git
* GitHub

---

## 📁 Project Structure

```text
AI-Virtual-Mouse/
│
├── camera/
│   └── camera_test.py
│
├── gestures/
│   └── gesture_detector.py
│
├── hand_tracking/
│   ├── hand_detector.py
│   └── hand_landmarker.task
│
├── models/
│   └── gesture_model.pkl
│
├── mouse/
│   └── mouse_controller.py
│
├── tests/
│   ├── test_hand_detection.py
│   └── test_mouse.py
│
├── dataset/
│   └── Training and experimentation files
│
├── main.py
├── ai_virtual_mouse.py
├── requirements.txt
├── README.md
└── .gitignore
```

> The training dataset is excluded from Git tracking to keep the repository lightweight.

---

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone https://github.com/ishaaaa64/AI-Virtual-Mouse.git
```

### 2. Open the project

```bash
cd AI-Virtual-Mouse
```

### 3. Create a virtual environment

```bash
python -m venv .venv
```

### 4. Activate the virtual environment

### Windows PowerShell

```powershell
.\.venv\Scripts\Activate.ps1
```

### 5. Install dependencies

```bash
pip install -r requirements.txt
```

---

## 📦 Model Setup

The project uses a MediaPipe Hand Landmarker model:

```text
hand_tracking/hand_landmarker.task
```

The trained gesture classifier is stored at:

```text
models/gesture_model.pkl
```

---

## ▶️ Run the Project

Activate the virtual environment:

```powershell
.\.venv\Scripts\Activate.ps1
```

Then run:

```bash
python main.py
```

A webcam window will open.

Use your hand gestures to control the mouse.

Press:

```text
Q
```

to exit the application.

---

## 🤖 Machine Learning Model

The gesture classifier is based on a **Random Forest Classifier**.

The model was trained using normalized hand landmark coordinates.

The final classifier recognizes:

```text
MOVE
LEFT_CLICK
RIGHT_CLICK
SCROLL
PAUSE
```

The model also provides a prediction confidence score which is used to filter uncertain predictions.

---

## 🔒 Safety & Stability

The application includes:

* Gesture confidence threshold
* Gesture stability filtering
* Click cooldown
* Scroll cooldown
* Drag hold detection
* Automatic mouse release when the hand disappears
* Cursor smoothing

These mechanisms help reduce accidental mouse actions.

---

## 🚀 Future Improvements

Possible future enhancements include:

* More advanced gesture recognition
* Custom gesture training interface
* Better drag-and-drop handling
* Two-hand interaction
* Gesture customization
* GUI control panel
* Voice + gesture hybrid control
* Cross-platform support
* Deep learning based gesture recognition
* User-specific model personalization

---

## 🎯 Project Goal

The goal of this project is to explore how **Artificial Intelligence and Computer Vision can create a touchless human-computer interaction system**.

Instead of relying on a physical mouse, users can interact with their computer through natural hand movements and gestures.

---

## 👩‍💻 Author

**Isha Kaliraman**

B.Tech — Information Technology

GitHub:
https://github.com/ishaaaa64

---

## ⭐ If you find this project interesting

Give the repository a ⭐ and feel free to explore or improve the project.
