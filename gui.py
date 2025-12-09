import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import cv2
import time
from camera import CameraStream
from inference import SignPredictor

class SignFlowApp:
    def __init__(self, root):
        self.root = root
        self.root.title("SignFlow - ASL Translator (Landmark Edition)")
        self.root.geometry("900x700")
        
        # Modules
        self.camera = CameraStream()
        self.predictor = SignPredictor()
        
        # State
        self.is_running = True
        self.current_sentence = ""
        self.last_predicted_char = None
        
        self._setup_ui()
        self.update_loop()

    def _setup_ui(self):
        # 1. Video Label
        self.video_label = tk.Label(self.root)
        self.video_label.pack(pady=10)
        
        # 2. Info Panel
        info_frame = tk.Frame(self.root)
        info_frame.pack(pady=10)
        
        self.prediction_label = tk.Label(info_frame, text="Detecting: ...", font=("Helvetica", 24, "bold"), fg="green")
        self.prediction_label.pack()
        
        # 3. Output Text Area
        self.text_output = tk.Text(self.root, height=5, width=40, font=("Helvetica", 18))
        self.text_output.pack(pady=20)
        
        # 4. Quit Button
        btn = tk.Button(self.root, text="Quit", command=self.close_app, font=("Arial", 14))
        btn.pack(pady=10)

    def update_loop(self):
        if not self.is_running:
            return
            
        # 1. Get Frame and Data
        # hand_data is now a LIST of 42 coordinates, NOT an image
        frame, hand_data = self.camera.get_frame()
        
        if frame is not None:
            # 2. Prediction Step
            predicted_char = None
            
            # Check if we have valid coordinate data
            if hand_data is not None and len(hand_data) > 0:
                raw_char, prob = self.predictor.predict(hand_data)
                predicted_char = self.predictor.get_stable_prediction(raw_char)
                
                # Update "Detecting" Label
                if raw_char:
                    disp_text = f"Detecting: {raw_char} ({prob:.2f})"
                    self.prediction_label.config(text=disp_text, fg="green")
                else:
                    self.prediction_label.config(text="Low Confidence...", fg="orange")
            else:
                self.prediction_label.config(text="Show Hand", fg="red")

            # 3. Handle Text Logic
            if predicted_char and predicted_char != self.last_predicted_char:
                self._handle_typing(predicted_char)
                self.last_predicted_char = predicted_char
            elif predicted_char is None:
                 pass

            # 4. Update Video in GUI
            cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(cv2image)
            imgtk = ImageTk.PhotoImage(image=img)
            self.video_label.imgtk = imgtk
            self.video_label.configure(image=imgtk)

        self.root.after(30, self.update_loop)

    def _handle_typing(self, char):
        if char == 'space':
            self.current_sentence += " "
        elif char == 'del':
            self.current_sentence = self.current_sentence[:-1]
        elif char == 'nothing':
            pass
        else:
            self.current_sentence += char
            
        self.text_output.delete("1.0", tk.END)
        self.text_output.insert(tk.END, self.current_sentence)

    def close_app(self):
        self.is_running = False
        self.camera.release()
        self.root.destroy()