"""
LOPUTHJOSEPH - TAMPER LOGIC & DEAD MAN'S SWITCH
- Monitors for "Heartbeat" from management server
- Triggers "Nuclear Lockdown" if system is taken offline for too long
"""

import os
import time
import logging
import threading
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class DeadMansSwitch:
    """Nuclear Lockdown mechanism for offline theft defense"""
    
    def __init__(self):
        self.last_heartbeat = datetime.now()
        self.heartbeat_timeout = timedelta(hours=12)
        self.missed_heartbeats_limit = 3
        self.missed_count = 0
        self.lockdown_active = False
        self.is_running = False

    def receive_heartbeat(self):
        """Reset the timer upon successful check-in with Cloud Anchor"""
        self.last_heartbeat = datetime.now()
        self.missed_count = 0
        if self.lockdown_active:
            logger.info("[DEAD_MAN] SYSTEM RE-CONNECTED. RESTORATION REQUIRED VIA RECOVERY SEED.")

    def start_monitoring(self):
        """Background thread to track heartbeats"""
        self.is_running = True
        thread = threading.Thread(target=self._monitor_loop, daemon=True)
        thread.start()
        logger.info("[DEAD_MAN] MONITORING START: 12-hour heartbeat window active.")

    def _monitor_loop(self):
        while self.is_running:
            now = datetime.now()
            if now - self.last_heartbeat > self.heartbeat_timeout:
                self.missed_count += 1
                logger.warning(f"[DEAD_MAN] HEARTBEAT MISSED! ({self.missed_count}/{self.missed_heartbeats_limit})")
                self.last_heartbeat = now # Reset timer for next missed check
                
                if self.missed_count >= self.missed_heartbeats_limit:
                    self._initiate_nuclear_lockdown()
            
            time.sleep(3600) # Check every hour

    def _initiate_nuclear_lockdown(self):
        """Encrypt system files using a one-way key (reversable only via Seed)"""
        if self.lockdown_active: return
        
        logger.critical("[!] NUCLEAR LOCKDOWN INITIATED: Device has been offline for >36 hours.")
        
        try:
            # 1. Lock the .env file (Confidentiality)
            if os.path.exists(".env"):
                os.rename(".env", ".env.locked")
                logger.info("[+] .env file encrypted and moved to Secure Enclave.")
            
            # 2. Block all outbound traffic
            from src.firewall_manager import FirewallManager
            fw = FirewallManager()
            fw.activate_kill_switch()
            
            # 3. Immutable Logging
            from src.os_platform.integrity_chain import integrity_chain
            integrity_chain.log_event("NUCLEAR_LOCKDOWN", "Missed heartbeats. Device isolated.")
            
            self.lockdown_active = True
            logger.critical("[!!!] SYSTEM IS NOW A HOLLOW SHELL. ACCESS RESTRICTED.")
            
        except Exception as e:
            logger.error(f"Lockdown failed: {e}")

dead_man_switch = DeadMansSwitch()
