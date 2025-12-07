import cv2
import numpy as np
import tensorflow as tf
import json
import os
from collections import Counter, deque
import config

class SignPredictor:
    def __init__(self):
        self.model = self._load_model()
        self.labels = self._load_labels()
        self.history = deque(maxlen=config.HISTORY_LENGTH)

    def _load_model(self):
        try:
            return tf.keras.models.load_model(config.MODEL_PATH)
        except:
            print("⚠️ Model not found.")
            return None

    def _load_labels(self):
        if os.path.exists(config.LABELS_PATH):
            with open(config.LABELS_PATH, 'r') as f:
                return json.load(f)
        return {str(i): "?" for i in range(29)}

    def preprocess_frame(self, roi_image):
        """
        --- Requirement #4: Strict Preprocessing Contract ---
        """
        try:
            # 1. Grayscale
            gray = cv2.cvtColor(roi_image, cv2.COLOR_BGR2GRAY)
            
            # 2. Resize to 64x64
            resized = cv2.resize(gray, (config.IMG_SIZE, config.IMG_SIZE))
            
            # (Optional Debug)
            cv2.imshow("Debug: AI Input", cv2.resize(resized, (200, 200), interpolation=cv2.INTER_NEAREST))
            
            # 3. Normalize
            normalized = resized / 255.0
            
            # 4. Reshape
            reshaped = normalized.reshape(1, config.IMG_SIZE, config.IMG_SIZE, config.CHANNELS)
            return reshaped
        except Exception as e:
            return None

    def predict(self, roi_image):
        """Returns (Label, Probability) only if high confidence."""
        processed = self.preprocess_frame(roi_image)
        if processed is None or self.model is None:
            return None, 0.0

        preds = self.model.predict(processed, verbose=0)
        idx = np.argmax(preds)
        prob = preds[0][idx]

        # --- Requirement #3: Threshold Logic ---
        if prob < config.CONFIDENCE_THRESHOLD:
            # If AI is unsure, return Nothing/None
            return None, prob
        
        label = self.labels.get(str(idx), "?")
        return label, prob

    def get_stable_prediction(self, raw_prediction):
        if raw_prediction:
            self.history.append(raw_prediction)
        
        if len(self.history) == config.HISTORY_LENGTH:
            most_common, count = Counter(self.history).most_common(1)[0]
            if count >= config.SMOOTHING_THRESHOLD:
                return most_common
        return None