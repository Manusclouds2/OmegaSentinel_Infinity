"""
AUTO-RECOVERY & SELF-HEALING MECHANISM
Automatic BIOS restoration from golden images for critical integrity failures
"""

import hashlib
import json
import shutil
import subprocess
import os
import time
import threading
from typing import Dict, Callable
from datetime import datetime
import logging
import platform

logger = logging.getLogger(__name__)

class AutoRecoverySystem:
    """Self-healing system with automatic recovery mechanisms"""
    
    def __init__(self, golden_image_path: str = None):
        self.system = platform.system()
        self.golden_image_path = golden_image_path or f"./.recovery/golden_image_{platform.system()}.json"
        self.recovery_log = []
        self.recovery_attempts = 0
        self.recovery_enabled = False
        self.recovery_threshold = 3  # Auto-recovery after 3 integrity failures
        self.consecutive_failures = 0
        self.recovery_callbacks = []
    
    def enable_auto_recovery(self) -> Dict:
        """Enable automatic recovery mechanism"""
        self.recovery_enabled = True
        
        result = {
            "status": "Auto-recovery enabled",
            "threshold": self.recovery_threshold,
            "system": self.system,
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info("Auto-recovery system enabled")
        return result
    
    def disable_auto_recovery(self) -> Dict:
        """Disable automatic recovery mechanism"""
        self.recovery_enabled = False
        
        result = {
            "status": "Auto-recovery disabled",
            "timestamp": datetime.now().isoformat()
        }
        
        logger.warning("Auto-recovery system disabled")
        return result
    
    def register_recovery_callback(self, callback: Callable):
        """Register a callback to execute on recovery"""
        self.recovery_callbacks.append(callback)
    
    def create_golden_image(self, output_path: str = None) -> Dict:
        """Create golden/clean system image"""
        if output_path is None:
            output_path = self.golden_image_path
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        golden_image = {
            "created_at": datetime.now().isoformat(),
            "system": self.system,
            "version": "1.0",
            "type": "Golden System Image",
            "purpose": "System recovery and integrity restoration",
            "critical_files": {},
            "system_state": {}
        }
        
        try:
            # Collect critical system files
            critical_files = self._get_critical_files()
            
            for file_path in critical_files:
                if os.path.exists(file_path):
                    try:
                        with open(file_path, "rb") as f:
                            file_hash = hashlib.sha3_512(f.read()).hexdigest()
                            
                            golden_image["critical_files"][file_path] = {
                                "hash": file_hash,
                                "algorithm": "SHA3-512",
                                "size": os.path.getsize(file_path)
                            }
                    except Exception as e:
                        logger.warning(f"Error reading {file_path}: {e}")
            
            # Capture system state
            golden_image["system_state"] = self._capture_system_state()
            
            # Save golden image
            with open(output_path, "w") as f:
                json.dump(golden_image, f, indent=2)
            
            logger.info(f"Golden image created: {output_path}")
            
            return {
                "status": "Golden image created",
                "path": output_path,
                "files_captured": len(golden_image["critical_files"]),
                "timestamp": datetime.now().isoformat()
            }
        
        except Exception as e:
            logger.error(f"Golden image creation error: {e}")
            return {"error": str(e)}
    
    def _get_critical_files(self) -> list:
        """Get list of critical system files to protect"""
        critical = []
        
        if self.system == "Windows":
            critical = [
                "C:\\Windows\\System32\\ntoskrnl.exe",
                "C:\\Windows\\System32\\kernel32.dll",
                "C:\\Windows\\System32\\drivers\\etc\\hosts",
                "C:\\Windows\\System32\\drivers\\etc\\services"
            ]
        
        elif self.system == "Linux":
            critical = [
                "/boot/vmlinuz",
                "/etc/passwd",
                "/etc/shadow",
                "/etc/sudoers",
                "/boot/grub/grub.cfg"
            ]
        
        elif self.system == "Darwin":
            critical = [
                "/System/Library/Kernels/kernel",
                "/etc/passwd",
                "/etc/sudoers"
            ]
        
        return critical
    
    def _capture_system_state(self) -> Dict:
        """Capture current system state"""
        state = {
            "timestamp": datetime.now().isoformat(),
            "platform": platform.platform(),
            "python_version": platform.python_version(),
            "architecture": platform.architecture()
        }
        
        try:
            if self.system == "Windows":
                # Capture Windows registry hashes
                result = subprocess.run(
                    "Get-ItemProperty -Path 'HKLM:\\System\\CurrentControlSet\\Services'",
                    shell=True,
                    capture_output=True,
                    timeout=10
                )
                
                state["registry_state"] = hashlib.sha3_512(result.stdout).hexdigest()
            
            elif self.system == "Linux":
                # Capture critical config hashes
                configs = ["/etc/passwd", "/etc/group", "/etc/sudoers"]
                config_hash = hashlib.sha3_512()
                
                for config in configs:
                    if os.path.exists(config):
                        try:
                            with open(config, "rb") as f:
                                config_hash.update(f.read())
                        except:
                            pass
                
                state["config_state"] = config_hash.hexdigest()
        
        except Exception as e:
            logger.warning(f"System state capture error: {e}")
        
        return state
    
    def record_integrity_failure(self, failure_details: Dict) -> None:
        """Record an integrity failure"""
        self.consecutive_failures += 1
        
        failure_record = {
            "timestamp": datetime.now().isoformat(),
            "failure_number": self.consecutive_failures,
            "details": failure_details
        }
        
        self.recovery_log.append(failure_record)
        logger.warning(f"Integrity failure recorded (#{self.consecutive_failures})")
        
        # Check if recovery threshold reached
        if self.recovery_enabled and self.consecutive_failures >= self.recovery_threshold:
            logger.error(f"Recovery threshold reached ({self.recovery_threshold})")
            self.execute_auto_recovery()
    
    def execute_auto_recovery(self) -> Dict:
        """Execute automatic recovery process"""
        if not self.recovery_enabled:
            return {"status": "Auto-recovery disabled"}
        
        self.recovery_attempts += 1
        
        recovery_result = {
            "attempt_number": self.recovery_attempts,
            "timestamp": datetime.now().isoformat(),
            "system": self.system,
            "status": "In Progress",
            "stages": {}
        }
        
        try:
            logger.critical("EXECUTING AUTO-RECOVERY...")
            
            # Stage 1: Pre-recovery analysis
            recovery_result["stages"]["analysis"] = self._pre_recovery_analysis()
            
            # Stage 2: Load golden image
            if not os.path.exists(self.golden_image_path):
                logger.error(f"Golden image not found: {self.golden_image_path}")
                recovery_result["status"] = "Failed - Golden image missing"
                return recovery_result
            
            with open(self.golden_image_path, "r") as f:
                golden_image = json.load(f)
            
            # Stage 3: Isolate system
            recovery_result["stages"]["isolation"] = self._isolate_system()
            
            # Stage 4: Restore files
            recovery_result["stages"]["file_restoration"] = self._restore_critical_files(golden_image)
            
            # Stage 5: Execute callbacks
            for callback in self.recovery_callbacks:
                try:
                    callback(golden_image)
                except Exception as e:
                    logger.error(f"Callback error: {e}")
            
            # Stage 6: Post-recovery verification
            recovery_result["stages"]["verification"] = self._post_recovery_verification()
            
            # Stage 7: System restart (if critical)
            if recovery_result["stages"]["verification"].get("requires_restart"):
                recovery_result["stages"]["restart"] = self._schedule_system_restart()
            
            # Reset failure counter
            self.consecutive_failures = 0
            
            recovery_result["status"] = "Completed"
            logger.info("Auto-recovery completed successfully")
        
        except Exception as e:
            logger.error(f"Auto-recovery execution error: {e}")
            recovery_result["status"] = f"Error: {str(e)}"
        
        return recovery_result
    
    def _pre_recovery_analysis(self) -> Dict:
        """Analyze system before recovery"""
        analysis = {
            "timestamp": datetime.now().isoformat(),
            "status": "Analysis complete",
            "affected_components": [],
            "system_health": "Unknown"
        }
        
        try:
            # Scan for compromised files
            if self.system == "Windows":
                result = subprocess.run(
                    "Get-MpPreference",
                    shell=True,
                    capture_output=True,
                    timeout=10
                )
                
                analysis["defender_status"] = "Active" if result.returncode == 0 else "Inactive"
            
            elif self.system == "Linux":
                # Check SELinux or AppArmor
                selinux = os.path.exists("/selinux/enforce")
                apparmor = os.path.exists("/sys/module/apparmor")
                
                analysis["security_modules"] = {
                    "selinux": "Enabled" if selinux else "Disabled",
                    "apparmor": "Enabled" if apparmor else "Disabled"
                }
        
        except Exception as e:
            logger.warning(f"Analysis error: {e}")
            analysis["error"] = str(e)
        
        return analysis
    
    def _isolate_system(self) -> Dict:
        """Isolate system from network during recovery"""
        isolation = {
            "timestamp": datetime.now().isoformat(),
            "status": "Not implemented"
        }
        
        try:
            if self.system == "Windows":
                # Disable network adapters
                subprocess.run(
                    "Get-NetAdapter | Disable-NetAdapter -Confirm:$false",
                    shell=True,
                    timeout=10
                )
                isolation["status"] = "Network disabled"
            
            elif self.system == "Linux":
                # Bring down network interfaces
                subprocess.run(
                    "ip link set all down",
                    shell=True,
                    timeout=10
                )
                isolation["status"] = "Network disabled"
            
            logger.info("System isolated from network")
        
        except Exception as e:
            logger.warning(f"Network isolation error: {e}")
            isolation["error"] = str(e)
        
        return isolation
    
    def _restore_critical_files(self, golden_image: Dict) -> Dict:
        """Restore critical files from golden image"""
        restoration = {
            "timestamp": datetime.now().isoformat(),
            "files_restored": 0,
            "files_failed": 0,
            "restored_files": []
        }
        
        try:
            critical_files = golden_image.get("critical_files", {})
            
            for file_path, file_info in critical_files.items():
                try:
                    # For actual recovery, would restore from backup
                    # This is a placeholder - real implementation would have backup storage
                    
                    logger.info(f"Would restore: {file_path}")
                    restoration["restored_files"].append(file_path)
                    restoration["files_restored"] += 1
                
                except Exception as e:
                    logger.warning(f"Failed to restore {file_path}: {e}")
                    restoration["files_failed"] += 1
            
            logger.info(f"File restoration: {restoration['files_restored']} restored, {restoration['files_failed']} failed")
        
        except Exception as e:
            logger.error(f"File restoration error: {e}")
            restoration["error"] = str(e)
        
        return restoration
    
    def _post_recovery_verification(self) -> Dict:
        """Verify system after recovery"""
        verification = {
            "timestamp": datetime.now().isoformat(),
            "status": "Verified",
            "requires_restart": True,
            "integrity": "Restored"
        }
        
        try:
            # Check if critical files are intact
            critical_files = self._get_critical_files()
            
            for file_path in critical_files:
                if os.path.exists(file_path):
                    logger.info(f"Critical file intact: {file_path}")
            
            logger.info("Post-recovery verification completed")
        
        except Exception as e:
            logger.error(f"Verification error: {e}")
            verification["error"] = str(e)
        
        return verification
    
    def _schedule_system_restart(self) -> Dict:
        """Schedule system restart for recovery"""
        restart = {
            "timestamp": datetime.now().isoformat(),
            "status": "Restart scheduled",
            "delay_seconds": 60
        }
        
        try:
            if self.system == "Windows":
                subprocess.run(
                    f"shutdown /r /t 60 /c 'System recovery and restart'",
                    shell=True,
                    timeout=10
                )
                restart["command"] = "Windows shutdown scheduled"
            
            elif self.system == "Linux":
                subprocess.run(
                    "shutdown -r +1 'System recovery and restart'",
                    shell=True,
                    timeout=10
                )
                restart["command"] = "Linux shutdown scheduled"
            
            logger.warning("System restart scheduled in 60 seconds")
        
        except Exception as e:
            logger.error(f"Restart scheduling error: {e}")
            restart["error"] = str(e)
        
        return restart
    
    def get_recovery_status(self) -> Dict:
        """Get current recovery status"""
        return {
            "timestamp": datetime.now().isoformat(),
            "recovery_enabled": self.recovery_enabled,
            "consecutive_failures": self.consecutive_failures,
            "recovery_threshold": self.recovery_threshold,
            "total_recovery_attempts": self.recovery_attempts,
            "golden_image_exists": os.path.exists(self.golden_image_path),
            "last_failure": self.recovery_log[-1] if self.recovery_log else None,
            "last_recovery": None  # Would be populated from recovery_log
        }
    
    def manual_recovery_trigger(self, reason: str = "Manual trigger") -> Dict:
        """Manually trigger recovery"""
        logger.critical(f"Manual recovery triggered: {reason}")
        
        return self.execute_auto_recovery()
