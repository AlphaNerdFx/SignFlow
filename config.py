# config.py (Updated for v1.0.0 Model)

IMG_SIZE = 64
CHANNELS = 1
MODEL_PATH = "signflow_model.h5"

# Derived from teammate's labels.json
LABELS = [
    'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 
    'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', 
    'del', 'nothing', 'space'
]

# Settings
ROI_BOX_SIZE = 300
HISTORY_LENGTH = 10
CONFIDENCE_THRESHOLD = 8
USE_MEDIAPIPE = False # Set to True if you fixed the install, otherwise False# config.py (Updated for v1.0.0 Model)

IMG_SIZE = 64
CHANNELS = 1
MODEL_PATH = "signflow_model.h5"

# Derived from teammate's labels.json
LABELS = [
    'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 
    'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', 
    'del', 'nothing', 'space'
]

# Settings
ROI_BOX_SIZE = 300
HISTORY_LENGTH = 10
CONFIDENCE_THRESHOLD = 8
USE_MEDIAPIPE = False # Set to True if you fixed the install, otherwise False