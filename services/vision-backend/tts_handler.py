import pyttsx3
import threading
import queue

class TTSHandler:
    def __init__(self):
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 160)
        
        # Set to a clear voice (prefer English)
        voices = self.engine.getProperty('voices')
        for voice in voices:
            if "english" in voice.name.lower():
                self.engine.setProperty('voice', voice.id)
                break
        
        # Queue for thread-safe TTS
        self.speech_queue = queue.Queue()
        self.running = True
        
        # Start worker thread
        self.worker = threading.Thread(target=self._worker, daemon=True)
        self.worker.start()
        print("[INFO] TTS Handler initialized")
    
    def _worker(self):
        """Worker thread to process TTS queue"""
        while self.running:
            try:
                text = self.speech_queue.get(timeout=0.5)
                if text:
                    print(f"[TTS] Speaking: {text}")
                    self.engine.say(text)
                    self.engine.runAndWait()
                self.speech_queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                print(f"[TTS ERROR] {e}")
    
    def speak(self, text):
        """Add text to speech queue"""
        self.speech_queue.put(text)
    
    def stop(self):
        """Stop the TTS handler"""
        self.running = False
        self.worker.join()
