code = r"""import cv2
import mediapipe as mp
import numpy as np
import config

class CameraStream:
    def __init__(self):
        # Try to open the default camera
        self.cap = cv2.VideoCapture(0)
        
        # MediaPipe Setup
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.5
        )
        self.mp_draw = mp.solutions.drawing_utils

    def get_frame(self):
        # 1. Try to read from the camera
        try:
            ret, frame = self.cap.read()
        except:
            ret = False
            frame = None

        # --- CRITICAL FIX FOR WSL / NO CAMERA ---
        if not ret or frame is None:
            # Create a black 640x480 dummy image
            h, w = 480, 640
            frame = np.zeros((h, w, 3), dtype=np.uint8)
            
            # Write error text on the screen
            cv2.putText(frame, "CAMERA NOT FOUND", (50, 200), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            cv2.putText(frame, "WSL cannot see Webcam", (50, 250), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 1)
            
            # Return tuple so main.py doesn't crash
            return frame, None
        # ----------------------------------------

        # 2. Flip horizontally (Mirror effect)
        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape
        
        roi_img = None
        
        # Logic for determining the Box Coordinates
        x1, y1, x2, y2 = 0, 0, 0, 0
        
        if config.USE_MEDIAPIPE:
            # Detect Hands
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.hands.process(rgb_frame)
            
            if results.multi_hand_landmarks:
                for hand_lms in results.multi_hand_landmarks:
                    self.mp_draw.draw_landmarks(frame, hand_lms, self.mp_hands.HAND_CONNECTIONS)
                    
                    # Calculate Bounding Box
                    x_list = [lm.x for lm in hand_lms.landmark]
                    y_list = [lm.y for lm in hand_lms.landmark]
                    
                    pad = 40
                    x1 = max(0, int(min(x_list) * w) - pad)
                    y1 = max(0, int(min(y_list) * h) - pad)
                    x2 = min(w, int(max(x_list) * w) + pad)
                    y2 = min(h, int(max(y_list) * h) + pad)
            else:
                x1, y1, x2, y2 = self._get_fixed_roi(w, h)
        else:
            x1, y1, x2, y2 = self._get_fixed_roi(w, h)

        # Draw the Green Box
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(frame, "Scan Area", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        # Crop logic
        if x2 > x1 and y2 > y1:
            roi_img = frame[y1:y2, x1:x2]
        
        return frame, roi_img

    def _get_fixed_roi(self, w, h):
        x_center, y_center = w // 2, h // 2
        half = config.ROI_BOX_SIZE // 2
        return x_center - half, y_center - half, x_center + half, y_center + half

    def release(self):
        self.cap.release()
"""

with open("camera.py", "w") as f:
    f.write(code)

print("✅ camera.py has been overwritten successfully!")

