import cv2
import mediapipe as mp
import numpy as np
import config

class CameraStream:
    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        
        # --- ANTI-JITTER VARIABLE ---
        # Stores the previous frame's coordinates
        self.prev_coords = None 
        # ----------------------------

        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.3, 
            min_tracking_confidence=0.3
        )
        self.mp_draw = mp.solutions.drawing_utils

    def get_frame(self):
        ret, frame = self.cap.read()
        
        if not ret:
            blank = np.zeros((480, 640, 3), dtype=np.uint8)
            cv2.putText(blank, "CAMERA ERROR", (50, 240), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            return blank, None

        # Digital Zoom (1.5x)
        h, w, _ = frame.shape
        zoom = 1.5
        nh, nw = int(h/zoom), int(w/zoom)
        y1, x1 = (h-nh)//2, (w-nw)//2
        frame = frame[y1:y1+nh, x1:x1+nw]
        frame = cv2.resize(frame, (w, h))

        # Mirror
        frame = cv2.flip(frame, 1)
        
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb_frame)
        
        data_aux = None

        if results.multi_hand_landmarks:
            hand_landmarks = results.multi_hand_landmarks[0]
            self.mp_draw.draw_landmarks(frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)
            
            # Extract Raw Coordinates
            raw_list = []
            for lm in hand_landmarks.landmark:
                true_x = 1.0 - lm.x  # Un-mirror X
                raw_list.append(true_x)
                raw_list.append(lm.y)
            
            # --- START ANTI-JITTER LOGIC ---
            curr_coords = np.array(raw_list)
            
            if self.prev_coords is None:
                # First frame: No history, just trust the current frame
                self.prev_coords = curr_coords
                final_coords = curr_coords
            else:
                # Math: New = (Current * 0.7) + (Old * 0.3)
                final_coords = (curr_coords * config.SMOOTHING_FACTOR) + (self.prev_coords * (1.0 - config.SMOOTHING_FACTOR))
                self.prev_coords = final_coords # Update history
                
            # Convert back to list for the predictor
            data_aux = final_coords.tolist()
            # -------------------------------
            
        else:
            # If hand is lost, reset the jitter buffer
            self.prev_coords = None
            cv2.putText(frame, "Show Hand", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        return frame, data_aux

    def release(self):
        self.cap.release()