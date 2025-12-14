# 🤟 SignFlow: Real-Time ASL Translator

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?style=for-the-badge&logo=python&logoColor=white)
![TensorFlow](https://img.shields.io/badge/TensorFlow-2.x-orange?style=for-the-badge&logo=tensorflow&logoColor=white)
![MediaPipe](https://img.shields.io/badge/MediaPipe-Vision-green?style=for-the-badge&logo=google&logoColor=white)
![OpenCV](https://img.shields.io/badge/OpenCV-Computer%20Vision-red?style=for-the-badge&logo=opencv&logoColor=white)
![Status](https://img.shields.io/badge/Status-Prototype-yellow?style=for-the-badge)

**SignFlow** is an assistive technology application designed to bridge the communication gap between the Deaf/Hard-of-Hearing community and non-signers. It leverages **Computer Vision** and **Deep Learning** to translate American Sign Language (ASL) gestures into text and speech in real-time.

---

## 🚀 Key Features

- **⚡ Real-Time Translation:** Low-latency inference (30+ FPS) using optimized MLP architecture.
- **🔁 Three Operation Modes:**
  - **Spell Mode (A-Z):** For fingerspelling names and specific terms.
  - **Talk Mode (Words):** Recognizes whole semantic gestures (e.g., "Hello", "Yes", "No").
  - **Hybrid Mode:** Seamlessly switches between spelling and words.
- **🗣️ Text-to-Speech (TTS):** Integrated voice synthesis to read translations aloud for accessibility.
- **🧠 Robust Engineering:**
  - **Translation Invariance:** Uses wrist-relative coordinates to detect hands anywhere in the frame.
  - **Anti-Jitter:** Implements exponential moving average smoothing for stable predictions.
  - **Hold-to-Type:** Smart logic to prevent accidental inputs during transitions.
- **🎨 Modern GUI:** A dark-mode, responsive interface built with `CustomTkinter`.

---

## 🛠️ Engineering Methodology & The Pivot

Our approach evolved significantly during development to ensure robustness in real-world environments.

### Phase 1: The CNN Approach (Deprecated)

Initially, we trained a Convolutional Neural Network (CNN) on 64x64 grayscale images.

- **The Problem:** The model suffered from the "Reality Gap." It was highly sensitive to lighting changes, skin tone bias and background noise (e.g., doorframes being misidentified as vertical hand shapes).

### Phase 2: The Landmark Pivot (Current Architecture)

We shifted to a **Geometric Feature Extraction** approach using Google MediaPipe.

1. **Feature Extraction:** We extract 21 skeletal landmarks (x, y coordinates) per frame.
2. **Normalization (The Wrist Tweak):** We implemented a custom algorithm to make coordinates relative to the **Wrist (Point 0)**.
```
   x_new = x_point - x_wrist
```
   This ensures the model works regardless of where the user stands in the frame.
3. **Model:** We trained a lightweight **Multi-Layer Perceptron (MLP)** on these coordinate vectors.
   - **Result:** 99% reduction in input size (4096 pixels → 42 numbers) and complete immunity to lighting/background issues.

---

## 📂 Project Structure
```text
SignFlow/
│
├── code/
│   ├── main_gui.py                # Application Entry Point (UI & Loop)
│   ├── logic_engine.py               # Backend Logic (TTS, Sentence Builder)
│   ├── SignFlow_V2_Pipeline.ipynb # Training Notebook (Google Colab)
│   └── config.py          # Utility to record custom datasets
│
├── models/
│   ├── Hybrid.h5  # The Hybrid Brain
│   ├── Letters.h5               # Specialized Alphabet Model
│   ├── Words.h5                 # Specialized Word Model
│   └── (Corresponding .json label files)
│
├── data/
│   └── raw_videos/               # Source videos for custom words
│
├── assets/                       # UI Assets and Screenshots
└── requirements.txt              # Dependency list
```

---

## ⚙️ Installation & Setup

### Prerequisites

- Python 3.8 - 3.11 (Python 3.12 is not yet supported by MediaPipe)
- A Webcam (or Camo Studio)

### 1. Clone the Repository
```bash
git clone https://github.com/YourUsername/SignFlow.git
cd SignFlow
```

### 2. Create a Virtual Environment (Recommended)
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install customtkinter opencv-python mediapipe tensorflow pyttsx3 pillow
```

### 4. Run the Application
```bash
python code/main_gui.py
```

---

## 🧪 Usage Guide

1. **Select Camera:** Use the dropdown menu to select your input device (0 for Laptop Webcam, 1 for External/Camo).
2. **Choose Mode:**
   - Use Spell Mode to type your name.
   - Switch to Talk Mode for common phrases.
3. **Signing:** Hold a sign steady for 0.5 seconds to confirm it. The progress bar/logic will lock it in.
4. **Speech:** Press the Green "Speak" button to hear the sentence.

---

## 📊 Dataset Sources

We utilized a hybrid dataset strategy:

- **ASL Alphabet:** Kaggle Dataset (87,000 images) for static letters.
- **Custom Data:** Self-recorded video samples for semantic gestures processed through our custom MediaPipe extraction pipeline.

---

## 📜 License

This project is licensed under the MIT License.

## 🤝 Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## 📧 Contact

For questions or collaboration opportunities, reach out at bhmounir04@gmail.com
