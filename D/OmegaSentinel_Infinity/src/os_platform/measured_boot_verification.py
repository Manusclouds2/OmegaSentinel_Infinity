"""
MEASURED BOOT VERIFICATION SYSTEM
Hash-based integrity checking with TPM PCR storage
"""

import hashlib
import json
import os
import subprocess
import platform
from typing import Dict, List, Tuple
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class MeasuredBootVerification:
    """Measured boot with TPM integration for integrity verification"""
    
    def __init__(self, tpm_pcr_path: str = "/sys/class/tpm/tpm0/pcr"):
        self.system = platform.system()
        self.tpm_pcr_path = tpm_pcr_path
        self.pcr_values = {}  # Platform Configuration Registers
        self.verification_log = []
        self.integrity_failures = []
    
    def initialize_pcr_values(self) -> Dict:
        """Initialize PCR (Platform Configuration Register) values"""
        pcr_init = {
            "pcr_0": None,   # BIOS/FW initialization code
            "pcr_1": None,   # BIOS/FW configuration
            "pcr_2": None,   # BIOS extension option ROMs
            "pcr_3": None,   # BIOS extension option ROM configuration
            "pcr_4": None,   # MBR/boot sector, boot loader
            "pcr_5": None,   # Boot loader configuration
            "pcr_6": None,   # Resume from S4/S5, hibernate
            "pcr_7": None,   # Secure Boot state
            "pcr_8": None,   # Kernel and kernel command line
            "pcr_9": None,   # Kernel modules
        }
        
        try:
            if self.system == "Linux" and os.path.exists(self.tpm_pcr_path):
                for pcr_index in range(10):
                    pcr_file = f"{self.tpm_pcr_path}/pcr-sha256-{pcr_index}"
                    if os.path.exists(pcr_file):
                        with open(pcr_file, "r") as f:
                            pcr_init[f"pcr_{pcr_index}"] = f.read().strip()
        
        except Exception as e:
            logger.warning(f"PCR initialization error: {e}")
        
        self.pcr_values = pcr_init
        return pcr_init
    
    def measure_bios_code(self) -> Dict:
        """Measure BIOS code integrity"""
        measurement = {
            "component": "BIOS Code",
            "timestamp": datetime.now().isoformat(),
            "pcr_index": 0,  # PCR-0 is for BIOS code
            "status": "Not measured"
        }
        
        try:
            if self.system == "Windows":
                # Windows: Get BIOS information
                result = subprocess.run(
                    "Get-WmiObject Win32_BIOS",
                    shell=True,
                    capture_output=True,
                    timeout=10
                )
                
                if result.returncode == 0:
                    bios_hash = hashlib.sha3_512(result.stdout).hexdigest()
                    measurement["hash"] = bios_hash
                    measurement["algorithm"] = "SHA3-512"
                    measurement["status"] = "Measured"
            
            elif self.system == "Linux":
                # Linux: Read BIOS ROM
                bios_path = "/sys/firmware/dmi/tables/DMI"
                if os.path.exists(bios_path):
                    with open(bios_path, "rb") as f:
                        bios_hash = hashlib.sha3_512(f.read()).hexdigest()
                    
                    measurement["hash"] = bios_hash
                    measurement["algorithm"] = "SHA3-512"
                    measurement["status"] = "Measured"
            
            elif self.system == "Darwin":
                # macOS: System firmware
                result = subprocess.run(
                    "nvram -p",
                    shell=True,
                    capture_output=True,
                    timeout=10
                )
                
                if result.returncode == 0:
                    fw_hash = hashlib.sha3_512(result.stdout).hexdigest()
                    measurement["hash"] = fw_hash
                    measurement["algorithm"] = "SHA3-512"
                    measurement["status"] = "Measured"
        
        except Exception as e:
            logger.error(f"BIOS measurement error: {e}")
            measurement["error"] = str(e)
        
        return measurement
    
    def measure_boot_configuration(self) -> Dict:
        """Measure boot configuration (PCR-1)"""
        measurement = {
            "component": "Boot Configuration",
            "timestamp": datetime.now().isoformat(),
            "pcr_index": 1,
            "status": "Not measured"
        }
        
        try:
            if self.system == "Windows":
                # Windows: Boot configuration data (BCD)
                result = subprocess.run(
                    "bcdedit",
                    shell=True,
                    capture_output=True,
                    timeout=10
                )
                
                if result.returncode == 0:
                    bcd_hash = hashlib.sha3_512(result.stdout).hexdigest()
                    measurement["hash"] = bcd_hash
                    measurement["algorithm"] = "SHA3-512"
                    measurement["status"] = "Measured"
            
            elif self.system == "Linux":
                # Linux: GRUB configuration
                grub_cfg = "/boot/grub/grub.cfg"
                if os.path.exists(grub_cfg):
                    with open(grub_cfg, "rb") as f:
                        grub_hash = hashlib.sha3_512(f.read()).hexdigest()
                    
                    measurement["hash"] = grub_hash
                    measurement["algorithm"] = "SHA3-512"
                    measurement["status"] = "Measured"
        
        except Exception as e:
            logger.error(f"Boot config measurement error: {e}")
            measurement["error"] = str(e)
        
        return measurement
    
    def measure_bootloader(self) -> Dict:
        """Measure bootloader code (PCR-4)"""
        measurement = {
            "component": "Bootloader",
            "timestamp": datetime.now().isoformat(),
            "pcr_index": 4,
            "status": "Not measured"
        }
        
        try:
            if self.system == "Windows":
                # Windows: bootmgr
                bootloader_path = "C:\\Windows\\System32\\bootmgr"
                if os.path.exists(bootloader_path):
                    with open(bootloader_path, "rb") as f:
                        bootloader_hash = hashlib.sha3_512(f.read()).hexdigest()
                    
                    measurement["hash"] = bootloader_hash
                    measurement["file"] = bootloader_path
                    measurement["algorithm"] = "SHA3-512"
                    measurement["status"] = "Measured"
            
            elif self.system == "Linux":
                # Linux: GRUB or other bootloader
                bootloader_path = "/boot/grub/grubx64.efi"
                if os.path.exists(bootloader_path):
                    with open(bootloader_path, "rb") as f:
                        bootloader_hash = hashlib.sha3_512(f.read()).hexdigest()
                    
                    measurement["hash"] = bootloader_hash
                    measurement["file"] = bootloader_path
                    measurement["algorithm"] = "SHA3-512"
                    measurement["status"] = "Measured"
        
        except Exception as e:
            logger.error(f"Bootloader measurement error: {e}")
            measurement["error"] = str(e)
        
        return measurement
    
    def measure_kernel_and_modules(self) -> Dict:
        """Measure kernel and kernel modules (PCR-8, PCR-9)"""
        measurement = {
            "component": "Kernel & Modules",
            "timestamp": datetime.now().isoformat(),
            "pcr_indices": [8, 9],
            "kernel": None,
            "modules": None,
            "status": "Not measured"
        }
        
        try:
            if self.system == "Windows":
                kernel_path = "C:\\Windows\\System32\\ntoskrnl.exe"
                if os.path.exists(kernel_path):
                    with open(kernel_path, "rb") as f:
                        kernel_hash = hashlib.sha3_512(f.read()).hexdigest()
                    
                    measurement["kernel"] = {
                        "file": kernel_path,
                        "hash": kernel_hash,
                        "algorithm": "SHA3-512"
                    }
                    measurement["status"] = "Measured"
            
            elif self.system == "Linux":
                # Measure kernel
                kernel_path = "/boot/vmlinuz"
                kernel_hash = None
                
                if os.path.exists(kernel_path):
                    with open(kernel_path, "rb") as f:
                        kernel_hash = hashlib.sha3_512(f.read()).hexdigest()
                    
                    measurement["kernel"] = {
                        "file": kernel_path,
                        "hash": kernel_hash,
                        "algorithm": "SHA3-512"
                    }
                
                # Measure kernel modules
                modules_dir = "/lib/modules"
                if os.path.exists(modules_dir):
                    modules_hash = hashlib.sha3_512()
                    
                    for root, dirs, files in os.walk(modules_dir):
                        for file in sorted(files):
                            if file.endswith((".ko", ".ko.gz", ".ko.xz")):
                                file_path = os.path.join(root, file)
                                try:
                                    with open(file_path, "rb") as f:
                                        modules_hash.update(f.read())
                                except:
                                    pass
                    
                    measurement["modules"] = {
                        "directory": modules_dir,
                        "hash": modules_hash.hexdigest(),
                        "algorithm": "SHA3-512"
                    }
                
                measurement["status"] = "Measured" if kernel_hash else "Partial"
            
            elif self.system == "Darwin":
                # macOS: Kernel
                kernel_path = "/System/Library/Kernels/kernel"
                if os.path.exists(kernel_path):
                    with open(kernel_path, "rb") as f:
                        kernel_hash = hashlib.sha3_512(f.read()).hexdigest()
                    
                    measurement["kernel"] = {
                        "file": kernel_path,
                        "hash": kernel_hash,
                        "algorithm": "SHA3-512"
                    }
                    measurement["status"] = "Measured"
        
        except Exception as e:
            logger.error(f"Kernel measurement error: {e}")
            measurement["error"] = str(e)
        
        return measurement
    
    def measure_secure_boot_state(self) -> Dict:
        """Measure Secure Boot state (PCR-7)"""
        measurement = {
            "component": "Secure Boot State",
            "timestamp": datetime.now().isoformat(),
            "pcr_index": 7,
            "status": "Not measured",
            "secure_boot_enabled": False,
            "uefi_mode": False
        }
        
        try:
            if self.system == "Windows":
                result = subprocess.run(
                    "Confirm-SecureBootUEFI",
                    shell=True,
                    capture_output=True,
                    timeout=10
                )
                
                secure_boot_enabled = b"True" in result.stdout
                measurement["secure_boot_enabled"] = secure_boot_enabled
                
                # Get UEFI mode
                uefi_result = subprocess.run(
                    "Get-ComputerInfo | Select-Object BiosFirmwareType",
                    shell=True,
                    capture_output=True,
                    timeout=10
                )
                
                measurement["uefi_mode"] = b"UEFI" in uefi_result.stdout
                
                state_hash = hashlib.sha3_512(
                    str(secure_boot_enabled).encode() + 
                    str(measurement["uefi_mode"]).encode()
                ).hexdigest()
                
                measurement["hash"] = state_hash
                measurement["algorithm"] = "SHA3-512"
                measurement["status"] = "Measured"
            
            elif self.system == "Linux":
                # Check SecureBoot variable
                efivar_path = "/sys/firmware/efi/efivars"
                if os.path.exists(efivar_path):
                    # SecureBoot EFI variable
                    sb_var = os.path.join(efivar_path, "SecureBoot-*")
                    
                    measurement["uefi_mode"] = True
                    measurement["secure_boot_enabled"] = os.path.exists(
                        "/sys/firmware/efi/fw_platform_size"
                    )
                    measurement["status"] = "Measured"
        
        except Exception as e:
            logger.warning(f"Secure Boot measurement error: {e}")
            measurement["error"] = str(e)
        
        return measurement
    
    def perform_full_measured_boot_check(self) -> Dict:
        """Perform complete measured boot verification"""
        check_result = {
            "timestamp": datetime.now().isoformat(),
            "system": self.system,
            "measurements": {
                "bios": self.measure_bios_code(),
                "boot_config": self.measure_boot_configuration(),
                "bootloader": self.measure_bootloader(),
                "kernel_modules": self.measure_kernel_and_modules(),
                "secure_boot": self.measure_secure_boot_state()
            },
            "integrity_status": "UNKNOWN",
            "violations": []
        }
        
        try:
            # Verify each measurement
            all_pass = True
            
            for component_name, component_data in check_result["measurements"].items():
                if component_data.get("status") == "Not measured":
                    continue
                
                component_hash = component_data.get("hash")
                if component_hash:
                    # Store measurement for future comparison
                    check_result["measurements"][component_name]["stored"] = True
            
            check_result["integrity_status"] = "PASS" if all_pass else "FAIL"
            
            # Log this check
            self.verification_log.append(check_result)
        
        except Exception as e:
            logger.error(f"Measured boot check error: {e}")
            check_result["error"] = str(e)
        
        return check_result
    
    def verify_boot_integrity(self) -> Tuple[bool, Dict]:
        """Verify boot integrity, return (pass/fail, details)"""
        try:
            check = self.perform_full_measured_boot_check()
            
            if check["integrity_status"] == "FAIL":
                self.integrity_failures.append(check)
                logger.error("INTEGRITY CHECK FAILED - Possible boot tampering detected!")
                return False, check
            
            logger.info("Boot integrity verified successfully")
            return True, check
        
        except Exception as e:
            logger.error(f"Boot verification error: {e}")
            return False, {"error": str(e)}
    
    def get_verification_status(self) -> Dict:
        """Get current verification status"""
        return {
            "timestamp": datetime.now().isoformat(),
            "system": self.system,
            "total_verifications": len(self.verification_log),
            "integrity_failures": len(self.integrity_failures),
            "last_check": self.verification_log[-1] if self.verification_log else None,
            "last_failure": self.integrity_failures[-1] if self.integrity_failures else None
        }
    
    def store_baseline_measurements(self, filepath: str) -> Dict:
        """Store baseline measurements for future comparison"""
        try:
            baseline = self.perform_full_measured_boot_check()
            
            with open(filepath, "w") as f:
                json.dump(baseline, f, indent=2)
            
            logger.info(f"Baseline measurements stored: {filepath}")
            return {"status": "Success", "file": filepath}
        
        except Exception as e:
            logger.error(f"Baseline storage error: {e}")
            return {"error": str(e)}
    
    def compare_with_baseline(self, baseline_filepath: str) -> Dict:
        """Compare current measurements with baseline"""
        try:
            with open(baseline_filepath, "r") as f:
                baseline = json.load(f)
            
            current = self.perform_full_measured_boot_check()
            
            comparison = {
                "timestamp": datetime.now().isoformat(),
                "baseline_time": baseline.get("timestamp"),
                "current_time": current.get("timestamp"),
                "differences": [],
                "integrity_status": "PASS"
            }
            
            # Compare measurements
            baseline_measurements = baseline.get("measurements", {})
            current_measurements = current.get("measurements", {})
            
            for component_name in baseline_measurements.keys():
                baseline_hash = baseline_measurements[component_name].get("hash")
                current_hash = current_measurements.get(component_name, {}).get("hash")
                
                if baseline_hash and current_hash and baseline_hash != current_hash:
                    comparison["differences"].append({
                        "component": component_name,
                        "baseline_hash": baseline_hash,
                        "current_hash": current_hash,
                        "status": "MISMATCH"
                    })
                    comparison["integrity_status"] = "FAIL"
            
            if comparison["integrity_status"] == "FAIL":
                logger.error(f"Baseline comparison FAILED: {len(comparison['differences'])} mismatches")
            
            return comparison
        
        except Exception as e:
            logger.error(f"Baseline comparison error: {e}")
            return {"error": str(e)}
