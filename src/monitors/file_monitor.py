"""
File System Monitoring Module
- Real-time file change detection
- Suspicious file activity detection
- Ransomware pattern detection
"""
import threading
import logging
from typing import Dict, List, Optional, Callable
from datetime import datetime
from pathlib import Path
import hashlib
import json

logger = logging.getLogger(__name__)

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler, FileModifiedEvent, FileCreatedEvent
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False
    logger.warning("watchdog not available - file monitoring disabled. Install: pip install watchdog")

class FileActivityHandler(FileSystemEventHandler):
    """Handle file system events"""
    
    def __init__(self, callback: Callable):
        super().__init__()
        self.callback = callback
    
    def on_created(self, event):
        if not event.is_directory:
            self.callback({
                "event": "file_created",
                "path": event.src_path,
                "timestamp": datetime.now().isoformat()
            })
    
    def on_modified(self, event):
        if not event.is_directory:
            self.callback({
                "event": "file_modified",
                "path": event.src_path,
                "timestamp": datetime.now().isoformat()
            })
    
    def on_deleted(self, event):
        if not event.is_directory:
            self.callback({
                "event": "file_deleted",
                "path": event.src_path,
                "timestamp": datetime.now().isoformat()
            })

class FileMonitor:
    """Monitor file system for suspicious activity"""
    
    def __init__(self):
        self.is_watching = False
        self.observer = None
        self.file_activities = []
        self.suspicious_activities = []
        
        # Tracking for ransomware detection
        self.file_extensions_changed = {}
        self.rapid_modifications = {}
        
        # Dangerous file operations
        self.dangerous_patterns = [
            '.locked',
            '.encrypted',
            '.locked_',
            '.crypt',
            '.cry',
            '.xtbl',
            '.osiris',
            '.aaa'
        ]
    
    def start_monitoring(self, directory: str = None) -> Dict:
        """Start monitoring file system"""
        if not WATCHDOG_AVAILABLE:
            return {
                "status": "error",
                "message": "watchdog library not installed. Run: pip install watchdog"
            }
        
        if self.is_watching:
            return {"status": "error", "message": "Already monitoring"}
        
        try:
            watch_path = directory or str(Path.home())
            
            self.observer = Observer()
            handler = FileActivityHandler(self._handle_event)
            self.observer.schedule(handler, watch_path, recursive=True)
            self.observer.start()
            
            self.is_watching = True
            logger.info(f"File monitoring started on {watch_path}")
            
            return {
                "status": "success",
                "message": f"Monitoring directory: {watch_path}",
                "directory": watch_path,
                "timestamp": datetime.now().isoformat()
            }
        
        except Exception as e:
            logger.error(f"Monitoring start failed: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def stop_monitoring(self) -> Dict:
        """Stop file monitoring"""
        if not self.is_watching:
            return {"status": "error", "message": "Not currently monitoring"}
        
        try:
            self.observer.stop()
            self.observer.join()
            self.is_watching = False
            
            return {
                "status": "success",
                "message": "File monitoring stopped",
                "activities_logged": len(self.file_activities),
                "suspicious_detected": len(self.suspicious_activities),
                "timestamp": datetime.now().isoformat()
            }
        
        except Exception as e:
            logger.error(f"Monitoring stop failed: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def _handle_event(self, event: Dict):
        """Handle file system event"""
        self.file_activities.append(event)
        
        # Check for suspicious patterns
        suspicious = self._check_suspicious_activity(event)
        if suspicious:
            self.suspicious_activities.append(suspicious)
            logger.warning(f"Suspicious activity detected: {suspicious['type']}")
    
    def _check_suspicious_activity(self, event: Dict) -> Optional[Dict]:
        """Detect suspicious file activity patterns"""
        path = event.get("path", "")
        event_type = event.get("event", "")
        
        # Check for dangerous extensions (ransomware)
        for pattern in self.dangerous_patterns:
            if path.endswith(pattern):
                return {
                    "type": "ransomware_indicator",
                    "severity": "high",
                    "path": path,
                    "pattern": pattern,
                    "event": event_type,
                    "timestamp": datetime.now().isoformat()
                }
        
        # Check for rapid mass file modifications (ransomware)
        if event_type in ["file_modified", "file_created"]:
            parent_dir = str(Path(path).parent)
            
            if parent_dir not in self.rapid_modifications:
                self.rapid_modifications[parent_dir] = []
            
            self.rapid_modifications[parent_dir].append(datetime.now())
            
            # If more than 50 files in 5 seconds
            recent = [
                t for t in self.rapid_modifications[parent_dir]
                if (datetime.now() - t).total_seconds() < 5
            ]
            
            if len(recent) > 50:
                return {
                    "type": "mass_file_modification",
                    "severity": "critical",
                    "directory": parent_dir,
                    "file_count": len(recent),
                    "detection": "Possible ransomware activity",
                    "timestamp": datetime.now().isoformat()
                }
        
        # Check for executable creation in suspicious locations
        if event_type == "file_created" and path.endswith((".exe", ".dll", ".scr", ".vbs", ".js")):
            suspicious_dirs = ["Temp", "AppData", "Downloads", "Documents"]
            if any(dir in path for dir in suspicious_dirs):
                return {
                    "type": "suspicious_executable",
                    "severity": "high",
                    "path": path,
                    "detection": "Executable created in suspicious location",
                    "timestamp": datetime.now().isoformat()
                }
        
        return None
    
    def get_activities(self, limit: int = 100) -> Dict:
        """Get recent file activities"""
        activities = self.file_activities[-limit:]
        
        return {
            "status": "success",
            "total_activities": len(self.file_activities),
            "recent_activities": activities,
            "suspicious_count": len(self.suspicious_activities),
            "is_monitoring": self.is_watching,
            "timestamp": datetime.now().isoformat()
        }
    
    def get_suspicious_activities(self, limit: int = 50) -> Dict:
        """Get suspicious activities"""
        suspicious = self.suspicious_activities[-limit:]
        
        return {
            "status": "success",
            "total_suspicious": len(self.suspicious_activities),
            "recent_suspicious": suspicious,
            "high_severity": len([s for s in suspicious if s.get("severity") == "high"]),
            "critical_severity": len([s for s in suspicious if s.get("severity") == "critical"]),
            "timestamp": datetime.now().isoformat()
        }
    
    def clear_history(self) -> Dict:
        """Clear activity history"""
        count = len(self.file_activities)
        self.file_activities.clear()
        self.suspicious_activities.clear()
        
        return {
            "status": "success",
            "message": f"Cleared {count} activities",
            "timestamp": datetime.now().isoformat()
        }
