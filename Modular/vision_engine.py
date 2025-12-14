import cv2
import mediapipe as mp
import numpy as np
import config

class VisionEngine:
    def __init__(self, camera_index=config.DEFAULT_CAMERA_INDEX):
        self.cap = cv2.VideoCapture(camera_index)
        
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False, 
            max_num_hands=1, 
            min_detection_confidence=0.3, 
            min_tracking_confidence=0.3
        )
        self.mp_draw = mp.solutions.drawing_utils

    def get_frame_and_landmarks(self):
        ret, frame = self.cap.read()
        if not ret: return None, None

        # --- 1. NO FLIP (Standard View) ---
        # We removed cv2.flip(frame, 1)
        # Result: Right Hand appears on Left Side of screen.
        
        img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # 2. Process
        results = self.hands.process(img_rgb)
        data_aux = []

        if results.multi_hand_landmarks:
            # Process only the first hand
            hand_landmarks = results.multi_hand_landmarks[0]
            
            # Draw Skeleton
            if config.DRAW_SKELETON:
                self.mp_draw.draw_landmarks(frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)
            
            # Extraction
            wrist = hand_landmarks.landmark[0]
            wx, wy = wrist.x, wrist.y
            
            for lm in hand_landmarks.landmark:
                # Calculate Relative Distance
                rel_x = lm.x - wx
                rel_y = lm.y - wy
                
                # --- NO MATH INVERSION ---
                # Since the screen isn't flipped, we send raw X data to the AI
                data_aux.append(rel_x) 
                data_aux.append(rel_y)

        return frame, data_aux

    def change_camera(self, index):
        self.cap.release()
        self.cap = cv2.VideoCapture(index)

    def release(self):
        self.cap.release()