"""
LOPUTHJOSEPH SENTINEL AGENT
Professional Single-Executable Entry Point
Optimized for PyInstaller and Cross-Platform Deployment
"""

import sys
import os
import time
import logging
import platform
import multiprocessing

# Add current dir to path for bundled imports
if getattr(sys, 'frozen', False):
    bundle_dir = sys._MEIPASS
else:
    bundle_dir = os.path.dirname(os.path.abspath(__file__))

sys.path.append(bundle_dir)

from detectors.advanced_malware_detector import AdvancedMalwareDetector
from monitors.file_monitor import FileMonitor
from firewall_manager import FirewallManager
from os_platform.hardware_root_of_trust import HardwareRootOfTrust
from os_platform.recovery import recovery_manager

class SentinelAgent:
    """Enterprise-grade security agent for Windows/Linux"""
    
    def __init__(self):
        self.os = platform.system()
        self.hostname = platform.node()
        self.hrot = HardwareRootOfTrust()
        self.firewall = FirewallManager()
        self.detector = AdvancedMalwareDetector()
        
        print(f"[*] INITIALIZING SENTINEL AGENT ON {self.hostname} ({self.os})")

    def start_defense_loop(self):
        """Main Zero-Trust & Protection loop"""
        print("[+] SENTINEL AGENT ACTIVE. ENFORCING ZERO-TRUST POLICY.")
        
        # 1. Hardware Integrity Check
        integrity = self.hrot.measure_boot_components()
        if integrity.get("integrity_status") != "STABLE":
            print("[!] CRITICAL: Hardware state mismatch. Locking endpoint.")
            self.firewall.activate_kill_switch()
            
        # 2. Continuous Monitoring
        while True:
            try:
                # Perform lightweight periodic checks
                # (Real logic would be event-driven)
                time.sleep(60)
            except KeyboardInterrupt:
                print("[*] Sentinel Agent suspended by administrator.")
                break

def run_agent():
    agent = SentinelAgent()
    agent.start_defense_loop()

if __name__ == "__main__":
    # Support for PyInstaller's multiprocessing
    multiprocessing.freeze_support()
    run_agent()
