"""
Email Attachment Scanner Module
- Scan email attachments before opening
- Detect malicious file types
- Block dangerous attachments
- Integration with email clients
"""
import logging
import os
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path
import mimetypes

logger = logging.getLogger(__name__)

class EmailAttachmentScanner:
    """Scan email attachments for threats"""
    
    def __init__(self, threat_intel=None):
        self.threat_intel = threat_intel
        
        # Dangerous file extensions
        self.dangerous_extensions = [
            # Executables
            '.exe', '.com', '.bat', '.cmd', '.scr', '.vbs', '.js', '.jse',
            '.wsf', '.wsh', '.msh', '.msi', '.dll', '.sys', '.cpl',
            # Archives that may contain executables
            '.zip', '.rar', '.7z', '.jar',
            # Scripts
            '.ps1', '.ps2', '.psc1', '.psc2',
            # Office with macros
            '.docm', '.xlsm', '.pptm', '.ppam', '.ppsm', '.xltm',
            # Other
            '.lnk', '.pif', '.chm', '.hta', '.sct',
        ]
        
        # Suspicious MIME types
        self.dangerous_mime_types = [
            'application/x-msdownload',  # EXE
            'application/x-msdos-program',
            'application/x-executable',
            'application/x-elf',
            'application/octet-stream',  # Unknown binary (suspicious)
            'application/x-wine-extension-msp',  # MSI
        ]
        
        self.scanned_attachments = []
        self.blocked_attachments = []
    
    def scan_attachment(self, file_path: str) -> Dict:
        """Scan an email attachment"""
        if not os.path.exists(file_path):
            return {"status": "error", "message": "File not found"}
        
        try:
            file_name = os.path.basename(file_path)
            file_size = os.path.getsize(file_path)
            file_ext = os.path.splitext(file_name)[1].lower()
            
            # Get MIME type
            mime_type, _ = mimetypes.guess_type(file_path)
            
            result = {
                "file": file_name,
                "path": file_path,
                "size_bytes": file_size,
                "extension": file_ext,
                "mime_type": mime_type,
                "timestamp": datetime.now().isoformat()
            }
            
            # Check for dangerous extension
            if file_ext in self.dangerous_extensions:
                result.update({
                    "status": "blocked",
                    "reason": "Dangerous file extension",
                    "threat_level": "high",
                    "action": "Block and quarantine"
                })
                self.blocked_attachments.append(result)
                logger.warning(f"Blocked dangerous attachment: {file_name}")
                return result
            
            # Check for dangerous MIME type
            if mime_type in self.dangerous_mime_types:
                result.update({
                    "status": "suspicious",
                    "reason": "Suspicious MIME type",
                    "threat_level": "medium",
                    "action": "Scan with antivirus before opening"
                })
                logger.warning(f"Suspicious MIME type: {file_name}")
                return result
            
            # Check file size (unusually large)
            if file_size > 100 * 1024 * 1024:  # 100MB
                result.update({
                    "status": "suspicious",
                    "reason": "Unusually large attachment",
                    "threat_level": "low",
                    "action": "Verify before opening"
                })
            
            # Scan with VirusTotal if available
            if self.threat_intel:
                vt_result = self.threat_intel.scan_file_virustotal(file_path)
                if vt_result.get("status") == "success":
                    if vt_result.get("detected"):
                        result.update({
                            "status": "blocked",
                            "reason": "Detected as malware by VirusTotal",
                            "threat_level": "critical",
                            "detections": vt_result.get("detections"),
                            "action": "Block and quarantine immediately"
                        })
                        self.blocked_attachments.append(result)
                        logger.critical(f"Malware detected in attachment: {file_name}")
                        return result
            
            # Safe attachment
            result.update({
                "status": "safe",
                "reason": "No threats detected",
                "threat_level": "none"
            })
            
            self.scanned_attachments.append(result)
            return result
        
        except Exception as e:
            logger.error(f"Attachment scan failed: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def scan_multiple_attachments(self, file_paths: List[str]) -> Dict:
        """Scan multiple attachments"""
        results = []
        blocked_count = 0
        safe_count = 0
        
        for file_path in file_paths:
            result = self.scan_attachment(file_path)
            results.append(result)
            
            if result.get("status") == "blocked":
                blocked_count += 1
            elif result.get("status") == "safe":
                safe_count += 1
        
        return {
            "status": "success",
            "total_attachments": len(file_paths),
            "scanned": len(results),
            "safe": safe_count,
            "suspicious": len(results) - safe_count - blocked_count,
            "blocked": blocked_count,
            "results": results,
            "timestamp": datetime.now().isoformat()
        }
    
    def quarantine_file(self, file_path: str) -> Dict:
        """Move file to quarantine"""
        try:
            quarantine_dir = Path.home() / "AppData" / "Local" / "Temp" / ".omega_quarantine"
            quarantine_dir.mkdir(parents=True, exist_ok=True)
            
            file_name = os.path.basename(file_path)
            quarantine_path = quarantine_dir / file_name
            
            # Move file to quarantine
            import shutil
            shutil.move(file_path, str(quarantine_path))
            
            logger.warning(f"File quarantined: {file_path} -> {quarantine_path}")
            
            return {
                "status": "success",
                "message": f"File quarantined: {file_name}",
                "original": file_path,
                "quarantine": str(quarantine_path),
                "timestamp": datetime.now().isoformat()
            }
        
        except Exception as e:
            logger.error(f"Quarantine failed: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def get_quarantine(self) -> Dict:
        """Get list of quarantined files"""
        try:
            quarantine_dir = Path.home() / "AppData" / "Local" / "Temp" / ".omega_quarantine"
            
            if not quarantine_dir.exists():
                return {
                    "status": "success",
                    "quarantine_count": 0,
                    "files": []
                }
            
            files = []
            for file in quarantine_dir.iterdir():
                if file.is_file():
                    files.append({
                        "name": file.name,
                        "path": str(file),
                        "size": file.stat().st_size,
                        "quarantined_date": datetime.fromtimestamp(file.stat().st_mtime).isoformat()
                    })
            
            return {
                "status": "success",
                "quarantine_count": len(files),
                "files": files,
                "timestamp": datetime.now().isoformat()
            }
        
        except Exception as e:
            logger.error(f"Quarantine list failed: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def restore_from_quarantine(self, file_name: str) -> Dict:
        """Restore a file from quarantine (after manual review)"""
        try:
            quarantine_dir = Path.home() / "AppData" / "Local" / "Temp" / ".omega_quarantine"
            quarantine_file = quarantine_dir / file_name
            
            if not quarantine_file.exists():
                return {"status": "error", "message": "File not found in quarantine"}
            
            # Move back to Downloads
            downloads = Path.home() / "Downloads"
            import shutil
            shutil.move(str(quarantine_file), str(downloads / file_name))
            
            return {
                "status": "success",
                "message": f"File restored to Downloads: {file_name}",
                "timestamp": datetime.now().isoformat()
            }
        
        except Exception as e:
            logger.error(f"Restore failed: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def get_scan_statistics(self) -> Dict:
        """Get attachment scanning statistics"""
        return {
            "status": "success",
            "total_scanned": len(self.scanned_attachments),
            "total_blocked": len(self.blocked_attachments),
            "safe_rate": (len(self.scanned_attachments) / (len(self.scanned_attachments) + len(self.blocked_attachments)) * 100) if (self.scanned_attachments or self.blocked_attachments) else 0,
            "timestamp": datetime.now().isoformat()
        }
