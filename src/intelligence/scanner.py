import psutil
import os
import time

# List of sensitive directories to watch
SENSITIVE_PATHS = ["C:\\Windows\\System32", "D:\\OmegaSentinel_Infinity\\.env"]

def monitor_behavior():
    print("[!] Sentinel-UG: Heuristic Scanner Active...")
    while True:
        for proc in psutil.process_iter(['pid', 'name', 'username']):
            try:
                # 1. Detect high CPU usage (Potential Miner/Ransomware)
                cpu_usage = proc.cpu_percent(interval=0.1)
                if cpu_usage > 80:
                    print(f"[ALERT] Zero-Day Suspect: {proc.info['name']} (PID: {proc.info['pid']})")
                    generate_vaccine(proc.info['pid'], proc.info['name'])

            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        time.sleep(1)

def generate_vaccine(pid, name):
    # This is the "Antivirus" generator
    print(f"[*] Analyzing {name}... Synthesizing Vaccine.")
    with open(f"vaccine_{name}.ps1", "w") as f:
        f.write(f"# Automated Vaccine for {name}\n")
        f.write(f"Stop-Process -ID {pid} -Force\n")
        f.write(f"Write-Host 'Threat {name} has been neutralized by OmegaSentinel.'")
    print(f"[SUCCESS] Vaccine generated: vaccine_{name}.ps1")

if __name__ == "__main__":
    monitor_behavior()