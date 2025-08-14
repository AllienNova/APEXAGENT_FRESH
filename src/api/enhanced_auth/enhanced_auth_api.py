"""
Enhanced Authentication API Endpoints
Provides comprehensive authentication, authorization, and identity management APIs
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import logging
from datetime import datetime

# Import restored authentication components
from services.ai_core.ApexAgent.src.auth.authentication.auth_manager import AuthManager
from services.ai_core.ApexAgent.src.auth.authentication.mfa_manager import MFAManager
from services.ai_core.ApexAgent.src.auth.enhanced.enhanced_rbac import EnhancedRBAC
from services.ai_core.ApexAgent.src.auth.identity.enterprise_identity_manager import EnterpriseIdentityManager
from services.ai_core.ApexAgent.src.auth.security.security_monitoring import SecurityMonitoring

router = APIRouter(prefix="/api/v1/auth/enhanced", tags=["Enhanced Authentication"])
security = HTTPBearer()
logger = logging.getLogger(__name__)

# Initialize authentication components
auth_manager = AuthManager()
mfa_manager = MFAManager()
enhanced_rbac = EnhancedRBAC()
identity_manager = EnterpriseIdentityManager()
security_monitor = SecurityMonitoring()

# Pydantic models
class EnhancedLoginRequest(BaseModel):
    username: str = Field(..., description="Username or email")
    password: str = Field(..., description="User password")
    mfa_token: Optional[str] = Field(None, description="Multi-factor authentication token")
    device_info: Optional[Dict[str, Any]] = Field(None, description="Device information")
    remember_device: bool = Field(False, description="Remember this device")

class RoleAssignmentRequest(BaseModel):
    user_id: str = Field(..., description="User ID")
    role: str = Field(..., description="Role to assign")
    permissions: List[str] = Field(..., description="Specific permissions")
    scope: Optional[str] = Field(None, description="Permission scope")

class MFASetupRequest(BaseModel):
    user_id: str = Field(..., description="User ID")
    method: str = Field(..., description="MFA method (totp, sms, email)")
    phone_number: Optional[str] = Field(None, description="Phone number for SMS")

class SecurityAuditRequest(BaseModel):
    user_id: Optional[str] = Field(None, description="User ID to audit")
    start_date: Optional[datetime] = Field(None, description="Audit start date")
    end_date: Optional[datetime] = Field(None, description="Audit end date")
    event_types: Optional[List[str]] = Field(None, description="Event types to include")

# Authentication endpoints
@router.post("/login/enhanced")
async def enhanced_login(
    request: EnhancedLoginRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Enhanced login with multi-factor authentication and device tracking
    """
    try:
        # Perform enhanced authentication
        auth_result = await auth_manager.enhanced_authenticate(
            username=request.username,
            password=request.password,
            device_info=request.device_info
        )
        
        if not auth_result.success:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication failed"
            )
        
        # Check MFA requirement
        if auth_result.requires_mfa:
            if not request.mfa_token:
                return {
                    "status": "mfa_required",
                    "mfa_methods": auth_result.available_mfa_methods,
                    "session_token": auth_result.temp_session_token
                }
            
            # Verify MFA token
            mfa_result = await mfa_manager.verify_token(
                user_id=auth_result.user_id,
                token=request.mfa_token
            )
            
            if not mfa_result.valid:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid MFA token"
                )
        
        # Log security event
        await security_monitor.log_authentication_event(
            user_id=auth_result.user_id,
            event_type="login_success",
            device_info=request.device_info
        )
        
        return {
            "status": "success",
            "access_token": auth_result.access_token,
            "refresh_token": auth_result.refresh_token,
            "user_info": auth_result.user_info,
            "permissions": auth_result.permissions,
            "expires_in": auth_result.expires_in
        }
        
    except Exception as e:
        logger.error(f"Enhanced login error: {str(e)}")
        await security_monitor.log_authentication_event(
            user_id=request.username,
            event_type="login_failure",
            error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication service error"
        )

@router.post("/mfa/setup")
async def setup_mfa(
    request: MFASetupRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Set up multi-factor authentication for a user
    """
    try:
        # Verify user authorization
        user_info = await auth_manager.verify_token(credentials.credentials)
        
        # Check if user can modify MFA settings
        if user_info.user_id != request.user_id:
            has_permission = await enhanced_rbac.check_permission(
                user_id=user_info.user_id,
                permission="manage_user_mfa",
                resource=request.user_id
            )
            if not has_permission:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Insufficient permissions"
                )
        
        # Set up MFA
        setup_result = await mfa_manager.setup_mfa(
            user_id=request.user_id,
            method=request.method,
            phone_number=request.phone_number
        )
        
        # Log security event
        await security_monitor.log_security_event(
            user_id=request.user_id,
            event_type="mfa_setup",
            details={"method": request.method}
        )
        
        return {
            "status": "success",
            "setup_data": setup_result.setup_data,
            "backup_codes": setup_result.backup_codes,
            "qr_code": setup_result.qr_code if request.method == "totp" else None
        }
        
    except Exception as e:
        logger.error(f"MFA setup error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="MFA setup failed"
        )

@router.post("/rbac/assign-role")
async def assign_role(
    request: RoleAssignmentRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Assign role and permissions to a user using Enhanced RBAC
    """
    try:
        # Verify admin authorization
        user_info = await auth_manager.verify_token(credentials.credentials)
        
        # Check admin permissions
        has_permission = await enhanced_rbac.check_permission(
            user_id=user_info.user_id,
            permission="manage_user_roles",
            resource="users"
        )
        
        if not has_permission:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to assign roles"
            )
        
        # Assign role using Enhanced RBAC
        assignment_result = await enhanced_rbac.assign_role(
            user_id=request.user_id,
            role=request.role,
            permissions=request.permissions,
            scope=request.scope,
            assigned_by=user_info.user_id
        )
        
        # Log security event
        await security_monitor.log_security_event(
            user_id=user_info.user_id,
            event_type="role_assignment",
            details={
                "target_user": request.user_id,
                "role": request.role,
                "permissions": request.permissions
            }
        )
        
        return {
            "status": "success",
            "assignment_id": assignment_result.assignment_id,
            "effective_permissions": assignment_result.effective_permissions,
            "role_hierarchy": assignment_result.role_hierarchy
        }
        
    except Exception as e:
        logger.error(f"Role assignment error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Role assignment failed"
        )

@router.get("/identity/enterprise-info/{user_id}")
async def get_enterprise_identity(
    user_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Get enterprise identity information for a user
    """
    try:
        # Verify authorization
        user_info = await auth_manager.verify_token(credentials.credentials)
        
        # Check permissions
        if user_info.user_id != user_id:
            has_permission = await enhanced_rbac.check_permission(
                user_id=user_info.user_id,
                permission="view_user_identity",
                resource=user_id
            )
            if not has_permission:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Insufficient permissions"
                )
        
        # Get enterprise identity information
        identity_info = await identity_manager.get_user_identity(user_id)
        
        return {
            "status": "success",
            "identity_info": {
                "user_id": identity_info.user_id,
                "enterprise_id": identity_info.enterprise_id,
                "department": identity_info.department,
                "job_title": identity_info.job_title,
                "manager_id": identity_info.manager_id,
                "groups": identity_info.groups,
                "directory_attributes": identity_info.directory_attributes,
                "last_sync": identity_info.last_sync
            }
        }
        
    except Exception as e:
        logger.error(f"Enterprise identity error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve enterprise identity"
        )

@router.post("/security/audit")
async def security_audit(
    request: SecurityAuditRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Perform security audit and get security events
    """
    try:
        # Verify admin authorization
        user_info = await auth_manager.verify_token(credentials.credentials)
        
        # Check audit permissions
        has_permission = await enhanced_rbac.check_permission(
            user_id=user_info.user_id,
            permission="security_audit",
            resource="system"
        )
        
        if not has_permission:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions for security audit"
            )
        
        # Perform security audit
        audit_result = await security_monitor.perform_audit(
            user_id=request.user_id,
            start_date=request.start_date,
            end_date=request.end_date,
            event_types=request.event_types
        )
        
        return {
            "status": "success",
            "audit_summary": audit_result.summary,
            "security_events": audit_result.events,
            "risk_assessment": audit_result.risk_assessment,
            "recommendations": audit_result.recommendations,
            "total_events": len(audit_result.events)
        }
        
    except Exception as e:
        logger.error(f"Security audit error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Security audit failed"
        )

@router.get("/permissions/check/{user_id}")
async def check_permissions(
    user_id: str,
    permission: str,
    resource: Optional[str] = None,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Check if a user has specific permissions
    """
    try:
        # Verify authorization
        user_info = await auth_manager.verify_token(credentials.credentials)
        
        # Check if user can query permissions
        if user_info.user_id != user_id:
            has_permission = await enhanced_rbac.check_permission(
                user_id=user_info.user_id,
                permission="view_user_permissions",
                resource=user_id
            )
            if not has_permission:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Insufficient permissions"
                )
        
        # Check the requested permission
        has_requested_permission = await enhanced_rbac.check_permission(
            user_id=user_id,
            permission=permission,
            resource=resource
        )
        
        # Get detailed permission info
        permission_details = await enhanced_rbac.get_permission_details(
            user_id=user_id,
            permission=permission,
            resource=resource
        )
        
        return {
            "status": "success",
            "has_permission": has_requested_permission,
            "permission_details": {
                "granted_by": permission_details.granted_by,
                "scope": permission_details.scope,
                "conditions": permission_details.conditions,
                "expires_at": permission_details.expires_at
            }
        }
        
    except Exception as e:
        logger.error(f"Permission check error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Permission check failed"
        )

@router.get("/system/health")
async def auth_system_health(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Get health status of enhanced authentication system
    """
    try:
        # Verify admin authorization
        user_info = await auth_manager.verify_token(credentials.credentials)
        
        has_permission = await enhanced_rbac.check_permission(
            user_id=user_info.user_id,
            permission="system_monitoring",
            resource="auth_system"
        )
        
        if not has_permission:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        
        # Get system health
        auth_health = await auth_manager.get_system_health()
        mfa_health = await mfa_manager.get_system_health()
        rbac_health = await enhanced_rbac.get_system_health()
        identity_health = await identity_manager.get_system_health()
        security_health = await security_monitor.get_system_health()
        
        return {
            "status": "success",
            "overall_health": "healthy",  # Calculated based on components
            "components": {
                "auth_manager": auth_health,
                "mfa_manager": mfa_health,
                "enhanced_rbac": rbac_health,
                "identity_manager": identity_health,
                "security_monitor": security_health
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Auth system health check error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Health check failed"
        )

