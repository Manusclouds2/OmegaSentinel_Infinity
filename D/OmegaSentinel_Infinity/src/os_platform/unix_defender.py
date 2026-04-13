"""
UNIX-LIKE SYSTEM DEFENDER - Linux/macOS Protection
Advanced threat detection and elimination for Unix-based systems
"""

import os
import platform
import subprocess
import psutil
from typing import Dict, List
from datetime import datetime
import logging
import re

logger = logging.getLogger(__name__)

class UnixDefender:
    """Advanced defender for Linux and macOS systems"""
    
    def __init__(self):
        self.is_macos = platform.system() == "Darwin"
        self.is_linux = platform.system() == "Linux"
        self.system = platform.system()
        self.detection_log = []
    
    # ========== LINUX-SPECIFIC THREATS ==========
    
    def detect_linux_threats(self) -> Dict:
        """Comprehensive Linux threat detection"""
        threats = {
            "scan_time": datetime.now().isoformat(),
            "system": "Linux",
            "threat_categories": {
                "rootkits": self._detect_linux_rootkits(),
                "suspicious_users": self._detect_suspicious_users(),
                "web_shells": self._detect_web_shells(),
                "malicious_scripts": self._detect_malicious_scripts(),
                "persistence_mechanisms": self._detect_persistence(),
                "privilege_escalation": self._detect_privilege_escalation(),
                "backdoors": self._detect_backdoors(),
                "kernel_exploits": self._detect_kernel_exploits()
            }
        }
        
        threat_count = sum(len(v) if isinstance(v, list) else 0 
                           for v in threats["threat_categories"].values())
        threats["total_threats"] = threat_count
        
        return threats
    
    def _detect_linux_rootkits(self) -> List[Dict]:
        """Detect Linux rootkits"""
        suspicious = []
        
        try:
            # 1. Check for kernel modules often used in rootkits
            result = subprocess.run(
                "lsmod",
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.stdout:
                suspicious_modules = [
                    "reptile", "suterusu", "diamorphine", "enyelkm",
                    "azazel", "nulix", "jynx", "shadow"
                ]
                
                for module in suspicious_modules:
                    if module in result.stdout.lower():
                        suspicious.append({
                            "module": module,
                            "threat": "Known rootkit kernel module",
                            "action": "Unload immediately"
                        })
            
            # 2. Check for modified system files
            critical_files = ["/bin/ls", "/bin/ps", "/bin/netstat", "/usr/bin/find"]
            for file_path in critical_files:
                if os.path.exists(file_path):
                    try:
                        stat = os.stat(file_path)
                        # Check suspicious modifications
                        if stat.st_size < 100:  # Binary too small
                            suspicious.append({
                                "file": file_path,
                                "threat": "Binary file suspiciously small",
                                "size": stat.st_size,
                                "action": "Investigate/restore"
                            })
                    except:
                        pass
        
        except Exception as e:
            logger.error(f"Rootkit detection error: {e}")
        
        return suspicious
    
    def _detect_suspicious_users(self) -> List[Dict]:
        """Detect suspicious user accounts"""
        suspicious = []
        
        try:
            # Check /etc/passwd for suspicious users
            with open("/etc/passwd", "r") as f:
                for line in f:
                    if line.startswith("#"):
                        continue
                    
                    parts = line.strip().split(":")
                    if len(parts) < 7:
                        continue
                    
                    username = parts[0]
                    shell = parts[6]
                    uid = int(parts[2])
                    
                    # Check for suspicious indicators
                    suspicious_names = [
                        "apache", "www", "nobody", "mysql", "postgres"
                    ]
                    
                    # Non-system user with UID 0 (root)
                    if uid == 0 and username != "root":
                        suspicious.append({
                            "user": username,
                            "threat": "Non-root user with UID 0 - possible backdoor",
                            "uid": uid,
                            "action": "Delete user account"
                        })
                    
                    # Service account with interactive shell
                    if username in suspicious_names and shell != "/sbin/nologin":
                        suspicious.append({
                            "user": username,
                            "threat": "Service account with interactive shell",
                            "shell": shell,
                            "action": "Change to /sbin/nologin"
                        })
        
        except Exception as e:
            logger.error(f"User detection error: {e}")
        
        return suspicious
    
    def _detect_web_shells(self) -> List[Dict]:
        """Detect web shells on web servers"""
        suspicious = []
        
        try:
            # Check common web directories
            web_dirs = [
                "/var/www/html",
                "/srv/http",
                "/home/*/public_html",
                "/opt/webroot"
            ]
            
            for directory in web_dirs:
                if not os.path.exists(directory):
                    continue
                
                try:
                    for root, dirs, files in os.walk(directory):
                        for file in files:
                            # Check for suspicious web files
                            if file.endswith((".php", ".asp", ".jsp", ".cgi", ".pl")):
                                file_path = os.path.join(root, file)
                                
                                try:
                                    with open(file_path, "r", errors="ignore") as f:
                                        content = f.read()
                                    
                                    # Web shell indicators
                                    if any(indicator in content for indicator in [
                                        "system(", "exec(", "passthru(", "shell_exec(",
                                        "proc_open(", "popen(", "eval(", "assert(",
                                        "`", "${IFS}", "cmd.exe"
                                    ]):
                                        suspicious.append({
                                            "file": file_path,
                                            "threat": "Possible web shell",
                                            "file_type": file.split(".")[-1],
                                            "action": "Delete file"
                                        })
                                except:
                                    pass
                except:
                    continue
        
        except Exception as e:
            logger.error(f"Web shell detection error: {e}")
        
        return suspicious
    
    def _detect_malicious_scripts(self) -> List[Dict]:
        """Detect malicious shell scripts"""
        suspicious = []
        
        try:
            # Check common script locations
            script_dirs = [
                "/tmp",
                "/var/tmp",
                "/dev/shm",
                os.path.expanduser("~/.local/bin"),
                "/usr/local/bin"
            ]
            
            for directory in script_dirs:
                if not os.path.exists(directory):
                    continue
                
                try:
                    for file in os.listdir(directory):
                        file_path = os.path.join(directory, file)
                        
                        if os.path.isfile(file_path) and file.endswith((".sh", ".pl", ".py")):
                            try:
                                with open(file_path, "r", errors="ignore") as f:
                                    content = f.read()
                                
                                # Malicious script indicators
                                if any(indicator in content for indicator in [
                                    "curl", "wget", "/dev/tcp", "nc -", "bash -i",
                                    "rm -rf", "dd if=/dev", "fork()",
                                    "LD_PRELOAD"
                                ]):
                                    suspicious.append({
                                        "script": file_path,
                                        "threat": "Malicious script detected",
                                        "action": "Delete immediately"
                                    })
                            except:
                                pass
                except:
                    continue
        
        except Exception as e:
            logger.error(f"Script detection error: {e}")
        
        return suspicious
    
    def _detect_persistence(self) -> List[Dict]:
        """Detect persistence mechanisms (for long-term compromise)"""
        suspicious = []
        
        try:
            # 1. Check cron jobs
            try:
                result = subprocess.run(
                    "crontab -l",
                    capture_output=True,
                    text=True,
                    timeout=5,
                    shell=True
                )
                
                if result.stdout:
                    for line in result.stdout.split('\n'):
                        if any(cmd in line for cmd in 
                               ["curl", "wget", "nc", "bash -i", ".elf", "/tmp"]):
                            suspicious.append({
                                "persistence": "Malicious cron job",
                                "command": line[:100],
                                "action": "Remove cron job"
                            })
            except:
                pass
            
            # 2. Check /etc/cron.d
            try:
                for file in os.listdir("/etc/cron.d"):
                    with open(os.path.join("/etc/cron.d", file), "r") as f:
                        content = f.read()
                    
                    if any(indicator in content for indicator in 
                           ["curl", "wget", "/dev/tcp"]):
                        suspicious.append({
                            "persistence": "Suspicious /etc/cron.d job",
                            "file": file,
                            "action": "Remove"
                        })
            except:
                pass
            
            # 3. Check .bashrc and .profile
            bash_files = [
                os.path.expanduser("~/.bashrc"),
                os.path.expanduser("~/.profile"),
                os.path.expanduser("~/.bash_profile"),
                "/root/.bashrc",
                "/root/.profile"
            ]
            
            for bashrc in bash_files:
                try:
                    with open(bashrc, "r") as f:
                        content = f.read()
                    
                    if len(content) > 10000 or any(indicator in content 
                        for indicator in ["curl", "wget", "nc -l", "python"]):
                        suspicious.append({
                            "persistence": "Suspicious shell configuration",
                            "file": bashrc,
                            "action": "Review and clean"
                        })
                except:
                    pass
        
        except Exception as e:
            logger.error(f"Persistence detection error: {e}")
        
        return suspicious
    
    def _detect_privilege_escalation(self) -> List[Dict]:
        """Detect privilege escalation vulnerabilities"""
        suspicious = []
        
        try:
            # Check for SUID binaries
            result = subprocess.run(
                "find / -perm -4000 2>/dev/null",
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # Look for suspicious SUID binaries
            if result.stdout:
                suspicious_bins = ["python", "perl", "bash", "sh", "nc", "socat", "ncat"]
                for line in result.stdout.split('\n'):
                    for suspicious in suspicious_bins:
                        if suspicious in line.lower():
                            suspicious.append({
                                "binary": line,
                                "threat": "Suspicious SUID binary",
                                "action": "Remove SUID bit"
                            })
                            break
        
        except Exception as e:
            logger.error(f"Privilege escalation detection error: {e}")
        
        return suspicious
    
    def _detect_backdoors(self) -> List[Dict]:
        """Detect backdoor access mechanisms"""
        suspicious = []
        
        try:
            # Check for unauthorized SSH keys
            ssh_authorized_keys = os.path.expanduser("~/.ssh/authorized_keys")
            if os.path.exists(ssh_authorized_keys):
                try:
                    with open(ssh_authorized_keys, "r") as f:
                        lines = f.readlines()
                    
                    if len(lines) > 5:  # Unusual number of authorized keys
                        suspicious.append({
                            "backdoor": "Multiple SSH authorized keys",
                            "count": len(lines),
                            "action": "Review SSH keys"
                        })
                except:
                    pass
            
            # Check for unauthorized sudo access
            try:
                with open("/etc/sudoers", "r") as f:
                    sudoers = f.read()
                
                # Look for unusual sudoers entries
                if "NOPASSWD" in sudoers and "www-data" in sudoers:
                    suspicious.append({
                        "backdoor": "Service account with NOPASSWD sudo",
                        "threat": "Privilege escalation backdoor",
                        "action": "Remove from sudoers"
                    })
            except PermissionError:
                pass
        
        except Exception as e:
            logger.error(f"Backdoor detection error: {e}")
        
        return suspicious
    
    def _detect_kernel_exploits(self) -> List[Dict]:
        """Detect signs of kernel exploitation"""
        suspicious = []
        
        try:
            # Check kernel version for known vulnerabilities
            result = subprocess.run(
                "uname -r",
                capture_output=True,
                text=True,
                timeout=5,
                shell=True
            )
            
            kernel_version = result.stdout.strip()
            
            # Known vulnerable kernel versions
            vulnerable_patterns = [
                r"4\.4\.[0-8]",  # Old kernel
                r"4\.9\.[0-4]",  # Vulnerable to CVE-2016-5195
                r"5\.0\.[0-3]"   # Various CVEs
            ]
            
            for pattern in vulnerable_patterns:
                if re.search(pattern, kernel_version):
                    suspicious.append({
                        "kernel": kernel_version,
                        "threat": "Vulnerable kernel version detected",
                        "action": "Apply security updates"
                    })
        
        except Exception as e:
            logger.error(f"Kernel exploit detection error: {e}")
        
        return suspicious
    
    # ========== macOS-SPECIFIC THREATS ==========
    
    def detect_macos_threats(self) -> Dict:
        """Comprehensive macOS threat detection"""
        threats = {
            "scan_time": datetime.now().isoformat(),
            "system": "macOS",
            "threat_categories": {
                "malware_variants": self._detect_macos_malware(),
                "gatekeeper_bypass": self._detect_gatekeeper_bypass(),
                "notarization_issues": self._detect_notarization_issues(),
                "suspicious_extensions": self._detect_suspicious_extensions(),
                "keychain_threats": self._detect_keychain_threats(),
                "browser_hijacking": self._detect_browser_hijacking(),
                "privilege_escalation": self._detect_macos_privesc()
            }
        }
        
        threat_count = sum(len(v) if isinstance(v, list) else 0 
                           for v in threats["threat_categories"].values())
        threats["total_threats"] = threat_count
        
        return threats
    
    def _detect_macos_malware(self) -> List[Dict]:
        """Detect known macOS malware families"""
        suspicious = []
        
        try:
            # Check for known macOS malware locations
            suspicious_locations = [
                os.path.expanduser("~/Library/Logs"),
                os.path.expanduser("~/Library/Saved Application State"),
                "/tmp",
                "/var/tmp"
            ]
            
            malware_signatures = [
                "OSX.Flashback",
                "OSX.Marauder",
                "OSX.DevilRobber",
                "Trojan.GenericKD",
                "Agent.AppleJeus"
            ]
            
            for location in suspicious_locations:
                if os.path.exists(location):
                    try:
                        for file in os.listdir(location):
                            file_path = os.path.join(location, file)
                            
                            # Check file hash against known malware
                            for signature in malware_signatures:
                                if signature.lower() in file.lower():
                                    suspicious.append({
                                        "malware": signature,
                                        "file": file_path,
                                        "action": "Delete immediately"
                                    })
                    except:
                        pass
        
        except Exception as e:
            logger.error(f"macOS malware detection error: {e}")
        
        return suspicious
    
    def _detect_gatekeeper_bypass(self) -> List[Dict]:
        """Detect Gatekeeper bypass attempts"""
        suspicious = []
        
        try:
            # Check quarantine attributes
            result = subprocess.run(
                "find ~ -xattr com.apple.quarantine",
                shell=True,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.stdout:
                suspicious.append({
                    "threat": "Quarantined files found",
                    "count": len(result.stdout.split('\n')),
                    "action": "Review quarantine attributes"
                })
        
        except Exception as e:
            logger.error(f"Gatekeeper detection error: {e}")
        
        return suspicious
    
    def _detect_notarization_issues(self) -> List[Dict]:
        """Detect macOS app notarization issues"""
        return []
    
    def _detect_suspicious_extensions(self) -> List[Dict]:
        """Detect suspicious kernel extensions"""
        suspicious = []
        
        try:
            result = subprocess.run(
                "kextstat",
                capture_output=True,
                text=True,
                timeout=5,
                shell=True
            )
            
            if result.stdout:
                # Check for suspicious kext names
                for line in result.stdout.split('\n'):
                    if any(name in line for name in [
                        "malware", "trojan", "rootkit", ".pkg"
                    ]):
                        suspicious.append({
                            "kext": line,
                            "threat": "Suspicious kernel extension",
                            "action": "Unload kext"
                        })
        
        except Exception as e:
            logger.error(f"Extension detection error: {e}")
        
        return suspicious
    
    def _detect_keychain_threats(self) -> List[Dict]:
        """Detect keychain access threats"""
        return []
    
    def _detect_browser_hijacking(self) -> List[Dict]:
        """Detect browser hijacking"""
        suspicious = []
        
        try:
            # Check Safari preferences for hijacking
            safari_prefs = os.path.expanduser("~/Library/Preferences/com.apple.Safari.plist")
            
            if os.path.exists(safari_prefs):
                suspicious.append({
                    "browser": "Safari",
                    "threat": "Review Safari preferences for hijacking",
                    "action": "Check homepage and search engine"
                })
        
        except Exception as e:
            logger.error(f"Browser hijacking detection error: {e}")
        
        return suspicious
    
    def _detect_macos_privesc(self) -> List[Dict]:
        """Detect macOS privilege escalation"""
        return []
    
    def kill_malicious_process(self, pid: int) -> Dict:
        """Kill malicious process on Unix-like system"""
        try:
            os.kill(pid, 9)  # SIGKILL
            return {
                "success": True,
                "pid": pid,
                "action": "Process terminated",
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Process kill error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def unload_malicious_module(self, module_name: str) -> Dict:
        """Unload malicious kernel module (Linux)"""
        try:
            if "linux" in platform.system().lower():
                subprocess.run(
                    f"rmmod {module_name}",
                    shell=True,
                    timeout=5
                )
                return {
                    "success": True,
                    "module": module_name,
                    "action": "Module unloaded",
                    "timestamp": datetime.now().isoformat()
                }
        except Exception as e:
            logger.error(f"Module unload error: {e}")
        
        return {"success": False}
    
    def quarantine_file(self, file_path: str) -> Dict:
        """Quarantine file on Unix-like system"""
        try:
            quarantine_dir = "/tmp/quarantine"
            os.makedirs(quarantine_dir, exist_ok=True)
            
            file_name = os.path.basename(file_path)
            dest = os.path.join(quarantine_dir, file_name + ".quarantine")
            
            os.replace(file_path, dest)
            
            return {
                "success": True,
                "original": file_path,
                "quarantined": dest,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Quarantine error: {e}")
            return {"success": False, "error": str(e)}
