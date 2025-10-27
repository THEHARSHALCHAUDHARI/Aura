import speech_recognition as sr

class STTHandler:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        # Adjust for ambient noise once
        print("[INFO] Calibrating microphone for ambient noise...")
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=2)
        print("[INFO] STT Handler ready")
    
    def listen(self, timeout=10):
        """Listen for speech and return text"""
        try:
            with self.microphone as source:
                print("[STT] Listening...")
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=10)
                
            print("[STT] Processing speech...")
            text = self.recognizer.recognize_google(audio)
            print(f"[STT] Recognized: {text}")
            return text.lower()
            
        except sr.UnknownValueError:
            print("[STT] Could not understand audio")
            return ""
        except sr.RequestError as e:
            print(f"[STT] API error: {e}")
            return ""
        except sr.WaitTimeoutError:
            print("[STT] Listening timeout")
            return ""
        except Exception as e:
            print(f"[STT] Error: {e}")
            return ""
