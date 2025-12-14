import tensorflow as tf
import numpy as np
import json
import os
import config

class AIEngine:
    def __init__(self):
        self.model = None
        self.labels = []
        # Load Default Mode
        self.switch_mode("Spell")

    def switch_mode(self, mode_name):
        if mode_name not in config.MODES_CONFIG:
            print(f"❌ Error: Mode {mode_name} not defined in config.")
            return

        print(f"🔄 Brain Engine: Switching to {mode_name} Mode...")
        paths = config.MODES_CONFIG[mode_name]
        
        if not os.path.exists(paths["model"]) or not os.path.exists(paths["labels"]):
            print(f"⚠️ Missing files for {mode_name}. Check models folder.")
            return

        # Load Model
        try:
            self.model = tf.keras.models.load_model(paths["model"])
            with open(paths["labels"], 'r') as f:
                label_map = json.load(f)
                self.labels = [label_map[str(i)] for i in range(len(label_map))]
            print(f"✅ Loaded {mode_name} Successfully. Labels: {len(self.labels)}")
        except Exception as e:
            print(f"❌ CRITICAL ERROR LOADING MODEL: {e}")

    def predict(self, landmark_list):
        if not landmark_list or self.model is None:
            return "--", 0.0

        # --- DEBUG CHECK 1: DATA SHAPE ---
        # Ensure we have exactly 42 coordinates (21 points * 2 x/y)
        if len(landmark_list) != 42:
            print(f"⚠️ Shape Error: Expected 42 coords, got {len(landmark_list)}")
            return "--", 0.0

        # Reshape
        input_data = np.array(landmark_list).reshape(1, 42)
        
        # Inference
        prediction = self.model.predict(input_data, verbose=0)
        idx = np.argmax(prediction)
        confidence = np.max(prediction)

        # --- DEBUG CHECK 2: WHAT DOES THE AI SEE? ---
        # This prints what the AI thinks it sees to your VS Code Terminal
        predicted_char = self.labels[idx]
        print(f"AI Sees: {predicted_char} | Confidence: {confidence:.2f}")

        if confidence > config.CONFIDENCE_THRESHOLD:
            return predicted_char, confidence
        
        return "--", confidence