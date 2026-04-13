"""
Global Threat Intelligence (API-less & Open Source)
- Open-source threat feed integration (OTX, MISP, etc.)
- Caching and local reputation lookups
- Fallback logic for when API keys are missing
"""

import os
import requests
import json
import logging
import datetime
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class GlobalIntelligence:
    """Universal threat intelligence from open-source feeds"""
    
    def __init__(self, cache_dir: str = "data/intel_cache"):
        self.cache_dir = cache_dir
        self.os_intel_feeds = [
            "https://raw.githubusercontent.com/stamparm/ipsum/master/ipsum.txt",
            "https://rules.emergingthreats.net/block-rules/compromised-ips.txt",
            "https://feodotracker.abuse.ch/downloads/ipblocklist.txt"
        ]
        self.malicious_ips = set()
        self.last_update = None
        
        # Create cache directory
        os.makedirs(self.cache_dir, exist_ok=True)
        self.load_cache()

    def update_feeds(self) -> Dict:
        """Fetch and aggregate open-source threat feeds"""
        try:
            new_ips = set()
            for url in self.os_intel_feeds:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    lines = response.text.splitlines()
                    for line in lines:
                        if line and not line.startswith('#'):
                            # Basic IP extraction
                            ip = line.split()[0].strip()
                            if '.' in ip: # Basic IPv4 validation
                                new_ips.add(ip)
            
            self.malicious_ips = new_ips
            self.last_update = datetime.datetime.now()
            self.save_cache()
            
            logger.info(f"Threat feeds updated: {len(new_ips)} malicious IPs tracked")
            return {"status": "success", "count": len(new_ips)}
        except Exception as e:
            logger.error(f"Feed update error: {e}")
            return {"status": "error", "message": str(e)}

    def check_reputation(self, ip_address: str) -> Dict:
        """Check IP against locally cached threat feeds"""
        is_malicious = ip_address in self.malicious_ips
        
        return {
            "ip": ip_address,
            "is_malicious": is_malicious,
            "source": "OPEN_SOURCE_FEEDS",
            "risk_level": "HIGH" if is_malicious else "LOW",
            "last_updated": self.last_update.isoformat() if self.last_update else "NEVER"
        }

    def save_cache(self):
        """Save IP list to local file"""
        cache_file = os.path.join(self.cache_dir, "malicious_ips.json")
        with open(cache_file, 'w') as f:
            json.dump(list(self.malicious_ips), f)

    def load_cache(self):
        """Load IP list from local file"""
        cache_file = os.path.join(self.cache_dir, "malicious_ips.json")
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r') as f:
                    self.malicious_ips = set(json.load(f))
                self.last_update = datetime.datetime.fromtimestamp(os.path.getmtime(cache_file))
                logger.info(f"Loaded {len(self.malicious_ips)} IPs from intel cache")
            except Exception as e:
                logger.error(f"Intel cache load error: {e}")
