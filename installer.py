import os
import sys
import platform
import subprocess
import shutil

def install_omega():
    """
    Universal 'One-Command' Installer for LOPUTHJOSEPH.
    Automatically detects OS, installs dependencies, and prepares the environment.
    """
    os_type = platform.system()
    print(f"[*] LOPUTHJOSEPH: UNIVERSAL INSTALLER")
    print(f"[*] DETECTED OS: {os_type}")
    print("="*40)

    # 1. Dependency Management
    print("[*] Phase 1: Installing Core Dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    except Exception as e:
        print(f"[!] Pip install failed: {e}")
        return

    # 2. OS-Specific Kernel Tools
    if os_type == "Windows":
        print("[*] Phase 2: Configuring Windows Filtering Platform (WFP)...")
        # Check for admin
        import ctypes
        if not ctypes.windll.shell32.IsUserAnAdmin():
            print("[!] WARNING: Not running as Administrator. Kernel features may be limited.")
        
    elif os_type == "Linux":
        print("[*] Phase 2: Configuring eBPF/XDP and Netfilter...")
        # Check for root
        if os.getuid() != 0:
            print("[!] WARNING: Not running as Root. eBPF/XDP requires root privileges.")
        
    elif os_type == "Darwin": # macOS
        print("[*] Phase 2: Configuring Packet Filter (PF)...")
        if os.getuid() != 0:
            print("[!] WARNING: Not running as Root. PF rules require sudo.")

    # 3. Environment Preparation
    print("[*] Phase 3: Preparing Data & Logs...")
    directories = ["logs", "data", "data/quarantine", "data/dark_intel_cache", "web", "data/vaccines"]
    for d in directories:
        os.makedirs(d, exist_ok=True)
        print(f" [+] Created: {d}")

    # 4. Finalizing
    print("="*40)
    print("[+] LOPUTHJOSEPH INSTALLATION COMPLETE.")
    print("[+] To start the system remotely, run: python watchdog_service.py")
    print("[+] To start the full suite locally, run: python control.py activate")
    print("="*40)

if __name__ == "__main__":
    install_omega()
