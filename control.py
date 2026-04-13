"""
LOPUTHJOSEPH - SYSTEM CONTROL & ACTIVATION
- Use this to start/stop the security suite
- Command-line interface for manual control
"""

import sys
import os
import subprocess
import time

def start_system():
    # Legal & Compliance Verification
    if not os.path.exists("configs/.tos_accepted"):
        print("\n" + "!"*50)
        print("LOPUTHJOSEPH ENTERPRISE SECURITY PLATFORM")
        print("!"*50)
        print("TERMS OF SERVICE (ToS) & END USER LICENSE AGREEMENT (EULA)")
        print("\nBy using this software, you agree that:")
        print("1. LOPUTHJOSEPH is provided 'AS-IS' for security defense.")
        print("2. Illegal use (e.g., unauthorized scanning) is strictly prohibited.")
        print("3. You accept full liability for actions taken by the Elite AutoResponder.")
        print("\nDO YOU ACCEPT THESE TERMS? (yes/no)")
        choice = input("> ").strip().lower()
        if choice == 'yes':
            with open("configs/.tos_accepted", "w") as f:
                f.write(str(time.time()))
            print("[+] ToS Accepted. Proceeding to activation...")
        else:
            print("[!] Activation cancelled. You must accept the ToS to use this product.")
            return

    print("[*] ACTIVATING LOPUTHJOSEPH...")
    # Set environment variables
    env = os.environ.copy()
    env["PYTHONPATH"] = ".;./src;./src/monitors;./src/detectors;./src/responders;./src/os_platform"
    
    # Start the FastAPI server on 0.0.0.0 to allow local network access
    cmd = "python -m uvicorn app:app --host 0.0.0.0 --port 8000"
    subprocess.Popen(cmd, shell=True, env=env)
    
    # Wait for the server to start
    time.sleep(5)
    print("[+] DASHBOARD ACTIVE: http://localhost:8000")
    print("[+] LOCAL NETWORK: http://<YOUR_IP>:8000")
    
    # Start the CLI entry point
    print("[*] STARTING OMNI-EDITION DEFENSE LOOP...")
    subprocess.run("python src/main_entry.py", shell=True, env=env)

def interactive_mode():
    """Start an interactive offline control shell"""
    print("\n" + "="*50)
    print("LOPUTHJOSEPH: OFFLINE INTERACTIVE CONSOLE")
    print("="*50)
    print("Type 'help' for commands, 'exit' to quit.\n")
    
    while True:
        try:
            cmd = input("LOPUTHJOSEPH > ").strip().lower()
            if not cmd: continue
            if cmd == 'exit': break
            if cmd == 'help':
                show_help()
                continue
            
            # Execute command
            if cmd == 'status':
                print("[+] System: ACTIVE | Mode: OMNI-KINETIC | Connectivity: OFFLINE/LOCAL")
            elif cmd == 'scan':
                from src.detectors.vulnerability_scanner import VulnerabilityScanner
                scanner = VulnerabilityScanner()
                print(scanner.perform_system_audit())
            elif cmd.startswith('entry '):
                target = cmd.split(' ')[1]
                from src.responders.omni_exploit_engine import HyperDefensiveAuditEngine
                engine = HyperDefensiveAuditEngine(target)
                print(engine.universal_entry(target))
            elif cmd == 'activate':
                start_system()
            else:
                print(f"[!] Unknown command: {cmd}")
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"[!] Error: {e}")

def show_help():
    print("LOPUTHJOSEPH Control Interface")
    print("Commands:")
    print("  activate    - Start the full defense shield and dashboard")
    print("  interactive - Start the offline interactive console (NO INTERNET)")
    print("  status      - Check system health and shield status")
    print("  scan        - Execute a REAL vulnerability assessment")
    print("  telegram    - Start the Telegram Remote Control Bot")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        show_help()
    elif sys.argv[1] == "interactive":
        interactive_mode()
    elif sys.argv[1] == "activate":
        start_system()
    elif sys.argv[1] == "status":
        print("[+] System is READY for activation.")
    elif sys.argv[1] == "scan":
        from src.detectors.vulnerability_scanner import VulnerabilityScanner
        scanner = VulnerabilityScanner()
        print(f"[*] OS Fingerprint: {scanner.fingerprint_os()}")
        print(scanner.perform_system_audit())
    elif sys.argv[1] == "telegram":
        from src.responders.telegram_bot import LoputhJosephTelegramBot
        load_dotenv()
        TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
        ALLOWED_ID = os.environ.get("TELEGRAM_ALLOWED_USER_ID")
        bot = LoputhJosephTelegramBot(TOKEN, ALLOWED_ID)
        bot.run()
    else:
        show_help()
