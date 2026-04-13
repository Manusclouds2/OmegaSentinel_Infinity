"""
LOPUTHJOSEPH - Enterprise Cybersecurity Platform
Real security features: VirusTotal, Network Monitoring, Firewall, RBAC
NO SIMULATIONS - ALL REAL THREATS AND OPERATIONS
"""
import asyncio
import hashlib
import json
import logging
import os
import sqlite3
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List

from fastapi import Depends, FastAPI, HTTPException, Request, WebSocket, WebSocketDisconnect, status
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, Field
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

# Import real security modules
from security_services import ThreatIntelligence
from network_monitor import NetworkMonitor
from firewall_manager import FirewallManager
from rbac import RBACManager, UserRole, Permission

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ---------- Configuration ----------
SECRET_KEY = os.environ.get("LOPUTHJOSEPH_SECRET", "supersecretkey")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
DATABASE_URL = os.environ.get("DATABASE_URL", f"sqlite:///{os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data/loputhjoseph.db')}")
DB_PATH = DATABASE_URL.replace("sqlite:///", "")
SCAN_ROOT = Path(os.environ.get("SCAN_ROOT", os.path.join(os.path.dirname(__file__), "scan"))).resolve()

# API Keys from environment
VIRUSTOTAL_API_KEY = os.environ.get("VIRUSTOTAL_API_KEY")
SHODAN_API_KEY = os.environ.get("SHODAN_API_KEY")

# Initialize real security services
threat_intel = ThreatIntelligence(
    virustotal_key=VIRUSTOTAL_API_KEY,
    shodan_key=SHODAN_API_KEY
)
network_monitor = NetworkMonitor()
firewall_manager = FirewallManager()

# ---------- FastAPI Setup ----------
app = FastAPI(title="LOPUTHJOSEPH - Enterprise Security Platform")
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

# ---------- Pydantic Models ----------

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None

class User(BaseModel):
    username: str
    full_name: str | None = None
    disabled: bool | None = None
    role: str | None = "viewer"

class UserInDB(User):
    hashed_password: str

# Real Security Request Models

class FileScanRequest(BaseModel):
    """Scan a file using VirusTotal"""
    file_path: str

class URLScanRequest(BaseModel):
    """Scan a URL for malicious content"""
    url: str

class IPReputationRequest(BaseModel):
    """Check IP reputation"""
    ip_address: str

class FirewallRuleRequest(BaseModel):
    """Create a firewall rule"""
    rule_name: str
    direction: str  # "in" or "out"
    action: str  # "allow" or "block"
    local_port: Optional[int] = None
    remote_ip: Optional[str] = None
    protocol: str = "tcp"

class BlockIPRequest(BaseModel):
    """Block an IP address"""
    ip_address: str

class UserCreate(BaseModel):
    """Create new user"""
    username: str = Field(min_length=3, max_length=50)
    full_name: str = Field(min_length=1, max_length=100)
    password: str = Field(min_length=8)
    role: str = Field(pattern="^(viewer|analyst|operator|admin)$", default="viewer")

# ---------- Database Helpers ----------

def get_db_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database with real security schema"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Users table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            full_name TEXT,
            hashed_password TEXT,
            disabled INTEGER DEFAULT 0,
            role TEXT DEFAULT 'viewer',
            created_at TIMESTAMP,
            last_login TIMESTAMP
        )
    """)
    
    # Threat detections (real threats only)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS threat_detections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            threat_type TEXT,
            severity TEXT,
            source_ip TEXT,
            target_ip TEXT,
            description TEXT,
            detection_method TEXT,
            detected_at TIMESTAMP,
            resolved INTEGER DEFAULT 0
        )
    """)
    
    # File scan history
    cur.execute("""
        CREATE TABLE IF NOT EXISTS file_scans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_path TEXT,
            sha256_hash TEXT,
            detected INTEGER,
            engine_count INTEGER,
            detections INTEGER,
            scanned_at TIMESTAMP,
            username TEXT
        )
    """)
    
    # IP reputation checks
    cur.execute("""
        CREATE TABLE IF NOT EXISTS ip_checks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ip_address TEXT,
            fraud_score INTEGER,
            is_vpn INTEGER,
            threat_level TEXT,
            checked_at TIMESTAMP,
            username TEXT
        )
    """)
    
    # Firewall rules
    cur.execute("""
        CREATE TABLE IF NOT EXISTS firewall_rules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rule_name TEXT,
            direction TEXT,
            action TEXT,
            local_port INTEGER,
            remote_ip TEXT,
            protocol TEXT,
            enabled INTEGER,
            created_at TIMESTAMP,
            created_by TEXT
        )
    """)
    
    # Audit logs
    cur.execute("""
        CREATE TABLE IF NOT EXISTS audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            action TEXT,
            details TEXT,
            timestamp TIMESTAMP
        )
    """)
    
    conn.commit()
    
    # Create default admin user if not exists
    cur.execute("SELECT username FROM users WHERE username = ?", ("admin",))
    if not cur.fetchone():
        hashed = pwd_context.hash("letmein")
        cur.execute(
            "INSERT INTO users (username, full_name, hashed_password, disabled, role, created_at) VALUES (?, ?, ?, 0, ?, ?)",
            ("admin", "Omega Administrator", hashed, "admin", datetime.now())
        )
        conn.commit()
        logger.info("Default admin user created")
    
    conn.close()

# ---------- Authentication Helpers ----------

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def get_user_from_db(username: str):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE username = ?", (username,))
    row = cur.fetchone()
    conn.close()
    if row:
        return dict(row)
    return None

async def get_current_user(token: str = Depends(oauth2_scheme)):
    """Validate JWT token and return current user"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = get_user_from_db(username)
    if user is None:
        raise credentials_exception
    return user

def check_permission(user_role: str, permission: Permission) -> bool:
    """Check if user role has permission"""
    try:
        role = UserRole(user_role)
        return RBACManager.has_permission(role, permission)
    except ValueError:
        return False

def log_audit(username: str, action: str, details: str = ""):
    """Log action to audit log"""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO audit_logs (username, action, details, timestamp) VALUES (?, ?, ?, ?)",
        (username, action, details, datetime.now())
    )
    conn.commit()
    conn.close()

# ---------- Authentication Endpoints ----------

@app.post("/auth/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login endpoint - returns JWT token"""
    user = get_user_from_db(form_data.username)
    
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        logger.warning(f"Failed login attempt for user: {form_data.username}")
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if user["disabled"]:
        raise HTTPException(status_code=400, detail="User account is disabled")
    
    # Update last login
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE users SET last_login = ? WHERE username = ?", (datetime.now(), form_data.username))
    conn.commit()
    conn.close()
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    expire = datetime.utcnow() + access_token_expires
    to_encode = {"sub": form_data.username, "exp": expire}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    logger.info(f"User {form_data.username} logged in successfully")
    return {"access_token": encoded_jwt, "token_type": "bearer"}

@app.get("/users/me", response_model=User)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get current logged-in user information"""
    return User(
        username=current_user["username"],
        full_name=current_user["full_name"],
        disabled=bool(current_user["disabled"]),
        role=current_user["role"]
    )

# ---------- REAL FILE SCANNING ENDPOINTS ----------

@app.post("/api/scan/file")
async def scan_file(request: FileScanRequest, current_user: dict = Depends(get_current_user)):
    """Scan a file using VirusTotal API (REAL)"""
    
    # Check permission
    if not check_permission(current_user["role"], Permission.RUN_FILE_SCAN):
        raise HTTPException(status_code=403, detail="Permission denied")
    
    if not VIRUSTOTAL_API_KEY:
        return {
            "status": "error",
            "message": "VirusTotal API key not configured. Set VIRUSTOTAL_API_KEY environment variable"
        }
    
    result = threat_intel.scan_file_virustotal(request.file_path)
    
    # Log to database if scan successful
    if result.get("status") == "success":
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO file_scans (file_path, sha256_hash, detected, engine_count, detections, scanned_at, username) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                request.file_path,
                result.get("sha256"),
                1 if result.get("detected") else 0,
                result.get("detections", {}).get("total", 0),
                result.get("detections", {}).get("malicious", 0),
                datetime.now(),
                current_user["username"]
            )
        )
        conn.commit()
        conn.close()
        log_audit(current_user["username"], "FILE_SCAN", f"Scanned: {request.file_path}")
    
    return result

@app.post("/api/scan/url")
async def scan_url(request: URLScanRequest, current_user: dict = Depends(get_current_user)):
    """Scan a URL using VirusTotal (REAL)"""
    
    if not check_permission(current_user["role"], Permission.RUN_URL_SCAN):
        raise HTTPException(status_code=403, detail="Permission denied")
    
    if not VIRUSTOTAL_API_KEY:
        return {
            "status": "error",
            "message": "VirusTotal API key not configured"
        }
    
    result = threat_intel.scan_url_virustotal(request.url)
    
    if result.get("status") == "success":
        log_audit(current_user["username"], "URL_SCAN", f"Scanned: {request.url}")
    
    return result

@app.post("/api/scan/ip")
async def check_ip_reputation(request: IPReputationRequest, current_user: dict = Depends(get_current_user)):
    """Check IP reputation (REAL)"""
    
    if not check_permission(current_user["role"], Permission.RUN_IP_SCAN):
        raise HTTPException(status_code=403, detail="Permission denied")
    
    result = threat_intel.check_ip_reputation(request.ip_address)
    
    if result.get("status") == "success":
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO ip_checks (ip_address, fraud_score, is_vpn, threat_level, checked_at, username) VALUES (?, ?, ?, ?, ?, ?)",
            (
                request.ip_address,
                result.get("fraud_score", 0),
                1 if result.get("is_vpn") else 0,
                result.get("threat_level", "unknown"),
                datetime.now(),
                current_user["username"]
            )
        )
        conn.commit()
        conn.close()
        log_audit(current_user["username"], "IP_CHECK", f"Checked: {request.ip_address}")
    
    return result

# ---------- FIREWALL ENDPOINTS ----------

@app.post("/api/firewall/rule")
async def create_firewall_rule(request: FirewallRuleRequest, current_user: dict = Depends(get_current_user)):
    """Create a firewall rule (REAL ENFORCEMENT)"""
    
    if not check_permission(current_user["role"], Permission.MANAGE_FIREWALL):
        raise HTTPException(status_code=403, detail="Permission denied")
    
    # Create on Windows Firewall
    result = firewall_manager.create_rule(
        rule_name=request.rule_name,
        direction=request.direction,
        action=request.action,
        local_port=request.local_port,
        remote_ip=request.remote_ip,
        protocol=request.protocol
    )
    
    # Log to database
    if result.get("status") == "success":
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO firewall_rules (rule_name, direction, action, local_port, remote_ip, protocol, enabled, created_at, created_by) VALUES (?, ?, ?, ?, ?, ?, 1, ?, ?)",
            (
                request.rule_name,
                request.direction,
                request.action,
                request.local_port,
                request.remote_ip,
                request.protocol,
                datetime.now(),
                current_user["username"]
            )
        )
        conn.commit()
        conn.close()
        log_audit(current_user["username"], "FIREWALL_RULE", f"Created: {request.rule_name}")
    
    return result

@app.post("/api/firewall/block-ip")
async def block_ip(request: BlockIPRequest, current_user: dict = Depends(get_current_user)):
    """Block traffic from an IP address (REAL)"""
    
    if not check_permission(current_user["role"], Permission.MANAGE_FIREWALL):
        raise HTTPException(status_code=403, detail="Permission denied")
    
    result = firewall_manager.block_ip(request.ip_address)
    
    if result.get("status") == "success":
        # Record threat
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO threat_detections (threat_type, severity, source_ip, detection_method, detected_at) VALUES (?, ?, ?, ?, ?)",
            ("IP Block", "medium", request.ip_address, "Manual Firewall", datetime.now())
        )
        conn.commit()
        conn.close()
        log_audit(current_user["username"], "IP_BLOCKED", f"Blocked: {request.ip_address}")
    
    return result

@app.get("/api/firewall/rules")
async def get_firewall_rules(current_user: dict = Depends(get_current_user)):
    """List all firewall rules"""
    
    if not check_permission(current_user["role"], Permission.VIEW_FIREWALL):
        raise HTTPException(status_code=403, detail="Permission denied")
    
    return firewall_manager.list_rules()

# ---------- NETWORK MONITORING ENDPOINTS ----------

@app.post("/api/network/start-capture")
async def start_network_capture(current_user: dict = Depends(get_current_user)):
    """Start real packet capture (REAL)"""
    
    if not check_permission(current_user["role"], Permission.RUN_NETWORK_SCAN):
        raise HTTPException(status_code=403, detail="Permission denied")
    
    result = network_monitor.start_capture(packet_count=500)
    
    if result.get("status") == "success":
        log_audit(current_user["username"], "NETWORK_CAPTURE", "Started packet capture")
    
    return result

@app.get("/api/network/traffic")
async def get_live_traffic(current_user: dict = Depends(get_current_user)):
    """Get live network traffic statistics (REAL)"""
    
    if not check_permission(current_user["role"], Permission.VIEW_NETWORK):
        raise HTTPException(status_code=403, detail="Permission denied")
    
    traffic = network_monitor.get_live_traffic()
    
    # Record any detected threats to database
    for threat in traffic.get("recent_threats", []):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO threat_detections (threat_type, severity, source_ip, target_ip, description, detection_method, detected_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                threat.get("threat_type"),
                threat.get("severity"),
                threat.get("src_ip"),
                threat.get("dst_ip"),
                f"Port: {threat.get('port')}",
                "Network Packet Analysis",
                threat.get("timestamp")
            )
        )
        conn.commit()
        conn.close()
    
    return traffic

@app.post("/api/network/stop-capture")
async def stop_network_capture(current_user: dict = Depends(get_current_user)):
    """Stop packet capture"""
    
    if not check_permission(current_user["role"], Permission.RUN_NETWORK_SCAN):
        raise HTTPException(status_code=403, detail="Permission denied")
    
    result = network_monitor.stop_capture()
    
    if result.get("status") == "success":
        log_audit(current_user["username"], "NETWORK_CAPTURE", "Stopped packet capture")
    
    return result

# ---------- THREAT & INCIDENT ENDPOINTS ----------

@app.get("/api/threats")
async def get_threats(current_user: dict = Depends(get_current_user)):
    """Get all detected threats from database (REAL)"""
    
    if not check_permission(current_user["role"], Permission.VIEW_THREATS):
        raise HTTPException(status_code=403, detail="Permission denied")
    
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM threat_detections ORDER BY detected_at DESC LIMIT 100")
    threats = [dict(row) for row in cur.fetchall()]
    conn.close()
    
    return {
        "status": "success",
        "threats": threats,
        "total": len(threats),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/analytics/summary")
async def get_analytics_summary(current_user: dict = Depends(get_current_user)):
    """Get security analytics summary with REAL data"""
    
    if not check_permission(current_user["role"], Permission.VIEW_DASHBOARD):
        raise HTTPException(status_code=403, detail="Permission denied")
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Get threat counts
    cur.execute("SELECT COUNT(*) as count FROM threat_detections WHERE resolved = 0")
    active_threats = dict(cur.fetchone()).get("count", 0)
    
    # Get file scan results
    cur.execute("SELECT COUNT(*) as count FROM file_scans WHERE detected = 1")
    malicious_files = dict(cur.fetchone()).get("count", 0)
    
    # Get IP checks
    cur.execute("SELECT COUNT(*) as count FROM ip_checks WHERE threat_level = 'high'")
    suspicious_ips = dict(cur.fetchone()).get("count", 0)
    
    conn.close()
    
    return {
        "status": "success",
        "summary": {
            "active_threats": active_threats,
            "malicious_files_detected": malicious_files,
            "suspicious_ips": suspicious_ips,
            "network_status": "monitoring active",
            "firewall_status": "operational",
            "timestamp": datetime.now().isoformat()
        }
    }

# ---------- USER MANAGEMENT ENDPOINTS ----------

@app.post("/api/users/")
async def create_user(user: UserCreate, current_user: dict = Depends(get_current_user)):
    """Create new user (ADMIN only)"""
    
    if not check_permission(current_user["role"], Permission.MANAGE_USERS):
        raise HTTPException(status_code=403, detail="Permission denied - Admin only")
    
    # Check if user exists
    if get_user_from_db(user.username):
        raise HTTPException(status_code=400, detail="User already exists")
    
    conn = get_db_connection()
    cur = conn.cursor()
    hashed = get_password_hash(user.password)
    
    cur.execute(
        "INSERT INTO users (username, full_name, hashed_password, disabled, role, created_at) VALUES (?, ?, ?, 0, ?, ?)",
        (user.username, user.full_name, hashed, user.role, datetime.now())
    )
    conn.commit()
    conn.close()
    
    log_audit(current_user["username"], "USER_CREATED", f"Created user: {user.username}")
    
    return {"status": "success", "message": f"User {user.username} created", "role": user.role}

@app.get("/api/users/")
async def list_users(current_user: dict = Depends(get_current_user)):
    """List all users (requires permission)"""
    
    if not check_permission(current_user["role"], Permission.VIEW_USERS):
        raise HTTPException(status_code=403, detail="Permission denied")
    
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT username, full_name, role, disabled, created_at, last_login FROM users")
    users = [dict(row) for row in cur.fetchall()]
    conn.close()
    
    return {
        "status": "success",
        "users": users,
        "total": len(users)
    }

# ---------- HEALTH & STATUS ENDPOINTS ----------

@app.get("/health")
async def health_check():
    """System health check"""
    return {
        "status": "operational",
        "version": "3.2.1",
        "timestamp": datetime.now().isoformat(),
        "components": {
            "database": "connected",
            "threat_intelligence": "online" if VIRUSTOTAL_API_KEY else "not_configured",
            "firewall": "operational",
            "network_monitor": "ready"
        }
    }

@app.get("/api/status")
async def system_status(current_user: dict = Depends(get_current_user)):
    """Get detailed system status"""
    
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) as count FROM threat_detections WHERE resolved = 0")
    threats = dict(cur.fetchone()).get("count", 0)
    
    cur.execute("SELECT MAX(detected_at) as last_threat FROM threat_detections")
    last_threat_row = cur.fetchone()
    last_threat = dict(last_threat_row).get("last_threat") if last_threat_row else None
    
    conn.close()
    
    return {
        "status": "operational",
        "user": current_user["username"],
        "user_role": current_user["role"],
        "active_threats": threats,
        "firewall_rules": len(firewall_manager.rules),
        "last_threat_detected": last_threat,
        "network_capture_active": network_monitor.is_running,
        "timestamp": datetime.now().isoformat()
    }

# ---------- STATIC FILES ----------

@app.get("/dashboard.html", response_class=FileResponse)
async def get_dashboard():
    """Serve dashboard"""
    return "dashboard.html"

@app.get("/login.html", response_class=FileResponse)
async def get_login():
    """Serve login page"""
    return "login.html"

# ---------- STARTUP ----------

@app.on_event("startup")
async def startup_event():
    """Initialize on startup"""
    init_db()
    logger.info("Sentinel-UG Omega started - REAL SECURITY MODE")
    logger.info(f"VirusTotal API: {'Configured' if VIRUSTOTAL_API_KEY else 'Not configured'}")
    logger.info(f"Shodan API: {'Configured' if SHODAN_API_KEY else 'Not configured'}")
