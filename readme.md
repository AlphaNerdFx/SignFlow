# SignFlow: Real-Time ASL Translator 🤟

SignFlow is a robust computer vision application that translates American Sign Language (ASL) alphabets into text in real-time. Designed to bridge the communication gap for the deaf and hard-of-hearing community, it leverages *MediaPipe* for hand tracking and a custom-trained *TensorFlow* neural network for gesture classification.

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![TensorFlow](https://img.shields.io/badge/TensorFlow-2.x-orange)
![MediaPipe](https://img.shields.io/badge/MediaPipe-Vision-green)
![OpenCV](https://img.shields.io/badge/OpenCV-Computer%20Vision-red)

## 🚀 Key Features
*   *Real-Time Translation:* Instantly converts hand signs to text via webcam.
*   *Robust to Lighting:* Uses skeletal tracking (Landmarks) instead of raw images, making it work in dark rooms or messy backgrounds.
*   *29 Classes Supported:* A-Z, Space, Delete, and Nothing.
*   *Smart Smoothing:* Implements a prediction buffer to prevent text flickering and ensure stable output.

## 🛠 The Technology Stack
*   *Model:* Multi-Layer Perceptron (MLP) built with TensorFlow/Keras.
*   *Input Data:* 42 Coordinate points (x, y) extracted from 21 hand landmarks.
*   *Vision Pipeline:* MediaPipe Hands for detection + OpenCV for rendering.
*   *GUI:* Python Tkinter.

## 🧠 Engineering Methodology (The Pivot)
Our team initially developed a *Convolutional Neural Network (CNN)* to classify 64x64 grayscale images. However, testing revealed significant challenges:
1.  *Sensitivity to Lighting:* Shadows caused false predictions (e.g., 'T' vs 'A').
2.  *Background Noise:* Door frames and furniture were sometimes misidentified as hand shapes.

*The Solution:* We pivoted to a *Landmark-based approach*. Instead of analyzing pixels, we use MediaPipe to extract the geometric coordinates of the hand skeleton. This reduced our input dimension from 4,096 pixels to just 42 numbers, resulting in:
*   99% reduction in computational load.
*   Complete immunity to skin tone bias and background clutter.