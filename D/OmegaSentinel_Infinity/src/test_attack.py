import socket
import time

def simulate_ping_flood():
    print("[*] Simulating a suspicious connection attempt to LOPUTHJOSEPH...")
    target_ip = "127.0.0.1"
    target_port = 80
    
    try:
        # Attempting a rapid connection to trigger a monitor alert
        for i in range(5):
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1)
            s.connect((target_ip, target_port))
            print(f"[!] Connection {i+1} established. System should log this.")
            s.close()
            time.sleep(0.5)
        print("[+] Simulation complete. Check your web dashboard for logs!")
    except Exception as e:
        print(f"[-] Simulation failed: {e}. Is the server running?")

if __name__ == "__main__":
    simulate_ping_flood()
