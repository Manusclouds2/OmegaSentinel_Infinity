"""
CLOUD NATIVE SECURITY (AWS/AZURE/GCP)
- Automated cloud infrastructure isolation
- Modify Security Groups and Network ACLs upon threat detection
- Support for AWS Boto3 and Azure/GCP APIs
"""

import os
import logging
from typing import Dict, List, Optional

try:
    import boto3
    AWS_AVAILABLE = True
except ImportError:
    AWS_AVAILABLE = False

logger = logging.getLogger(__name__)

class CloudProtector:
    """Automated security enforcement for cloud-native infrastructure"""
    
    def __init__(self):
        self.aws_access_key = os.environ.get("AWS_ACCESS_KEY_ID")
        self.aws_secret_key = os.environ.get("AWS_SECRET_ACCESS_KEY")
        self.aws_region = os.environ.get("AWS_REGION", "us-east-1")
        self.is_enabled = AWS_AVAILABLE and bool(self.aws_access_key)

    def isolate_ec2_instance(self, instance_id: str) -> Dict:
        """Automate: Revoke all inbound/outbound rules for a compromised instance"""
        if not self.is_enabled:
            return {"status": "error", "message": "AWS Boto3 not configured"}
            
        logger.critical(f"[CLOUD_RESPONSE] ISOLATING COMPROMISED AWS EC2 INSTANCE: {instance_id}")
        
        try:
            ec2 = boto3.resource('ec2', region_name=self.aws_region)
            instance = ec2.Instance(instance_id)
            
            # Find associated Security Groups
            sg_ids = [sg['GroupId'] for sg in instance.security_groups]
            
            # For each SG, revoke all ingress and egress
            for sg_id in sg_ids:
                sg = ec2.SecurityGroup(sg_id)
                
                # Revoke all ingress
                if sg.ip_permissions:
                    sg.revoke_ingress(IpPermissions=sg.ip_permissions)
                    
                # Revoke all egress
                if sg.ip_permissions_egress:
                    sg.revoke_egress(IpPermissions=sg.ip_permissions_egress)
            
            # 2. Add an "Isolator" Security Group with Deny-All (or just no rules)
            # sg.authorize_ingress(...) could allow only management IP if needed
            
            logger.info(f"[+] AWS EC2 {instance_id} isolated. All Security Group rules revoked.")
            return {"status": "SUCCESS", "action": "EC2_ISOLATED", "id": instance_id}
            
        except Exception as e:
            logger.error(f"AWS EC2 isolation failed: {e}")
            return {"status": "ERROR", "message": str(e)}

    def quarantine_cloud_identity(self, iam_user: str) -> Dict:
        """Automate: Revoke all IAM policies for a compromised cloud user"""
        if not self.is_enabled:
            return {"status": "error", "message": "AWS IAM Integration not configured"}
            
        logger.critical(f"[CLOUD_RESPONSE] REVOKING PERMISSIONS FOR COMPROMISED IAM USER: {iam_user}")
        
        try:
            iam = boto3.client('iam', region_name=self.aws_region)
            
            # 1. Attach Deny-All Policy
            policy_arn = "arn:aws:iam::aws:policy/AWSDenyAll"
            iam.attach_user_policy(UserName=iam_user, PolicyArn=policy_arn)
            
            # 2. Deactivate Access Keys
            response = iam.list_access_keys(UserName=iam_user)
            for key in response.get('AccessKeyMetadata', []):
                iam.update_access_key(UserName=iam_user, AccessKeyId=key['AccessKeyId'], Status='Inactive')
                
            logger.info(f"[+] IAM User {iam_user} quarantined. All access keys deactivated.")
            return {"status": "SUCCESS", "action": "IAM_USER_QUARANTINED", "user": iam_user}
            
        except Exception as e:
            logger.error(f"AWS IAM quarantine failed: {e}")
            return {"status": "ERROR", "message": str(e)}

cloud_protector = CloudProtector()
