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
        self.labels = self._load_labels() # <--- Load labels dynamically
        self.history = deque(maxlen=config.HISTORY_LENGTH)

    def _load_model(self):
        try:
            model = tf.keras.models.load_model(config.MODEL_PATH)
            print(f"✅ SUCCESS: Loaded {config.MODEL_PATH}")
            return model
        except (OSError, IOError):
            print(f"⚠️ WARNING: {config.MODEL_PATH} not found. Using DUMMY mode.")
            return None

    def _load_labels(self):
        """Loads the labels.json file provided by the Model Engineer."""
        if not os.path.exists(config.LABELS_PATH):
            print(f"⚠️ ERROR: {config.LABELS_PATH} not found! Using fallback.")
            return {str(i): "?" for i in range(29)}
        
        try:
            with open(config.LABELS_PATH, 'r') as f:
                # Returns dict like {"0": "A", "1": "B" ...}
                return json.load(f)
        except Exception as e:
            print(f"Error loading labels: {e}")
            return {}

    def preprocess_frame(self, roi_image):
        """
        STRICT PROTOCOL: ROI -> Gray -> Resize(64) -> Norm(/255) -> Reshape
        """
        try:
            # 1. Grayscale
            gray = cv2.cvtColor(roi_image, cv2.COLOR_BGR2GRAY)
            
            # 2. Resize to 64x64
            resized = cv2.resize(gray, (config.IMG_SIZE, config.IMG_SIZE))
            
            # --- VISUAL DEBUGGING START ---
            # Show exactly what the AI sees (64x64 image)
            # We scale it up x4 just so you can see it on your monitor comfortably
            debug_view = cv2.resize(resized, (256, 256), interpolation=cv2.INTER_NEAREST)
            cv2.imshow("Debug: AI Input", debug_view)
            # ------------------------------

            # 3. Normalize (0.0 to 1.0)
            normalized = resized / 255.0
            
            # 4. Reshape (Batch, H, W, Channels)
            reshaped = normalized.reshape(1, config.IMG_SIZE, config.IMG_SIZE, config.CHANNELS)
            
            return reshaped
        except Exception as e:
            print(f"Preprocessing Error: {e}")
            return None

    def predict(self, roi_image):
        """Returns (predicted_label, confidence_score)"""
        processed = self.preprocess_frame(roi_image)
        if processed is None:
            return None, 0.0

        if self.model:
            # Predict
            preds = self.model.predict(processed, verbose=0)
            idx = np.argmax(preds)
            prob = preds[0][idx]
            
            # Map Index -> Label using the loaded JSON
            # JSON keys are strings ("0"), numpy index is int (0), so cast to string
            label = self.labels.get(str(idx), "Unknown")
            return label, prob
        else:
            return "A", 0.99

    def get_stable_prediction(self, raw_prediction):
        if raw_prediction:
            self.history.append(raw_prediction)

        if len(self.history) == config.HISTORY_LENGTH:
            most_common, count = Counter(self.history).most_common(1)[0]
            if count >= config.CONFIDENCE_THRESHOLD:
                return most_common
        return None