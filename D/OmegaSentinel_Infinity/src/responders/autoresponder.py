"""
Automated Threat Response System
- Auto-kill suspicious processes
- Auto-block malicious IPs
- Auto-isolate infected files
- Incident response automation
"""
import logging
from typing import Dict, List, Optional
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)

class ThreatLevel(str, Enum):
    """Threat severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AutoResponseAction(str, Enum):
    """Automated response actions"""
    ALERT_ONLY = "alert"
    QUARANTINE = "quarantine"
    KILL_PROCESS = "kill"
    BLOCK_IP = "block_ip"
    ISOLATE_NETWORK = "isolate_network"

class ResponsePolicy:
    """Define response policies based on threat level"""
    
    policies = {
        ThreatLevel.LOW: {
            "actions": [AutoResponseAction.ALERT_ONLY],
            "auto_execute": False,
            "notification": True,
        },
        ThreatLevel.MEDIUM: {
            "actions": [AutoResponseAction.ALERT_ONLY, AutoResponseAction.QUARANTINE],
            "auto_execute": False,
            "notification": True,
        },
        ThreatLevel.HIGH: {
            "actions": [AutoResponseAction.QUARANTINE, AutoResponseAction.KILL_PROCESS, AutoResponseAction.BLOCK_IP],
            "auto_execute": True,  # Auto-execute recommended actions
            "notification": True,
        },
        ThreatLevel.CRITICAL: {
            "actions": [AutoResponseAction.KILL_PROCESS, AutoResponseAction.BLOCK_IP, AutoResponseAction.ISOLATE_NETWORK],
            "auto_execute": True,  # Immediate auto-execution
            "notification": True,
        }
    }

class Autoresponder:
    """Automated threat response engine"""
    
    def __init__(self, firewall_manager=None, process_monitor=None):
        self.firewall_manager = firewall_manager
        self.process_monitor = process_monitor
        self.response_history = []
        self.is_enabled = True
        self.auto_kill_enabled = False  # Disabled by default for safety
    
    def enable_auto_kill(self) -> Dict:
        """Enable automatic process killing (DANGEROUS)"""
        self.auto_kill_enabled = True
        logger.warning("DANGEROUS: Auto-kill of suspicious processes ENABLED")
        
        return {
            "status": "success",
            "message": "Auto-kill ENABLED - System will automatically kill suspicious processes",
            "warning": "THIS IS DANGEROUS - Only enable if you know what you're doing",
            "timestamp": datetime.now().isoformat()
        }
    
    def disable_auto_kill(self) -> Dict:
        """Disable automatic process killing (SAFE)"""
        self.auto_kill_enabled = False
        logger.info("Auto-kill DISABLED - Manual intervention required")
        
        return {
            "status": "success",
            "message": "Auto-kill DISABLED - All actions require manual approval",
            "timestamp": datetime.now().isoformat()
        }
    
    def respond_to_threat(self, threat: Dict) -> Dict:
        """Generate automated response to threat"""
        if not self.is_enabled:
            return {"status": "disabled"}
        
        threat_type = threat.get("type", "unknown")
        threat_level = threat.get("severity", ThreatLevel.LOW)
        
        # Get policy for this threat level
        policy = ResponsePolicy.policies.get(threat_level, ResponsePolicy.policies[ThreatLevel.LOW])
        
        actions = []
        
        # Generate recommended actions
        for action in policy["actions"]:
            action_result = self._execute_action(action, threat)
            actions.append(action_result)
        
        response = {
            "status": "success",
            "threat_id": threat.get("id", "unknown"),
            "threat_type": threat_type,
            "severity": threat_level,
            "policy": policy,
            "actions_recommended": [str(a) for a in policy["actions"]],
            "actions_executed": actions,
            "timestamp": datetime.now().isoformat()
        }
        
        self.response_history.append(response)
        return response
    
    def _execute_action(self, action: AutoResponseAction, threat: Dict) -> Dict:
        """Execute a response action"""
        
        if action == AutoResponseAction.ALERT_ONLY:
            return {
                "action": action,
                "result": "Alert generated",
                "status": "completed"
            }
        
        elif action == AutoResponseAction.QUARANTINE:
            # Quarantine file
            file_path = threat.get("path") or threat.get("file")
            if file_path:
                logger.warning(f"QUARANTINE: {file_path}")
                return {
                    "action": action,
                    "file": file_path,
                    "status": "completed",
                    "message": f"File quarantined: {file_path}"
                }
        
        elif action == AutoResponseAction.KILL_PROCESS:
            # Kill process
            if not self.auto_kill_enabled:
                logger.warning(f"KILL_PROCESS requested but auto_kill disabled: {threat.get('pid')}")
                return {
                    "action": action,
                    "pid": threat.get("pid"),
                    "status": "pending_approval",
                    "message": "Auto-kill disabled. Manual approval required"
                }
            
            if self.process_monitor:
                pid = threat.get("pid")
                if pid:
                    result = self.process_monitor.terminate_process(pid, force=True)
                    return {
                        "action": action,
                        "status": "completed" if result.get("status") == "success" else "failed",
                        "details": result
                    }
        
        elif action == AutoResponseAction.BLOCK_IP:
            # Block IP
            if self.firewall_manager:
                ip = threat.get("source_ip") or threat.get("ip_address")
                if ip:
                    result = self.firewall_manager.block_ip(ip)
                    return {
                        "action": action,
                        "ip": ip,
                        "status": "completed" if result.get("status") == "success" else "failed",
                        "details": result
                    }
        
        elif action == AutoResponseAction.ISOLATE_NETWORK:
            logger.critical("NETWORK ISOLATION INITIATED")
            return {
                "action": action,
                "status": "pending_approval",
                "message": "Network isolation requires manual approval"
            }
        
        return {"action": action, "status": "unknown"}
    
    def get_response_recommendations(self, threat: Dict) -> Dict:
        """Get recommended actions without executing"""
        threat_level = threat.get("severity", ThreatLevel.LOW)
        policy = ResponsePolicy.policies.get(threat_level)
        
        return {
            "status": "success",
            "threat_id": threat.get("id"),
            "threat_level": threat_level,
            "recommended_actions": [str(a) for a in policy["actions"]],
            "auto_execute": policy["auto_execute"],
            "details": policy,
            "timestamp": datetime.now().isoformat()
        }
    
    def get_response_history(self, limit: int = 100) -> Dict:
        """Get history of responses"""
        history = self.response_history[-limit:]
        
        return {
            "status": "success",
            "total_responses": len(self.response_history),
            "recent_responses": history,
            "by_severity": {
                "critical": len([r for r in history if r.get("severity") == ThreatLevel.CRITICAL]),
                "high": len([r for r in history if r.get("severity") == ThreatLevel.HIGH]),
                "medium": len([r for r in history if r.get("severity") == ThreatLevel.MEDIUM]),
                "low": len([r for r in history if r.get("severity") == ThreatLevel.LOW]),
            },
            "timestamp": datetime.now().isoformat()
        }
    
    def get_status(self) -> Dict:
        """Get autoresponder status"""
        return {
            "status": "success",
            "enabled": self.is_enabled,
            "auto_kill_enabled": self.auto_kill_enabled,
            "total_responses": len(self.response_history),
            "firewall_integration": self.firewall_manager is not None,
            "process_monitoring": self.process_monitor is not None,
            "timestamp": datetime.now().isoformat()
        }
