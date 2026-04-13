"""
CROSS-PLATFORM AUTO-RESPONDER - Universal Threat Elimination
Works on Windows, macOS, Linux, and any computerized device
"""

import os
import platform
import subprocess
import psutil
from typing import Dict, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class UniversalAutoResponder:
    """Cross-platform automatic threat response system"""
    
    def __init__(self):
        self.os_type = platform.system()
        self.is_windows = self.os_type == "Windows"
        self.is_macos = self.os_type == "Darwin"
        self.is_linux = self.os_type == "Linux"
        
        self.response_history = []
        self.threat_log = []
        self.quarantine_dir = self._get_quarantine_dir()
        
        # Create quarantine directory
        os.makedirs(self.quarantine_dir, exist_ok=True)
        
        # Response settings
        self.auto_kill_enabled = False
        self.auto_quarantine_enabled = True
        self.auto_isolate_enabled = False
    
    def _get_quarantine_dir(self) -> str:
        """Get OS-appropriate quarantine directory"""
        # For local activation/testing, use project directory
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        return os.path.join(project_root, "data", "quarantine")
    
    def respond_to_threat(self, threat: Dict) -> Dict:
        """Respond to threat based on OS and severity"""
        response = {
            "threat_id": threat.get("id"),
            "os": self.os_type,
            "response_time": datetime.now().isoformat(),
            "actions_taken": [],
            "success": False
        }
        
        try:
            threat_level = threat.get("severity", "MEDIUM").upper()
            
            # CRITICAL threats
            if threat_level == "CRITICAL":
                if self.auto_kill_enabled:
                    response["actions_taken"].append("INSTANT_KILL")
                    self._kill_process_cross_platform(threat.get("pid"))
                
                response["actions_taken"].append("QUARANTINE")
                self._quarantine_file_cross_platform(threat.get("file_path"))
                
                if self.auto_isolate_enabled:
                    response["actions_taken"].append("ISOLATE_NETWORK")
                    self._isolate_network()
                
                response["success"] = True
            
            # HIGH threats
            elif threat_level == "HIGH":
                if self.auto_kill_enabled:
                    response["actions_taken"].append("KILL_PROCESS")
                    self._kill_process_cross_platform(threat.get("pid"))
                
                response["actions_taken"].append("QUARANTINE")
                self._quarantine_file_cross_platform(threat.get("file_path"))
                
                response["success"] = True
            
            # MEDIUM threats
            else:
                response["actions_taken"].append("ALERT")
                if self.auto_quarantine_enabled:
                    response["actions_taken"].append("QUARANTINE")
                    self._quarantine_file_cross_platform(threat.get("file_path"))
                
                response["success"] = True
        
        except Exception as e:
            logger.error(f"Response error: {e}")
            response["error"] = str(e)
        
        self.response_history.append(response)
        self.threat_log.append(threat)
        
        return response
    
    def _kill_process_cross_platform(self, pid: int) -> bool:
        """Kill process on any OS"""
        try:
            if self.is_windows:
                # Windows: taskkill
                subprocess.run(
                    f"taskkill /PID {pid} /F",
                    shell=True,
                    timeout=5,
                    capture_output=True
                )
            elif self.is_macos or self.is_linux:
                # Unix: kill -9
                os.kill(pid, 9)
            
            logger.warning(f"Killed process {pid} on {self.os_type}")
            return True
        
        except Exception as e:
            logger.error(f"Kill process error: {e}")
            return False
    
    def _quarantine_file_cross_platform(self, file_path: str) -> bool:
        """Quarantine file on any OS"""
        try:
            if not file_path or not os.path.exists(file_path):
                return False
            
            os.makedirs(self.quarantine_dir, exist_ok=True)
            
            file_name = os.path.basename(file_path)
            dest_path = os.path.join(self.quarantine_dir, file_name + ".quarantine")
            
            # Handle file/directory quarantine
            if os.path.isdir(file_path):
                import shutil
                shutil.move(file_path, dest_path)
            else:
                os.rename(file_path, dest_path)
            
            logger.warning(f"Quarantined: {file_path} -> {dest_path}")
            return True
        
        except Exception as e:
            logger.error(f"Quarantine error: {e}")
            return False
    
    def _isolate_network(self) -> bool:
        """Isolate system from network (OS-dependent)"""
        try:
            if self.is_windows:
                # Windows: disable network adapters
                subprocess.run(
                    "netsh int set interface ethernet admin=disabled",
                    shell=True,
                    timeout=10
                )
            elif self.is_macos:
                # macOS: disable Wi-Fi
                subprocess.run(
                    "networksetup -setairportpower en0 off",
                    shell=True,
                    timeout=10
                )
            elif self.is_linux:
                # Linux: bring down network interfaces
                subprocess.run(
                    "ip link set all down",
                    shell=True,
                    timeout=10
                )
            
            logger.critical(f"Network isolated on {self.os_type}")
            return True
        
        except Exception as e:
            logger.error(f"Network isolation error: {e}")
            return False
    
    def scan_running_processes(self) -> List[Dict]:
        """Scan all running processes for threats"""
        threats = []
        
        try:
            for proc in psutil.process_iter(['pid', 'name', 'ppid', 'memory_info']):
                try:
                    proc_info = proc.as_dict()
                    
                    # Check process name for suspicious patterns
                    proc_name = proc_info['name'].lower()
                    
                    # Platform-specific suspicious processes
                    suspicious_names = []
                    
                    if self.is_windows:
                        suspicious_names = [
                            "rundll32", "regsvcs", "certutil", "schtasks",
                            "powershell", "cmd", "wmic"
                        ]
                    elif self.is_linux:
                        suspicious_names = [
                            "curl", "wget", "nc", "bash", "perl", "python"
                        ]
                    elif self.is_macos:
                        suspicious_names = [
                            "osascript", "curl", "wget", "perl", "python"
                        ]
                    
                    for suspicious in suspicious_names:
                        if suspicious in proc_name:
                            # Verify it's actually suspicious
                            memory_mb = proc_info.get('memory_info', {}).rss / 1024 / 1024
                            
                            if memory_mb > 500:  # > 500MB is suspicious
                                threats.append({
                                    "pid": proc_info['pid'],
                                    "name": proc_info['name'],
                                    "memory_mb": memory_mb,
                                    "threat_level": "MEDIUM",
                                    "reason": "Suspicious process + high memory"
                                })
                except:
                    continue
        
        except Exception as e:
            logger.error(f"Process scan error: {e}")
        
        return threats
    
    def get_os_info(self) -> Dict:
        """Get detailed OS information"""
        return {
            "os": self.os_type,
            "version": platform.platform(),
            "architecture": platform.machine(),
            "processor": platform.processor(),
            "hostname": platform.node(),
            "python_version": platform.python_version(),
            "timestamp": datetime.now().isoformat()
        }
    
    def enable_auto_kill(self) -> Dict:
        """Enable auto-kill across all platforms"""
        self.auto_kill_enabled = True
        logger.critical(f"Auto-kill ENABLED on {self.os_type}")
        
        return {
            "status": "Auto-kill enabled",
            "os": self.os_type,
            "warning": "System in aggressive defense mode"
        }
    
    def disable_auto_kill(self) -> Dict:
        """Disable auto-kill"""
        self.auto_kill_enabled = False
        logger.info("Auto-kill disabled")
        
        return {
            "status": "Auto-kill disabled",
            "os": self.os_type,
            "mode": "Normal detection"
        }
    
    def get_status(self) -> Dict:
        """Get responder status"""
        return {
            "os": self.os_type,
            "auto_kill_enabled": self.auto_kill_enabled,
            "auto_quarantine_enabled": self.auto_quarantine_enabled,
            "auto_isolate_enabled": self.auto_isolate_enabled,
            "responses_executed": len(self.response_history),
            "threats_logged": len(self.threat_log),
            "quarantine_location": self.quarantine_dir,
            "defense_mode": "AGGRESSIVE" if self.auto_kill_enabled else "NORMAL"
        }
    
    def get_response_history(self, limit: int = 100) -> List[Dict]:
        """Get response history"""
        return self.response_history[-limit:]
    
    def get_quarantine_contents(self) -> Dict:
        """Get contents of quarantine"""
        quarantined = []
        
        try:
            if os.path.exists(self.quarantine_dir):
                for file in os.listdir(self.quarantine_dir):
                    file_path = os.path.join(self.quarantine_dir, file)
                    try:
                        stat = os.stat(file_path)
                        quarantined.append({
                            "file": file,
                            "path": file_path,
                            "size": stat.st_size,
                            "quarantine_time": datetime.fromtimestamp(stat.st_ctime).isoformat()
                        })
                    except:
                        pass
        
        except Exception as e:
            logger.error(f"Quarantine listing error: {e}")
        
        return {
            "quarantine_dir": self.quarantine_dir,
            "files": quarantined,
            "count": len(quarantined)
        }
    
    def restore_from_quarantine(self, file_name: str) -> Dict:
        """Restore file from quarantine"""
        try:
            quarantine_path = os.path.join(self.quarantine_dir, file_name)
            
            if not os.path.exists(quarantine_path):
                return {"success": False, "error": "File not found in quarantine"}
            
            # Remove .quarantine extension
            restored_name = file_name.replace(".quarantine", "")
            restored_path = os.path.join(os.path.expanduser("~"), "Restored_Files", restored_name)
            
            os.makedirs(os.path.dirname(restored_path), exist_ok=True)
            os.replace(quarantine_path, restored_path)
            
            return {
                "success": True,
                "original": quarantine_path,
                "restored": restored_path,
                "timestamp": datetime.now().isoformat()
            }
        
        except Exception as e:
            logger.error(f"Restore error: {e}")
            return {"success": False, "error": str(e)}
    
    def emergency_response(self) -> Dict:
        """Emergency system response"""
        logger.critical("EMERGENCY RESPONSE ACTIVATED")
        
        results = {
            "status": "Emergency response activated",
            "os": self.os_type,
            "timestamp": datetime.now().isoformat(),
            "actions": []
        }
        
        try:
            # Kill suspicious processes from threat log
            for threat in self.threat_log[-20:]:
                if threat.get("pid"):
                    if self._kill_process_cross_platform(threat["pid"]):
                        results["actions"].append(f"Killed PID {threat['pid']}")
            
            # Isolate network
            if self._isolate_network():
                results["actions"].append("Network isolated")
            
            results["success"] = True
        
        except Exception as e:
            logger.error(f"Emergency response error: {e}")
            results["success"] = False
            results["error"] = str(e)
        
        return results
