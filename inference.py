import numpy as np
import tensorflow as tf
import json
import os
import config

class SignPredictor:
    def __init__(self):
        self.model = self._load_model()
        self.labels = self._load_labels()
        
        # --- HOLD-TO-TYPE STATE VARIABLES ---
        self.last_char = None
        self.streak_count = 0
        # ------------------------------------

    def _load_model(self):
        try:
            return tf.keras.models.load_model(config.MODEL_PATH)
        except:
            return None

    def _load_labels(self):
        if os.path.exists(config.LABELS_PATH):
            with open(config.LABELS_PATH, 'r') as f:
                return json.load(f)
        return {str(i): "?" for i in range(29)}

    def predict(self, landmark_list):
        """Returns the raw character prediction."""
        if landmark_list is None or self.model is None:
            return None, 0.0

        input_data = np.array(landmark_list).reshape(1, 42)
        preds = self.model.predict(input_data, verbose=0)
        idx = np.argmax(preds)
        prob = preds[0][idx]

        if prob < config.CONFIDENCE_THRESHOLD:
            return None, prob
        
        label = self.labels.get(str(idx), "?")
        return label, prob

    def get_stable_prediction(self, raw_char):
        """
        THE HOLD-TO-TYPE LOGIC
        Only returns a letter if it has been held for 'HOLD_FRAMES' in a row.
        """
        # If input is None (Low confidence or no hand), reset streak
        if raw_char is None:
            self.streak_count = 0
            self.last_char = None
            return None

        # Check if the new char matches the previous frame
        if raw_char == self.last_char:
            self.streak_count += 1
        else:
            # Character changed! Reset counter.
            self.streak_count = 0
            self.last_char = raw_char

        # --- THE TRIGGER ---
        # If we hit the target (e.g., 12 frames), return the letter
        if self.streak_count == config.HOLD_FRAMES:
            return raw_char
            
        # Otherwise, return None (keep waiting)
        return None