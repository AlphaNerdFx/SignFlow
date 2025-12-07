# config.py
import os

IMG_SIZE = 64
CHANNELS = 1
MODEL_PATH = "signflow_model.h5"
LABELS_PATH = "labels.json"

# Thresholds
CONFIDENCE_THRESHOLD = 0.80  # <--- Requirement #3 (80% confidence)
HISTORY_LENGTH = 10
SMOOTHING_THRESHOLD = 8