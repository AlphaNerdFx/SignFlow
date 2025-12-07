import cv2
import numpy as np
import config

# --- SAFE IMPORT: Handle missing MediaPipe gracefully ---
try:
    import mediapipe as mp
    MEDIAPIPE_AVAILABLE = True
except ImportError:
    MEDIAPIPE_AVAILABLE = False
    print("\n⚠️ MEDIA-PIPE ERROR: Library still not found.")
    print("👉 Did you run: 'py -3.10 -m pip install mediapipe'?\n")

class CameraStream:
    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        
        # Setup MediaPipe ONLY if available
        if MEDIAPIPE_AVAILABLE:
            self.mp_hands = mp.solutions.hands
            self.hands = self.mp_hands.Hands(
                static_image_mode=False,
                max_num_hands=1,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5
            )
            self.mp_draw = mp.solutions.drawing_utils

    def get_frame(self):
        ret, frame = self.cap.read()
        
        # Fallback
        if not ret:
            blank = np.zeros((480, 640, 3), dtype=np.uint8)
            cv2.putText(blank, "CAMERA ERROR", (50, 240), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            return blank, None

        # Mirror the Camera
        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape
        
        roi_img = None
        
        # --- PATH 1: Dynamic MediaPipe Tracking ---
        if MEDIAPIPE_AVAILABLE:
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.hands.process(rgb_frame)

            if results.multi_hand_landmarks:
                hand_lms = results.multi_hand_landmarks[0]
                self.mp_draw.draw_landmarks(frame, hand_lms, self.mp_hands.HAND_CONNECTIONS)
                
                # Calculate Bounding Box
                x_list = [lm.x for lm in hand_lms.landmark]
                y_list = [lm.y for lm in hand_lms.landmark]
                
                # Convert to pixels
                x_min, x_max = int(min(x_list) * w), int(max(x_list) * w)
                y_min, y_max = int(min(y_list) * h), int(max(y_list) * h)
                
                # Make Square + Padding
                box_w = x_max - x_min
                box_h = y_max - y_min
                padding = 50 
                square_len = max(box_w, box_h) + padding
                
                cx, cy = x_min + box_w // 2, y_min + box_h // 2
                x1 = max(0, cx - square_len // 2)
                y1 = max(0, cy - square_len // 2)
                x2 = min(w, cx + square_len // 2)
                y2 = min(h, cy + square_len // 2)
                
                # Draw Box
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, "Tracking", (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2)
                
                # Crop
                if x2 > x1 and y2 > y1:
                    roi_img = frame[y1:y2, x1:x2]
            else:
                cv2.putText(frame, "Show Hand", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        # --- PATH 2: Fixed Box Fallback ---
        else:
            box_size = 300
            cx, cy = w // 2, h // 2
            cx += 50 # Move right to avoid face
            
            x1 = cx - (box_size // 2)
            y1 = cy - (box_size // 2)
            x2 = cx + (box_size // 2)
            y2 = cy + (box_size // 2)

            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, "FIXED MODE", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            if x2 > x1 and y2 > y1:
                roi_img = frame[y1:y2, x1:x2]

        return frame, roi_img

    def release(self):
        self.cap.release()