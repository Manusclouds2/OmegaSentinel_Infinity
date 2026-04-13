"""
Real Threat Intelligence & File Scanning Module
- VirusTotal API integration
- Shodan threat intelligence
- IP reputation checking
"""
import hashlib
import requests
import json
from typing import Dict, List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class ThreatIntelligence:
    """Real threat intelligence service using public APIs"""
    
    def __init__(self, virustotal_key: str = None, shodan_key: str = None):
        self.virustotal_key = virustotal_key
        self.shodan_key = shodan_key
        self.vt_base_url = "https://www.virustotal.com/api/v3"
        self.shodan_base_url = "https://api.shodan.io"
        self.abuseipdb_url = "https://api.abuseipdb.com/api/v2"
    
    def scan_file_virustotal(self, file_path: str) -> Dict:
        """
        Scan a file using VirusTotal API
        Returns real detection results from 70+ antivirus engines
        """
        if not self.virustotal_key:
            return {
                "status": "error",
                "message": "VirusTotal API key not configured",
                "file": file_path,
                "timestamp": datetime.now().isoformat()
            }
        
        try:
            # Calculate file hash
            sha256_hash = self._calculate_file_hash(file_path)
            
            # Query VirusTotal for existing analysis
            headers = {"x-apikey": self.virustotal_key}
            url = f"{self.vt_base_url}/files/{sha256_hash}"
            
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                analysis = data.get("data", {}).get("attributes", {})
                
                return {
                    "status": "success",
                    "file": file_path,
                    "sha256": sha256_hash,
                    "detected": analysis.get("last_analysis_stats", {}).get("malicious", 0) > 0,
                    "detections": {
                        "malicious": analysis.get("last_analysis_stats", {}).get("malicious", 0),
                        "suspicious": analysis.get("last_analysis_stats", {}).get("suspicious", 0),
                        "undetected": analysis.get("last_analysis_stats", {}).get("undetected", 0),
                        "total": 70  # Approximate total engines
                    },
                    "type_description": analysis.get("type_description", "Unknown"),
                    "last_analysis_date": analysis.get("last_analysis_date", "Never"),
                    "vendor_results": analysis.get("last_analysis_results", {}),
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "status": "not_found",
                    "message": "File not in VirusTotal database",
                    "file": file_path,
                    "sha256": sha256_hash,
                    "timestamp": datetime.now().isoformat()
                }
        
        except Exception as e:
            logger.error(f"VirusTotal scan failed: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "file": file_path,
                "timestamp": datetime.now().isoformat()
            }
    
    def scan_url_virustotal(self, url: str) -> Dict:
        """Scan a URL for malicious content using VirusTotal"""
        if not self.virustotal_key:
            return {"status": "error", "message": "VirusTotal API key not configured"}
        
        try:
            headers = {"x-apikey": self.virustotal_key}
            url_id = self._url_to_id(url)
            
            response = requests.get(
                f"{self.vt_base_url}/urls/{url_id}",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                analysis = data.get("data", {}).get("attributes", {})
                
                return {
                    "status": "success",
                    "url": url,
                    "detected": analysis.get("last_analysis_stats", {}).get("malicious", 0) > 0,
                    "detections": analysis.get("last_analysis_stats", {}),
                    "categories": analysis.get("categories", {}),
                    "timestamp": datetime.now().isoformat()
                }
            return {"status": "not_found", "url": url}
        
        except Exception as e:
            logger.error(f"URL scan failed: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def check_ip_reputation(self, ip: str) -> Dict:
        """Check IP reputation using AbuseIPDB"""
        try:
            # Free IP reputation check (without API key)
            response = requests.get(
                f"https://ipqualityscore.com/api/json/ip/reputation/{ip}?strictness=0",
                params={"ip": ip},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "status": "success",
                    "ip": ip,
                    "is_vpn": data.get("is_vpn", False),
                    "is_bot": data.get("is_bot", False),
                    "fraud_score": data.get("fraud_score", 0),
                    "threat_level": "high" if data.get("fraud_score", 0) > 75 else "medium" if data.get("fraud_score", 0) > 25 else "low",
                    "last_seen": data.get("last_seen", "Unknown"),
                    "timestamp": datetime.now().isoformat()
                }
        except Exception as e:
            logger.error(f"IP reputation check failed: {str(e)}")
        
        return {"status": "error", "ip": ip}
    
    def search_shodan(self, query: str) -> Dict:
        """Search Shodan for exposed services/vulnerabilities"""
        if not self.shodan_key:
            return {"status": "error", "message": "Shodan API key not configured"}
        
        try:
            response = requests.get(
                f"{self.shodan_base_url}/shodan/host/search",
                params={"query": query, "key": self.shodan_key},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "status": "success",
                    "query": query,
                    "results": data.get("matches", [])[:10],  # Top 10 results
                    "total": data.get("total", 0),
                    "timestamp": datetime.now().isoformat()
                }
        except Exception as e:
            logger.error(f"Shodan search failed: {str(e)}")
        
        return {"status": "error", "query": query}
    
    @staticmethod
    def _calculate_file_hash(file_path: str) -> str:
        """Calculate SHA256 hash of a file"""
        sha256 = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    sha256.update(chunk)
            return sha256.hexdigest()
        except Exception as e:
            logger.error(f"Hash calculation failed: {str(e)}")
            return ""
    
    @staticmethod
    def _url_to_id(url: str) -> str:
        """Convert URL to VirusTotal URL ID"""
        import base64
        return base64.urlsafe_b64encode(url.encode()).decode().rstrip("=")
