import socket

class OffensiveAI:
    def scan_target(self, target_ip):
        print(f"[*] AI-Fuzzer: Scanning {target_ip} for service vulnerabilities...")
        open_ports = []
        # Scanning common ports for service version identification
        for port in [80, 443, 22, 3389]:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.1)
            if sock.connect_ex((target_ip, port)) == 0:
                open_ports.append(port)
            sock.close()
        return open_ports
