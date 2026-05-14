# ==========================================
# config.py - Kinetix OS Settings
# ==========================================

# Set to True to suppress the camera feed UI and run as a background process
GHOST_MODE = False 

# Camera hardware constraints (optimized for low latency)
CAM_WIDTH = 640
CAM_HEIGHT = 480
FPS = 30

# Computer Vision and ML Configuration
MODEL_PATH = 'gesture_recognizer.task'
MAX_HANDS = 2 
MIN_CONFIDENCE = 0.70