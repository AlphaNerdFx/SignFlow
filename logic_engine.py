import pyttsx3
import threading
import time
import config

class TextToSpeech:
    def __init__(self):
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 150)

    def speak(self, text):
        threading.Thread(target=self._speak, args=(text,)).start()

    def _speak(self, text):
        try:
            self.engine.say(text)
            self.engine.runAndWait()
        except: pass

class SentenceBuilder:
    def __init__(self):
        self.sentence = []
        self.last_pred = ""
        self.frame_count = 0
        self.threshold = 10
        self.repeat_delay = 15
        self.cooldown = 0
        self.last_sign_time = time.time()
        self.space_threshold = 2.0

    def update(self, prediction, confidence):
        # Only process if AI is confident
        if confidence < config.CONFIDENCE_THRESHOLD:
            return self.get_text(), False

        # Stability Check (Hold-to-Type)
        if prediction == self.last_pred:
            self.frame_count += 1
        else:
            self.frame_count = 0
            self.last_pred = prediction

        # Confirm Sign
        if self.frame_count == config.HOLD_FRAMES:
            self.last_sign_time = time.time()
            return self._add_word(prediction)

        return self.get_text(), False

    def _add_word(self, word):
        if word == "space":
            self.sentence.append(" ")
        elif word == "del":
            if self.sentence: self.sentence.pop()
        elif word == "nothing":
            pass
        else:
            # Prevent duplicate words (optional)
            if not self.sentence or self.sentence[-1] != word:
                self.sentence.append(word)
                return self.get_text(), True # True = New word added
        return self.get_text(), False

    def check_auto_space(self):
        if (time.time() - self.last_sign_time > config.AUTO_SPACE_TIME):
            if self.sentence and self.sentence[-1] != " ":
                self.sentence.append(" ")
                self.last_sign_time = time.time()

    def get_text(self):
        return "".join(self.sentence)

    def clear(self):
        self.sentence = []