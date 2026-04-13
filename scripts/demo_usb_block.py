"""
LOPUTHJOSEPH - PROOF OF VALUE DEMO
Scenario: Malicious Employee Attempting Data Exfiltration via USB
"""

import os
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("DEMO")

def simulate_usb_insertion():
    print("\n" + "="*50)
    print("DEMO: MALICIOUS EMPLOYEE SCENARIO")
    print("="*50)
    print("[*] Simulating USB Drive insertion (Drive E: detected)...")
    time.sleep(2)
    
    # Target "Company Secrets"
    secret_file = "configs/.env"
    print(f"[*] Attacker attempting to copy {secret_file} to USB...")
    
    # Sentinel Logic: Intercepting file access to sensitive configs
    print("[!] SENTINEL INTERCEPTION: Unauthorized access to 'quantum-keys' directory detected.")
    print("[!] POLICY ENFORCED: USB Write Access BLOCKED for process 'explorer.exe'.")
    
    # Alert the Admin
    print("[+] ALERT SENT: Telegram challenge issued to IT Director.")
    print("[+] INCIDENT LOGGED: User 'MaliciousEmp' flagged for exfiltration attempt.")
    print("="*50 + "\n")

if __name__ == "__main__":
    simulate_usb_insertion()
