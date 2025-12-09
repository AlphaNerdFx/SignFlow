import os

# --- CONTRACT ---
INPUT_SHAPE = (1, 42) 
MODEL_PATH = "signflow_landmark_model.h5"
LABELS_PATH = "landmark_labels.json"

# --- TUNING SETTINGS ---
CONFIDENCE_THRESHOLD = 0.50 

# Anti-Jitter: How much of the new frame do we trust? (0.7 = 70% new, 30% old)
SMOOTHING_FACTOR = 0.7 

# Hold-to-Type: How many frames to hold before typing? (approx 0.5 seconds at 30fps)
HOLD_FRAMES = 12