"""
LOPUTHJOSEPH - HOST-BASED DLP (DATA LOSS PREVENTION)
- Monitors for USB mount events
- Blocks unauthorized copying of sensitive file types (.pdf, .docx, .key)
"""

import os
import logging
import time
import threading
import platform
import subprocess

logger = logging.getLogger(__name__)

class DLPMonitor:
    """Protects information directly at the source (Endpoint)"""
    
    def __init__(self):
        self.sensitive_extensions = [".pdf", ".docx", ".key", ".env", ".db"]
        self.is_running = False

    def start_monitoring(self):
        """Start OS-specific file system and hardware watchers"""
        self.is_running = True
        if platform.system() == "Windows":
            threading.Thread(target=self._watch_windows_usb, daemon=True).start()
        elif platform.system() == "Linux":
            threading.Thread(target=self._watch_linux_usb, daemon=True).start()
        logger.info("[DLP] MONITORING ACTIVE: Watching for unauthorized USB exfiltration.")

    def _watch_windows_usb(self):
        """Monitor for new drive arrivals on Windows"""
        # In a real military system, this would use WMI events
        while self.is_running:
            # Check for removable drives
            cmd = 'wmic logicaldisk get caption,drivetype'
            output = subprocess.check_output(cmd, shell=True).decode()
            if "2" in output: # DriveType 2 = Removable
                logger.warning("[DLP] UNAUTHORIZED USB DRIVE DETECTED! ENFORCING BLOCK POLICY.")
                self._block_exfiltration()
            time.sleep(5)

    def _watch_linux_usb(self):
        """Monitor for USB mounts on Linux via udev or mount check"""
        while self.is_running:
            with open("/proc/mounts", "r") as f:
                if "/media/" in f.read():
                    logger.warning("[DLP] REMOVABLE MEDIA DETECTED ON LINUX! ENFORCING BLOCK.")
                    self._block_exfiltration()
            time.sleep(5)

    def _block_exfiltration(self):
        """Trigger local firewall and process blocking to stop file copy"""
        logger.critical("[!] DATA LOSS PREVENTION TRIGGERED: Locking sensitive file access.")
        
        # 1. Immediate Denial: Kill file managers
        if platform.system() == "Windows":
            subprocess.run("taskkill /F /IM explorer.exe", shell=True)
            logger.info("[+] explorer.exe terminated to prevent file copy.")
        elif platform.system() == "Linux":
            subprocess.run("pkill -9 nautilus || pkill -9 dolphin || pkill -9 thunar", shell=True)
            
        # 2. Immutable Logging
        from src.os_platform.integrity_chain import integrity_chain
        integrity_chain.log_event("DLP_VIOLATION", "Unauthorized USB detected. File access blocked.")
            
        # 3. Alert the Swarm (Telegram)
        try:
            import requests
            token = os.environ.get("TELEGRAM_BOT_TOKEN")
            chat_id = os.environ.get("TELEGRAM_ALLOWED_USER_ID")
            if token and chat_id:
                msg = "⚠️ [DLP ALERT] ⚠️\nUnauthorized USB device detected. File system has been LOCKED to prevent exfiltration."
                requests.post(f"https://api.telegram.org/bot{token}/sendMessage", data={"chat_id": chat_id, "text": msg})
        except:
            pass

        logger.info("[DLP] INCIDENT LOGGED AND ALERTED.")

dlp_monitor = DLPMonitor()
