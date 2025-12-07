import os

# --- THE CONTRACT ---
IMG_SIZE = 64
CHANNELS = 1
MODEL_PATH = "signflow_model.h5"
LABELS_PATH = "labels.json"  # <--- New Pointer

# --- APP SETTINGS ---
ROI_BOX_SIZE = 300
HISTORY_LENGTH = 10
CONFIDENCE_THRESHOLD = 8
USE_MEDIAPIPE = False