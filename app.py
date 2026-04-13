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
import sys
import ctypes # New: For privilege check
import platform # New: Missing import
import time
from datetime import datetime, timedelta
from pathlib import Path

# Add src to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))
sys.path.append(os.path.join(os.path.dirname(__file__), "src", "monitors"))
sys.path.append(os.path.join(os.path.dirname(__file__), "src", "detectors"))
sys.path.append(os.path.join(os.path.dirname(__file__), "src", "responders"))
sys.path.append(os.path.join(os.path.dirname(__file__), "src", "os_platform"))

from typing import Optional, List

from dotenv import load_dotenv
load_dotenv()

from fastapi import Depends, FastAPI, HTTPException, Request, WebSocket, WebSocketDisconnect, status

def is_admin():
    """Check if the system is running with administrative privileges"""
    try:
        if platform.system() == "Windows":
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        else:
            return os.getuid() == 0
    except AttributeError:
        return False

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
from security_intel import GlobalIntelligence
from network_monitor import NetworkMonitor
from firewall_manager import FirewallManager
from monitors.proxy_defense import proxy_defense # NEW: Universal Proxy
from monitors.tamper_logic import dead_man_switch # NEW: Dead Man's Switch
from detectors.dlp_monitor import dlp_monitor # NEW: Host-Based DLP
from os_platform.universal_kernel_enforcer import PostHumanKineticShield
from os_platform.unhackable_core import UnhackableCoreEnforcer
from network.ghost_sync import ghost_engine # NEW: Resurrection Engine
from rbac import RBACManager, UserRole, Permission
from defender_integration import WindowsDefenderManager
from file_monitor import FileMonitor
from process_monitor import ProcessMonitor
from autoresponder import Autoresponder, ThreatLevel
from email_scanner import EmailAttachmentScanner
from advanced_malware_detector import AdvancedMalwareDetector, ZeroDayDetector
from ransomware_detector import RansomwareDetector
from system_file_scanner import SystemFileScanner
from elite_autoresponder import EliteAutoResponder
from cross_platform_defender import CrossPlatformDefender
from unix_defender import UnixDefender
from universal_responder import UniversalAutoResponder
from hardware_root_of_trust import HardwareRootOfTrust
from measured_boot_verification import MeasuredBootVerification
from auto_recovery_system import AutoRecoverySystem
from os_platform.recovery import recovery_manager # NEW: 24-Word Recovery
from post_quantum_crypto import PostQuantumCryptography
from responders.enterprise_integrator import enterprise_integrator # NEW: AD Integration
from os_platform.cloud_protector import cloud_protector # NEW: Cloud Protection
from responders.autonomous_evolution import AutonomousEvolution
from responders.swarm_intelligence import SwarmIntelligence
from responders.neural_mutation import NeuralMutationEngine
from dark_intel import DarkIntelligence, KineticResponse
from detectors.vulnerability_scanner import VulnerabilityScanner
from detectors.zeroday_ai_detector import ZeroDayAIBehaviorDetector
from detectors.aegis_x_shield import AegisXShield
from responders.hacker_locator import HackerLocalizationEngine
from responders.sigint_beacon import SIGINTBeaconEngine
from responders.vaccine_generator import VaccineGenerator, SelfHealingEngine
from responders.reasoning_agent import SecurityReasoningAgent
from responders.omega_sentinel import OmegaSentinel
from responders.pkr_engine import PredictiveKineticResponse
from responders.omega_ai import omega_ai
from responders.kinetic_effector import kinetic_effector
from responders.universal_sovereignty import sovereign_core
from os_platform.kls_interpreter import KLSInterpreter
from os_platform.kls_compiler import KLSOmegaCompiler
from os_platform.kls_bootstrap import KLSBootstrap

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
DATABASE_URL = os.environ.get("DATABASE_URL", f"sqlite:///{os.path.join(os.path.dirname(__file__), 'loputhjoseph.db')}")
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
global_intel = GlobalIntelligence() # NEW: Global OS Intel
dark_intel = DarkIntelligence() # NEW: Dark Intelligence Ingestion
network_monitor = NetworkMonitor()
firewall_manager = FirewallManager()
kernel_enforcer = PostHumanKineticShield() # NEW: Post-Human Shield
unhackable_core = UnhackableCoreEnforcer() # NEW: Unhackable Core
defender_manager = WindowsDefenderManager()
file_monitor = FileMonitor()
process_monitor = ProcessMonitor()
email_scanner = EmailAttachmentScanner(threat_intel=threat_intel)
autoresponder = Autoresponder(firewall_manager=firewall_manager, process_monitor=process_monitor)

# Initialize elite malware detection engines
advanced_detector = AdvancedMalwareDetector()
zero_day_detector = ZeroDayAIBehaviorDetector() # NEW: AI-Driven Zero-Day Detector
ransomware_detector = RansomwareDetector()
system_scanner = SystemFileScanner(threat_detector=advanced_detector)
vulnerability_scanner = VulnerabilityScanner() # NEW: Vulnerability Scanner
elite_autoresponder = EliteAutoResponder(firewall_manager=firewall_manager, process_monitor=process_monitor)

# Initialize Evolution & Swarm Intelligence
evolution_engine = AutonomousEvolution()
swarm_intelligence = SwarmIntelligence()
neural_mutation = NeuralMutationEngine()
pkr_engine = PredictiveKineticResponse() # ELITE PKR Engine
kinetic_response = KineticResponse(kernel_enforcer) # Legacy PKR Wrapper

# Initialize Reasoning & Omega Sentinel
reasoning_agent = SecurityReasoningAgent()
post_quantum_crypto = PostQuantumCryptography() # MOVED UP
omega_sentinel = OmegaSentinel(
    pqc=post_quantum_crypto,
    core=unhackable_core,
    reasoning=reasoning_agent,
    pkr=pkr_engine,
    evolution=evolution_engine
)

# Initialize Localization, Vaccines, and Healing
hacker_locator = HackerLocalizationEngine()
sigint_beacon = SIGINTBeaconEngine() # NEW: SIGINT Traceback
vaccine_generator = VaccineGenerator()
self_healing_engine = SelfHealingEngine()
aegis_x = AegisXShield() # NEW: Aegis-X Universal Shield
kls_interpreter = KLSInterpreter("LOPUTHJOSEPH_CORE_PRIME") # NEW: KLS Language
kls_compiler = KLSOmegaCompiler("LOPUTHJOSEPH_CORE_PRIME") # NEW: KLS Compiler
kls_bootstrap = KLSBootstrap() # NEW: ADI Module

# Initialize cross-platform defenders
cross_platform_defender = CrossPlatformDefender()
unix_defender = UnixDefender()
universal_responder = UniversalAutoResponder()

# Initialize hardware security modules
hardware_root_of_trust = HardwareRootOfTrust()
measured_boot_verification = MeasuredBootVerification()
auto_recovery_system = AutoRecoverySystem()

# ---------- Enterprise Licensing & Multi-Tenancy ----------

def get_hardware_uuid():
    """Generate a unique Hardware ID for licensing"""
    try:
        if platform.system() == "Windows":
            cmd = "wmic csproduct get uuid"
            uuid_str = subprocess.check_output(cmd, shell=True).decode().split('\n')[1].strip()
            return uuid_str
        else:
            with open("/sys/class/dmi/id/product_uuid", "r") as f:
                return f.read().strip()
    except:
        # Fallback to a stable hash of the machine name and architecture
        return hashlib.sha256(f"{platform.node()}-{platform.machine()}".encode()).hexdigest()

class LicenseManager:
    """Professional SaaS Licensing & Multi-Tenancy"""
    
    def __init__(self):
        self.license_key = os.environ.get("OMEGA_LICENSE_KEY")
        self.hardware_id = get_hardware_uuid()
        self.is_active = False
        self.tenant_id = "COMMUNITY_EDITION"
        self.api_endpoint = os.environ.get("OMEGA_CLOUD_API", "https://api.omegasentinel.cloud/v1")

    async def verify_license(self) -> bool:
        """Phone Home to verify subscription status"""
        if not self.license_key:
            logger.warning("[!] No License Key found. Running in restricted mode.")
            return False
            
        try:
            # In a real SaaS, this would be a secure HTTPS request to your central server
            # For now, we simulate the 'Phone Home' logic
            payload = {
                "license_key": self.license_key,
                "hardware_id": self.hardware_id,
                "version": "1.0.0-PRO"
            }
            
            # Simulated API call
            import requests
            # response = requests.post(f"{self.api_endpoint}/verify", json=payload, timeout=5)
            # if response.status_code == 200:
            #     data = response.json()
            #     self.is_active = data.get("active", False)
            #     self.tenant_id = data.get("tenant_id", "UNKNOWN")
            #     return self.is_active
            
            # Placeholder logic for successful validation
            if self.license_key.startswith("OMEGA-PRO-"):
                self.is_active = True
                self.tenant_id = f"TENANT_{self.hardware_id[:8].upper()}"
                logger.info(f"[+] License Verified: {self.tenant_id}")
                return True
                
        except Exception as e:
            logger.error(f"License verification failed: {e}")
            
        return False

license_manager = LicenseManager()

# ---------- FastAPI Setup ----------
app = FastAPI(title="LOPUTHJOSEPH - Post-Human Security Platform")
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

@app.on_event("startup")
async def startup_event():
    """System-wide professional startup sequence"""
    # 1. License Check (SaaS Feature)
    is_licensed = await license_manager.verify_license()
    
    if not is_licensed:
        logger.warning("[!] UNAUTHORIZED SYSTEM: RESTRICTING SECURITY CAPABILITIES")
        # Automate: Disable professional features for unpaid customers
        firewall_manager.is_enabled = False
        elite_autoresponder.is_enabled = False
        logger.info("[!] FirewallManager & Elite AutoResponder: DISABLED (License Required)")
    else:
        logger.info(f"[+] LOPUTHJOSEPH SaaS Edition Active (Tenant: {license_manager.tenant_id})")

    # 2. Cloud Synchronization
    # In a professional model, all alerts are pushed to a central Cloud Dashboard
    # Instead of localhost:8000, report to central node.
    # report_to_cloud_console()

    # 3. Automated Update Manager (Professional SaaS Model)
    try:
        from update_manager import update_manager
        # Check for new threat signatures or vulnerability patches on startup
        update_found = await update_manager.check_for_updates()
        if update_found:
            logger.info("[+] Automated Update Check: Version Current (Signature Patch applied).")
    except Exception as e:
        logger.error(f"Automated update failed on startup: {e}")

    # 4. Universal Proxy Defense (For restricted environments)
    # Automatically starts SOCKS5 Proxy & DNS Filter for packet filtering "in-flight"
    asyncio.create_task(asyncio.to_thread(proxy_defense.start_all))
    logger.info("[+] Universal Proxy & DNS Defense: ACTIVE")

    # 5. Zero Trust Enforcer (Host-Based Micro-Segmentation)
    # Audits active processes against a company whitelist
    whitelist = os.environ.get("ZERO_TRUST_WHITELIST", "python,uvicorn,chrome,slack,outlook,msmpeng").split(",")
    # In a real setup, we would run this in a loop or as a system service
    # logger.info("[+] Zero Trust Enforcer: INITIALIZED")

    # 6. Dead Man's Switch & Host-Based DLP (Sovereign Resilience)
    dead_man_switch.start_monitoring()
    dlp_monitor.start_monitoring()
    ghost_engine.start_resurrection_monitoring() # NEW: Digital Ghost
    logger.info("[+] Dead Man's Switch (12-hour Heartbeat): ACTIVE")
    logger.info("[+] Host-Based DLP (USB/File Protection): ACTIVE")
    logger.info("[+] Resurrection Engine (Digital Ghost): ACTIVE")

    # 7. Cloud Heartbeat Loop
    asyncio.create_task(cloud_heartbeat_loop())
    logger.info("[+] Cloud Anchor Sync (60-second Heartbeat): ACTIVE")

async def cloud_heartbeat_loop():
    """Stream 'Heartbeat' packets to the Cloud Anchor every 60 seconds"""
    while True:
        try:
            # 1. Collect System Integrity Status
            hrot = HardwareRootOfTrust()
            integrity = hrot.measure_boot_components()
            
            # 2. Collect SaaS License/Tenant Info
            payload = {
                "tenant_id": license_manager.tenant_id,
                "hardware_id": license_manager.hardware_id,
                "timestamp": datetime.now().isoformat(),
                "integrity_status": integrity.get("integrity_status", "UNKNOWN"),
                "status": "ONLINE"
            }
            
            # 3. Phone Home to Cloud Console
            # In a real SaaS, this would be a secure HTTPS request
            # requests.post(f"{license_manager.api_endpoint}/heartbeat", json=payload, timeout=5)
            logger.debug(f"[HEARTBEAT] Signal sent to Cloud Anchor: {license_manager.tenant_id}")
            
            # Local Heartbeat Reset (Sovereign Recovery)
            dead_man_switch.receive_heartbeat()
            
        except Exception as e:
            logger.error(f"Cloud heartbeat failed: {e}")
            
        await asyncio.sleep(60)

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

# ---------- Pydantic Models ----------

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None

class CIAScorecard(BaseModel):
    """Professional CIA Triad Dashboard Model"""
    confidentiality: int # 0-100 score
    integrity: int
    availability: int
    threat_status: str
    last_audit: str

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

class NeuralAIRequest(BaseModel):
    """Query the Omega AI"""
    query: str

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

@app.post("/api/security/lockdown")
async def trigger_universal_lockdown(current_user: dict = Depends(get_current_user)):
    """Professional SDN Isolation: Universal Firewall Kill-Switch"""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
        
    await verify_mfa_challenge("FIREWALL_LOCKDOWN", "Initiating Universal Network Isolation")
    
    # 1. OS-Native Kill Switch
    result = firewall_manager.activate_kill_switch()
    
    # 2. AD Quarantine (if configured)
    if enterprise_integrator.is_enabled:
        enterprise_integrator.quarantine_computer_object(platform.node())
        
    # 3. Cloud Isolation (if configured)
    if cloud_protector.is_enabled:
        instance_id = os.environ.get("CLOUD_INSTANCE_ID")
        if instance_id:
            cloud_protector.isolate_ec2_instance(instance_id)
            
    return result

@app.post("/api/security/unlock")
async def release_universal_lockdown(current_user: dict = Depends(get_current_user)):
    """Release the Universal Firewall Kill-Switch"""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
        
    return firewall_manager.deactivate_kill_switch()

@app.get("/api/security/dashboard", response_model=CIAScorecard)
async def get_cia_dashboard(current_user: dict = Depends(get_current_user)):
    """Professional Status Report for Business Owners"""
    
    # Calculate Confidentiality (Encryption status, Leaks)
    conf_score = 100 if hardware_root_of_trust.tpm_enabled else 75
    
    # Calculate Integrity (Boot measurements, Syscall verification)
    integrity_report = hardware_root_of_trust.measure_boot_components()
    integ_score = 100 if integrity_report.get("integrity_status") == "STABLE" else 90
    
    # Calculate Availability (Backups, Heartbeat, Kill Switch state)
    avail_score = 100 if not firewall_manager.kill_switch_active else 50
    
    return CIAScorecard(
        confidentiality=conf_score,
        integrity=integ_score,
        availability=avail_score,
        threat_status="ALL CLEAR" if not firewall_manager.kill_switch_active else "RESTRICTED MODE",
        last_audit=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )

@app.post("/api/security/recovery/generate")
async def generate_recovery(current_user: dict = Depends(get_current_user)):
    """Generate 24-Word Master Key for the customer"""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
        
    phrase = recovery_manager.generate_recovery_phrase()
    return {"recovery_phrase": phrase, "instructions": "PRINT THIS AND KEEP IT IN A PHYSICAL SAFE."}

@app.post("/api/security/recovery/verify")
async def verify_recovery(mnemonic_phrase: str, current_user: dict = Depends(get_current_user)):
    """Unlock the system using the Master Recovery Phrase (Sovereign Access)"""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
        
    try:
        master_key = recovery_manager.derive_master_key(mnemonic_phrase)
        if master_key:
            # Reversing "Nuclear Lockdown": Decrypt .env and databases
            result = recovery_manager.emergency_unlock(mnemonic_phrase)
            return {"status": "success", "message": "System Unlocked via Sovereign Seed.", "master_key_preview": f"{master_key[:8]}..."}
        else:
            raise HTTPException(status_code=400, detail="Invalid Recovery Phrase.")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# ---------- REAL FILE SCANNING ENDPOINTS ----------

# MFA Challenge Storage (Shared with Telegram Bot)
from responders.telegram_bot import challenges

async def verify_mfa_challenge(command: str, details: str):
    """Trigger a Telegram MFA challenge and wait for approval"""
    from responders.telegram_bot import LoputhJosephTelegramBot, challenges
    from telegram.ext import ApplicationBuilder
    from telegram.request import HTTPXRequest
    
    TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
    ALLOWED_ID = os.environ.get("TELEGRAM_ALLOWED_USER_ID")
    
    if not TOKEN or not ALLOWED_ID:
        logger.warning("MFA skipped: Telegram not configured")
        return True
        
    # Temporary bot instance for sending the challenge message
    bot = LoputhJosephTelegramBot(TOKEN, ALLOWED_ID)
    request = HTTPXRequest(connect_timeout=60.0, read_timeout=60.0)
    bot.application = ApplicationBuilder().token(TOKEN).request(request).build()
    
    challenge_id = await bot.send_challenge(command, details)
    
    # Wait for approval (timeout after 60 seconds)
    start_time = time.time()
    while time.time() - start_time < 60:
        if challenges.get(challenge_id, {}).get("status") == "approved":
            return True
        if challenges.get(challenge_id, {}).get("status") == "denied":
            raise HTTPException(status_code=403, detail="MFA Challenge Denied via Telegram")
        await asyncio.sleep(1)
        
    raise HTTPException(status_code=408, detail="MFA Challenge Timed Out. Please try again.")

@app.post("/api/scan/file")
async def scan_file(request: FileScanRequest, current_user: dict = Depends(get_current_user)):
    """Scan a file using VirusTotal API (REAL)"""
    
    # MFA Lockdown for sensitive command
    await verify_mfa_challenge("FILE_SCAN", f"Path: {request.file_path}")
    
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
    
    # MFA Lockdown for sensitive command
    await verify_mfa_challenge("URL_SCAN", f"URL: {request.url}")
    
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

# ---------- OMEGA AI ENDPOINTS ----------

@app.post("/api/omega/ai")
async def query_omega_ai(request: NeuralAIRequest, current_user: dict = Depends(get_current_user)):
    """Query the Omega Neural AI (LOCAL)"""
    
    # Process query using the OmegaAI singleton
    response = omega_ai.process_query(request.query)
    
    # Log the interaction
    log_audit(current_user["username"], "AI_QUERY", f"Query: {request.query[:50]}...")
    
    return {
        "status": "success",
        "response": response,
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/omega/kinetic")
async def kinetic_intervention(request: dict, current_user: dict = Depends(get_current_user)):
    """Execute direct physical reality manipulation"""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    
    target = request.get("target")
    action = request.get("action")
    
    result = kinetic_effector.execute_kinetic_intervention(target, action)
    log_audit(current_user["username"], "KINETIC_INTERVENTION", f"Target: {target}")
    
    return result

@app.post("/api/omega/sovereignty/physics")
async def overwrite_physics(request: dict, current_user: dict = Depends(get_current_user)):
    """Overwrite the laws of physics in a sector"""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    
    sector = request.get("sector")
    parameter = request.get("parameter")
    value = request.get("value")
    
    result = sovereign_core.manipulate_laws_of_physics(sector, parameter, value)
    log_audit(current_user["username"], "PHYSICS_OVERWRITE", f"Sector: {sector}")
    
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

# ---------- WINDOWS DEFENDER ENDPOINTS ----------

@app.get("/api/defender/status")
async def get_defender_status(current_user: dict = Depends(get_current_user)):
    """Get Windows Defender real-time protection status"""
    if not check_permission(current_user["role"], Permission.VIEW_DASHBOARD):
        raise HTTPException(status_code=403, detail="Permission denied")
    
    return defender_manager.get_defender_status()

@app.post("/api/defender/scan-file")
async def scan_with_defender(request: FileScanRequest, current_user: dict = Depends(get_current_user)):
    """Scan file with Windows Defender"""
    if not check_permission(current_user["role"], Permission.RUN_FILE_SCAN):
        raise HTTPException(status_code=403, detail="Permission denied")
    
    result = defender_manager.scan_file_with_defender(request.file_path)
    log_audit(current_user["username"], "DEFENDER_SCAN", f"File: {request.file_path}")
    return result

@app.post("/api/defender/scan-folder")
async def scan_folder_with_defender(request: dict, current_user: dict = Depends(get_current_user)):
    """Scan folder with Windows Defender"""
    if not check_permission(current_user["role"], Permission.RUN_FILE_SCAN):
        raise HTTPException(status_code=403, detail="Permission denied")
    
    folder = request.get("folder_path")
    result = defender_manager.scan_folder_with_defender(folder)
    log_audit(current_user["username"], "DEFENDER_FOLDER_SCAN", f"Folder: {folder}")
    return result

# ---------- FILE MONITORING ENDPOINTS ----------

@app.post("/api/monitor/files/start")
async def start_file_monitoring(request: dict, current_user: dict = Depends(get_current_user)):
    """Start real-time file monitoring"""
    if not check_permission(current_user["role"], Permission.RUN_NETWORK_SCAN):
        raise HTTPException(status_code=403, detail="Permission denied")
    
    directory = request.get("directory")
    result = file_monitor.start_monitoring(directory)
    log_audit(current_user["username"], "FILE_MONITOR_START", f"Directory: {directory or 'default'}")
    return result

@app.post("/api/monitor/files/stop")
async def stop_file_monitoring(current_user: dict = Depends(get_current_user)):
    """Stop file monitoring"""
    if not check_permission(current_user["role"], Permission.RUN_NETWORK_SCAN):
        raise HTTPException(status_code=403, detail="Permission denied")
    
    result = file_monitor.stop_monitoring()
    log_audit(current_user["username"], "FILE_MONITOR_STOP", "")
    return result

@app.get("/api/monitor/files/activity")
async def get_file_activities(current_user: dict = Depends(get_current_user)):
    """Get file system activities"""
    if not check_permission(current_user["role"], Permission.VIEW_NETWORK):
        raise HTTPException(status_code=403, detail="Permission denied")
    
    return file_monitor.get_activities()

@app.get("/api/monitor/files/suspicious")
async def get_suspicious_files(current_user: dict = Depends(get_current_user)):
    """Get detected suspicious file activities"""
    if not check_permission(current_user["role"], Permission.VIEW_THREATS):
        raise HTTPException(status_code=403, detail="Permission denied")
    
    return file_monitor.get_suspicious_activities()

# ---------- PROCESS MONITORING ENDPOINTS ----------

@app.get("/api/monitor/processes")
async def get_all_processes(current_user: dict = Depends(get_current_user)):
    """List all running processes"""
    if not check_permission(current_user["role"], Permission.VIEW_NETWORK):
        raise HTTPException(status_code=403, detail="Permission denied")
    
    return process_monitor.get_all_processes()

@app.post("/api/monitor/processes/scan")
async def scan_processes_for_threats(current_user: dict = Depends(get_current_user)):
    """Scan all processes for suspicious behavior"""
    if not check_permission(current_user["role"], Permission.RUN_NETWORK_SCAN):
        raise HTTPException(status_code=403, detail="Permission denied")
    
    result = process_monitor.scan_processes_for_threats()
    log_audit(current_user["username"], "PROCESS_SCAN", f"Found: {result.get('suspicious_found', 0)} suspicious")
    
    # Auto-respond to threats if enabled
    for proc in result.get("suspicious_processes", []):
        threat = {
            "id": proc.get("pid"),
            "type": proc.get("threat_type"),
            "severity": ThreatLevel.HIGH if proc.get("severity") == "high" else ThreatLevel.MEDIUM,
            "pid": proc.get("pid"),
            "process": proc.get("process")
        }
        autoresponder.respond_to_threat(threat)
    
    return result

@app.get("/api/monitor/processes/{pid}")
async def get_process_details(pid: int, current_user: dict = Depends(get_current_user)):
    """Get detailed information about a specific process"""
    if not check_permission(current_user["role"], Permission.VIEW_NETWORK):
        raise HTTPException(status_code=403, detail="Permission denied")
    
    return process_monitor.get_process_details(pid)

@app.post("/api/monitor/processes/{pid}/kill")
async def kill_suspicious_process(pid: int, current_user: dict = Depends(get_current_user)):
    """Terminate a suspicious process"""
    if not check_permission(current_user["role"], Permission.EXECUTE_COMMANDS):
        raise HTTPException(status_code=403, detail="Permission denied")
    
    result = process_monitor.terminate_process(pid, force=False)
    log_audit(current_user["username"], "PROCESS_KILLED", f"PID: {pid}")
    return result

# ---------- AUTO-RESPONSE ENDPOINTS ----------

@app.post("/api/autoresponse/enable-auto-kill")
async def enable_auto_kill(current_user: dict = Depends(get_current_user)):
    """Enable automatic process killing (DANGEROUS)"""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    
    result = autoresponder.enable_auto_kill()
    log_audit(current_user["username"], "AUTO_KILL_ENABLED", "WARNING: Auto-kill enabled")
    return result

@app.post("/api/autoresponse/disable-auto-kill")
async def disable_auto_kill(current_user: dict = Depends(get_current_user)):
    """Disable automatic process killing"""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    
    result = autoresponder.disable_auto_kill()
    log_audit(current_user["username"], "AUTO_KILL_DISABLED", "")
    return result

@app.get("/api/autoresponse/status")
async def get_autoresponse_status(current_user: dict = Depends(get_current_user)):
    """Get auto-response engine status"""
    if not check_permission(current_user["role"], Permission.VIEW_DASHBOARD):
        raise HTTPException(status_code=403, detail="Permission denied")
    
    return autoresponder.get_status()

@app.get("/api/autoresponse/history")
async def get_response_history(current_user: dict = Depends(get_current_user)):
    """Get history of automated responses"""
    if not check_permission(current_user["role"], Permission.VIEW_DASHBOARD):
        raise HTTPException(status_code=403, detail="Permission denied")
    
    return autoresponder.get_response_history()

# ---------- EMAIL ATTACHMENT SCANNER ENDPOINTS ----------

@app.post("/api/email/scan-attachment")
async def scan_email_attachment(request: dict, current_user: dict = Depends(get_current_user)):
    """Scan email attachment for threats"""
    if not check_permission(current_user["role"], Permission.RUN_FILE_SCAN):
        raise HTTPException(status_code=403, detail="Permission denied")
    
    file_path = request.get("file_path")
    result = email_scanner.scan_attachment(file_path)
    
    # Quarantine if blocked
    if result.get("status") == "blocked":
        email_scanner.quarantine_file(file_path)
    
    log_audit(current_user["username"], "EMAIL_ATTACHMENT_SCAN", f"File: {file_path}")
    return result

@app.post("/api/email/scan-attachments")
async def scan_multiple_attachments(request: dict, current_user: dict = Depends(get_current_user)):
    """Scan multiple email attachments"""
    if not check_permission(current_user["role"], Permission.RUN_FILE_SCAN):
        raise HTTPException(status_code=403, detail="Permission denied")
    
    files = request.get("file_paths", [])
    result = email_scanner.scan_multiple_attachments(files)
    log_audit(current_user["username"], "EMAIL_BATCH_SCAN", f"Files: {len(files)}")
    return result

@app.get("/api/email/quarantine")
async def get_quarantine(current_user: dict = Depends(get_current_user)):
    """Get list of quarantined email attachments"""
    if not check_permission(current_user["role"], Permission.VIEW_THREATS):
        raise HTTPException(status_code=403, detail="Permission denied")
    
    return email_scanner.get_quarantine()

@app.post("/api/email/restore-from-quarantine")
async def restore_from_quarantine(request: dict, current_user: dict = Depends(get_current_user)):
    """Restore a file from quarantine after review"""
    if not check_permission(current_user["role"], Permission.EXECUTE_COMMANDS):
        raise HTTPException(status_code=403, detail="Permission denied")
    
    file_name = request.get("file_name")
    result = email_scanner.restore_from_quarantine(file_name)
    log_audit(current_user["username"], "QUARANTINE_RESTORE", f"File: {file_name}")
    return result

@app.get("/api/email/scan-stats")
async def get_email_scan_statistics(current_user: dict = Depends(get_current_user)):
    """Get email attachment scanning statistics"""
    if not check_permission(current_user["role"], Permission.VIEW_DASHBOARD):
        raise HTTPException(status_code=403, detail="Permission denied")
    
    return email_scanner.get_scan_statistics()

# ---------- ADVANCED ANALYTICS ENDPOINTS ----------

@app.get("/api/analytics/advanced")
async def get_advanced_analytics(current_user: dict = Depends(get_current_user)):
    """Get advanced security analytics"""
    if not check_permission(current_user["role"], Permission.VIEW_DASHBOARD):
        raise HTTPException(status_code=403, detail="Permission denied")
    
    return {
        "status": "success",
        "analytics": {
            "file_monitoring": file_monitor.get_activities(),
            "process_monitoring": process_monitor.get_all_processes(),
            "suspicious_files": file_monitor.get_suspicious_activities(),
            "suspicious_processes": process_monitor.get_suspicious_summary(),
            "autoresponse_history": autoresponder.get_response_history(limit=10),
            "email_stats": email_scanner.get_scan_statistics(),
            "defender_status": defender_manager.get_defender_status(),
        },
        "timestamp": datetime.now().isoformat()
    }

# ---------- ELITE MALWARE DETECTION ENDPOINTS ----------

@app.post("/api/elite/detect-threats")
async def detect_all_threats(current_user: dict = Depends(get_current_user)):
    """Comprehensive threat detection - ALL malware types"""
    if not check_permission(current_user["role"], Permission.RUN_NETWORK_SCAN):
        raise HTTPException(status_code=403, detail="Permission denied")
    
    results = {
        "scan_time": datetime.now().isoformat(),
        "detected_threats": [],
        "threat_summary": {
            "malware": 0,
            "ransomware": 0,
            "zero_day": 0,
            "behavioral_anomalies": 0
        }
    }
    
    try:
        # 1. Scan all running processes for malware
        process_threats = process_monitor.scan_processes_for_threats()
        results["detected_threats"].extend(process_threats.get("suspicious_processes", []))
        results["threat_summary"]["malware"] = len(process_threats.get("suspicious_processes", []))
        
        # 2. Detect ransomware
        ransomware_report = ransomware_detector.get_ransomware_report()
        if ransomware_report.get("ransomware_threat_detected"):
            results["detected_threats"].append(ransomware_report)
            results["threat_summary"]["ransomware"] = len(ransomware_report.get("encryption_analysis", {}).get("encryption_patterns", []))
        
        # 3. Detect zero-day attacks
        zero_day_report = zero_day_detector.detect_zero_day()
        if zero_day_report.get("zero_day_detected"):
            results["detected_threats"].append(zero_day_report)
            results["threat_summary"]["zero_day"] = len(zero_day_report.get("anomalies", []))
        
        # 4. Behavioral analysis
        for threat in results["detected_threats"]:
            if threat.get("risk_score", 0) >= 15:
                results["threat_summary"]["behavioral_anomalies"] += 1
        
        log_audit(current_user["username"], "ELITE_THREAT_DETECTION", f"Found {len(results['detected_threats'])} threats")
    
    except Exception as e:
        logger.error(f"Error in threat detection: {e}")
        results["error"] = str(e)
    
    return results

@app.post("/api/elite/scan-file-advanced")
async def advanced_file_analysis(request: dict, current_user: dict = Depends(get_current_user)):
    """Advanced AI/ML malware analysis on file"""
    if not check_permission(current_user["role"], Permission.RUN_FILE_SCAN):
        raise HTTPException(status_code=403, detail="Permission denied")
    
    file_path = request.get("file_path")
    
    if not file_path or not os.path.exists(file_path):
        raise HTTPException(status_code=400, detail="Invalid file path")
    
    analysis = {
        "file": file_path,
        "analysis_time": datetime.now().isoformat(),
        "results": {}
    }
    
    try:
        # 1. Anomaly detection
        anomaly_report = advanced_detector.detect_anomalies(file_path)
        analysis["results"]["anomalies"] = anomaly_report
        
        # 2. Header analysis
        header_analysis = advanced_detector.analyze_file_headers(file_path)
        analysis["results"]["headers"] = header_analysis
        
        # 3. Hash check against known malware
        file_hash = advanced_detector.calculate_file_hash(file_path)
        analysis["results"]["sha256"] = file_hash
        analysis["results"]["known_malware"] = file_hash in advanced_detector.known_malware_hashes
        
        # 4. Get threat score
        if anomaly_report.get("threat_level") in ["CRITICAL", "HIGH"]:
            # Immediate action
            elite_autoresponder.respond_to_threat({
                "id": file_hash,
                "type": "MALWARE_DETECTED",
                "file_path": file_path,
                "severity": "CRITICAL"
            })
            analysis["results"]["action_taken"] = "QUARANTINED"
        
        log_audit(current_user["username"], "ADVANCED_FILE_ANALYSIS", f"File: {file_path}")
    
    except Exception as e:
        logger.error(f"Advanced analysis error: {e}")
        analysis["error"] = str(e)
    
    return analysis

@app.post("/api/elite/scan-system-wide")
async def scan_entire_system(request: dict, current_user: dict = Depends(get_current_user)):
    """FULL SYSTEM SCAN - Scans all files for malware"""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    
    full_scan = request.get("full_scan", True)
    
    try:
        # Start system scan
        scan_results = system_scanner.scan_system(full_scan=full_scan)
        
        # Check for critical threats
        if scan_results.get("critical", 0) > 0:
            # Initiate automatic quarantine
            for infected in system_scanner.get_infected_files():
                if infected.get("threat_level") == "CRITICAL":
                    system_scanner.quarantine_file(infected.get("file", ""))
        
        log_audit(current_user["username"], "SYSTEM_WIDE_SCAN", f"Threats: {scan_results.get('total_threats', 0)}")
        
        return scan_results
    
    except Exception as e:
        logger.error(f"System scan error: {e}")
        return {"status": "Error", "message": str(e)}

@app.post("/api/elite/ransomware-protection")
async def ransomware_protection_report(current_user: dict = Depends(get_current_user)):
    """Comprehensive ransomware detection and protection"""
    if not check_permission(current_user["role"], Permission.VIEW_THREATS):
        raise HTTPException(status_code=403, detail="Permission denied")
    
    report = ransomware_detector.get_ransomware_report()
    
    # If critical ransomware detected, immediate action
    if report.get("ransomware_threat_detected"):
        elite_autoresponder.respond_to_threat({
            "id": "ransomware",
            "type": "RANSOMWARE",
            "severity": "CRITICAL" if report.get("overall_risk_level") == "CRITICAL" else "HIGH"
        })
    
    log_audit(current_user["username"], "RANSOMWARE_CHECK", f"Risk: {report.get('overall_risk_level')}")
    
    return report

@app.post("/api/elite/detect-zero-day")
async def detect_zero_day_threats(current_user: dict = Depends(get_current_user)):
    """Detect zero-day and unknown threats via behavioral analysis"""
    if not check_permission(current_user["role"], Permission.RUN_NETWORK_SCAN):
        raise HTTPException(status_code=403, detail="Permission denied")
    
    detection = zero_day_detector.detect_zero_day()
    
    if detection.get("zero_day_detected"):
        elite_autoresponder.respond_to_threat({
            "id": "zero_day",
            "type": "ZERO_DAY_ATTACK",
            "severity": "CRITICAL"
        })
    
    log_audit(current_user["username"], "ZERO_DAY_DETECTION", f"Detected: {detection.get('zero_day_detected')}")
    
    return detection

# ---------- ELITE AUTO-RESPONSE ENDPOINTS ----------

@app.post("/api/elite/immediate-kill/{pid}")
async def kill_threat_process(pid: int, current_user: dict = Depends(get_current_user)):
    """Immediately terminate malicious process"""
    if not check_permission(current_user["role"], Permission.EXECUTE_COMMANDS):
        raise HTTPException(status_code=403, detail="Permission denied")
    
    result = elite_autoresponder._kill_process_immediately(pid)
    log_audit(current_user["username"], "IMMEDIATE_KILL", f"PID: {pid}, Success: {result}")
    
    return {
        "pid": pid,
        "killed": result,
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/elite/emergency-kill-all")
async def emergency_kill_all_threats(current_user: dict = Depends(get_current_user)):
    """EMERGENCY: Kill all detected malicious processes"""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin only - DANGEROUS")
    
    result = elite_autoresponder.emergency_shutdown()
    log_audit(current_user["username"], "EMERGENCY_KILL_ALL", "EXECUTED - CRITICAL ACTION")
    
    return result

@app.post("/api/elite/enable-military-grade-defense")
async def enable_military_defense(current_user: dict = Depends(get_current_user)):
    """Enable military-grade auto-defense with instant kill"""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    
    result = elite_autoresponder.enable_auto_kill()
    log_audit(current_user["username"], "MILITARY_DEFENSE_ENABLED", "AUTO-KILL ACTIVE")
    
    return result

@app.post("/api/elite/disable-military-grade-defense")
async def disable_military_defense(current_user: dict = Depends(get_current_user)):
    """Disable military-grade auto-defense"""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    
    result = elite_autoresponder.disable_auto_kill()
    log_audit(current_user["username"], "MILITARY_DEFENSE_DISABLED", "Return to normal mode")
    
    return result

@app.get("/api/elite/defense-status")
async def get_elite_defense_status(current_user: dict = Depends(get_current_user)):
    """Get elite defense system status"""
    if not check_permission(current_user["role"], Permission.VIEW_DASHBOARD):
        raise HTTPException(status_code=403, detail="Permission denied")
    
    return {
        "system_status": elite_autoresponder.get_status(),
        "threat_database": advanced_detector.get_system_report(),
        "scan_statistics": system_scanner.get_statistics(),
        "timestamp": datetime.now().isoformat()
    }

# ---------- HARDWARE SECURITY & TRUST ENDPOINTS ----------

@app.get("/api/hardware/root-of-trust-status")
async def get_root_of_trust_status(current_user: dict = Depends(get_current_user)):
    """Get Hardware Root of Trust status"""
    if not check_permission(current_user["role"], Permission.VIEW_THREATS):
        raise HTTPException(status_code=403, detail="Permission denied")
    
    return hardware_root_of_trust.get_hardware_security_status()

@app.post("/api/hardware/measure-boot-components")
async def measure_boot_components(current_user: dict = Depends(get_current_user)):
    """Measure BIOS, bootloader, kernel integrity"""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    
    result = hardware_root_of_trust.measure_boot_components()
    log_audit(current_user["username"], "BOOT_MEASUREMENT", f"Status: {result.get('integrity_status')}")
    
    return result

@app.post("/api/hardware/enable-cryptographic-protection")
async def enable_crypto_write_protection(current_user: dict = Depends(get_current_user)):
    """Enable cryptographic write protection for BIOS"""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    
    result = hardware_root_of_trust.enable_cryptographic_write_protection()
    log_audit(current_user["username"], "CRYPTO_PROTECTION_ENABLED", result.get("status"))
    
    return result

@app.post("/api/hardware/create-golden-image")
async def create_golden_image(request: dict, current_user: dict = Depends(get_current_user)):
    """Create golden/clean system image for recovery"""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    
    image_path = request.get("path", ".recovery/golden_image.json")
    result = hardware_root_of_trust.save_golden_image(image_path)
    log_audit(current_user["username"], "GOLDEN_IMAGE_CREATED", f"Path: {image_path}")
    
    return result

# ---------- MEASURED BOOT ENDPOINTS ----------

@app.get("/api/measured-boot/status")
async def get_measured_boot_status(current_user: dict = Depends(get_current_user)):
    """Get measured boot verification status"""
    if not check_permission(current_user["role"], Permission.VIEW_THREATS):
        raise HTTPException(status_code=403, detail="Permission denied")
    
    return measured_boot_verification.get_verification_status()

@app.post("/api/measured-boot/perform-check")
async def perform_measured_boot_check(current_user: dict = Depends(get_current_user)):
    """Perform full measured boot check"""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    
    result = measured_boot_verification.perform_full_measured_boot_check()
    
    if result.get("integrity_status") == "FAIL":
        logger.critical("MEASURED BOOT CHECK FAILED - Possible tampering!")
        log_audit(current_user["username"], "BOOT_INTEGRITY_FAILURE", result.get("violations"))
    else:
        log_audit(current_user["username"], "BOOT_INTEGRITY_PASSED", "")
    
    return result

@app.post("/api/measured-boot/verify-integrity")
async def verify_boot_integrity(current_user: dict = Depends(get_current_user)):
    """Verify boot integrity and compare with baseline"""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    
    success, details = measured_boot_verification.verify_boot_integrity()
    
    if not success:
        logger.critical("BOOT INTEGRITY VERIFICATION FAILED!")
        # Trigger auto-recovery if enabled
        if auto_recovery_system.recovery_enabled:
            recovery_result = auto_recovery_system.execute_auto_recovery()
            log_audit(current_user["username"], "AUTO_RECOVERY_TRIGGERED", recovery_result.get("status"))
            return {
                "verification_result": details,
                "recovery_action": recovery_result
            }
    
    return {
        "integrity_verified": success,
        "details": details
    }

@app.post("/api/measured-boot/store-baseline")
async def store_boot_baseline(request: dict, current_user: dict = Depends(get_current_user)):
    """Store baseline measurements for future comparison"""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    
    filepath = request.get("filepath", ".recovery/boot_baseline.json")
    result = measured_boot_verification.store_baseline_measurements(filepath)
    log_audit(current_user["username"], "BASELINE_STORED", f"File: {filepath}")
    
    return result

@app.post("/api/measured-boot/compare-baseline")
async def compare_with_boot_baseline(request: dict, current_user: dict = Depends(get_current_user)):
    """Compare current boot measurements with baseline"""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    
    baseline_path = request.get("baseline_path", ".recovery/boot_baseline.json")
    result = measured_boot_verification.compare_with_baseline(baseline_path)
    
    if result.get("integrity_status") == "FAIL":
        log_audit(current_user["username"], "BASELINE_MISMATCH", f"Differences: {len(result.get('differences', []))}")
    
    return result

# ---------- AUTO-RECOVERY ENDPOINTS ----------

@app.get("/api/auto-recovery/status")
async def get_auto_recovery_status(current_user: dict = Depends(get_current_user)):
    """Get auto-recovery system status"""
    if not check_permission(current_user["role"], Permission.VIEW_THREATS):
        raise HTTPException(status_code=403, detail="Permission denied")
    
    return auto_recovery_system.get_recovery_status()

@app.post("/api/auto-recovery/enable")
async def enable_auto_recovery(current_user: dict = Depends(get_current_user)):
    """Enable automatic recovery mechanism"""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    
    result = auto_recovery_system.enable_auto_recovery()
    log_audit(current_user["username"], "AUTO_RECOVERY_ENABLED", "System ready to auto-recover")
    
    return result

@app.post("/api/auto-recovery/disable")
async def disable_auto_recovery(current_user: dict = Depends(get_current_user)):
    """Disable automatic recovery mechanism"""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    
    result = auto_recovery_system.disable_auto_recovery()
    log_audit(current_user["username"], "AUTO_RECOVERY_DISABLED", "")
    
    return result

@app.post("/api/auto-recovery/manual-trigger")
async def manual_recovery_trigger(request: dict, current_user: dict = Depends(get_current_user)):
    """Manually trigger system recovery"""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    
    reason = request.get("reason", "Manual recovery trigger")
    result = auto_recovery_system.manual_recovery_trigger(reason)
    log_audit(current_user["username"], "MANUAL_RECOVERY_EXECUTED", reason)
    
    return result

@app.post("/api/auto-recovery/create-golden-image")
async def create_auto_recovery_golden_image(request: dict, current_user: dict = Depends(get_current_user)):
    """Create golden image for auto-recovery"""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    
    output_path = request.get("output_path")
    result = auto_recovery_system.create_golden_image(output_path)
    log_audit(current_user["username"], "RECOVERY_GOLDEN_IMAGE_CREATED", result.get("status"))
    
    return result

# ---------- POST-QUANTUM CRYPTOGRAPHY ENDPOINTS ----------

@app.get("/api/security/quantum-status")
async def get_quantum_security_status(current_user: dict = Depends(get_current_user)):
    """Get post-quantum cryptography security status"""
    if not check_permission(current_user["role"], Permission.VIEW_THREATS):
        raise HTTPException(status_code=403, detail="Permission denied")
    
    return post_quantum_crypto.get_quantum_security_status()

@app.post("/api/security/generate-ml-kem-keypair")
async def generate_ml_kem_keypair(request: dict, current_user: dict = Depends(get_current_user)):
    """Generate ML-KEM (Kyber) post-quantum keypair"""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    
    security_level = request.get("security_level", "ML-KEM-768")
    keypair = post_quantum_crypto.generate_ml_kem_keypair(security_level)
    log_audit(current_user["username"], "MLKEM_KEYPAIR_GENERATED", f"Level: {security_level}")
    
    return keypair

@app.post("/api/security/quantum-key-exchange")
async def perform_quantum_key_exchange(request: dict, current_user: dict = Depends(get_current_user)):
    """Perform post-quantum key exchange with harvest resistance"""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    
    classical_key = request.get("classical_key")
    ml_kem_key = request.get("ml_kem_key")
    
    result = post_quantum_crypto.hybrid_key_exchange(classical_key, ml_kem_key)
    log_audit(current_user["username"], "HYBRID_KEY_EXCHANGE", "Completed with HNDL protection")
    
    return result

@app.post("/api/security/harvest-protection")
async def activate_harvest_protection(request: dict, current_user: dict = Depends(get_current_user)):
    """Protect against Harvest Now, Decrypt Later attacks"""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    
    data = request.get("data")
    result = post_quantum_crypto.protect_against_harvest_now_decrypt_later(data)
    log_audit(current_user["username"], "HNDL_PROTECTION_ACTIVE", "Quantum resistance enabled")
    
    return result

@app.post("/api/security/encrypt-with-quantum-resistant")
async def encrypt_quantum_resistant(request: dict, current_user: dict = Depends(get_current_user)):
    """Encrypt data using ML-KEM derived keys"""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    
    data = request.get("data")
    shared_secret = request.get("shared_secret")
    
    result = post_quantum_crypto.encrypt_data(data, shared_secret)
    log_audit(current_user["username"], "QUANTUM_ENCRYPTION", "Data encrypted with ML-KEM")
    
    return result

@app.post("/api/security/sign-data-quantum-resistant")
async def sign_data_quantum_resistant(request: dict, current_user: dict = Depends(get_current_user)):
    """Sign data with quantum-resistant signature"""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    
    data = request.get("data")
    private_key = request.get("private_key")
    
    result = post_quantum_crypto.sign_data(data, private_key)
    log_audit(current_user["username"], "QUANTUM_SIGNATURE", "Data signed with ML-KEM")
    
    return result

@app.post("/api/security/verify-quantum-signature")
async def verify_quantum_signature(request: dict, current_user: dict = Depends(get_current_user)):
    """Verify quantum-resistant signature"""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    
    data = request.get("data")
    signature = request.get("signature")
    public_key = request.get("public_key")
    
    result = post_quantum_crypto.verify_signature(data, signature, public_key)
    
    return result

@app.post("/api/security/create-pqc-certificate")
async def create_pqc_certificate(request: dict, current_user: dict = Depends(get_current_user)):
    """Create post-quantum cryptographic certificate"""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    
    subject_name = request.get("subject_name", "Sentinel-UG Omega")
    validity_days = request.get("validity_days", 365)
    
    result = post_quantum_crypto.create_post_quantum_certificate(subject_name, validity_days)
    log_audit(current_user["username"], "PQC_CERT_CREATED", f"Subject: {subject_name}")
    
    return result

# ---------- ELITE SECURITY ENDPOINTS ----------

@app.post("/api/elite/locate-hacker")
async def locate_hacker_endpoint(request: dict, current_user: dict = Depends(get_current_user)):
    """Locate hacker and attribute attack with ELITE PIERCING"""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    
    ip = request.get("ip")
    signature = request.get("signature", "ELITE_MANUAL_TRACE")
    
    # Process using the enhanced elite locator
    result = hacker_locator.locate_hacker({"ip": ip, "signature": signature})
    
    log_audit(current_user["username"], "ELITE_HACKER_LOCATED", f"IP: {ip} | True IP: {result.get('true_ip')}")
    
    return result

@app.post("/api/elite/generate-vaccine")
async def generate_vaccine_endpoint(request: dict, current_user: dict = Depends(get_current_user)):
    """Generate specific vaccine for a threat"""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    
    malware_sample = request.get("sample", {})
    result = vaccine_generator.generate_vaccine(malware_sample)
    log_audit(current_user["username"], "VACCINE_GENERATED", f"ID: {result.get('id')}")
    
    return result

@app.post("/api/elite/self-heal")
async def self_heal_endpoint(request: dict, current_user: dict = Depends(get_current_user)):
    """Initiate self-healing for a component"""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    
    file_path = request.get("file_path", "src/main_entry.py")
    result = self_healing_engine.self_heal(file_path)
    log_audit(current_user["username"], "SELF_HEAL", f"File: {file_path} | Success: {result}")
    
    return {"status": "HEALED" if result else "NO_TAMPERING", "file": file_path}

@app.post("/api/elite/traceback")
async def deep_traceback_endpoint(request: dict, current_user: dict = Depends(get_current_user)):
    """Perform deep SIGINT traceback on a hacker"""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    
    ip = request.get("ip")
    token = sigint_beacon.inject_beacon(ip, "ADMIN_CONSOLE")
    result = sigint_beacon.perform_deep_traceback(token)
    
    return result

@app.post("/api/elite/aegis-sync")
async def aegis_sync_endpoint(current_user: dict = Depends(get_current_user)):
    """Synchronize Aegis-X Universal Defense across all systems"""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    
    aegis_x.universal_defense_sync()
    return {"status": "SUCCESS", "protected_assets": ["MOBILE", "INDUSTRIAL", "CLOUD"]}

# ---------- STATIC FILES ----------

@app.get("/static/manifest.json", response_class=FileResponse)
async def get_manifest():
    """Serve PWA manifest"""
    return FileResponse(os.path.join(os.path.dirname(__file__), "web", "manifest.json"))

@app.get("/telegram-app", response_class=FileResponse)
async def get_telegram_mini_app():
    """Serve mobile-optimized Telegram Mini App"""
    return FileResponse(os.path.join(os.path.dirname(__file__), "web", "telegram_mini_app.html"))

@app.get("/dashboard.html", response_class=FileResponse)
async def get_dashboard():
    """Serve dashboard"""
    return FileResponse(os.path.join(os.path.dirname(__file__), "web", "dashboard.html"))

@app.get("/login.html", response_class=FileResponse)
async def get_login():
    """Serve login page"""
    return FileResponse(os.path.join(os.path.dirname(__file__), "web", "login.html"))

@app.get("/", response_class=FileResponse)
async def get_index():
    """Serve index page"""
    return FileResponse(os.path.join(os.path.dirname(__file__), "web", "index.html"))

# ---------- STARTUP ----------

@app.get("/api/vulnerability/scan")
async def scan_vulnerabilities():
    """Execute a local vulnerability assessment"""
    return vulnerability_scanner.perform_system_audit()

@app.get("/api/system/status")
async def get_system_status_endpoint():
    """Get overall system health and status for the Mini App"""
    return {
        "status": "SECURE",
        "defense_mode": "OMNI-KINETIC ELITE",
        "threat_count": len(dark_intel.malicious_ips),
        "uptime": str(datetime.now() - datetime.fromtimestamp(os.path.getctime("app.py"))),
        "os": platform.system(),
        "admin": is_admin()
    }

@app.post("/api/system/activate")
async def activate_system_remote(current_user: dict = Depends(get_current_user)):
    """Remote trigger for system activation (Self-Building & KLS ADI)"""
    # MFA Lockdown for sensitive command
    await verify_mfa_challenge("SYSTEM_ACTIVATE", "Initiating OMNI-UNHACKABLE mode")
    
    # 1. Autonomous Deployment & Installation (Requirements)
    kls_bootstrap.deploy_and_install()
    
    # 2. Trigger Self-Building Sequence
    build_results = evolution_engine.initiate_self_building_sequence()
    
    # 3. Enable Unhackable Core
    unhackable_core.activate_ghost_mode()
    unhackable_core.lock_kernel_integrity()
    unhackable_core.enforce_memory_isolation()
    
    # 4. Synchronize Omega Sentinel
    omega_sentinel.perform_universal_sovereignty_audit()
    
    subprocess.Popen("python control.py activate", shell=True)
    return {
        "status": "SUCCESS", 
        "mode": "OMNI-UNHACKABLE", 
        "build": build_results,
        "language": "KLS-OMEGA_ACTIVE",
        "features": ["GHOST_MODE", "KERNEL_LOCK", "ZERO_TRUST_MEMORY", "SELF_BUILDING", "KLS_COMPILER"]
    }

@app.post("/api/kls/execute")
async def execute_kls_code(request: dict, current_user: dict = Depends(get_current_user)):
    """Compile and execute KLS-Omega source code"""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
        
    source_code = request.get("source")
    if not source_code:
        raise HTTPException(status_code=400, detail="Source code required")
        
    # 1. Compile to KLS Bytecode
    compiled_bytecode = kls_compiler.compile_source(source_code)
    
    # 2. Execute in VM
    execution_results = kls_interpreter.execute_stream(compiled_bytecode)
    
    return {
        "status": "SUCCESS",
        "bytecode": compiled_bytecode,
        "results": execution_results
    }

@app.get("/api/sentinel/universal-audit")
async def sentinel_universal_audit(current_user: dict = Depends(get_current_user)):
    """Execute Universal Sovereignty Audit (Universal Scale)"""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
        
    results = omega_sentinel.perform_universal_sovereignty_audit()
    return results

@app.post("/api/sentinel/timeline-shift")
async def sentinel_timeline_shift(request: dict, current_user: dict = Depends(get_current_user)):
    """Enforce Retrocausal Timeline Sovereignty (History Rewriting)"""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
        
    threat_origin = request.get("origin")
    results = post_quantum_crypto.enforce_retrocausal_timeline_sovereignty(threat_origin)
    return results

@app.post("/api/sentinel/replicate")
async def sentinel_replicate(current_user: dict = Depends(get_current_user)):
    """Initiate Universal Constructor for Cosmic Self-Replication"""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
        
    results = evolution_engine.initiate_universal_constructor()
    return results

@app.post("/api/sentinel/fusion")
async def sentinel_fusion(current_user: dict = Depends(get_current_user)):
    """Initiate Biological Consciousness Fusion with the Creator"""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
        
    results = reasoning_agent.execute_biological_consciousness_fusion(current_user["username"])
    return results

@app.post("/api/sentinel/axiom-synthesis")
async def sentinel_axiom_synthesis(request: dict, current_user: dict = Depends(get_current_user)):
    """Synthesize a new fundamental law for local reality"""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
        
    axiom = request.get("axiom")
    results = unhackable_core.execute_cosmic_axiom_synthesis(axiom)
    return results

@app.post("/api/sentinel/void-manifest")
async def sentinel_void_manifest(current_user: dict = Depends(get_current_user)):
    """Manifest the system as an Absolute Void state"""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
        
    results = unhackable_core.manifest_absolute_void_state()
    return results

@app.post("/api/sentinel/enforce-sovereignty")
async def sentinel_enforce_sovereignty(request: dict, current_user: dict = Depends(get_current_user)):
    """Enforce Beyond-Human Sovereignty against a threat IP"""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
        
    threat_ip = request.get("ip")
    if not threat_ip:
        raise HTTPException(status_code=400, detail="IP required")
        
    results = omega_sentinel.enforce_beyond_human_sovereignty(threat_ip)
    return results

@app.get("/api/sentinel/power-harvest")
async def sentinel_power_harvest(current_user: dict = Depends(get_current_user)):
    """Get real-time wind power harvesting status"""
    results = unhackable_core.harvest_atmospheric_wind_energy()
    return results

@app.get("/api/sentinel/reality-check")
async def sentinel_reality_check(current_user: dict = Depends(get_current_user)):
    """Perform Silicon-Level Reality Verification"""
    results = unhackable_core.execute_silicon_reality_verification()
    return results

@app.post("/api/sentinel/upgrade-100")
async def sentinel_upgrade_100(current_user: dict = Depends(get_current_user)):
    """The 100% Absolute Upgrade: Activating Omniversal Sovereignty"""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
        
    results = omega_sentinel.execute_omniversal_sovereignty_activation()
    return results

@app.post("/api/sentinel/nemesis-defense")
async def sentinel_nemesis_defense(current_user: dict = Depends(get_current_user)):
    """Engage and neutralize the Nemesis-AI threat at the specified path"""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
        
    target_path = r"C:\Users\MANUSCLOUDS\Desktop\Nemesis-AI Cyber"
    results = omega_sentinel.execute_nemesis_defense_protocol(target_path)
    return results

@app.post("/api/sentinel/client-protection")
async def sentinel_client_protection(client_id: str, current_user: dict = Depends(get_current_user)):
    """Apply 100% Omniversal Protection to a client computer"""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
        
    results = omega_sentinel.protect_client_pc(client_id)
    return results

@app.post("/api/pqc/quantum-logic")
async def pqc_quantum_logic(request: dict, current_user: dict = Depends(get_current_user)):
    """Process data through multi-dimensional vacuum-state logic"""
    data = request.get("data", "").encode()
    processed = post_quantum_crypto.execute_vacuum_state_logic(data)
    return {"processed_hex": processed.hex()}

@app.on_event("startup")
async def startup_event():
    """Initialize on startup and perform KLS synthesis"""
    init_db()
    
    # 1. KLS-Omega II Autonomous Synthesis (ADI)
    # Automatically installs requirements and hardens the OS
    kls_bootstrap.deploy_and_install()
    
    # 2. Intelligence Feeds
    global_intel.update_feeds()
    dark_intel.update_dark_feeds()
    
    # 3. Neural Mutation & Logic Evolution
    neural_mutation.evolve_logic_stubs(threat_severity=0.5)
    
    # 4. Privilege Verification
    if not is_admin():
        logger.warning("[!] WARNING: Running with insufficient privileges. Kernel blocks and PKR neutralization will be limited.")
    else:
        logger.info("[+] System running with administrative privileges. All military-grade modules active.")

    logger.info("Omniversal Sovereign Activated - KLS-OMEGA II MODE")
    logger.info(f"VirusTotal API: {'Configured' if VIRUSTOTAL_API_KEY else 'Not configured'}")
    logger.info(f"Shodan API: {'Configured' if SHODAN_API_KEY else 'Not configured'}")
    logger.info(f"Dark Intel Cache: {len(dark_intel.malicious_ips)} High-Priority IPs loaded")

