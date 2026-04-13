"""
Windows Firewall Management Module
- Create/delete firewall rules
- Enable/disable rules
- Real enforcement on Windows
"""
import subprocess
import logging
import json
from typing import Dict, List, Optional
from datetime import datetime
import platform

logger = logging.getLogger(__name__)

class FirewallManager:
    """Manage Windows Firewall rules"""
    
    def __init__(self):
        self.is_windows = platform.system() == "Windows"
        self.rules = {}
    
    def create_rule(self, rule_name: str, direction: str, action: str, 
                   local_port: Optional[int] = None, remote_ip: Optional[str] = None,
                   protocol: str = "tcp") -> Dict:
        """Create a new firewall rule"""
        
        if not self.is_windows:
            logger.warning("Firewall enforcement only available on Windows")
            return {
                "status": "warning",
                "message": "Firewall enforcement requires Windows",
                "rule_name": rule_name
            }
        
        try:
            # Build netsh command
            cmd = [
                "netsh", "advfirewall", "firewall", "add", "rule",
                f"name=\"{rule_name}\"",
                f"dir={direction.lower()}",
                f"action={action.lower()}"
            ]
            
            if local_port:
                cmd.append(f"localport={local_port}")
            if remote_ip:
                cmd.append(f"remoteip={remote_ip}")
            
            cmd.append(f"protocol={protocol}")
            cmd.append("enable=yes")
            
            # Execute with admin privileges
            result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
            
            if result.returncode == 0:
                self.rules[rule_name] = {
                    "name": rule_name,
                    "direction": direction,
                    "action": action,
                    "local_port": local_port,
                    "remote_ip": remote_ip,
                    "protocol": protocol,
                    "enabled": True,
                    "created_at": datetime.now().isoformat()
                }
                logger.info(f"Firewall rule created: {rule_name}")
                return {
                    "status": "success",
                    "message": f"Rule '{rule_name}' created successfully",
                    "rule": self.rules[rule_name]
                }
            else:
                logger.error(f"Firewall rule creation failed: {result.stderr}")
                return {
                    "status": "error",
                    "message": result.stderr or "Failed to create rule",
                    "rule_name": rule_name
                }
        
        except Exception as e:
            logger.error(f"Firewall rule creation error: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "rule_name": rule_name
            }
    
    def delete_rule(self, rule_name: str) -> Dict:
        """Delete a firewall rule"""
        
        if not self.is_windows:
            return {
                "status": "warning",
                "message": "Firewall enforcement requires Windows"
            }
        
        try:
            cmd = ["netsh", "advfirewall", "firewall", "delete", "rule", f"name=\"{rule_name}\""]
            result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
            
            if result.returncode == 0:
                if rule_name in self.rules:
                    del self.rules[rule_name]
                logger.info(f"Firewall rule deleted: {rule_name}")
                return {
                    "status": "success",
                    "message": f"Rule '{rule_name}' deleted successfully"
                }
            else:
                return {
                    "status": "error",
                    "message": result.stderr or "Failed to delete rule"
                }
        
        except Exception as e:
            logger.error(f"Firewall rule deletion error: {str(e)}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    def enable_rule(self, rule_name: str) -> Dict:
        """Enable a firewall rule"""
        
        if not self.is_windows:
            return {
                "status": "warning",
                "message": "Firewall enforcement requires Windows"
            }
        
        try:
            cmd = ["netsh", "advfirewall", "firewall", "set", "rule", f"name=\"{rule_name}\"", "new", "enable=yes"]
            result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
            
            if result.returncode == 0:
                if rule_name in self.rules:
                    self.rules[rule_name]["enabled"] = True
                return {
                    "status": "success",
                    "message": f"Rule '{rule_name}' enabled"
                }
            else:
                return {
                    "status": "error",
                    "message": result.stderr or "Failed to enable rule"
                }
        
        except Exception as e:
            logger.error(f"Enable rule error: {str(e)}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    def disable_rule(self, rule_name: str) -> Dict:
        """Disable a firewall rule"""
        
        if not self.is_windows:
            return {
                "status": "warning",
                "message": "Firewall enforcement requires Windows"
            }
        
        try:
            cmd = ["netsh", "advfirewall", "firewall", "set", "rule", f"name=\"{rule_name}\"", "new", "enable=no"]
            result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
            
            if result.returncode == 0:
                if rule_name in self.rules:
                    self.rules[rule_name]["enabled"] = False
                return {
                    "status": "success",
                    "message": f"Rule '{rule_name}' disabled"
                }
            else:
                return {
                    "status": "error",
                    "message": result.stderr or "Failed to disable rule"
                }
        
        except Exception as e:
            logger.error(f"Disable rule error: {str(e)}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    def list_rules(self) -> Dict:
        """List all active firewall rules"""
        
        if not self.is_windows:
            return {
                "status": "success",
                "rules": self.rules,
                "message": "Local rules (Windows Firewall management requires Windows OS)"
            }
        
        try:
            # Show all rules via netsh
            cmd = ["netsh", "advfirewall", "firewall", "show", "rule", "name=all"]
            result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
            
            return {
                "status": "success",
                "rules": self.rules,
                "system_rules_count": len(result.stdout.split('\n')) if result.returncode == 0 else 0,
                "timestamp": datetime.now().isoformat()
            }
        
        except Exception as e:
            logger.error(f"List rules error: {str(e)}")
            return {
                "status": "success",
                "rules": self.rules,
                "note": "Could not fetch system rules"
            }
    
    def block_ip(self, ip_address: str) -> Dict:
        """Block traffic from an IP address"""
        rule_name = f"BLOCK-{ip_address}"
        return self.create_rule(
            rule_name=rule_name,
            direction="in",
            action="block",
            remote_ip=ip_address,
            protocol="tcp"
        )
    
    def allow_ip(self, ip_address: str) -> Dict:
        """Allow traffic from an IP address"""
        rule_name = f"ALLOW-{ip_address}"
        return self.create_rule(
            rule_name=rule_name,
            direction="in",
            action="allow",
            remote_ip=ip_address,
            protocol="tcp"
        )
    
    def block_port(self, port: int, protocol: str = "tcp") -> Dict:
        """Block incoming connections on a port"""
        rule_name = f"BLOCK-{protocol.upper()}-{port}"
        return self.create_rule(
            rule_name=rule_name,
            direction="in",
            action="block",
            local_port=port,
            protocol=protocol
        )
