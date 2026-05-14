# ==========================================
# main.py - Kinetix Engine Final Build
# ==========================================
import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import time
import math
import sys
import os
import numpy as np 

import config
from actions import ActionController

def resource_path(relative_path):
    """Resolves the absolute path to resources, accommodating PyInstaller environments."""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

print("Booting Kinetix OS Controller...")

# Initialize the Mediapipe gesture recognition model
base_options = python.BaseOptions(model_asset_path=resource_path(config.MODEL_PATH))
options = vision.GestureRecognizerOptions(
    base_options=base_options,
    running_mode=vision.RunningMode.VIDEO,
    num_hands=config.MAX_HANDS, 
    min_tracking_confidence=config.MIN_CONFIDENCE
)
recognizer = vision.GestureRecognizer.create_from_options(options)

# Configure the camera capture stream
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.CAM_WIDTH)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.CAM_HEIGHT)
cap.set(cv2.CAP_PROP_FPS, config.FPS)
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

controller = ActionController()

hand_lost_time = 0
last_timestamp_ms = 0 
last_zoom_time = 0 

if config.GHOST_MODE:
    print("\n👻 GHOST MODE ACTIVE: Running invisibly.")
else:
    print("\n🟢 Kinetix System Online!")

while cap.isOpened():
    success, frame = cap.read()
    if not success: break

    # Pre-process the frame for the ML pipeline
    frame = cv2.flip(frame, 1)
    rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    safe_rgb_image = np.ascontiguousarray(rgb_image.copy())
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=safe_rgb_image)
    
    current_timestamp_ms = int(time.time() * 1000)
    if current_timestamp_ms <= last_timestamp_ms:
        current_timestamp_ms = last_timestamp_ms + 1
    last_timestamp_ms = current_timestamp_ms
    
    results = recognizer.recognize_for_video(mp_image, current_timestamp_ms)
    
    hud_text = "Idle"
    hud_color = (200, 200, 200) 
    
    if results.gestures and results.hand_landmarks:
        hand_lost_time = 0 
        num_hands = len(results.hand_landmarks)
        
        # Spatial Filter: Merge overlapping hands tracking the same physical limb
        if num_hands == 2:
            w1 = results.hand_landmarks[0][0] 
            w2 = results.hand_landmarks[1][0] 
            wrist_dist = math.hypot(w1.x - w2.x, w1.y - w2.y)
            if wrist_dist < 0.20:
                num_hands = 1 
        
        # --- 2 HANDS: ZOOM ROUTING ---
        if num_hands == 2:
            last_zoom_time = time.time() 
            hand1, hand2 = results.hand_landmarks[0], results.hand_landmarks[1]
            dist = math.hypot(hand1[8].x - hand2[8].x, hand1[8].y - hand2[8].y)
            controller.two_hand_zoom(dist)
            hud_text, hud_color = "🤌 ZOOMING", (0, 165, 255)
            
        # --- 1 HAND: GESTURE ROUTING ---
        elif num_hands == 1:
            controller.anchors["zoom_dist"] = None 
            
            # Zoom Shield: Enforce a 0.4s buffer to prevent erroneous single-hand triggers post-zoom
            if time.time() - last_zoom_time < 0.4:
                hud_text = "⏳ ZOOM SHIELD"
                hud_color = (150, 150, 150)
            else:
                # Core single-hand recognition and routing logic
                hand = results.hand_landmarks[0]
                gesture = results.gestures[0][0].category_name
                hand_x, hand_y = hand[9].x, hand[9].y
                in_typing_zone = hand[0].y > 0.95
                
                if in_typing_zone and gesture in ["Closed_Fist"]:
                    hud_text = "⌨️ TYPING SHIELD"
                    hud_color = (100, 100, 100)
                    controller.reset_anchors()
                    
                elif gesture == "Open_Palm":
                    hud_text = controller.handle_navigation(hand_x, hand_y)
                    hud_color = (255, 255, 0)
                
                elif gesture == "Victory":
                    hud_text = controller.smooth_scroll(hand_y)
                    hud_color = (255, 105, 180)
                
                elif gesture == "ILoveYou":
                    hud_text = controller.volume_slider(hand_y)
                    hud_color = (255, 0, 255)
                
                elif gesture == "Closed_Fist":
                    hud_text = controller.trigger_action_held('esc', 'ESCAPE', gesture)
                    hud_color = (0, 0, 255)
                
                elif gesture == "Thumb_Down":
                    hud_text = controller.trigger_action_held('desktop', 'DESKTOP', gesture)
                    hud_color = (0, 0, 255)

                if gesture not in ["Open_Palm", "Victory", "ILoveYou", "Closed_Fist", "Thumb_Down", "None"]:
                    controller.reset_anchors()
    else:
        # Handle loss of tracking gracefully by resetting anchors after a brief delay
        if hand_lost_time == 0:
            hand_lost_time = time.time()
            
        if time.time() - hand_lost_time > 0.3:
            controller.reset_anchors()

    # Render HUD if running in visible mode
    if not config.GHOST_MODE:
        cv2.rectangle(frame, (10, 10), (380, 60), (20, 20, 20), -1) 
        cv2.putText(frame, hud_text, (20, 45), cv2.FONT_HERSHEY_SIMPLEX, 1, hud_color, 2)
        cv2.imshow('Kinetix OS', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'): break
    else:
        time.sleep(0.01)

cap.release()
cv2.destroyAllWindows()