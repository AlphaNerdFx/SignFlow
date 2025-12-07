import cv2
import numpy as np
import tensorflow as tf
from collections import Counter, deque
import config

class SignPredictor:
    def __init__(self):
        self.model = self._load_model()
        # Buffer to store last N predictions for smoothing
        self.history = deque(maxlen=config.HISTORY_LENGTH)

    def _load_model(self):
        """Safely attempts to load the model. Falls back to Dummy if missing."""
        try:
            model = tf.keras.models.load_model(config.MODEL_PATH)
            print(f"✅ SUCCESS: Loaded {config.MODEL_PATH}")
            return model
        except (OSError, IOError):
            print(f"⚠️ WARNING: {config.MODEL_PATH} not found. Using DUMMY mode.")
            return None

    def preprocess_frame(self, roi_image):
        """
        STRICT PREPROCESSING PROTOCOL
        1. Grayscale
        2. Resize (64x64)
        3. Normalize (/255.0)
        4. Reshape (1, 64, 64, 1)
        """
        try:
            # Step 1: Grayscale
            # Convert BGR (OpenCV default) to Grayscale
            gray = cv2.cvtColor(roi_image, cv2.COLOR_BGR2GRAY)
            
            # Step 2: Resize
            # Must match the input shape of the CNN (64x64)
            resized = cv2.resize(gray, (config.IMG_SIZE, config.IMG_SIZE))
            
            # Step 3: Normalization
            # Convert integer 0-255 to float 0.0-1.0
            normalized = resized / 255.0
            
            # Step 4: Reshape
            # Add batch dimension and channel dimension: (1, 64, 64, 1)
            reshaped = normalized.reshape(1, config.IMG_SIZE, config.IMG_SIZE, config.CHANNELS)
            
            return reshaped
        except Exception as e:
            print(f"Preprocessing Error: {e}")
            return None

    def predict(self, roi_image):
        """Returns (predicted_label, confidence_score)"""
        # Apply the strict preprocessing
        processed = self.preprocess_frame(roi_image)
        
        if processed is None:
            return None, 0.0

        if self.model:
            # Real Inference
            preds = self.model.predict(processed, verbose=0)
            
            # Get the index with the highest probability
            idx = np.argmax(preds)
            prob = preds[0][idx]
            
            # Map index to Label (e.g., 0 -> 'A')
            return config.LABELS[idx], prob
        else:
            # Dummy Inference (For testing GUI/Logic without model)
            return "A", 0.99

    def get_stable_prediction(self, raw_prediction):
        """
        Smoothing Logic:
        Only returns a character if it appears in >8 of the last 10 frames.
        """
        if raw_prediction:
            self.history.append(raw_prediction)

        if len(self.history) == config.HISTORY_LENGTH:
            # Find most common element
            most_common, count = Counter(self.history).most_common(1)[0]
            
            # Threshold Check (e.g., must see 'A' 8 times out of 10)
            if count >= config.CONFIDENCE_THRESHOLD:
                return most_common
        
        return None