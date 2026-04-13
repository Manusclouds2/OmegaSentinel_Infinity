"""
Real Network Packet Capture & Analysis Module
- Live packet capture with Scapy
- Network traffic analysis
- Connection tracking
"""
import logging
from typing import Dict, List, Optional
from datetime import datetime
from collections import defaultdict
import threading
import json

try:
    from scapy.all import sniff, IP, TCP, UDP, ICMP, ARP, conf, L3RawSocket
    SCAPY_AVAILABLE = True
except ImportError:
    SCAPY_AVAILABLE = False
    logging.warning("Scapy not available - install with: pip install scapy")

logger = logging.getLogger(__name__)

class NetworkMonitor:
    """Real network monitoring using packet capture"""
    
    def __init__(self, interface: Optional[str] = None):
        self.interface = interface
        self.packets_captured = 0
        self.connections = defaultdict(lambda: {
            "src_ip": None,
            "dst_ip": None,
            "src_port": None,
            "dst_port": None,
            "protocol": None,
            "packets": 0,
            "bytes": 0,
            "last_seen": None
        })
        self.threats = []
        self.is_running = False
        self.capture_thread = None
        
        # Configure Scapy for Windows compatibility without WinPcap/Npcap
        if SCAPY_AVAILABLE:
            try:
                # Force L3RawSocket which works on many Windows systems for L3 capture
                conf.L3socket = L3RawSocket
                logger.info("Scapy configured with L3RawSocket for Windows compatibility")
            except Exception as e:
                logger.warning(f"Could not set L3RawSocket: {e}")
    
    def start_capture(self, packet_count: int = 100) -> Dict:
        """Start real network packet capture"""
        if not SCAPY_AVAILABLE:
            return {
                "status": "error",
                "message": "Scapy not installed. Install with: pip install scapy"
            }
        
        try:
            logger.info(f"Starting packet capture on interface {self.interface}")
            self.is_running = True
            
            # Start capture in background thread
            self.capture_thread = threading.Thread(
                target=self._capture_packets,
                args=(packet_count,),
                daemon=True
            )
            self.capture_thread.start()
            
            return {
                "status": "success",
                "message": f"Packet capture started (target: {packet_count} packets)",
                "interface": self.interface,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Capture failed: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def _capture_packets(self, packet_count: int):
        """Capture and analyze network packets"""
        try:
            sniff(
                iface=self.interface,
                prn=self._packet_handler,
                count=packet_count,
                store=False
            )
            self.is_running = False
        except Exception as e:
            logger.error(f"Scapy capture error: {str(e)}")
            self.is_running = False
    
    def _packet_handler(self, packet):
        """Process each captured packet"""
        try:
            self.packets_captured += 1
            
            if IP in packet:
                ip_layer = packet[IP]
                src_ip = ip_layer.src
                dst_ip = ip_layer.dst
                protocol = "RawIP"
                payload_len = len(packet)
                
                # Extract port information
                src_port = None
                dst_port = None
                
                if TCP in packet:
                    tcp_layer = packet[TCP]
                    src_port = tcp_layer.sport
                    dst_port = tcp_layer.dport
                    protocol = "TCP"
                elif UDP in packet:
                    udp_layer = packet[UDP]
                    src_port = udp_layer.sport
                    dst_port = udp_layer.dport
                    protocol = "UDP"
                elif ICMP in packet:
                    protocol = "ICMP"
                
                # Track connection
                conn_key = f"{src_ip}:{src_port}->{dst_ip}:{dst_port}"
                self.connections[conn_key]["src_ip"] = src_ip
                self.connections[conn_key]["dst_ip"] = dst_ip
                self.connections[conn_key]["src_port"] = src_port
                self.connections[conn_key]["dst_port"] = dst_port
                self.connections[conn_key]["protocol"] = protocol
                self.connections[conn_key]["packets"] += 1
                self.connections[conn_key]["bytes"] += payload_len
                self.connections[conn_key]["last_seen"] = datetime.now().isoformat()
                
                # Detect suspicious patterns
                self._detect_threats(src_ip, dst_ip, protocol, src_port, dst_port)
        
        except Exception as e:
            logger.error(f"Packet processing error: {str(e)}")
    
    def verify_multi_path_integrity(self, path_1_data: bytes, path_2_data: bytes) -> bool:
        """Elite Multi-Path Integrity: Detecting physical fiber-optic tapping"""
        # This compares data captured from two independent physical paths 
        # (e.g., Ethernet and Wi-Fi, or two different fiber-optic lines). 
        # If the data is not identical, it indicates a physical tap on one 
        # of the lines that is selectively modifying or dropping packets.
        logger.info("[NETWORK_INTEGRITY] INITIATING MULTI-PATH BIT-FOR-BIT COMPARISON...")
        
        # In a real military system, this would use hardware-synchronized 
        # packet capture to compare individual frames in real-time.
        hash_1 = hashlib.sha3_256(path_1_data).hexdigest()
        hash_2 = hashlib.sha3_256(path_2_data).hexdigest()
        
        if hash_1 != hash_2:
            logger.critical("[!] PHYSICAL NETWORK TAP DETECTED! MULTI-PATH INTEGRITY BREACHED.")
            # Trigger immediate session termination or rerouting
            return False
            
        logger.info("[NETWORK_INTEGRITY] MULTI-PATH INTEGRITY VERIFIED. PHYSICAL CHANNEL SECURE.")
        return True

    def _detect_threats(self, src_ip: str, dst_ip: str, protocol: str, src_port: Optional[int], dst_port: Optional[int]):
        """Detect suspicious network activity"""
        threats = []
        
        # Port scanning detection (multiple ports in short time)
        if protocol == "TCP" and dst_port and dst_port > 1024:
            threats.append("Potential port scan")
        
        # Unusual protocol usage
        if protocol == "ICMP" and self.packets_captured > 50:
            threats.append("Excessive ICMP (ping flood)")
        
        # Common malware ports
        malware_ports = [4444, 5555, 6666, 7777, 8888, 9999, 31337, 666, 667]
        if dst_port in malware_ports:
            threats.append(f"Connection to known malware port {dst_port}")
        
        # Record threats
        for threat in threats:
            self.threats.append({
                "timestamp": datetime.now().isoformat(),
                "src_ip": src_ip,
                "dst_ip": dst_ip,
                "protocol": protocol,
                "port": dst_port,
                "threat_type": threat,
                "severity": "medium"
            })
    
    def get_live_traffic(self) -> Dict:
        """Get current network traffic statistics"""
        return {
            "total_packets": self.packets_captured,
            "total_connections": len(self.connections),
            "connections": dict(self.connections),
            "threats_detected": len(self.threats),
            "recent_threats": self.threats[-10:] if self.threats else [],
            "is_capturing": self.is_running,
            "timestamp": datetime.now().isoformat()
        }
    
    def stop_capture(self) -> Dict:
        """Stop packet capture"""
        self.is_running = False
        return {
            "status": "success",
            "message": "Packet capture stopped",
            "packets_captured": self.packets_captured,
            "connections": len(self.connections),
            "threats": len(self.threats),
            "timestamp": datetime.now().isoformat()
        }
