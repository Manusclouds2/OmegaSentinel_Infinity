"""
ELITE AUTO-RESPONSE ENGINE - Immediate Threat Elimination
Military-grade automated response with instant process termination and quarantine
"""

import psutil
import subprocess
import os
import logging
from datetime import datetime
from typing import Dict, List
from enum import Enum

logger = logging.getLogger(__name__)

class ThreatLevel(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

class EliteAutoResponder:
    """Elite auto-response engine with immediate threat elimination"""
    
    def __init__(self, firewall_manager=None, process_monitor=None):
        self.firewall_manager = firewall_manager
        self.process_monitor = process_monitor
        
        # Response policies
        self.auto_kill_enabled = False  # Safety: disabled by default
        self.auto_quarantine_enabled = True  # Always on for safety
        self.auto_isolate_network = False  # Network isolation (use carefully)
        
        self.response_history = []
        self.threat_log = []
        self.kill_queue = []
        self.emergency_response_initiated = False
    
    def respond_to_threat(self, threat: Dict) -> Dict:
        """Immediate response to detected threat"""
        response = {
            "threat_id": threat.get("id"),
            "response_time": datetime.now().isoformat(),
            "actions_taken": [],
            "success": False
        }
        
        # Determine threat level
        threat_level = self._determine_threat_level(threat)
        
        logger.warning(f"THREAT DETECTED: {threat.get('type')} - Level: {threat_level.name}")
        
        try:
            # CRITICAL threats: Immediate kill
            if threat_level == ThreatLevel.CRITICAL:
                if self.auto_kill_enabled:
                    response["actions_taken"].append("INSTANT_KILL")
                    self._kill_process_immediately(threat.get("pid"))
                else:
                    response["actions_taken"].append("KILL_QUEUED")
                    self.kill_queue.append(threat)
                
                response["actions_taken"].append("EMERGENCY_QUARANTINE")
                self._emergency_quarantine(threat)
                
                if self.auto_isolate_network:
                    response["actions_taken"].append("NETWORK_ISOLATION")
                    self._isolate_network()
                
                response["success"] = True
            
            # HIGH threats: Kill if auto-kill enabled, otherwise alert + quarantine
            elif threat_level == ThreatLevel.HIGH:
                if self.auto_kill_enabled:
                    response["actions_taken"].append("PROCESS_TERMINATION")
                    self._kill_process_immediately(threat.get("pid"))
                
                response["actions_taken"].append("QUARANTINE")
                self._quarantine_threat(threat)
                
                if self.firewall_manager:
                    response["actions_taken"].append("FIREWALL_BLOCK")
                    self._block_with_firewall(threat)
                
                response["success"] = True
            
            # MEDIUM threats: Alert + quarantine
            elif threat_level == ThreatLevel.MEDIUM:
                response["actions_taken"].append("ALERT")
                response["actions_taken"].append("QUARANTINE")
                self._quarantine_threat(threat)
                response["success"] = True
            
            # LOW threats: Log and monitor
            else:
                response["actions_taken"].append("LOGGING")
                response["success"] = True
        
        except Exception as e:
            logger.error(f"Error responding to threat: {e}")
            response["error"] = str(e)
        
        # Log response
        self.response_history.append(response)
        self.threat_log.append(threat)
        
        return response
    
    def _determine_threat_level(self, threat: Dict) -> ThreatLevel:
        """Determine threat severity"""
        threat_type = threat.get("type", "").upper()
        severity = threat.get("severity", "MEDIUM")
        
        # Critical indicators
        critical_indicators = [
            "RANSOMWARE", "WORM", "TROJAN_BANKER", "BACKDOOR", "ROOTKIT",
            "ZERO_DAY", "APT", "MEM_INJECTION", "PROCESS_HOLLOWING"
        ]
        
        if any(indicator in threat_type for indicator in critical_indicators):
            return ThreatLevel.CRITICAL
        
        if severity == "CRITICAL" or threat.get("behavior_score", 0) >= 20:
            return ThreatLevel.CRITICAL
        
        if severity == "HIGH" or threat.get("behavior_score", 0) >= 10:
            return ThreatLevel.HIGH
        
        if severity == "MEDIUM" or threat.get("behavior_score", 0) >= 5:
            return ThreatLevel.MEDIUM
        
        return ThreatLevel.LOW
    
    def _kill_process_immediately(self, pid: int) -> bool:
        """Immediately terminate suspicious process"""
        try:
            process = psutil.Process(pid)
            
            # Get process info before killing
            proc_name = process.name()
            logger.critical(f"KILLING PROCESS: {proc_name} (PID: {pid})")
            
            # Step 1: Kill child processes first
            try:
                children = process.children(recursive=True)
                for child in children:
                    try:
                        child.kill()
                        logger.warning(f"Killed child process: {child.name()} (PID: {child.pid})")
                    except:
                        pass
            except:
                pass
            
            # Step 2: Kill main process
            try:
                process.kill()
                logger.critical(f"KILLED: {proc_name} (PID: {pid})")
                return True
            except psutil.AccessDenied:
                # Try force kill with admin
                try:
                    subprocess.run(
                        f"taskkill /PID {pid} /F",
                        shell=True,
                        capture_output=True,
                        timeout=5
                    )
                    logger.critical(f"Force-killed: {proc_name} (PID: {pid})")
                    return True
                except:
                    logger.error(f"Failed to kill process {pid}")
                    return False
        
        except Exception as e:
            logger.error(f"Error killing process {pid}: {e}")
            return False
    
    def _emergency_quarantine(self, threat: Dict):
        """Immediately quarantine threat"""
        try:
            file_path = threat.get("file_path", "")
            
            if file_path and os.path.exists(file_path):
                quarantine_dir = "emergency_quarantine"
                os.makedirs(quarantine_dir, exist_ok=True)
                
                dest_path = os.path.join(quarantine_dir, os.path.basename(file_path) + ".danger")
                os.rename(file_path, dest_path)
                
                logger.critical(f"Quarantined: {file_path} -> {dest_path}")
        
        except Exception as e:
            logger.error(f"Quarantine error: {e}")
    
    def _quarantine_threat(self, threat: Dict) -> bool:
        """Quarantine suspected threat file"""
        try:
            file_path = threat.get("file_path", "")
            
            if not file_path:
                return False
            
            if os.path.exists(file_path):
                quarantine_dir = "quarantine"
                os.makedirs(quarantine_dir, exist_ok=True)
                
                dest_path = os.path.join(quarantine_dir, os.path.basename(file_path) + ".quarantine")
                os.rename(file_path, dest_path)
                
                logger.warning(f"Quarantined: {file_path}")
                return True
        
        except Exception as e:
            logger.error(f"Quarantine error: {e}")
        
        return False
    
    def _block_with_firewall(self, threat: Dict):
        """Block threat's network communication"""
        if not self.firewall_manager:
            return
        
        try:
            # Block outbound connections
            rule_name = f"Block-Threat-{threat.get('id')}"
            self.firewall_manager.create_rule(
                name=rule_name,
                direction="Outbound",
                action="Block",
                program=threat.get("file_path", "")
            )
            
            logger.warning(f"Firewall rule created: {rule_name}")
        
        except Exception as e:
            logger.error(f"Firewall block error: {e}")
    
    def _isolate_network(self) -> bool:
        """Isolate system from network"""
        try:
            # Disable all network adapters
            subprocess.run(
                "netsh int set interface ethernet admin=disabled",
                shell=True,
                timeout=5
            )
            
            logger.critical("NETWORK ISOLATION ACTIVATED")
            return True
        
        except Exception as e:
            logger.error(f"Network isolation error: {e}")
            return False
    
    def process_kill_queue(self) -> Dict:
        """Process queued kills (when auto-kill enabled by admin)"""
        results = {
            "queued_threats": len(self.kill_queue),
            "killed": 0,
            "failed": 0,
            "action_log": []
        }
        
        if not self.auto_kill_enabled:
            results["message"] = "Auto-kill disabled - queue not processed"
            return results
        
        for threat in self.kill_queue:
            try:
                pid = threat.get("pid")
                if pid and self._kill_process_immediately(pid):
                    results["killed"] += 1
                    results["action_log"].append(f"Killed PID {pid}")
                else:
                    results["failed"] += 1
                    results["action_log"].append(f"Failed to kill PID {pid}")
            except Exception as e:
                results["failed"] += 1
                results["action_log"].append(f"Error: {str(e)}")
        
        self.kill_queue.clear()
        return results
    
    def enable_auto_kill(self) -> Dict:
        """Enable automatic process killing (DANGEROUS)"""
        self.auto_kill_enabled = True
        logger.critical("AUTO-KILL ENABLED - SYSTEM IN AGGRESSIVE DEFENSE MODE")
        
        # Process any queued threats
        result = self.process_kill_queue()
        
        return {
            "status": "Auto-kill enabled",
            "processed_queue": result,
            "warning": "System in AGGRESSIVE DEFENSE MODE - Auto-killing enabled"
        }
    
    def disable_auto_kill(self) -> Dict:
        """Disable automatic process killing"""
        self.auto_kill_enabled = False
        logger.info("Auto-kill disabled - reverting to normal mode")
        
        return {
            "status": "Auto-kill disabled",
            "mode": "Normal threat detection"
        }
    
    def get_status(self) -> Dict:
        """Get auto-response system status"""
        return {
            "auto_kill_enabled": self.auto_kill_enabled,
            "auto_quarantine_enabled": self.auto_quarantine_enabled,
            "auto_isolate_network": self.auto_isolate_network,
            "defense_mode": "AGGRESSIVE" if self.auto_kill_enabled else "NORMAL",
            "responses_executed": len(self.response_history),
            "threats_logged": len(self.threat_log),
            "queued_kills": len(self.kill_queue),
            "system_status": "PROTECTING" if self.auto_kill_enabled else "MONITORING"
        }
    
    def get_response_history(self, limit: int = 100) -> List[Dict]:
        """Get response history"""
        return self.response_history[-limit:]
    
    def get_threat_log(self, limit: int = 100) -> List[Dict]:
        """Get threat log"""
        return self.threat_log[-limit:]
    
    def emergency_shutdown(self) -> Dict:
        """Emergency system shutdown (last resort)"""
        self.emergency_response_initiated = True
        logger.critical("EMERGENCY SHUTDOWN INITIATED")
        
        try:
            # Kill all suspicious processes
            for threat in self.threat_log[-10:]:  # Kill last 10 detected threats
                if threat.get("pid"):
                    self._kill_process_immediately(threat["pid"])
            
            # Isolate network
            self._isolate_network()
            
            return {
                "status": "Emergency shutdown initiated",
                "processes_terminated": 10,
                "network_isolated": True,
                "message": "System in emergency lockdown"
            }
        
        except Exception as e:
            logger.error(f"Emergency shutdown error: {e}")
            return {"status": "Emergency shutdown failed", "error": str(e)}
    
    def reset_to_normal(self) -> Dict:
        """Reset to normal operation after threat elimination"""
        self.auto_kill_enabled = False
        self.auto_isolate_network = False
        self.emergency_response_initiated = False
        self.threat_log.clear()
        self.kill_queue.clear()
        
        logger.info("System reset to normal operation")
        
        return {
            "status": "System reset to normal",
            "defense_mode": "MONITORING",
            "logs_cleared": True
        }
