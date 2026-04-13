"""
SYSTEM-WIDE FILE SCANNER - Comprehensive Threat Detection Engine
Scans entire file system for malware, threats, and anomalies
"""

import os
import threading
import time
from pathlib import Path
from typing import Dict, List, Callable
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class SystemFileScanner:
    """Elite system-wide file scanning system"""
    
    def __init__(self, threat_detector=None):
        self.threat_detector = threat_detector
        self.scan_running = False
        self.scan_thread = None
        self.scan_progress = {
            "files_scanned": 0,
            "threats_found": 0,
            "scan_started": None,
            "estimated_time_remaining": None,
            "status": "Idle"
        }
        self.scan_history = []
        self.infected_files = []
    
    def scan_directory(self, directory: str, recursive: bool = True, callback: Callable = None) -> Dict:
        """Scan specific directory for threats"""
        results = {
            "directory": directory,
            "scan_start": datetime.now().isoformat(),
            "files_scanned": 0,
            "threats_found": 0,
            "critical_threats": [],
            "high_threats": [],
            "medium_threats": [],
            "skipped_files": 0,
            "scan_errors": [],
            "status": "Scanning"
        }
        
        if not os.path.exists(directory):
            results["status"] = "Error: Directory not found"
            return results
        
        try:
            # Dangerous file extensions to prioritize
            priority_extensions = [
                ".exe", ".dll", ".sys", ".scr", ".vbs", ".ps1", ".bat", ".cmd",
                ".jar", ".app", ".deb", ".rpm", ".msi", ".dmg"
            ]
            
            # Extensions to skip (safe)
            skip_extensions = [
                ".txt", ".doc", ".xlsx", ".pdf", ".jpg", ".png", ".mp3", ".mp4",
                ".git", ".lock", ".tmp"
            ]
            
            files_to_scan = []
            
            # Collect files
            if recursive:
                for root, dirs, files in os.walk(directory):
                    # Skip system directories
                    dirs[:] = [d for d in dirs if d not in [
                        "$Recycle.Bin", "System Volume Information", "PageFile.sys",
                        "hiberfil.sys", ".git", "__pycache__", "node_modules"
                    ]]
                    
                    for file in files:
                        file_path = os.path.join(root, file)
                        
                        # Check extensions
                        ext = os.path.splitext(file)[1].lower()
                        if ext in skip_extensions:
                            continue
                        
                        files_to_scan.append((file_path, ext in priority_extensions))
            else:
                for file in os.listdir(directory):
                    file_path = os.path.join(directory, file)
                    if os.path.isfile(file_path):
                        ext = os.path.splitext(file)[1].lower()
                        if ext not in skip_extensions:
                            files_to_scan.append((file_path, ext in priority_extensions))
            
            # Sort: priority files first
            files_to_scan.sort(key=lambda x: not x[1])
            
            # Scan files
            for file_path, is_priority in files_to_scan:
                try:
                    threat_analysis = self._scan_single_file(file_path)
                    results["files_scanned"] += 1
                    
                    if threat_analysis.get("threat_detected"):
                        results["threats_found"] += 1
                        
                        threat_level = threat_analysis.get("threat_level", "Unknown")
                        if threat_level == "CRITICAL":
                            results["critical_threats"].append(threat_analysis)
                        elif threat_level == "HIGH":
                            results["high_threats"].append(threat_analysis)
                        else:
                            results["medium_threats"].append(threat_analysis)
                        
                        self.infected_files.append(threat_analysis)
                    
                    # Callback for progress updates
                    if callback:
                        callback(results["files_scanned"], len(files_to_scan), threat_analysis)
                
                except Exception as e:
                    results["skipped_files"] += 1
                    results["scan_errors"].append(f"{file_path}: {str(e)}")
                    logger.error(f"Error scanning {file_path}: {e}")
        
        except Exception as e:
            results["status"] = f"Error: {str(e)}"
            logger.error(f"Directory scan error: {e}")
        
        results["scan_end"] = datetime.now().isoformat()
        results["status"] = "Complete"
        self.scan_history.append(results)
        
        return results
    
    def scan_system(self, full_scan: bool = True) -> Dict:
        """Comprehensive system-wide scan"""
        self.scan_progress["status"] = "Initializing"
        self.scan_progress["scan_started"] = datetime.now().isoformat()
        self.scan_running = True
        
        results = {
            "scan_type": "Full System" if full_scan else "Quick",
            "scan_start": datetime.now().isoformat(),
            "directories_scanned": [],
            "total_files_scanned": 0,
            "total_threats": 0,
            "critical": 0,
            "high": 0,
            "medium": 0,
            "status": "In Progress"
        }
        
        try:
            if full_scan:
                # Full system scan
                critical_paths = [
                    "C:\\Windows\\System32",
                    "C:\\Program Files",
                    "C:\\Program Files (x86)",
                    os.path.expanduser("~\\AppData\\Local"),
                    os.path.expanduser("~\\AppData\\Roaming"),
                    os.path.expanduser("~\\Documents"),
                    os.path.expanduser("~\\Downloads"),
                    os.path.expanduser("~\\Desktop"),
                ]
            else:
                # Quick scan - only dangerous locations
                critical_paths = [
                    os.path.expanduser("~\\Downloads"),
                    os.path.expanduser("~\\AppData\\Local\\Temp"),
                    "C:\\Temp",
                ]
            
            # Scan each critical path
            for path in critical_paths:
                if not os.path.exists(path):
                    continue
                
                self.scan_progress["status"] = f"Scanning {path}"
                
                dir_results = self.scan_directory(path, recursive=True)
                
                results["directories_scanned"].append({
                    "directory": path,
                    "files": dir_results["files_scanned"],
                    "threats": dir_results["threats_found"]
                })
                
                results["total_files_scanned"] += dir_results["files_scanned"]
                results["total_threats"] += dir_results["threats_found"]
                results["critical"] += len(dir_results["critical_threats"])
                results["high"] += len(dir_results["high_threats"])
                results["medium"] += len(dir_results["medium_threats"])
                
                if not self.scan_running:
                    results["status"] = "Cancelled"
                    break
        
        except Exception as e:
            results["status"] = f"Error: {str(e)}"
            logger.error(f"System scan error: {e}")
        
        results["scan_end"] = datetime.now().isoformat()
        if results["status"] == "In Progress":
            results["status"] = "Complete"
        
        self.scan_running = False
        self.scan_progress["status"] = "Idle"
        
        return results
    
    def _scan_single_file(self, file_path: str) -> Dict:
        """Scan individual file"""
        analysis = {
            "file": file_path,
            "threat_detected": False,
            "threat_level": "NONE",
            "reasons": [],
            "file_size": 0,
            "file_type": "Unknown"
        }
        
        try:
            # Get file info
            stat = os.stat(file_path)
            analysis["file_size"] = stat.st_size
            
            # Determine file type
            ext = os.path.splitext(file_path)[1].lower()
            analysis["file_type"] = ext or "No extension"
            
            # Use threat detector if available
            if self.threat_detector:
                threat_result = self.threat_detector.detect_anomalies(file_path)
                
                analysis["threat_detected"] = threat_result["threat_level"] != "LOW"
                analysis["threat_level"] = threat_result["threat_level"]
                analysis["reasons"] = threat_result["anomalies"]
            
            # Additional checks
            # 1. Executable with no extension
            if not ext and self._is_executable(file_path):
                analysis["threat_detected"] = True
                analysis["threat_level"] = "HIGH"
                analysis["reasons"].append("Executable without extension")
            
            # 2. Double extension (exe.txt, etc)
            if file_path.count(".") > 1:
                parts = file_path.split(".")
                if parts[-2] in ["exe", "dll", "scr", "bat"]:
                    analysis["threat_detected"] = True
                    analysis["threat_level"] = "HIGH"
                    analysis["reasons"].append("Suspicious double extension")
            
            # 3. Size anomalies
            if stat.st_size == 0:
                analysis["threat_detected"] = True
                analysis["threat_level"] = "MEDIUM"
                analysis["reasons"].append("Empty executable")
            
        except Exception as e:
            analysis["error"] = str(e)
        
        return analysis
    
    def _is_executable(self, file_path: str) -> bool:
        """Check if file is executable"""
        try:
            with open(file_path, "rb") as f:
                header = f.read(2)
            return header == b"MZ"  # Windows PE executable
        except:
            return False
    
    def scan_file(self, file_path: str) -> Dict:
        """Scan single file"""
        if not os.path.exists(file_path):
            return {"status": "Error", "message": "File not found"}
        
        return self._scan_single_file(file_path)
    
    def stop_scan(self):
        """Stop ongoing scan"""
        self.scan_running = False
        self.scan_progress["status"] = "Stopped"
    
    def get_scan_progress(self) -> Dict:
        """Get current scan progress"""
        return self.scan_progress
    
    def quarantine_file(self, file_path: str) -> Dict:
        """Move infected file to quarantine"""
        try:
            quarantine_dir = "quarantine"
            os.makedirs(quarantine_dir, exist_ok=True)
            
            # Generate safe filename
            file_name = os.path.basename(file_path)
            dest_path = os.path.join(quarantine_dir, file_name + ".quarantine")
            
            # Move file
            os.rename(file_path, dest_path)
            
            return {
                "success": True,
                "original": file_path,
                "quarantined": dest_path,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Quarantine error: {e}")
            return {"success": False, "error": str(e)}
    
    def get_scan_history(self) -> List[Dict]:
        """Get scan history"""
        return self.scan_history
    
    def get_infected_files(self) -> List[Dict]:
        """Get all infected files found"""
        return self.infected_files
    
    def clear_scan_history(self):
        """Clear scan history"""
        self.scan_history.clear()
        self.infected_files.clear()
    
    def get_statistics(self) -> Dict:
        """Get scanning statistics"""
        total_scans = len(self.scan_history)
        total_files = sum(s["files_scanned"] for s in self.scan_history if "files_scanned" in s)
        total_threats = sum(s["threats_found"] for s in self.scan_history if "threats_found" in s)
        
        return {
            "total_scans": total_scans,
            "total_files_scanned": total_files,
            "total_threats_found": total_threats,
            "infected_files": len(self.infected_files),
            "last_scan": self.scan_history[-1]["scan_start"] if self.scan_history else "Never"
        }
