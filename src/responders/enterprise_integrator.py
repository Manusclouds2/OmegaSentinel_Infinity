"""
ENTERPRISE INTEGRATION MODULE (AD/LDAP)
- Automate threat response at the Domain level
- Disable compromised user accounts in Active Directory
- Move infected computer objects to Quarantine GPOs
"""

import os
import logging
from typing import Dict, List, Optional

try:
    import ldap3
    from ldap3 import Server, Connection, ALL, MODIFY_REPLACE
    LDAP_AVAILABLE = True
except ImportError:
    LDAP_AVAILABLE = False

logger = logging.getLogger(__name__)

class EnterpriseIntegrator:
    """Enterprise-level threat response via AD/LDAP"""
    
    def __init__(self):
        self.server_uri = os.environ.get("AD_SERVER", "ldap://domain-controller.local")
        self.admin_user = os.environ.get("AD_ADMIN_USER", "CN=Admin,CN=Users,DC=domain,DC=local")
        self.admin_pass = os.environ.get("AD_ADMIN_PASS", "")
        self.is_enabled = LDAP_AVAILABLE and bool(self.admin_pass)

    def disable_user_account(self, username: str) -> Dict:
        """Automate: Disable a compromised user account in AD"""
        if not self.is_enabled:
            return {"status": "error", "message": "AD Integration not configured"}
            
        logger.critical(f"[AD_RESPONSE] INITIATING ACCOUNT LOCKDOWN: {username}")
        
        try:
            server = Server(self.server_uri, get_info=ALL)
            conn = Connection(server, user=self.admin_user, password=self.admin_pass, auto_bind=True)
            
            # Find the user's Distinguished Name (DN)
            search_filter = f"(&(objectClass=user)(sAMAccountName={username}))"
            conn.search("DC=domain,DC=local", search_filter, attributes=['distinguishedName', 'userAccountControl'])
            
            if not conn.entries:
                return {"status": "error", "message": f"User {username} not found"}
                
            user_dn = conn.entries[0].distinguishedName.value
            current_uac = conn.entries[0].userAccountControl.value
            
            # 2 = ACCOUNTDISABLE
            new_uac = current_uac | 2
            
            conn.modify(user_dn, {'userAccountControl': [(MODIFY_REPLACE, [new_uac])]})
            
            logger.info(f"[+] User {username} has been DISABLED in Active Directory.")
            return {"status": "SUCCESS", "action": "ACCOUNT_DISABLED", "user": username}
            
        except Exception as e:
            logger.error(f"AD account disable failed: {e}")
            return {"status": "ERROR", "message": str(e)}

    def quarantine_computer_object(self, computer_name: str) -> Dict:
        """Automate: Move infected computer to a Quarantine OU/GPO"""
        if not self.is_enabled:
            return {"status": "error", "message": "AD Integration not configured"}
            
        logger.critical(f"[AD_RESPONSE] ISOLATING COMPUTER OBJECT: {computer_name}")
        
        try:
            server = Server(self.server_uri, get_info=ALL)
            conn = Connection(server, user=self.admin_user, password=self.admin_pass, auto_bind=True)
            
            # Target Quarantine OU
            quarantine_ou = "OU=Quarantine,DC=domain,DC=local"
            
            # Find computer object
            search_filter = f"(&(objectClass=computer)(cn={computer_name}))"
            conn.search("DC=domain,DC=local", search_filter, attributes=['distinguishedName'])
            
            if not conn.entries:
                return {"status": "error", "message": f"Computer {computer_name} not found"}
                
            computer_dn = conn.entries[0].distinguishedName.value
            
            # Move object to Quarantine OU
            conn.modify_dn(computer_dn, f"CN={computer_name}", new_superior=quarantine_ou)
            
            logger.info(f"[+] Computer {computer_name} moved to {quarantine_ou} for isolation.")
            return {"status": "SUCCESS", "action": "COMPUTER_QUARANTINED", "target": computer_name}
            
        except Exception as e:
            logger.error(f"AD computer quarantine failed: {e}")
            return {"status": "ERROR", "message": str(e)}

enterprise_integrator = EnterpriseIntegrator()
