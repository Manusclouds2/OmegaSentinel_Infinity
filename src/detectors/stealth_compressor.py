"""
LOPUTHJOSEPH - STEALTH COMPRESSOR
- Recursive video compression using ffmpeg
- Motion-aware incident capture
- Keyframe extraction for high-res snapshots
- Disk cleanup and process masking logic
"""

import cv2
import subprocess
import os
import logging
import time
import shutil
from typing import Tuple, Optional

logger = logging.getLogger("STEALTH_COMPRESSOR")

class StealthCompressor:
    def __init__(self):
        self.temp_dir = "data/temp_clips"
        os.makedirs(self.temp_dir, exist_ok=True)
        self._mask_process()

    def _mask_process(self):
        """Attempts to rename the process for stealth (OS dependent)"""
        try:
            import setproctitle
            # Disguise as a system worker
            setproctitle.setproctitle("kworker/u256:1-events_unbound")
        except ImportError:
            # On Windows, setproctitle is not standard, we rely on other stealth
            pass

    def extract_keyframe(self, video_path: str) -> Optional[str]:
        """
        Identifies the 'most important' frame (e.g., first frame with most motion or face).
        For now, we'll take the middle frame as a heuristic for the 'incident' center.
        """
        snapshot_path = video_path.replace(".avi", "_snapshot.jpg").replace(".mp4", "_snapshot.jpg")
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            return None
        
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        # Seek to middle frame
        cap.set(cv2.CAP_PROP_POS_FRAMES, total_frames // 2)
        ret, frame = cap.read()
        if ret:
            # Save high-quality JPEG
            cv2.imwrite(snapshot_path, frame, [cv2.IMWRITE_JPEG_QUALITY, 90])
            cap.release()
            return snapshot_path
        
        cap.release()
        return None

    def compress_and_send(self, input_file: str, output_file: str) -> str:
        """
        Uses ffmpeg to crush a video file size by 90% without 
        losing the ability to identify a face.
        """
        # CRITICAL: We reduce the resolution to 480p and lower the bitrate
        logger.info(f"[*] Compressing {input_file} for stealth transmission...")
        
        cmd = [
            'ffmpeg', '-i', input_file,
            '-vcodec', 'libx264',
            '-crf', '28',        # Constant Rate Factor (Higher = smaller file)
            '-preset', 'veryfast',
            '-vf', 'scale=640:-1', # Resize to 640px width
            output_file, '-y'
        ]
        
        try:
            # Masking: We can't easily rename the ffmpeg process here, 
            # but we run it silently.
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT, check=True)
            return output_file
        except Exception as e:
            logger.error(f"[-] Compression failed: {e}")
            return input_file

    def capture_incident(self, duration: int = 5) -> Tuple[Optional[str], Optional[str]]:
        """
        Captures a short burst when the 'Wise' thief is detected.
        Returns: (snapshot_path, compressed_video_path)
        """
        timestamp = int(time.time())
        raw_path = os.path.join(self.temp_dir, f"raw_{timestamp}.avi")
        final_path = os.path.join(self.temp_dir, f"incident_{timestamp}.mp4")
        
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            logger.error("[-] Camera not accessible for incident capture.")
            return None, None

        # Define the codec and create VideoWriter object
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        out = cv2.VideoWriter(raw_path, fourcc, 20.0, (640, 480))
        
        logger.info(f"[*] CAPTURING {duration}s INCIDENT BURST...")
        
        # Record for the specified duration (20 FPS * duration)
        for _ in range(20 * duration):
            ret, frame = cap.read()
            if ret:
                out.write(frame)
            else:
                break
                
        cap.release()
        out.release()
        
        # 1. Extract Keyframe (High-Res Snapshot)
        snapshot_file = self.extract_keyframe(raw_path)
        
        # 2. Compress for stealth transmission
        compressed_file = self.compress_and_send(raw_path, final_path)
        
        # 3. Disk Cleanup: Immediately delete the raw AVI to leave no traces
        if os.path.exists(raw_path):
            os.remove(raw_path)
            logger.info("[+] Disk Cleanup: Raw AVI purged.")
            
        return snapshot_file, compressed_file

    def cleanup_temp(self):
        """Purge all temporary files in the temp directory"""
        if os.path.exists(self.temp_dir):
            try:
                shutil.rmtree(self.temp_dir)
                os.makedirs(self.temp_dir, exist_ok=True)
            except Exception as e:
                logger.error(f"[-] Cleanup failed: {e}")

stealth_compressor = StealthCompressor()
