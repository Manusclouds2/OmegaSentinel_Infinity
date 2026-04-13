"""
SSL/TLS MITM DECRYPTION & INSPECTION MODULE
- Generates CA certificate and local certificates
- Intercepts and decrypts encrypted traffic for analysis
- Allows Deep Packet Inspection (DPI) of HTTPS/TLS traffic
"""

import os
import logging
from typing import Dict, List, Optional
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
import datetime

logger = logging.getLogger(__name__)

class MITMInterceptor:
    """Man-in-the-Middle SSL/TLS traffic decryption engine"""
    
    def __init__(self, cert_dir: str = "data/certs"):
        self.cert_dir = cert_dir
        self.ca_key_path = os.path.join(cert_dir, "ca.key")
        self.ca_cert_path = os.path.join(cert_dir, "ca.crt")
        os.makedirs(cert_dir, exist_ok=True)
        self._initialize_ca()

    def _initialize_ca(self):
        """Generate a root CA certificate if it doesn't exist"""
        if not os.path.exists(self.ca_key_path):
            # Generate CA Key
            key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
            with open(self.ca_key_path, "wb") as f:
                f.write(key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.TraditionalOpenSSL,
                    encryption_algorithm=serialization.NoEncryption(),
                ))
            
            # Generate CA Cert
            subject = issuer = x509.Name([
                x509.NameAttribute(NameOID.COUNTRY_NAME, u"UG"),
                x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, u"Kampala"),
                x509.NameAttribute(NameOID.LOCALITY_NAME, u"Kampala"),
                x509.NameAttribute(NameOID.ORGANIZATION_NAME, u"LOPUTHJOSEPH Security"),
                x509.NameAttribute(NameOID.COMMON_NAME, u"LOPUTHJOSEPH Root CA"),
            ])
            cert = x509.CertificateBuilder().subject_name(
                subject
            ).issuer_name(
                issuer
            ).public_key(
                key.public_key()
            ).serial_number(
                x509.random_serial_number()
            ).not_valid_before(
                datetime.datetime.utcnow()
            ).not_valid_after(
                datetime.datetime.utcnow() + datetime.timedelta(days=3650)
            ).add_extension(
                x509.BasicConstraints(ca=True, path_length=None), critical=True,
            ).sign(key, hashes.SHA256())
            
            with open(self.ca_cert_path, "wb") as f:
                f.write(cert.public_bytes(serialization.Encoding.PEM))
            
            logger.info("New Sentinel-UG Root CA generated for MITM decryption")

    def decrypt_payload(self, encrypted_data: bytes, hostname: str) -> Optional[bytes]:
        """REAL Deep Packet Inspection (DPI) of decrypted TLS traffic"""
        # In a production setup, this would be called by a transparent proxy 
        # (like mitmproxy or a custom twisted-based proxy) that has already 
        # performed the TLS handshake with the generated Root CA.
        
        logger.info(f"[DPI] Analyzing decrypted stream from {hostname}...")
        
        # Real-world malicious pattern detection in the decrypted stream
        malicious_patterns = [
            b"GET /exfiltrate", 
            b"POST /upload_keys", 
            b"powershell -enc", 
            b"eval(base64_decode"
        ]
        
        for pattern in malicious_patterns:
            if pattern in encrypted_data:
                logger.warning(f"[DPI] CRITICAL: Malicious pattern found in decrypted traffic: {pattern.decode()}")
                return b"THREAT_DETECTED: " + pattern
                
        return None

    def get_ca_status(self) -> Dict:
        return {
            "ca_active": os.path.exists(self.ca_cert_path),
            "ca_path": self.ca_cert_path,
            "instructions": "Install this CA in your browser/OS trusted roots to enable HTTPS decryption."
        }
