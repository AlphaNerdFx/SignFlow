# 🤟 SignFlow: Real-Time ASL Translator

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?style=for-the-badge&logo=python&logoColor=white)
![TensorFlow](https://img.shields.io/badge/TensorFlow-2.x-orange?style=for-the-badge&logo=tensorflow&logoColor=white)
![MediaPipe](https://img.shields.io/badge/MediaPipe-Vision-green?style=for-the-badge&logo=google&logoColor=white)
![OpenCV](https://img.shields.io/badge/OpenCV-Computer%20Vision-red?style=for-the-badge&logo=opencv&logoColor=white)
![Status](https://img.shields.io/badge/Status-Prototype-yellow?style=for-the-badge)

**SignFlow** is an assistive technology application designed to bridge the communication gap between the Deaf/Hard-of-Hearing community and non-signers. It leverages **Computer Vision** and **Deep Learning** to translate American Sign Language gestures into text and speech in real-time.

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

##⚙️ Installation & Setup

Prerequisites

Operating System: Windows 10 or 11.

- Python: You must have Python 3.10 installed.
During installation, ensure "Add Python to PATH" is checked.
Webcam: Any standard built-in or external USB webcam.

1. Clone the Repository
```
git clone https://github.com/YourUsername/SignFlow.git
cd SignFlow
```
2. Launch the Application (One-Click Setup)
The project includes an automated setup script for ease of use.
a. Navigate to the cloned SignFlow directory.
b. Double-click START_APP.bat.
c. This script will automatically:
  - Check for Python 3.10.
  - Create a dedicated Python virtual environment (env/).
  - Install all necessary Python dependencies (TensorFlow, MediaPipe, CustomTkinter, etc.) into the virtual environment.
  - Launch main_gui.py.
    
Note: The first launch will take a few minutes to set up the environment and download libraries. Subsequent launches will be significantly faster.
---
## ⚠️ Troubleshooting Common Issues
1. "DLL Load Failed" or TensorFlow Crash
Cause: Your system is missing essential Microsoft Visual C++ Runtime libraries.
Fix: We have included the required installer. Double-click vc_redist.x64.exe in the project root, install it, and restart your computer.

2. "Python 3.10 is missing!" Error
Cause: The START_APP.bat script could not find Python 3.10 on your system.
Fix: Manually install Python 3.10 from python.org/downloads/release/python-31011/ and ensure "Add Python to PATH" is selected during installation.

3. Black Camera Screen
Cause: The application might be trying to access the wrong camera index (e.g., a virtual camera, or a non-existent one).
Fix: In the application's sidebar, use the "Video Source" dropdown to try different camera indices (e.g., Camera 0, Camera 1). Ensure your webcam is not in use by another application.
## 🧪 Usage Guide

1. Select Camera: Choose your active webcam from the "Video Source" dropdown in the sidebar.
2. Choose Mode:
3. Click "🔤 Spell Mode" for letter-by-letter translation (e.g., typing a name).
4. Click "💬 Talk Mode" for recognizing common words or phrases.
5. Click "🚀 Hybrid Mode" to switch dynamically (if implemented in your brain_engine).
6. Signing: Position your hand clearly in front of the camera. Hold a sign steady for approximately 0.5 seconds for the system to confirm and type it.
7. Speech Output: Click the "🔊 SPEAK" button to hear the current translated sentence.
8. Transcript Control: Use "⌫ BACKSPACE" to delete the last character or "🗑 CLEAR ALL" to reset the transcript.
---

## 📊 Dataset Sources

We utilized a hybrid dataset strategy:

- **ASL Alphabet:** Kaggle Dataset (87,000 images) for static letters.
- **Custom Data:** Self-recorded video samples for semantic gestures processed through our custom MediaPipe extraction pipeline.

---

## 📜 License

This project is licensed under the MIT License.

## 🤝 Contributing

Contributions are welcome! Feel free to open an issue or submit a pull request on our GitHub repository.

## 📧 Contact

For questions or collaboration opportunities, reach out to the project authors:
- Youssef Larbi: yousseflarbiprofessional@gmail.com
- Mounir: bhmounir04@gmail.com
