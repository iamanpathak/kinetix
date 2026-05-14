# ==========================================
# actions.py - OS Control & Context Router
# ==========================================
import pyautogui
import time
import pygetwindow as gw

# Safety mechanisms for PyAutoGUI
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0 

# Ensure modifier keys are released upon initialization
pyautogui.keyUp('ctrl')
pyautogui.keyUp('shift')
pyautogui.keyUp('alt')

class ActionController:
    def __init__(self):
        self.screen_w, self.screen_h = pyautogui.size()
        self.last_action = {"trigger": 0, "swipe": 0, "play_pause": 0}
        self.anchors = {
            "scroll_y": None, "vol_y": None, "zoom_dist": None, 
            "swipe_x": None, "swipe_y": None, "palm_time": None, "trigger_time": None,
            "play_pause_locked": False
        }
        self.current_trigger = None 

    def get_active_app(self):
        """Identifies the currently active window to route context-specific commands."""
        try:
            window = gw.getActiveWindow()
            if window is None: return "desktop"
            title = window.title.lower()
            if any(b in title for b in ["chrome", "edge", "brave", "firefox"]): return "browser"
            if any(i in title for i in ["code", "visual studio", "pycharm"]): return "ide"
            if "powerpoint" in title or "presentation" in title: return "presentation"
            if "spotify" in title or "media" in title: return "media"
            return "general"
        except Exception:
            return "general"

    # --- ✋ NAVIGATION ENGINE ---
    def handle_navigation(self, hand_x, hand_y):
        """Handles spatial navigation, including swiping and media play/pause."""
        current_time = time.time()
        
        # Initialize anchor points for spatial tracking
        if self.anchors["palm_time"] is None:
            self.anchors["palm_time"] = current_time
            self.anchors["swipe_x"] = hand_x
            self.anchors["swipe_y"] = hand_y
            return "✋ NAVIGATION"

        dx = hand_x - self.anchors["swipe_x"]
        dy = hand_y - self.anchors["swipe_y"]

        # Detect static hover for Play/Pause functionality
        if abs(dx) < 0.15 and abs(dy) < 0.15:
            if current_time - self.anchors["palm_time"] > 0.15:
                if not self.anchors.get("play_pause_locked", False):
                    app = self.get_active_app()
                    if app == "browser": pyautogui.press('k') 
                    else: pyautogui.press('playpause') 
                    self.anchors["play_pause_locked"] = True 
                    return "⏯️ PLAY/PAUSE"
        else:
            self.anchors["palm_time"] = current_time 

        # Detect horizontal swipes with a 1-second cooldown
        if current_time - self.last_action["swipe"] > 1.0:
            app = self.get_active_app()
            if dx > 0.12: 
                if app in ["browser", "ide"]: pyautogui.hotkey('ctrl', 'tab')
                elif app == "presentation": pyautogui.press('right')
                elif app == "media": pyautogui.press('nexttrack')
                else: pyautogui.hotkey('win', 'right') 
                self.last_action["swipe"] = current_time
                self.anchors["swipe_x"] = hand_x 
                self.anchors["palm_time"] = current_time 
                return "👉 SWIPE RIGHT"
            elif dx < -0.12: 
                if app in ["browser", "ide"]: pyautogui.hotkey('ctrl', 'shift', 'tab')
                elif app == "presentation": pyautogui.press('left')
                elif app == "media": pyautogui.press('prevtrack')
                else: pyautogui.hotkey('win', 'left') 
                self.last_action["swipe"] = current_time
                self.anchors["swipe_x"] = hand_x 
                self.anchors["palm_time"] = current_time
                return "👈 SWIPE LEFT"
        return "✋ NAVIGATION"

    # --- 🔊 AUDIO CONTROL ---
    def volume_slider(self, hand_y):
        """Translates vertical hand movement into system volume adjustments."""
        if self.anchors["vol_y"] is None:
            self.anchors["vol_y"] = hand_y
            return "🔊 VOLUME MODE"
        
        dy = hand_y - self.anchors["vol_y"]
        if abs(dy) > 0.03: 
            if dy < 0: pyautogui.press('volumeup')
            else: pyautogui.press('volumedown')
            self.anchors["vol_y"] = hand_y 
        return "🔊 ADJUSTING..."

    # --- ✌️ SCROLL ENGINE ---
    def smooth_scroll(self, hand_y):
        """Translates vertical hand movement into smooth scrolling events."""
        if self.anchors["scroll_y"] is None:
            self.anchors["scroll_y"] = hand_y
            return "✌️ SCROLL MODE"
            
        dy = hand_y - self.anchors["scroll_y"]
        if abs(dy) > 0.01:
            pyautogui.scroll(int(-dy * 12000))
            self.anchors["scroll_y"] = hand_y
        return "✌️ SCROLLING..."

    # --- 🤌 TWO-HAND ZOOM ---
    def two_hand_zoom(self, current_dist):
        """Calculates distance between two hands to simulate pinch-to-zoom."""
        if self.anchors["zoom_dist"] is None:
            self.anchors["zoom_dist"] = current_dist
            
        diff = current_dist - self.anchors["zoom_dist"]
        
        if diff > 0.02: 
            pyautogui.hotkey('ctrl', '=') 
            self.anchors["zoom_dist"] = current_dist
        elif diff < -0.02:
            pyautogui.hotkey('ctrl', '-') 
            self.anchors["zoom_dist"] = current_dist

    # --- ⚡ SYSTEM TRIGGERS (THE COOLDOWN FIX) ---
    def trigger_action_held(self, key, name, gesture_name):
        """Executes one-time atomic actions with an enforced cooldown to prevent spamming."""
        current_time = time.time()
        
        # Initialize trigger validation state
        if self.current_trigger != gesture_name:
            self.current_trigger = gesture_name
            self.anchors["trigger_time"] = current_time
            return "⏳ Catching..."
         
        # Require holding the gesture for 0.1s to prevent accidental execution
        if current_time - self.anchors["trigger_time"] > 0.1:
            # Enforce a 1.5s cooldown interval between execution events
            if current_time - self.last_action["trigger"] > 1.5: 
                pyautogui.keyUp('ctrl') 
                if key == 'desktop': pyautogui.hotkey('win', 'd')
                else: pyautogui.press(key)
                self.last_action["trigger"] = current_time
                return f"⚡ {name}"
                
        return "⏳ Catching..."

    def reset_anchors(self):
        """Clears all spatial tracking anchors to reset state."""
        self.anchors["scroll_y"] = None
        self.anchors["vol_y"] = None
        self.anchors["zoom_dist"] = None
        self.anchors["swipe_x"] = None
        self.anchors["swipe_y"] = None
        self.anchors["palm_time"] = None
        self.anchors["play_pause_locked"] = False 
        self.current_trigger = None