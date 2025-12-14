import customtkinter as ctk
from PIL import Image, ImageTk
import cv2
import threading
import time
import numpy as np
import sys

# Backend
import config
from vision_engine import VisionEngine
from brain_engine import AIEngine
from logic_engine import SentenceBuilder, TextToSpeech

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

COLORS = {
    "bg": "#0F0F0F", "panel": "#1A1A1A", "accent": "#00E5FF",
    "success": "#00FF9F", "warning": "#FFB800", "danger": "#FF2E63",
    "text": "#FFFFFF", "text_dim": "#888888"
}

class SignFlowApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("SignFlow AI - Enterprise Suite")
        self.geometry("1400x800")
        self.configure(fg_color=COLORS["bg"])

        # --- INIT ENGINES ---
        self.vision = VisionEngine()
        self.brain = AIEngine() # Loads "Spell" by default
        self.logic = SentenceBuilder()
        self.tts = TextToSpeech()
        
        self.is_running = True
        self.current_mode = "Spell"

        # --- UI LAYOUT ---
        self.grid_columnconfigure(1, weight=1) 
        self.grid_rowconfigure(0, weight=1)
        self._init_sidebar()
        self._init_center_hud()
        self._init_right_panel()
        
        # Start REAL Loop
        self.after(100, self.update_loop)

    def _init_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, width=220, corner_radius=0, fg_color=COLORS["panel"])
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        ctk.CTkLabel(self.sidebar, text="SignFlow", font=("Montserrat", 32, "bold"), text_color=COLORS["text"]).pack(pady=(40, 5))
        ctk.CTkLabel(self.sidebar, text="v5.0 Ultimate", font=("Consolas", 12), text_color=COLORS["text_dim"]).pack(pady=(0, 40))

        # Mode Buttons
        self.btn_spell = self._nav_btn("🔤  Spell Mode", "Spell")
        self.btn_talk  = self._nav_btn("💬  Talk Mode", "Talk")
        self.btn_hybrid= self._nav_btn("🚀  Hybrid Mode", "Hybrid")
        
        self._highlight_nav("Spell")

    def _nav_btn(self, text, mode):
        btn = ctk.CTkButton(self.sidebar, text=text, height=50, anchor="w", fg_color="transparent",
                            text_color=COLORS["text_dim"], hover_color="#252525",
                            command=lambda: self.change_mode(mode))
        btn.pack(fill="x", padx=10, pady=5)
        return btn

    def _highlight_nav(self, mode):
        for btn in [self.btn_spell, self.btn_talk, self.btn_hybrid]:
            btn.configure(fg_color="transparent", text_color=COLORS["text_dim"], border_width=0)
        
        target = {"Spell": self.btn_spell, "Talk": self.btn_talk, "Hybrid": self.btn_hybrid}.get(mode)
        if target: target.configure(fg_color="#2A2A2A", text_color=COLORS["text"], border_width=2, border_color=COLORS["accent"])

    def _init_center_hud(self):
        self.center = ctk.CTkFrame(self, fg_color="transparent")
        self.center.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.center.grid_rowconfigure(1, weight=1); self.center.grid_columnconfigure(0, weight=1)

        # Badge & Confidence
        info = ctk.CTkFrame(self.center, height=50, fg_color="transparent")
        info.grid(row=0, column=0, sticky="ew")
        self.mode_badge = ctk.CTkButton(info, text="SPELL ENGINE ACTIVE", fg_color=COLORS["accent"], text_color="black", hover=False, width=200, corner_radius=20)
        self.mode_badge.pack(side="left")
        self.conf_lbl = ctk.CTkLabel(info, text="Confidence: 0%", font=("Consolas", 14), text_color=COLORS["accent"])
        self.conf_lbl.pack(side="right")

        # Video
        self.vid_box = ctk.CTkFrame(self.center, corner_radius=20, fg_color="#000000", border_width=1, border_color="#333333")
        self.vid_box.grid(row=1, column=0, sticky="nsew", pady=10)
        self.vid_lbl = ctk.CTkLabel(self.vid_box, text="")
        self.vid_lbl.place(relx=0.5, rely=0.5, anchor="center")
        
        # Result Display
        self.res_box = ctk.CTkFrame(self.center, height=100, corner_radius=15, fg_color=COLORS["panel"])
        self.res_box.grid(row=2, column=0, sticky="ew")
        ctk.CTkLabel(self.res_box, text="DETECTED SIGN", font=("Arial", 10, "bold"), text_color="gray").pack(pady=(15,0))
        self.res_val = ctk.CTkLabel(self.res_box, text="--", font=("Roboto", 40, "bold"), text_color=COLORS["text"])
        self.res_val.pack()

    def _init_right_panel(self):
        self.right = ctk.CTkFrame(self, width=320, corner_radius=0, fg_color=COLORS["panel"])
        self.right.grid(row=0, column=2, sticky="nsew")
        ctk.CTkLabel(self.right, text="TRANSCRIPT", font=("Roboto", 18, "bold"), text_color=COLORS["text"]).pack(pady=30)
        
        self.chat = ctk.CTkTextbox(self.right, font=("Consolas", 16), text_color=COLORS["text"], fg_color="#222222")
        self.chat.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        self.btns = ctk.CTkFrame(self.right, fg_color="transparent")
        self.btns.pack(fill="x", padx=20, pady=20, side="bottom")
        ctk.CTkButton(self.btns, text="🔊 SPEAK", height=50, fg_color=COLORS["success"], text_color="black", command=self.speak).pack(fill="x", pady=5)
        ctk.CTkButton(self.btns, text="🗑 CLEAR", height=40, fg_color=COLORS["danger"], command=self.clear).pack(fill="x", pady=5)

    # --- CORE LOGIC ---
    def update_loop(self):
        if not self.is_running: return

        # 1. Vision (Get Frame & Coordinates)
        frame, landmarks = self.vision.get_frame_and_landmarks()
        
        if frame is not None:
            # 2. Brain (Predict using current loaded model)
            sign, conf = self.brain.predict(landmarks)
            
            # 3. Logic (Build Sentence)
            sentence, new_word = self.logic.update(sign, conf)
            self.logic.check_auto_space()
            
            # 4. GUI Updates
            self.res_val.configure(text=sign)
            self.conf_lbl.configure(text=f"Confidence: {int(conf*100)}%")
            
            # Update Chat
            curr = self.chat.get("1.0", "end-1c")
            if curr.strip() != sentence.strip():
                self.chat.delete("1.0", "end")
                self.chat.insert("end", sentence)
                self.chat.see("end")
                if new_word: self.tts.speak(sentence.split()[-1])

            # Update Video
            w = self.vid_box.winfo_width()
            h = self.vid_box.winfo_height()
            if w > 10 and h > 10:
                img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                pil = Image.fromarray(img)
                cimg = ctk.CTkImage(pil, size=(w, h))
                self.vid_lbl.configure(image=cimg)
                self.vid_lbl.image = cimg

        self.after(15, self.update_loop)

    def change_mode(self, mode):
        if mode == self.current_mode: return
        # Call Backend Switcher
        self.brain.switch_mode(mode)
        self.current_mode = mode
        self._highlight_nav(mode)
        self.mode_badge.configure(text=f"{mode.upper()} ENGINE ACTIVE")
        self.logic.clear() # Clear sentence on mode switch

    def speak(self): self.tts.speak(self.logic.get_text())
    def clear(self): self.logic.clear()
    def on_close(self):
        self.is_running = False
        self.vision.release()
        self.destroy()
        sys.exit()

if __name__ == "__main__":
    app = SignFlowApp()
    app.protocol("WM_DELETE_WINDOW", app.on_close)
    app.mainloop()