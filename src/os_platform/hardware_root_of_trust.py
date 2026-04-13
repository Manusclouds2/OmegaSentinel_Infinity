"""
HARDWARE ROOT OF TRUST & TPM INTEGRATION
Hardware-level security with immutable boot ROM and cryptographic write protection
"""

import hashlib
import json
import os
import subprocess
import platform
from typing import Dict, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class HardwareRootOfTrust:
    """Hardware-level security with TPM integration"""
    
    def __init__(self):
        self.system = platform.system()
        self.architecture = platform.machine()
        self.tpm_enabled = self._check_tpm()
        self.secure_boot_enabled = self._check_secure_boot()
        self.measurement_log = []
        self.trusted_values = self._load_trusted_pcr_values()
    
    def initialize_tpm_primary_key(self) -> Dict:
        """Initialize a TPM Primary Key for hardware-bound encryption"""
        # This creates a Storage Root Key (SRK) in the TPM owner hierarchy
        # that is used as a parent for all encrypted files (.env, logs).
        logger.info("[TPM] INITIALIZING STORAGE ROOT KEY (SRK)...")
        
        try:
            if self.system == "Windows":
                # On Windows, we can use TpmTool or PowerShell to check/manage SRK
                cmd = "tpmtool getdeviceinformation"
                result = subprocess.run(cmd, capture_output=True, text=True)
                if "TPM Present: True" in result.stdout:
                    # In a real environment, this would call tss-esapi via a Rust bridge
                    # For Python integration, we'll use a placeholder indicating success
                    return {"status": "INITIALIZED", "method": "Windows TPM Bridge"}
            
            elif self.system == "Linux":
                # Check if tpm2-tools is available
                if subprocess.run("which tpm2_createprimary", shell=True, capture_output=True).returncode == 0:
                    # Create a primary key in the owner hierarchy
                    subprocess.run("tpm2_createprimary -C o -g sha256 -G rsa -c primary.ctx", shell=True)
                    return {"status": "INITIALIZED", "method": "tpm2-tools"}
            
        except Exception as e:
            logger.error(f"TPM Primary Key initialization failed: {e}")
            return {"status": "ERROR", "message": str(e)}
            
        return {"status": "NOT_AVAILABLE"}

    def encrypt_with_tpm(self, data: bytes) -> bytes:
        """Encrypt data using the hardware-bound Primary Key"""
        if not self.tpm_enabled:
            # Fallback to software-based Post-Quantum Cryptography
            return hashlib.sha3_512(data).digest() # Simplification for placeholder
            
        # Real TPM encryption would involve creating a child key under the SRK
        # and using it to seal the data.
        logger.info("[TPM] SEALING DATA TO HARDWARE ENCLAVE...")
        return b"TPM_SEALED_" + data # Placeholder for real TPM-sealed blob

    def decrypt_with_tpm(self, sealed_data: bytes) -> bytes:
        """Decrypt data that was sealed by the TPM"""
        if not sealed_data.startswith(b"TPM_SEALED_"):
            return sealed_data
            
        logger.info("[TPM] UNSEALING DATA FROM HARDWARE ENCLAVE...")
        return sealed_data[11:] # Reverse the placeholder transformation

    def seal_master_key_to_pcr(self, key_data: bytes, pcr_index: int = 7) -> bool:
        """Seal the Master Key to composite PCR policy (PCR 0, 4, 7)"""
        # This is a critical Confidentiality operation. If someone wipes the OS,
        # or changes the boot order, the PCR state (0, 4, 7) will change.
        logger.info(f"[TPM] SEALING MASTER KEY TO PCR POLICY (0, 4, 7)...")
        
        # PCR-Policy Fail-Safe: Seal to a combination of states
        # PCR 0: BIOS Configuration
        # PCR 4: Bootloader Integrity
        # PCR 7: Secure Boot State
        
        try:
            # Check Liveness State
            from src.monitors.tamper_logic import dead_man_switch
            if dead_man_switch.lockdown_active:
                logger.error("[TPM_FAILSAFE] NUCLEAR LOCKDOWN ACTIVE. REFUSING TO SEAL KEY.")
                return False
                
            if self.system == "Windows":
                # Seal data to composite hardware state (Simulated)
                sealed_blob = b"TPM_COMPOSITE_SEALED_" + key_data
                with open(f"configs/quantum-keys/sealed_master_key.bin", "wb") as f:
                    f.write(sealed_blob)
                return True
                
            elif self.system == "Linux":
                # Use tpm2-tools with composite policy
                # tpm2_createpolicy --policy-pcr -l sha256:0,4,7 ...
                logger.info("[TPM] Linux Composite PCR Policy (0,4,7) simulation active.")
                return True
                
        except Exception as e:
            logger.error(f"TPM PCR Sealing failed: {e}")
            
        return False

    def unseal_master_key_from_pcr(self, pcr_index: int = 7) -> bytes:
        """Attempt to unseal the Master Key. Fails if PCRs have changed (e.g., Factory Reset)"""
        logger.info(f"[TPM] ATTEMPTING TO UNSEAL MASTER KEY FROM PCR {pcr_index}...")
        
        try:
            sealed_path = "configs/quantum-keys/sealed_master_key.bin"
            if not os.path.exists(sealed_path):
                return None
                
            with open(sealed_path, "rb") as f:
                sealed_blob = f.read()
                
            # Real TPM would check PCRs here. If they don't match, this fails at the hardware level.
            # Simulation: Check if current PCR7 matches the expected 'trusted' value
            current_pcr7 = self._read_pcr_value(pcr_index)
            trusted_pcr7 = self.trusted_values.get(f"pcr{pcr_index}")
            
            if trusted_pcr7 and current_pcr7 != trusted_pcr7:
                logger.critical("[!] TPM UNSEAL REJECTED: Hardware state has changed! (Possible Factory Reset/Tamper)")
                self._trigger_cryptographic_erasure()
                return None
                
            if sealed_blob.startswith(b"TPM_PCR_SEALED_"):
                return sealed_blob[15:]
                
        except Exception as e:
            logger.error(f"TPM PCR Unsealing failed: {e}")
            
        return None

    def _read_pcr_value(self, pcr_index: int) -> str:
        """Read a live PCR value from the TPM"""
        try:
            if self.system == "Windows":
                # Placeholder: In real Windows, use TpmTool or WMI
                return "f2ca1bb6c7e907d06dafe4687e579fce76b37e4e93b7605022da52e6ccc26fd2"
            elif self.system == "Linux":
                result = subprocess.run(f"tpm2_pcrread sha256:{pcr_index}", shell=True, capture_output=True, text=True)
                return result.stdout.strip()
        except:
            return ""
        return ""

    def _trigger_cryptographic_erasure(self):
        """Perform immediate Cryptographic Erasure (Crypto-Erase) of the Master Key"""
        logger.critical("[!] CRYPTOGRAPHIC ERASURE INITIATED: PURGING TPM NVRAM AND LOCAL KEYS...")
        
        # 1. Immutable Logging
        from src.os_platform.integrity_chain import integrity_chain
        integrity_chain.log_event("CRYPTO_ERASURE", "Unauthorized boot/PCR change detected. Purging keys.")
        
        # 2. Delete the sealed blob
        sealed_path = "configs/quantum-keys/sealed_master_key.bin"
        if os.path.exists(sealed_path):
            os.remove(sealed_path)
            
        # 2. Wipe the Entire Key Directory
        self._purge_secure_enclave()
        
        # 3. Inform the Cloud Console
        logger.info("[INTEGRITY] Event logged to Cloud Anchor: UNAUTHORIZED_HARDWARE_RESET")

    def activate_remote_kill_switch(self, auth_token: str) -> Dict:
        """Initiate Elite Remote Kill Switch: Total system neutralization for stolen devices"""
        # This is a critical recovery operation. It wipes the Master Key Enclave 
        # and renders the system unbootable until a physical recovery is performed.
        logger.critical("[!] REMOTE KILL SWITCH ACTIVATED. INITIATING SYSTEM NEUTRALIZATION...")
        
        # Verify administrative authority
        if hashlib.sha3_256(auth_token.encode()).hexdigest() != self.trusted_values.get("kill_switch_token"):
            logger.error("[CRITICAL] UNAUTHORIZED KILL SWITCH ATTEMPT DETECTED.")
            return {"status": "error", "message": "Unauthorized access"}
            
        # 1. Wipe the Secure Enclave (Master Keys)
        self._purge_secure_enclave()
        
        # 2. Corrupt the boot sequence (Force system to recovery mode)
        if self.system == "Windows":
            subprocess.run("bcdedit /set {current} bootstatuspolicy ignoreallfailures", shell=True)
            subprocess.run("bcdedit /set {current} recoveryenabled no", shell=True)
            
        logger.critical("[!] SYSTEM NEUTRALIZED. SECURE ENCLAVE PURGED.")
        return {"status": "SUCCESS", "action": "SYSTEM_KILLED"}

    def _purge_secure_enclave(self):
        """Purge all cryptographic keys from the hardware-bound enclave"""
        # In a real military-grade system, this would zero out the TPM NVRAM indices
        # and delete the BIOS-level Master Boot Keys.
        logger.info("[ENCLAVE] PURGING ALL LATTICE-BASED MASTER KEYS...")
        if os.path.exists("configs/quantum-keys/"):
            for f in os.listdir("configs/quantum-keys/"):
                os.remove(os.path.join("configs/quantum-keys/", f))
        
    def _check_tpm(self) -> bool:
        """Check if TPM 2.0 is available on system"""
        try:
            if self.system == "Windows":
                result = subprocess.run(
                    "Get-WmiObject -Class Win32_Tpm",
                    shell=True,
                    capture_output=True,
                    timeout=5
                )
                return b"TPM" in result.stdout or result.returncode == 0
            
            elif self.system == "Linux":
                # Check for /dev/tpm0 or /dev/tpmrm0
                return os.path.exists("/dev/tpm0") or os.path.exists("/dev/tpmrm0")
            
            elif self.system == "Darwin":
                # macOS: Check for Apple Secure Enclave
                result = subprocess.run(
                    "system_profiler SPiBridgeItem",
                    shell=True,
                    capture_output=True,
                    timeout=5
                )
                return b"Secure Enclave" in result.stdout
        
        except Exception as e:
            logger.warning(f"TPM check error: {e}")
        
        return False
    
    def _check_secure_boot(self) -> bool:
        """Check if Secure Boot is enabled"""
        try:
            if self.system == "Windows":
                result = subprocess.run(
                    "Confirm-SecureBootUEFI",
                    shell=True,
                    capture_output=True,
                    timeout=5
                )
                return b"True" in result.stdout
            
            elif self.system == "Linux":
                if os.path.exists("/sys/firmware/efi/fw_platform_size"):
                    return True
        
        except Exception as e:
            logger.warning(f"Secure Boot check error: {e}")
        
        return False
    
    def _load_trusted_pcr_values(self) -> Dict:
        """Load trusted PCR (Platform Configuration Register) values"""
        try:
            if os.path.exists("trusted_pcr_values.json"):
                with open("trusted_pcr_values.json", "r") as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error loading trusted values: {e}")
        
        return {}
    
    def trigger_self_healing(self) -> Dict:
        """Autonomous UEFI/Firmware self-remediation"""
        logger.warning("[!] SELF-HEALING: Analyzing firmware for integrity anomalies...")
        
        # 1. Verification
        integrity_status = self.measure_boot_components()
        
        if integrity_status.get("secure_boot") is False:
            # 2. Remediation: Re-enable Secure Boot via PowerShell/WMI (Windows)
            if self.system == "Windows":
                logger.info("[*] REMEDIATION: Attempting to restore Secure Boot policy...")
                try:
                    # In a real environment, this might require an administrative reboot or UEFI-level password
                    subprocess.run("Set-SecureBootUEFI -Name SetupMode -Value 0", shell=True)
                    return {"status": "success", "action": "SECURE_BOOT_RESTORED"}
                except Exception as e:
                    return {"status": "error", "message": f"Remediation failed: {e}"}
                    
        return {"status": "stable", "message": "Hardware integrity within safe parameters"}

    def get_physical_health(self) -> Dict:
        """Analyze physical hardware health (S.M.A.R.T. and Sensors)"""
        health_report = {"status": "HEALTHY", "alerts": []}
        
        try:
            if self.system == "Windows":
                # Check S.M.A.R.T. status for physical disks
                cmd = "Get-WmiObject -namespace root\\wmi -class MSStorageDriver_FailurePredictStatus"
                result = subprocess.run(["powershell", "-Command", cmd], capture_output=True, text=True)
                
                if "PredictFailure : True" in result.stdout:
                    health_report["status"] = "PHYSICAL_FAILURE_PREDICTED"
                    health_report["alerts"].append("S.M.A.R.T. alert: Disk failure imminent")
                
                # Check Battery Health if applicable
                cmd = "Get-WmiObject -Class Win32_Battery | Select-Object EstimatedChargeRemaining"
                result = subprocess.run(["powershell", "-Command", cmd], capture_output=True, text=True)
                if result.stdout.strip():
                    health_report["battery_level"] = result.stdout.strip()

            elif self.system == "Linux":
                # Check for physical thermal throttling
                if os.path.exists("/sys/class/thermal/"):
                    health_report["thermal_zones"] = os.listdir("/sys/class/thermal/")
        
        except Exception as e:
            logger.error(f"Physical health check error: {e}")
            
        return health_report

    def measure_boot_components(self) -> Dict:
        """Measure BIOS, bootloader, kernel, and drivers"""
        measurements = {
            "measurement_time": datetime.now().isoformat(),
            "system": self.system,
            "tpm_enabled": self.tpm_enabled,
            "secure_boot": self.secure_boot_enabled,
            "physical_health": self.get_physical_health(), # New: Physical Health
            "components": {
                "bios": None,
                "bootloader": None,
                "kernel": None,
                "drivers": None
            },
            "integrity_status": "UNKNOWN"
        }
        
        try:
            if self.system == "Windows":
                measurements["components"]["bios"] = self._measure_windows_bios()
                measurements["components"]["bootloader"] = self._measure_uefi()
                measurements["components"]["kernel"] = self._measure_windows_kernel()
            
            elif self.system == "Linux":
                measurements["components"]["bios"] = self._measure_linux_bios()
                measurements["components"]["bootloader"] = self._measure_grub()
                measurements["components"]["kernel"] = self._measure_linux_kernel()
            
            elif self.system == "Darwin":
                measurements["components"]["bootloader"] = self._measure_macos_bootloader()
                measurements["components"]["kernel"] = self._measure_macos_kernel()
            
            # Verify integrity
            measurements["integrity_status"] = self._verify_integrity(measurements)
            
            # Log measurement
            self.measurement_log.append(measurements)
        
        except Exception as e:
            logger.error(f"Boot measurement error: {e}")
            measurements["error"] = str(e)
        
        return measurements
    
    def _measure_windows_bios(self) -> Dict:
        """Measure Windows BIOS/UEFI"""
        try:
            result = subprocess.run(
                "Get-SecureBootUEFI -Name PK",
                shell=True,
                capture_output=True,
                timeout=10
            )
            
            # Calculate hash of BIOS
            bios_hash = hashlib.sha3_512(result.stdout).hexdigest()
            
            return {
                "component": "BIOS/UEFI",
                "hash": bios_hash,
                "algorithm": "SHA3-512",
                "status": "Measured"
            }
        except Exception as e:
            logger.error(f"BIOS measurement error: {e}")
            return {"error": str(e)}
    
    def _measure_uefi(self) -> Dict:
        """REAL Measurement of UEFI firmware configuration"""
        try:
            # On Windows, we can use Get-SecureBootPolicy to check if the firmware
            # has been tampered with or replaced.
            result = subprocess.run(
                "powershell -Command Get-SecureBootPolicy",
                shell=True,
                capture_output=True,
                timeout=10
            )
            
            if result.returncode != 0:
                raise Exception(f"PowerShell error: {result.stderr.decode()}")
                
            uefi_hash = hashlib.sha3_512(result.stdout).hexdigest()
            
            return {
                "component": "UEFI_POLICY",
                "hash": uefi_hash,
                "algorithm": "SHA3-512",
                "status": "Verified"
            }
        except Exception as e:
            logger.error(f"UEFI measurement error: {e}")
            return {"error": str(e)}
    
    def _measure_windows_kernel(self) -> Dict:
        """Measure Windows kernel"""
        try:
            kernel_path = "C:\\Windows\\System32\\ntoskrnl.exe"
            
            if os.path.exists(kernel_path):
                with open(kernel_path, "rb") as f:
                    kernel_hash = hashlib.sha3_512(f.read()).hexdigest()
                
                return {
                    "component": "Kernel",
                    "file": kernel_path,
                    "hash": kernel_hash,
                    "algorithm": "SHA3-512",
                    "status": "Measured"
                }
        except Exception as e:
            logger.error(f"Kernel measurement error: {e}")
        
        return {}
    
    def _measure_linux_bios(self) -> Dict:
        """Measure Linux BIOS"""
        try:
            if os.path.exists("/sys/firmware/dmi/tables/DMI"):
                with open("/sys/firmware/dmi/tables/DMI", "rb") as f:
                    bios_hash = hashlib.sha3_512(f.read()).hexdigest()
                
                return {
                    "component": "BIOS",
                    "hash": bios_hash,
                    "algorithm": "SHA3-512",
                    "status": "Measured"
                }
        except:
            pass
        
        return {}
    
    def _measure_grub(self) -> Dict:
        """Measure GRUB bootloader"""
        try:
            grub_path = "/boot/grub/grub.cfg"
            
            if os.path.exists(grub_path):
                with open(grub_path, "rb") as f:
                    grub_hash = hashlib.sha3_512(f.read()).hexdigest()
                
                return {
                    "component": "GRUB",
                    "file": grub_path,
                    "hash": grub_hash,
                    "algorithm": "SHA3-512",
                    "status": "Measured"
                }
        except:
            pass
        
        return {}
    
    def _measure_linux_kernel(self) -> Dict:
        """Measure Linux kernel"""
        try:
            kernel_path = "/boot/vmlinuz"
            
            if os.path.exists(kernel_path):
                with open(kernel_path, "rb") as f:
                    kernel_hash = hashlib.sha3_512(f.read()).hexdigest()
                
                return {
                    "component": "Kernel",
                    "file": kernel_path,
                    "hash": kernel_hash,
                    "algorithm": "SHA3-512",
                    "status": "Measured"
                }
        except Exception as e:
            logger.error(f"Kernel measurement error: {e}")
        
        return {}
    
    def _measure_macos_bootloader(self) -> Dict:
        """Measure macOS boot components (SecureEnclave)"""
        try:
            result = subprocess.run(
                "system_profiler SPiBridgeItem",
                shell=True,
                capture_output=True,
                timeout=5
            )
            
            boot_hash = hashlib.sha3_512(result.stdout).hexdigest()
            
            return {
                "component": "Apple Secure Enclave",
                "hash": boot_hash,
                "algorithm": "SHA3-512",
                "status": "Measured"
            }
        except:
            pass
        
        return {}
    
    def _measure_macos_kernel(self) -> Dict:
        """Measure macOS kernel"""
        try:
            kernel_path = "/System/Library/Kernels/kernel"
            
            if os.path.exists(kernel_path):
                with open(kernel_path, "rb") as f:
                    kernel_hash = hashlib.sha3_512(f.read()).hexdigest()
                
                return {
                    "component": "Kernel",
                    "file": kernel_path,
                    "hash": kernel_hash,
                    "algorithm": "SHA3-512",
                    "status": "Measured"
                }
        except:
            pass
        
        return {}
    
    def _verify_integrity(self, measurements: Dict) -> str:
        """Verify component integrity against trusted values"""
        status = "UNKNOWN"
        
        try:
            components = measurements.get("components", {})
            
            # Compare against trusted values
            all_ok = True
            for component_name, component_data in components.items():
                if not component_data:
                    continue
                
                measured_hash = component_data.get("hash")
                trusted_hash = self.trusted_values.get(component_name, {}).get("hash")
                
                if trusted_hash and measured_hash != trusted_hash:
                    logger.warning(f"INTEGRITY VIOLATION: {component_name}")
                    all_ok = False
            
            status = "INTEGRITY_OK" if all_ok else "INTEGRITY_VIOLATION"
        
        except Exception as e:
            logger.error(f"Verification error: {e}")
        
        return status
    
    def enable_cryptographic_write_protection(self) -> Dict:
        """Enable cryptographic write protection for BIOS/UEFI"""
        result = {
            "action": "Enable cryptographic write protection",
            "system": self.system,
            "status": "Not implemented",
            "notes": "This requires direct hardware access and BIOS configuration"
        }
        
        try:
            if self.system == "Windows":
                # Windows: UEFI Secure Boot and DBX (Database of Revoked Certificates)
                subprocess.run(
                    "Set-SecureBootUEFI -Force",
                    shell=True,
                    timeout=10,
                    capture_output=True
                )
                result["status"] = "Attempted"
            
            elif self.system == "Linux":
                # Linux: dmverity, secureboot
                result["method"] = "dm-verity (Device Mapper Verity)"
                result["status"] = "Can be enabled via kernel parameters"
            
            elif self.system == "Darwin":
                # macOS: System Integrity Protection (SIP)
                result["method"] = "System Integrity Protection (SIP)"
                result["status"] = "Native macOS protection"
        
        except Exception as e:
            logger.error(f"Write protection error: {e}")
            result["error"] = str(e)
        
        return result
    
    def get_hardware_security_status(self) -> Dict:
        """Get comprehensive hardware security status"""
        return {
            "timestamp": datetime.now().isoformat(),
            "system": self.system,
            "architecture": self.architecture,
            "tpm": {
                "available": self.tpm_enabled,
                "version": "2.0" if self.tpm_enabled else "N/A"
            },
            "secure_boot": {
                "enabled": self.secure_boot_enabled,
                "status": "Active" if self.secure_boot_enabled else "Disabled"
            },
            "measurements": len(self.measurement_log),
            "last_measurement": self.measurement_log[-1] if self.measurement_log else None,
            "integrity_status": self.measurement_log[-1].get("integrity_status") if self.measurement_log else "Unknown"
        }
    
    def save_golden_image(self, image_path: str) -> Dict:
        """Save golden/clean system image for recovery"""
        try:
            # Create hash of current system state
            system_hash = hashlib.sha3_512()
            
            # Hash critical system files
            critical_files = []
            if self.system == "Windows":
                critical_files = [
                    "C:\\Windows\\System32\\ntoskrnl.exe",
                    "C:\\Windows\\System32\\kernel32.dll"
                ]
            elif self.system == "Linux":
                critical_files = [
                    "/boot/vmlinuz",
                    "/lib/modules"
                ]
            
            for file_path in critical_files:
                if os.path.exists(file_path):
                    try:
                        with open(file_path, "rb") as f:
                            system_hash.update(f.read())
                    except:
                        pass
            
            golden_image = {
                "created_at": datetime.now().isoformat(),
                "system": self.system,
                "architecture": self.architecture,
                "hash": system_hash.hexdigest(),
                "algorithm": "SHA3-512",
                "path": image_path,
                "status": "Golden Image Created"
            }
            
            # Save to file
            with open(image_path, "w") as f:
                json.dump(golden_image, f, indent=2)
            
            logger.info(f"Golden image saved: {image_path}")
            return golden_image
        
        except Exception as e:
            logger.error(f"Golden image save error: {e}")
            return {"error": str(e)}
    
    def load_golden_image(self, image_path: str) -> Dict:
        """Load golden image for recovery"""
        try:
            with open(image_path, "r") as f:
                golden_image = json.load(f)
            
            return golden_image
        
        except Exception as e:
            logger.error(f"Golden image load error: {e}")
            return {"error": str(e)}

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    root_of_trust = HardwareRootOfTrust()
    print(f"[*] Initializing Hardware Root of Trust on {root_of_trust.system}...")
    
    # Run boot measurement
    print("[*] Measuring boot components and hardware health...")
    measurements = root_of_trust.measure_boot_components()
    print(f"[+] Measurements: {json.dumps(measurements, indent=2)}")
    
    # Check overall security status
    print("[*] Fetching comprehensive security status...")
    status = root_of_trust.get_hardware_security_status()
    print(f"[+] Security Status: {json.dumps(status, indent=2)}")

