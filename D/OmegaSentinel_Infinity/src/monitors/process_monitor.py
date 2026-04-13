"""
Process Monitoring & Detection Module
- Monitor running processes
- Detect suspicious process behavior
- Handle process termination
"""
import os
import logging
import subprocess
from typing import Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    logger.warning("psutil not available - process monitoring disabled. Install: pip install psutil")

class ProcessMonitor:
    """Monitor and detect suspicious processes"""
    
    def __init__(self):
        self.suspicious_processes = []
        self.running_processes = {}
        
        # Known malicious process names
        self.malicious_process_names = [
            "cmd.exe",  # Command prompt (context dependent)
            "powershell.exe",  # PowerShell (context dependent)
            "wscript.exe",  # Windows Script Host
            "cscript.exe",  # Command Script Host
            "mshta.exe",  # HTML Application Host
            "regsvr32.exe",  # Register COM objects (abuse vector)
            "certutil.exe",  # Certificate (abuse vector)
            "bitsadmin.exe",  # Background Intelligent Transfer Service (abuse vector)
            "rundll32.exe",  # Rundll32 (abuse vector)
            "svchost.exe",  # System service (only in System32)
        ]
        
        # Suspicious behavior indicators
        self.suspicious_behaviors = {
            "suspicious_child": ["cmd.exe", "powershell.exe", "cscript.exe"],
            "suspicious_network": ["wget", "curl", "powershell"],
            "suspicious_memory": [],  # Filled with checks
        }
    
    def get_all_processes(self) -> Dict:
        """Get list of all running processes"""
        if not PSUTIL_AVAILABLE:
            return {
                "status": "error",
                "message": "psutil not installed. Run: pip install psutil"
            }
        
        try:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'exe', 'cmdline']):
                try:
                    processes.append({
                        "pid": proc.info['pid'],
                        "name": proc.info['name'],
                        "path": proc.info['exe'],
                        "command": ' '.join(proc.info['cmdline'] or []),
                    })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            return {
                "status": "success",
                "total_processes": len(processes),
                "processes": processes[:100],  # Limit to 100
                "timestamp": datetime.now().isoformat()
            }
        
        except Exception as e:
            logger.error(f"Process enumeration failed: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def scan_processes_for_threats(self) -> Dict:
        """Scan all processes for suspicious behavior"""
        if not PSUTIL_AVAILABLE:
            return {"status": "error", "message": "psutil not available"}
        
        suspicious = []
        
        try:
            for proc in psutil.process_iter(['pid', 'name', 'exe', 'cmdline']):
                try:
                    proc_info = proc.info
                    pid = proc_info['pid']
                    name = proc_info['name']
                    exe = proc_info['exe'] or ""
                    cmdline = proc_info['cmdline'] or []
                    
                    # Check for suspicious process names
                    if name.lower() in [p.lower() for p in self.malicious_process_names]:
                        # Exception: svchost should only be in System32
                        if name.lower() == "svchost.exe" and "System32" not in exe:
                            suspicious.append({
                                "pid": pid,
                                "process": name,
                                "threat_type": "suspicious_location",
                                "reason": "svchost.exe not in System32",
                                "path": exe,
                                "severity": "high",
                                "timestamp": datetime.now().isoformat()
                            })
                        elif name.lower() != "svchost.exe":
                            suspicious.append({
                                "pid": pid,
                                "process": name,
                                "threat_type": "known_abuse_vector",
                                "reason": f"{name} commonly used in attacks",
                                "cmdline": ' '.join(cmdline),
                                "severity": "medium",
                                "timestamp": datetime.now().isoformat()
                            })
                    
                    # Check for PowerShell encoded commands
                    cmd_str = ' '.join(cmdline).lower()
                    if "powershell" in cmd_str and ("-enc" in cmd_str or "-encodedcommand" in cmd_str):
                        suspicious.append({
                            "pid": pid,
                            "process": name,
                            "threat_type": "encoded_command",
                            "reason": "PowerShell with encoded command",
                            "cmdline": ' '.join(cmdline)[:100],  # Truncate
                            "severity": "high",
                            "timestamp": datetime.now().isoformat()
                        })
                    
                    # Check for suspicious network operations
                    if any(tool in cmd_str for tool in ["certutil", "bitsadmin", "wget", "curl"]):
                        suspicious.append({
                            "pid": pid,
                            "process": name,
                            "threat_type": "suspicious_download",
                            "reason": "Process commonly used for downloads",
                            "cmdline": ' '.join(cmdline)[:100],
                            "severity": "high",
                            "timestamp": datetime.now().isoformat()
                        })
                
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            self.suspicious_processes = suspicious
            
            return {
                "status": "success",
                "total_scanned": psutil.pid_exists(1),
                "suspicious_found": len(suspicious),
                "suspicious_processes": suspicious,
                "timestamp": datetime.now().isoformat()
            }
        
        except Exception as e:
            logger.error(f"Process scan failed: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def get_process_details(self, pid: int) -> Dict:
        """Get detailed information about a process"""
        if not PSUTIL_AVAILABLE:
            return {"status": "error", "message": "psutil not available"}
        
        try:
            proc = psutil.Process(pid)
            
            with proc.oneshot():
                return {
                    "status": "success",
                    "pid": pid,
                    "name": proc.name(),
                    "exe": proc.exe(),
                    "cmdline": ' '.join(proc.cmdline()),
                    "status": proc.status(),
                    "create_time": datetime.fromtimestamp(proc.create_time()).isoformat(),
                    "memory_mb": proc.memory_info().rss / 1024 / 1024,
                    "cpu_percent": proc.cpu_percent(interval=0.1),
                    "connections": len(proc.connections()),
                    "timestamp": datetime.now().isoformat()
                }
        
        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            return {"status": "error", "message": f"Cannot access process: {str(e)}"}
    
    def terminate_process(self, pid: int, force: bool = False) -> Dict:
        """Terminate a suspicious process"""
        if not PSUTIL_AVAILABLE:
            return {"status": "error", "message": "psutil not available"}
        
        try:
            proc = psutil.Process(pid)
            name = proc.name()
            
            if force:
                proc.kill()
                message = f"Forcefully killed process: {name} (PID: {pid})"
            else:
                proc.terminate()
                message = f"Terminated process: {name} (PID: {pid})"
            
            logger.warning(f"Process terminated: {name} (PID: {pid})")
            
            return {
                "status": "success",
                "message": message,
                "pid": pid,
                "process_name": name,
                "method": "force_kill" if force else "terminate",
                "timestamp": datetime.now().isoformat()
            }
        
        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            return {"status": "error", "message": f"Cannot terminate: {str(e)}"}
    
    def get_suspicious_summary(self) -> Dict:
        """Get summary of suspicious processes"""
        return {
            "status": "success",
            "total_suspicious": len(self.suspicious_processes),
            "by_severity": {
                "critical": len([p for p in self.suspicious_processes if p.get("severity") == "critical"]),
                "high": len([p for p in self.suspicious_processes if p.get("severity") == "high"]),
                "medium": len([p for p in self.suspicious_processes if p.get("severity") == "medium"]),
            },
            "by_type": {},
            "timestamp": datetime.now().isoformat()
        }
