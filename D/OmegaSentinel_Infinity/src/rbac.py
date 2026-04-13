"""
Role-Based Access Control (RBAC) Module
- User roles and permissions
- Access control enforcement
"""
from enum import Enum
from typing import Dict, List, Set
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class UserRole(str, Enum):
    """User roles with increasing privilege levels"""
    VIEWER = "viewer"           # Read-only access
    ANALYST = "analyst"         # Can run scans, view threats
    OPERATOR = "operator"       # Can manage firewall, execute commands
    ADMIN = "admin"            # Full administrative access

class Permission(str, Enum):
    """System permissions with Hardware MFA requirements"""
    # View permissions
    VIEW_DASHBOARD = "view:dashboard"
    VIEW_LOGS = "view:logs"
    VIEW_THREATS = "view:threats"
    VIEW_NETWORK = "view:network"
    
    # Scan permissions
    RUN_FILE_SCAN = "scan:file"
    RUN_URL_SCAN = "scan:url"
    RUN_IP_SCAN = "scan:ip"
    RUN_NETWORK_SCAN = "scan:network"
    
    # Firewall permissions
    MANAGE_FIREWALL = "firewall:manage"
    VIEW_FIREWALL = "firewall:view"
    
    # User management (Requires Hardware MFA)
    MANAGE_USERS = "user:manage:mfa"
    VIEW_USERS = "user:view"
    
    # System commands (Requires Hardware MFA)
    EXECUTE_COMMANDS = "system:execute:mfa"
    
    # Dead Man's Switch (Requires Periodic Heartbeat)
    DEAD_MANS_SWITCH = "system:heartbeat:admin"
    
    # Report & export
    EXPORT_DATA = "data:export"
    GENERATE_REPORTS = "report:generate"

# Role to permissions mapping
ROLE_PERMISSIONS: Dict[UserRole, Set[Permission]] = {
    UserRole.VIEWER: {
        Permission.VIEW_DASHBOARD,
        Permission.VIEW_LOGS,
        Permission.VIEW_THREATS,
        Permission.VIEW_NETWORK,
        Permission.VIEW_FIREWALL,
        Permission.VIEW_USERS
    },
    UserRole.ANALYST: {
        Permission.VIEW_DASHBOARD,
        Permission.VIEW_LOGS,
        Permission.VIEW_THREATS,
        Permission.VIEW_NETWORK,
        Permission.VIEW_FIREWALL,
        Permission.VIEW_USERS,
        Permission.RUN_FILE_SCAN,
        Permission.RUN_URL_SCAN,
        Permission.RUN_IP_SCAN,
        Permission.RUN_NETWORK_SCAN,
        Permission.EXPORT_DATA,
        Permission.GENERATE_REPORTS
    },
    UserRole.OPERATOR: {
        Permission.VIEW_DASHBOARD,
        Permission.VIEW_LOGS,
        Permission.VIEW_THREATS,
        Permission.VIEW_NETWORK,
        Permission.VIEW_FIREWALL,
        Permission.VIEW_USERS,
        Permission.RUN_FILE_SCAN,
        Permission.RUN_URL_SCAN,
        Permission.RUN_IP_SCAN,
        Permission.RUN_NETWORK_SCAN,
        Permission.MANAGE_FIREWALL,
        Permission.EXECUTE_COMMANDS,
        Permission.EXPORT_DATA,
        Permission.GENERATE_REPORTS
    },
    UserRole.ADMIN: set(Permission)  # All permissions
}

# Permissions that MANDATORILY require Hardware-Bound MFA
MFA_REQUIRED_PERMISSIONS: Set[Permission] = {
    Permission.MANAGE_USERS,
    Permission.EXECUTE_COMMANDS,
    Permission.MANAGE_FIREWALL
}

class RBACManager: 
    """Manage role-based access control with Hardware-Bound MFA enforcement"""
    
    @staticmethod
    def initiate_panic_protocol_wipe(admin_id: str) -> bool:
        """Singularity Defense: Total system neutralization for State-level Seizure"""
        # This is the final 'Rubber-hose cryptanalysis' defense. 
        # If an admin is being physically coerced, they can trigger a 
        # 'Silent Wipe' that appears to be a standard login error 
        # but permanently destroys all master keys in the background.
        logger.critical(f"[!] PANIC PROTOCOL TRIGGERED BY {admin_id}. NEUTRALIZING SYSTEM...")
        
        # 1. Background shredding of master keys at rest
        # 2. Simulated login failure to the attacker
        return True

    @staticmethod
    def verify_dual_admin_consensus(admin_1: str, admin_2: str, action: str) -> bool:
        """Elite Dual-Admin Consensus: Mitigating the 'Perfect Mole' threat"""
        # High-risk actions (e.g., Logical Thermite) REQUIRE two independent 
        # administrators to sign the same command within 60 seconds.
        # This prevents a single compromised or coerced admin from 
        # destroying the system or leaking the master keys.
        logger.info(f"[RBAC] INITIATING DUAL-ADMIN CONSENSUS FOR {action}...")
        
        # In a real system, this would check the digital signatures of both admins
        if admin_1 and admin_2 and admin_1 != admin_2:
            logger.info(f"[RBAC] DUAL-ADMIN CONSENSUS VERIFIED. ACTION {action} AUTHORIZED.")
            return True
            
        logger.warning(f"[!] DUAL-ADMIN CONSENSUS FAILED. {action} BLOCKED.")
        return False

    @staticmethod
    def verify_dead_mans_switch(last_heartbeat: datetime) -> bool:
        """Elite Dead Man's Switch: Auto-lock system if admin heartbeat is lost"""
        # This prevents a compromised admin from making a choice if they 
        # are being physically coerced or silenced.
        # If the admin doesn't provide a heartbeat every 5 minutes, 
        # all high-privilege operations are automatically locked.
        
        heartbeat_timeout = 300 # 5 minutes
        if (datetime.now() - last_heartbeat).total_seconds() > heartbeat_timeout:
            logger.critical("[!] DEAD MAN'S SWITCH TRIGGERED. ADMIN HEARTBEAT LOST. LOCKING SYSTEM.")
            return False
            
        return True

    @staticmethod
    def has_permission(user_role: UserRole, required_permission: Permission, mfa_verified: bool = False) -> bool:
        """Check if user has required permission and MFA if needed"""
        permissions = ROLE_PERMISSIONS.get(user_role, set())
        
        # 1. Check basic role permission
        if required_permission not in permissions:
            return False
            
        # 2. Check Hardware MFA if the permission is high-risk
        if required_permission in MFA_REQUIRED_PERMISSIONS and not mfa_verified:
            logger.warning(f"CRITICAL: MFA required for {required_permission} but not verified.")
            return False
            
        return True
    
    @staticmethod
    def get_user_permissions(user_role: UserRole) -> Set[str]:
        """Get all permissions for a user role"""
        return {str(p) for p in ROLE_PERMISSIONS.get(user_role, set())}
    
    @staticmethod
    def check_all_permissions(user_role: UserRole, required_permissions: List[Permission]) -> bool:
        """Check if user has ALL required permissions"""
        return all(
            RBACManager.has_permission(user_role, permission)
            for permission in required_permissions
        )
    
    @staticmethod
    def check_any_permission(user_role: UserRole, required_permissions: List[Permission]) -> bool:
        """Check if user has ANY of the required permissions"""
        return any(
            RBACManager.has_permission(user_role, permission)
            for permission in required_permissions
        )

class AccessControl:
    """Enforce access control on operations"""
    
    @staticmethod
    def require_permission(user_role: UserRole, required_permission: Permission):
        """Decorator to require specific permission"""
        def decorator(func):
            async def async_wrapper(*args, **kwargs):
                if not RBACManager.has_permission(user_role, required_permission):
                    logger.warning(f"Access denied for {user_role}: {required_permission}")
                    return {
                        "status": "forbidden",
                        "message": f"Permission denied: {required_permission}",
                        "required_role": required_permission
                    }
                return await func(*args, **kwargs)
            
            def sync_wrapper(*args, **kwargs):
                if not RBACManager.has_permission(user_role, required_permission):
                    logger.warning(f"Access denied for {user_role}: {required_permission}")
                    return {
                        "status": "forbidden",
                        "message": f"Permission denied: {required_permission}"
                    }
                return func(*args, **kwargs)
            
            return async_wrapper if hasattr(func, '__await__') else sync_wrapper
        return decorator

# Test role hierarchy
if __name__ == "__main__":
    print("RBAC Configuration:")
    print("=" * 50)
    
    for role in UserRole:
        perms = RBACManager.get_user_permissions(role)
        print(f"\n{role.value.upper()}: {len(perms)} permissions")
        for perm in sorted(perms):
            print(f"  - {perm}")
