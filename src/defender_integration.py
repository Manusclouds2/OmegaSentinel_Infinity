"""
Windows Defender Integration Module
- Real-time threat scanning
- Quarantine management
- Threat history
"""
import subprocess
import json
import logging
from typing import Dict, List, Optional
from datetime import datetime
import os

logger = logging.getLogger(__name__)

class WindowsDefenderManager:
    """Integrate with Windows Defender for real-time protection"""
    
    def __init__(self):
        self.is_windows = os.name == 'nt'
        self.quarantine_list = []
    
    def get_defender_status(self) -> Dict:
        """Get Windows Defender real-time protection status"""
        if not self.is_windows:
            return {"status": "windows_only", "message": "Windows Defender integration requires Windows OS"}
        
        try:
            # PowerShell command to get Defender status
            cmd = [
                "powershell", "-Command",
                "Get-MpComputerStatus | Select-Object -Property RealTimeProtectionEnabled, AntivirusSignatureLastUpdated | ConvertTo-Json"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, shell=False)
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                return {
                    "status": "success",
                    "real_time_protection": data.get("RealTimeProtectionEnabled", False),
                    "last_signature_update": data.get("AntivirusSignatureLastUpdated", "Unknown"),
                    "timestamp": datetime.now().isoformat()
                }
        except Exception as e:
            logger.error(f"Defender status check failed: {str(e)}")
        
        return {"status": "error", "message": "Could not retrieve Defender status"}
    
    def scan_file_with_defender(self, file_path: str) -> Dict:
        """Scan a file with Windows Defender"""
        if not self.is_windows:
            return {"status": "windows_only"}
        
        try:
            # PowerShell command to scan file
            cmd = [
                "powershell", "-Command",
                f"Start-MpScan -ScanPath '{file_path}' -ScanType QuickScan"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"Defender scan initiated for: {file_path}")
                return {
                    "status": "success",
                    "message": f"Quick scan started for {file_path}",
                    "file": file_path,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "status": "error",
                    "message": result.stderr or "Scan failed"
                }
        
        except Exception as e:
            logger.error(f"Defender scan failed: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def scan_folder_with_defender(self, folder_path: str) -> Dict:
        """Scan an entire folder with Windows Defender"""
        if not self.is_windows:
            return {"status": "windows_only"}
        
        try:
            cmd = [
                "powershell", "-Command",
                f"Start-MpScan -ScanPath '{folder_path}' -ScanType FullScan"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                return {
                    "status": "success",
                    "message": f"Full scan started for {folder_path}",
                    "folder": folder_path,
                    "scan_type": "full",
                    "timestamp": datetime.now().isoformat()
                }
        
        except Exception as e:
            logger.error(f"Folder scan failed: {str(e)}")
        
        return {"status": "error"}
    
    def get_quarantined_items(self) -> Dict:
        """Get list of items in Windows Defender quarantine"""
        if not self.is_windows:
            return {"status": "windows_only", "items": []}
        
        try:
            cmd = [
                "powershell", "-Command",
                "Get-MpPreference | Select-Object -Property QuarantinePath | ConvertTo-Json"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                return {
                    "status": "success",
                    "message": "Retrieved quarantine information",
                    "timestamp": datetime.now().isoformat()
                }
        
        except Exception as e:
            logger.error(f"Quarantine check failed: {str(e)}")
        
        return {"status": "error"}
    
    def enable_real_time_protection(self) -> Dict:
        """Enable Windows Defender real-time protection"""
        if not self.is_windows:
            return {"status": "windows_only"}
        
        try:
            cmd = [
                "powershell", "-Command",
                "Set-MpPreference -DisableRealtimeMonitoring $false"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info("Real-time protection enabled")
                return {
                    "status": "success",
                    "message": "Real-time protection enabled",
                    "timestamp": datetime.now().isoformat()
                }
        
        except Exception as e:
            logger.error(f"Failed to enable protection: {str(e)}")
        
        return {"status": "error"}
    
    def disable_cloud_protection(self, enabled: bool = True) -> Dict:
        """Configure cloud-delivered protection"""
        if not self.is_windows:
            return {"status": "windows_only"}
        
        try:
            value = "true" if enabled else "false"
            cmd = [
                "powershell", "-Command",
                f"Set-MpPreference -CloudBlockLevel High -SubmitSamplesConsent SendSafeSamples"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                return {
                    "status": "success",
                    "message": "Cloud protection configured",
                    "timestamp": datetime.now().isoformat()
                }
        
        except Exception as e:
            logger.error(f"Failed to configure cloud protection: {str(e)}")
        
        return {"status": "error"}
