"""
Real-Time Sign Language Translator GUI (Integrated)
"""

import customtkinter as ctk
from PIL import Image, ImageTk
import cv2
import numpy as np
import tensorflow as tf
import mediapipe as mp
import json
import os
import threading

# Import your backend logic
from app_utils import SentenceBuilder, TextToSpeech

# Set appearance mode and color theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class ASLTranslatorGUI:
    def __init__(self):
        self.window = ctk.CTk()
        self.window.title("SignFlow - Real Time Translator")
        self.window.geometry("1400x800")
        
        # --- 1. SETUP BACKEND ---
        print("⏳ Loading Model & Engine...")
        self.cwd = os.getcwd()
        self.model_path = os.path.join(self.cwd, 'models', 'signflow_landmark_model_v3.h5')
        self.labels_path = os.path.join(self.cwd, 'models', 'landmark_labels_v3.json')
        
        # Load AI
        self.model = tf.keras.models.load_model(self.model_path)
        with open(self.labels_path, 'r') as f:
            label_map = json.load(f)
        # Sort labels correctly
        self.labels = [label_map[str(i)] for i in range(len(label_map))]
        
        # Load Logic
        self.sentence_builder = SentenceBuilder()
        self.tts = TextToSpeech()
        
        # Setup MediaPipe
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False, 
            max_num_hands=1, 
            min_detection_confidence=0.5
        )
        self.mp_draw = mp.solutions.drawing_utils
        
        # Video variables
        self.cap = None
        self.camera_index = 0
        self.is_running = False
        
        # Build the GUI
        self.setup_gui()
        
        # Start video feed
        self.start_camera()
        print("✅ System Ready.")
        
    def setup_gui(self):
        """Create the main GUI layout"""
        self.window.grid_columnconfigure(0, weight=2)
        self.window.grid_columnconfigure(1, weight=1)
        self.window.grid_rowconfigure(0, weight=1)
        
        # === LEFT SIDE: VIDEO ===
        self.video_frame = ctk.CTkFrame(self.window, corner_radius=15)
        self.video_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        
        video_title = ctk.CTkLabel(self.video_frame, text="📹 Live Camera Feed", font=ctk.CTkFont(size=24, weight="bold"))
        video_title.pack(pady=(20, 10))
        
        # Camera Selector
        cam_frame = ctk.CTkFrame(self.video_frame, fg_color="transparent")
        cam_frame.pack(pady=5)
        ctk.CTkLabel(cam_frame, text="Camera Input:").pack(side="left", padx=5)
        self.camera_selector = ctk.CTkOptionMenu(cam_frame, values=["Camera 0", "Camera 1", "Camera 2"], command=self.change_camera)
        self.camera_selector.pack(side="left", padx=5)
        
        self.video_label = ctk.CTkLabel(self.video_frame, text="", width=800, height=600)
        self.video_label.pack(padx=20, pady=20, expand=True, fill="both")
        
        # === RIGHT SIDE: OUTPUT ===
        self.control_frame = ctk.CTkFrame(self.window, corner_radius=15)
        self.control_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        
        ctk.CTkLabel(self.control_frame, text="🤟 Translation Output", font=ctk.CTkFont(size=22, weight="bold")).pack(pady=20)
        
        # Current Sign
        ctk.CTkLabel(self.control_frame, text="Detected Sign:", font=ctk.CTkFont(size=14), anchor="w").pack(pady=(10,0), padx=20, anchor="w")
        self.current_prediction_box = ctk.CTkLabel(
            self.control_frame, text="--", font=ctk.CTkFont(size=48, weight="bold"),
            fg_color=("#2B2B2B", "#1A1A1A"), corner_radius=10, height=100
        )
        self.current_prediction_box.pack(pady=10, padx=20, fill="x")
        
        # Sentence History
        ctk.CTkLabel(self.control_frame, text="Full Sentence:", font=ctk.CTkFont(size=14), anchor="w").pack(pady=(20,0), padx=20, anchor="w")
        self.text_display = ctk.CTkTextbox(self.control_frame, font=ctk.CTkFont(size=18), wrap="word", height=200)
        self.text_display.pack(pady=10, padx=20, fill="both", expand=True)
        
        # Buttons
        btn_frame = ctk.CTkFrame(self.control_frame, fg_color="transparent")
        btn_frame.pack(pady=20, padx=20, fill="x")
        
        ctk.CTkButton(btn_frame, text="🔊 Speak", command=self.speak_text, fg_color="#28A745", hover_color="#218838", height=45).pack(pady=5, fill="x")
        ctk.CTkButton(btn_frame, text="🗑️ Clear", command=self.clear_history, fg_color="#DC3545", hover_color="#C82333", height=45).pack(pady=5, fill="x")
        ctk.CTkButton(btn_frame, text="❌ Exit", command=self.on_closing, fg_color="#6C757D", hover_color="#5A6268", height=45).pack(pady=5, fill="x")

        self.status_label = ctk.CTkLabel(self.control_frame, text="Status: Ready", text_color="gray")
        self.status_label.pack(pady=10)

    def start_camera(self):
        if self.cap is not None: self.cap.release()
        self.cap = cv2.VideoCapture(self.camera_index)
        if not self.cap.isOpened():
            self.status_label.configure(text="Error: No Camera Found", text_color="red")
            return
        self.is_running = True
        self.status_label.configure(text="Camera Active", text_color="green")
        self.update_frame()
        
    def change_camera(self, choice):
        self.camera_index = int(choice.split(" ")[1])
        self.start_camera()
        
    def update_frame(self):
        if not self.is_running: return
        
        ret, frame = self.cap.read()
        if ret:
            # 1. VISUAL MIRROR (Keep this! It makes the UX feel natural)
            # frame = cv2.flip(frame, 1)
            img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # 2. MEDIAPIPE DETECTION
            results = self.hands.process(img_rgb)
            
            current_sign = "--"
            confidence_score = 0.0
            
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    # Draw Skeleton
                    self.mp_draw.draw_landmarks(frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)
                    
                    # --- 3. WRIST TWEAK MATH (CRITICAL) ---
                    wrist = hand_landmarks.landmark[0]
                    wx, wy = wrist.x, wrist.y
                    
                    data_aux = []
                    for lm in hand_landmarks.landmark:
                        # --- DATA UN-MIRRORING ---
                        # Because we flipped the frame (Line 133), the X-axis is inverted.
                        # We must multiply the X-distance by -1 to fix it for the AI.
                        
                        # Relative X (Mirrored)
                        rel_x = lm.x - wx
                        # Relative Y (Normal)
                        rel_y = lm.y - wy
                        
                        # Fix: Invert X back to reality
                        data_aux.append(rel_x * -1) 
                        data_aux.append(rel_y)
                    
                    # --- 4. PREDICT ---
                    input_data = np.array(data_aux).reshape(1, 42)
                    prediction = self.model.predict(input_data, verbose=0)
                    idx = np.argmax(prediction)
                    confidence_score = np.max(prediction)
                    
                    if confidence_score > 0.7:
                        current_sign = self.labels[idx]
            
            # --- 5. LOGIC UPDATE ---
            # Update Sentence Builder
            full_sentence, is_new_word = self.sentence_builder.update(current_sign, confidence_score)
            if is_new_word:
                word_to_speak = full_sentence.split()[-1] 
                self.tts.speak(word_to_speak)
            
            self.sentence_builder.check_auto_space()
            
            # --- 6. GUI UPDATE ---
            self.current_prediction_box.configure(text=current_sign)
            
            current_display_text = self.text_display.get("1.0", "end-1c")
            if full_sentence != current_display_text:
                self.text_display.delete("1.0", "end")
                self.text_display.insert("end", full_sentence)
            
            # Render Video
            img_final = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            ctk_img = ctk.CTkImage(light_image=img_final, dark_image=img_final, size=(640, 480))
            self.video_label.configure(image=ctk_img)
            self.video_label.image = ctk_img
            
        self.window.after(10, self.update_frame)
        
    def speak_text(self):
        text = self.text_display.get("1.0", "end-1c")
        if text.strip():
            self.status_label.configure(text="Speaking...", text_color="#17A2B8")
            self.tts.speak(text)
            self.window.after(2000, lambda: self.status_label.configure(text="Ready", text_color="gray"))
        
    def clear_history(self):
        self.sentence_builder.clear()
        self.text_display.delete("1.0", "end")
        self.status_label.configure(text="History Cleared", text_color="gray")

    def run(self):
        """Starts the main application loop"""
        self.window.mainloop()

    def on_closing(self):
        self.is_running = False
        if self.cap: self.cap.release()
        self.window.destroy()

if __name__ == "__main__":
    app = ASLTranslatorGUI()
    app.run()