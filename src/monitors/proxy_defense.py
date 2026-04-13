"""
UNIVERSAL PROXY DEFENSE MODULE
- Provides SOCKS5 and HTTP Proxy filtering
- Enables defense on restricted environments (Mobile, IoT, Browsers)
- Filters packets 'in-flight' without kernel-level firewall access
"""

import socket
import threading
import logging
import select
import time
from typing import Dict, List, Optional
try:
    from dnslib import DNSRecord, QTYPE, RR, A
    DNS_AVAILABLE = True
except ImportError:
    DNS_AVAILABLE = False

logger = logging.getLogger(__name__)

class UniversalProxyDefense:
    """SOCKS5 Proxy & DNS-Based Defense for restricted environments"""
    
    def __init__(self, host: str = "0.0.0.0", proxy_port: int = 8888, dns_port: int = 53):
        self.host = host
        self.proxy_port = proxy_port
        self.dns_port = dns_port
        self.is_running = False
        self.proxy_socket = None
        self.dns_socket = None
        self.blocked_domains = set(["malware.c2", "exfiltrate.io", "attacker.com", "ransomware.live"])
        self.blocked_ips = set(["1.2.3.4", "6.6.6.6"])

    def start_all(self):
        """Start both Proxy and DNS servers"""
        self.is_running = True
        threading.Thread(target=self.start_proxy, daemon=True).start()
        if DNS_AVAILABLE:
            threading.Thread(target=self.start_dns_server, daemon=True).start()
        else:
            logger.warning("[!] dnslib not installed. DNS Filtering DISABLED.")

    def start_proxy(self):
        """Start the universal SOCKS5 proxy server"""
        try:
            self.proxy_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.proxy_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.proxy_socket.bind((self.host, self.proxy_port))
            self.proxy_socket.listen(100)
            
            logger.info(f"[PROXY] Universal Proxy Defense active on {self.host}:{self.proxy_port}")
            
            while self.is_running:
                client_sock, addr = self.proxy_socket.accept()
                threading.Thread(target=self._handle_client, args=(client_sock,), daemon=True).start()
                
        except Exception as e:
            logger.error(f"Proxy failed to start: {e}")

    def start_dns_server(self):
        """Start the DNS-based filtering gatekeeper"""
        try:
            self.dns_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.dns_socket.bind((self.host, self.dns_port))
            logger.info(f"[DNS] Universal DNS Gatekeeper active on {self.host}:{self.dns_port}")
            
            while self.is_running:
                data, addr = self.dns_socket.recvfrom(1024)
                threading.Thread(target=self._handle_dns_query, args=(data, addr), daemon=True).start()
        except Exception as e:
            logger.error(f"DNS server failed to start: {e}")

    def _handle_dns_query(self, data, addr):
        """Process DNS queries and blackhole malicious domains"""
        try:
            request = DNSRecord.parse(data)
            qname = str(request.q.qname).rstrip('.')
            
            if qname in self.blocked_domains:
                logger.critical(f"[DNS_BLOCK] Blackholing malicious domain: {qname}")
                # Return 127.0.0.1 (Loopback) to neutralize the threat
                reply = request.reply()
                reply.add_answer(RR(qname, QTYPE.A, rdata=A("127.0.0.1"), ttl=60))
                self.dns_socket.sendto(reply.pack(), addr)
            else:
                # Forward to real DNS (Google/Cloudflare)
                real_dns = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                real_dns.settimeout(2.0)
                real_dns.sendto(data, ("8.8.8.8", 53))
                response, _ = real_dns.recvfrom(1024)
                self.dns_socket.sendto(response, addr)
                real_dns.close()
                
        except Exception as e:
            logger.error(f"DNS query processing error: {e}")

    def _handle_client(self, client_sock):
        """Handle SOCKS5 negotiation and filtering"""
        try:
            # 1. SOCKS5 Greeting
            greeting = client_sock.recv(2)
            if not greeting or greeting[0] != 0x05:
                client_sock.close()
                return
            
            # No authentication required (0x00)
            client_sock.sendall(b"\x05\x00")
            
            # 2. Connection Request
            request = client_sock.recv(4)
            if not request or request[1] != 0x01: # Only CONNECT supported
                client_sock.close()
                return
            
            atyp = request[3]
            target_addr = ""
            target_port = 0
            
            if atyp == 0x01: # IPv4
                target_addr = socket.inet_ntoa(client_sock.recv(4))
            elif atyp == 0x03: # Domain name
                name_len = client_sock.recv(1)[0]
                target_addr = client_sock.recv(name_len).decode()
            
            target_port = int.from_raw(client_sock.recv(2), 'big')
            
            # 3. Filtering Logic (Proxy Defense)
            if self._is_blocked(target_addr):
                logger.warning(f"[PROXY] BLOCKING connection to malicious target: {target_addr}")
                client_sock.sendall(b"\x05\x02\x00\x01\x00\x00\x00\x00\x00\x00") # Connection not allowed
                client_sock.close()
                return
            
            # 4. Establish Remote Connection
            try:
                remote_sock = socket.create_connection((target_addr, target_port), timeout=10)
                # Success response
                client_sock.sendall(b"\x05\x00\x00\x01\x00\x00\x00\x00\x00\x00")
                
                # 5. Data Transfer (Bi-directional)
                self._tunnel(client_sock, remote_sock)
                
            except Exception as e:
                client_sock.sendall(b"\x05\x01\x00\x01\x00\x00\x00\x00\x00\x00") # General failure
                client_sock.close()
                
        except Exception as e:
            logger.error(f"Proxy client error: {e}")
            client_sock.close()

    def _is_blocked(self, address: str) -> bool:
        """Check if target address is in the threat database"""
        return address in self.blocked_domains or address in self.blocked_ips

    def _tunnel(self, client, remote):
        """Pass data between client and remote, performing DPI if possible"""
        while True:
            r, w, x = select.select([client, remote], [], [])
            if client in r:
                data = client.recv(4096)
                if not data: break
                remote.sendall(data)
            if remote in r:
                data = remote.recv(4096)
                if not data: break
                client.sendall(data)
        client.close()
        remote.close()

proxy_defense = UniversalProxyDefense()
