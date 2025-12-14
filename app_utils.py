import pyttsx3
import threading
import time

# --- 1. TEXT TO SPEECH ENGINE ---
class TextToSpeech:
    def __init__(self):
        self.engine = pyttsx3.init()
        # Set properties (Optional: Speed and Volume)
        self.engine.setProperty('rate', 150)  # Speed percent (can go over 100)
        self.engine.setProperty('volume', 1.0)  # Volume 0-1

    def speak(self, text):
        """Runs speaking in a separate thread so video doesn't freeze"""
        thread = threading.Thread(target=self._speak_thread, args=(text,))
        thread.start()

    def _speak_thread(self, text):
        try:
            self.engine.say(text)
            self.engine.runAndWait()
        except RuntimeError:
            pass # Handle loop errors if button clicked too fast

# --- 2. SENTENCE BUILDER LOGIC ---
class SentenceBuilder:
    def __init__(self):
        self.sentence = []       # List of words
        self.current_word = ""   # Current word being spelled (if spelling)
        self.last_pred = ""
        self.frame_count = 0
        self.threshold = 15      # Frames to hold a sign to confirm it
        
        # Auto-Space Logic
        self.last_sign_time = time.time()
        self.space_threshold = 2.5 # Seconds of no signing to add a space

    def update(self, prediction, confidence):
        """
        Returns: (display_text, is_confirmed_just_now)
        """
        # 1. Filter Low Confidence
        if confidence < 0.6:
            return self._get_display_text(), False

        # 2. Check for Stability (Hold to Type)
        if prediction == self.last_pred:
            self.frame_count += 1
        else:
            self.frame_count = 0
            self.last_pred = prediction

        # 3. Confirm Prediction
        if self.frame_count == self.threshold:
            self.last_sign_time = time.time() # Reset space timer
            
            # Handle Special Keys
            if prediction == "Space":
                self.sentence.append(" ")
            elif prediction == "del":
                if self.sentence: 
                    self.sentence.pop()
            elif prediction == "Nothing":
                pass
            else:
                # Logic: Don't repeat the same word immediately
                # (e.g. don't write "Hello Hello")
                if not self.sentence or self.sentence[-1] != prediction:
                    self.sentence.append(prediction)
                    return self._get_display_text(), True # True = Trigger sound?

        return self._get_display_text(), False

    def check_auto_space(self):
        """Call this every frame to check if we should add a space"""
        # If 2.5 seconds passed since last sign, and we haven't just added a space
        if (time.time() - self.last_sign_time > self.space_threshold):
            if self.sentence and self.sentence[-1] != " ":
                self.sentence.append(" ")
                print("Auto-Space Added")
                self.last_sign_time = time.time() # Reset

    def _get_display_text(self):
        return "".join(self.sentence)

    def clear(self):
        self.sentence = []