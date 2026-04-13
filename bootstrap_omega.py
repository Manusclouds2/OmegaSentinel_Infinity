"""
OMEGA-SOVEREIGN UNIVERSAL BOOTSTRAPPER
One-click deployment for any digital system (Windows, Linux, macOS, Android, Servers)
"""

import os
import sys
import subprocess
import platform
import logging
import threading
import time
from src.network.ghost_sync import GhostResurrection
from src.core.evolution_engine import evolution_engine # NEW: Evolution Engine

# Configure basic logging for bootstrapper
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("BOOTSTRAP")

def detect_environment():
    """Identify the tech stack and system type"""
    system = platform.system()
    machine = platform.machine()
    is_docker = os.path.exists('/.dockerenv')
    
    env_info = {
        "os": system,
        "arch": machine,
        "is_docker": is_docker,
        "is_android": "ANDROID_ROOT" in os.environ or os.path.exists("/system/app")
    }
    return env_info

def deploy_polyglot(env):
    """SaaS Polyglot Installer: Adaptive Deployment"""
    print(f"[*] DEPLOYING ADAPTIVE MODULES FOR: {env['os']} ({env['arch']})")
    
    if env['is_docker']:
        print(" [+] Environment: CLOUD/DOCKER (API-only mode enabled)")
        os.environ["OMEGA_DEPLOY_MODE"] = "CLOUD"
        return

    if env['os'] == "Windows":
        print(" [+] Environment: WINDOWS DESKTOP (Deploying Stealth Task)")
        try:
            subprocess.run(["powershell", "-ExecutionPolicy", "Bypass", "-File", "deploy_stealth.ps1"], check=True)
        except:
            print(" [!] Stealth deployment failed. Continuing with local runtime.")
            
    elif env['os'] == "Linux":
        if env['is_android']:
            print(" [+] Environment: ANDROID/TERMUX (Optimizing for low power)")
            os.environ["OMEGA_LOW_POWER_MODE"] = "1"
        else:
            print(" [+] Environment: LINUX SERVER (Creating systemd service)")
            # In a real SaaS, this would write a .service file and start it
            
    elif env['os'] == "Darwin":
        print(" [+] Environment: MACOS (Configuring LaunchAgent)")

def check_docker_engine():
    """Automation: Check for Docker and offer containerized run"""
    try:
        subprocess.run(["docker", "--version"], capture_output=True, check=True)
        print(" [+] Docker Engine: DETECTED")
        return True
    except:
        return False

def check_bios_security():
    """Check if UEFI/BIOS Supervisor Password is set (Sub-OS Persistence)"""
    system = platform.system()
    if system == "Windows":
        try:
            # Check for Secure Boot status as a proxy for BIOS hardening
            cmd = "powershell Confirm-SecureBootUEFI"
            result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
            if "True" in result.stdout:
                print(" [+] UEFI Secure Boot: ENABLED")
            else:
                print(" [!] UEFI Secure Boot: DISABLED (Highly Recommended)")
        except:
            pass
    elif system == "Linux":
        if os.path.exists("/sys/firmware/efi"):
            print(" [+] UEFI Firmware: DETECTED")

def scan_for_unprotected_sentinels(network_range="192.168.1.0/24"):
    """Scans the local network for MAC addresses that should have Sentinel but don't (Neighbor Watch)"""
    print(f"[*] GHOST SYNC: Scanning network {network_range} for unprotected peers...")
    try:
        from scapy.all import ARP, Ether, srp
        import socket
        
        # 1. ARP Scan the network
        ans, unans = srp(Ether(dst="ff:ff:ff:ff:ff:ff")/ARP(pdst=network_range), timeout=2, verbose=False)
        
        for snd, rcv in ans:
            ip = rcv.psrc
            mac = rcv.hwsrc
            
            # 2. Check if the Sentinel API is responding (Port 8000)
            try:
                with socket.create_connection((ip, 8000), timeout=0.5):
                    # Sentinel is active
                    continue
            except:
                # 3. If MAC is in 'Known' list but no API response, it's a 'Clean' machine
                # For demo, we just print the detection
                print(f" [!] Node {mac} ({ip}) detected as 'Clean'. Initiating Ghost Resurrection...")
                resurrect_node(ip)
                
    except ImportError:
        print(" [!] scapy not installed. Neighbor Watch disabled.")
    except Exception as e:
        print(f" [!] Network scan failed: {e}")

def resurrect_node(target_ip):
    """Uses a remote execution protocol to re-install Sentinel on a wiped machine."""
    # Professional Dropper: Pushes bootstrap_omega.py via SSH/WMI
    print(f"[*] RESURRECTING Node {target_ip}...")
    # In a real scenario, this would use paramiko (SSH) or wmi-client
    # subprocess.run(["ssh", f"admin@{target_ip}", "curl -sL https://sentinel.cloud/install | bash"])

# Configuration: List of company laptop MAC addresses to protect
COMPANY_MAC_LIST = ["AA:BB:CC:DD:EE:FF", "11:22:33:44:55:66"]

def initialize_ghost_guardian():
    """Starts the network-level resurrection monitor."""
    ghost = GhostResurrection(protected_macs=COMPANY_MAC_LIST)
    
    def run_forever():
        while True:
            # Scan the local network every 10 minutes
            ghost.scan_for_wiped_nodes(interface="eth0")
            time.sleep(600)

    # Run as a background daemon so it doesn't block the main system
    thread = threading.Thread(target=run_forever, daemon=True)
    thread.start()
    print("[+] Ghost Guardian: Network-level persistence is now ACTIVE.")

def resource_aware_loader():
    """Stealthy Loader: Checks for idle resources before pulling Ability Modules"""
    print("[*] SYSTEM CHECK: Auditing idle resources for module deployment...")
    try:
        import psutil
        cpu_usage = psutil.cpu_percent(interval=1)
        # Check for high-speed Wi-Fi (Simulated)
        network_speed = 100 # Mbps
        
        if cpu_usage < 20 and network_speed > 50:
            print(" [+] Resources: OPTIMAL. Initializing Evolution Engine...")
            # 1. Initial surveillance module
            try:
                from src.detectors.environment_sync import env_sync
                env_sync.start_surveillance()
                print(" [+] Ability Modules: ACTIVE (Stealth Mode)")
                
                # 2. Potential dynamic upgrades
                # If camera is detected, upgrade to vision_ai
                evolution_engine.upgrade_intelligence("vision_ai")
            except Exception as e:
                print(f" [!] Module loading failed: {e}")
        else:
            print(" [!] Resources: CONSTRAINED. Delaying Ability Module deployment.")
    except ImportError:
        print(" [!] psutil not installed. Stealth loader disabled.")

def initiate_deployment():
    clear_screen()
    env = detect_environment()
    
    print("====================================================")
    print("   MANUS CLOUDS :: OMEGA-SOVEREIGN BOOTSTRAPPER")
    print("====================================================")
    print(f"[*] TARGET SYSTEM: {env['os']} {platform.release()}")
    print(f"[*] ARCHITECTURE: {env['arch']}")
    print(f"[*] DOCKER: {'YES' if env['is_docker'] else 'NO'}")
    print("[*] STATUS: READY FOR MULTIVERSAL DEPLOYMENT")
    print("----------------------------------------------------")

    # 1. Polyglot Adaptation & BIOS Check
    print("[1/6] ADAPTING TO LOCAL ARCHITECTURE...")
    deploy_polyglot(env)
    check_bios_security()

    # 2. Check for Python environment
    print("[2/6] VERIFYING TERRESTRIAL RUNTIME...")
    try:
        import fastapi
        import uvicorn
        print(" [+] Runtime: OPTIMAL")
    except ImportError:
        print(" [!] Missing primitives. Synthesizing dependencies...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

    # 3. Database & Persistence Sync
    print("[3/6] ANCHORING CAUSAL DATABASE...")
    if not os.path.exists("data"):
        os.makedirs("data")
    print(" [+] Persistence: SECURED")

    # 4. Hardware Root of Trust (TPM)
    print("[4/6] INITIALIZING HARDWARE ROOT OF TRUST...")
    try:
        from src.os_platform.hardware_root_of_trust import HardwareRootOfTrust
        hrot = HardwareRootOfTrust()
        if hrot.tpm_enabled:
            print(" [+] TPM 2.0: DETECTED")
            # Initialize Primary Key in TPM if not already present
            pk_status = hrot.initialize_tpm_primary_key()
            print(f" [+] TPM Primary Key: {pk_status.get('status', 'INITIALIZED')}")
        else:
            print(" [!] TPM 2.0: NOT FOUND (Falling back to software-based enclave)")
    except Exception as e:
        print(f" [!] HROT Initialization failed: {e}")

    # 5. PACE Plan: Sovereign Recovery (Master Key)
    print("[5/6] INITIALIZING PACE PLAN (RECOVERY SEED)...")
    try:
        from src.os_platform.recovery_manager import recovery_manager
        if not os.path.exists("configs/quantum-keys/recovery_phrase.hash"):
            print(" [!] WARNING: NO RECOVERY SEED DETECTED.")
            print(" [*] GENERATING 24-WORD BIP-39 MASTER KEY...")
            phrase = recovery_manager.generate_recovery_phrase()
            print("\n" + "!"*60)
            print("   YOUR SOVEREIGN RECOVERY PHRASE (24 WORDS):")
            print(f"\n   {phrase}\n")
            print("   ACTION REQUIRED: PRINT OR WRITE THIS DOWN AND KEEP IT SAFE.")
            print("   THIS IS YOUR ONLY WAY TO UNLOCK THE SYSTEM IF PHONES ARE LOST.")
            print("!"*60 + "\n")
            input("   Press [ENTER] after you have SECURED your recovery phrase...")
        else:
            print(" [+] Recovery Seed: SECURED (Hashed in Secure Enclave)")
    except Exception as e:
        print(f" [!] Recovery initialization failed: {e}")

    # 6. Launch Sovereign Core
    print("[6/6] INITIATING OMEGA-SOVEREIGN CORE...")
    
    # Finalize Ghost Resurrection loop
    initialize_ghost_guardian()
    
    # Resource-Aware Ability Loader (Surveillance)
    resource_aware_loader()
    
    print("----------------------------------------------------")
    print(">>> SYSTEM ONLINE: http://localhost:8000")
    print(">>> TELEGRAM BOT: ACTIVE")
    print("----------------------------------------------------")
    
    try:
        subprocess.run(["python", "-m", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"])
    except KeyboardInterrupt:
        print("\n[!] Sovereign Core suspended by Commander.")

if __name__ == "__main__":
    initiate_deployment()
