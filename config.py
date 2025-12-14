import os

# --- PATH CALCULATION (Bulletproof) ---
# This gets the folder where 'config.py' is located (i.e., 'Modular')
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Construct path to models folder
MODELS_DIR = os.path.join(BASE_DIR, 'models')

# --- MODEL PATHS MAP ---
MODES_CONFIG = {
    "Spell": {
        "model": os.path.join(MODELS_DIR, 'Letters.h5'),
        "labels": os.path.join(MODELS_DIR, 'Letters.json')
    },
    "Talk": {
        "model": os.path.join(MODELS_DIR, 'Words.h5'),
        "labels": os.path.join(MODELS_DIR, 'Words.json')
    },
    "Hybrid": {
        "model": os.path.join(MODELS_DIR, 'Hybrid.h5'),
        "labels": os.path.join(MODELS_DIR, 'Hybrid.json')
    }
}

# --- TUNING SETTINGS ---
CONFIDENCE_THRESHOLD = 0.50 
HOLD_FRAMES = 5
SMOOTHING_FACTOR = 0.7
AUTO_SPACE_TIME = 2.5

# --- VISUAL SETTINGS ---
# This fixes the AttributeError you saw earlier
DRAW_SKELETON = True     
THEME_MODE = "Dark"

# --- HARDWARE ---
DEFAULT_CAMERA_INDEX = 0