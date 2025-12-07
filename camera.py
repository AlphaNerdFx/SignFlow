import cv2
import numpy as np
import config

class CameraStream:
    def __init__(self):
        # Try to open the default camera
        self.cap = cv2.VideoCapture(0)

    def get_frame(self):
        ret, frame = self.cap.read()
        
        if not ret:
            # Fallback for camera failure
            h, w = 480, 640
            frame = np.zeros((h, w, 3), dtype=np.uint8)
            cv2.putText(frame, "CAMERA NOT FOUND", (50, 240), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            return frame, None

        # 1. Flip horizontally (Mirror effect)
        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape
        
        # 2. Draw Fixed Green Box (ROI)
        # Center the box
        x_center, y_center = w // 2, h // 2
        half = config.ROI_BOX_SIZE // 2
        
        x1 = x_center - half
        y1 = y_center - half
        x2 = x_center + half
        y2 = y_center + half

        # Draw the Green Box
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(frame, "Put Hand Here", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        # 3. Crop logic
        roi_img = None
        if x2 > x1 and y2 > y1:
            roi_img = frame[y1:y2, x1:x2]
        
        return frame, roi_img

    def release(self):
        self.cap.release()