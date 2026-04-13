"""
LOPUTHJOSEPH - IMMUTABLE INTEGRITY CHAIN
- Hash-chains all security logs to prevent tampering
- Every log entry includes the SHA-256 hash of the previous entry
"""

import os
import hashlib
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class IntegrityChain:
    """Blockchain-style immutable logging for system evidence"""
    
    def __init__(self, log_file: str = "logs/security_audit.chain"):
        self.log_file = log_file
        self.last_hash = self._get_last_hash()
        os.makedirs("logs", exist_ok=True)

    def _get_last_hash(self) -> str:
        """Retrieve the hash of the last valid entry in the chain"""
        if not os.path.exists(self.log_file):
            return "0" * 64 # Genesis block hash
            
        try:
            with open(self.log_file, "r") as f:
                lines = f.readlines()
                if not lines: return "0" * 64
                last_entry = json.loads(lines[-1])
                return last_entry.get("hash", "0" * 64)
        except:
            return "0" * 64

    def log_event(self, event_type: str, details: str):
        """Append a new, hash-chained entry to the log"""
        timestamp = datetime.now().isoformat()
        
        # Data to be hashed (Previous Hash + Current Event)
        payload = f"{self.last_hash}|{timestamp}|{event_type}|{details}"
        current_hash = hashlib.sha256(payload.encode()).hexdigest()
        
        entry = {
            "timestamp": timestamp,
            "event": event_type,
            "details": details,
            "prev_hash": self.last_hash,
            "hash": current_hash
        }
        
        with open(self.log_file, "a") as f:
            f.write(json.dumps(entry) + "\n")
            
        self.last_hash = current_hash
        logger.debug(f"[INTEGRITY] Event Logged: {event_type} (Chain Hash: {current_hash[:8]})")

    def verify_chain_integrity(self) -> bool:
        """Audit the entire log file to detect deleted or modified entries"""
        if not os.path.exists(self.log_file): return True
        
        current_prev_hash = "0" * 64
        line_num = 1
        
        try:
            with open(self.log_file, "r") as f:
                for line in f:
                    entry = json.loads(line)
                    
                    # Verify Linkage
                    if entry["prev_hash"] != current_prev_hash:
                        logger.critical(f"[!] INTEGRITY GAP DETECTED at entry #{line_num}! Log history has been tampered with.")
                        return False
                        
                    # Verify Hash
                    payload = f"{entry['prev_hash']}|{entry['timestamp']}|{entry['event']}|{entry['details']}"
                    verified_hash = hashlib.sha256(payload.encode()).hexdigest()
                    if entry["hash"] != verified_hash:
                        logger.critical(f"[!] HASH MISMATCH at entry #{line_num}! Event content has been modified.")
                        return False
                        
                    current_prev_hash = entry["hash"]
                    line_num += 1
                    
            logger.info(f"[+] Integrity Chain Verified: {line_num-1} entries intact.")
            return True
        except Exception as e:
            logger.error(f"Verification failed: {e}")
            return False

integrity_chain = IntegrityChain()
