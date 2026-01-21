"""Permission management system for AI operations."""
from enum import Enum
from typing import Dict, Set
from datetime import datetime, timedelta
import json
import os


class PermissionLevel(Enum):
    """Permission levels for operations."""
    DENY = 0
    REQUIRE_CONFIRMATION = 1
    ALLOW = 2


class OperationType(Enum):
    """Types of operations that require permissions."""
    FILE_READ = "file_read"
    FILE_WRITE = "file_write"
    FILE_DELETE = "file_delete"
    APP_LAUNCH = "app_launch"
    SYSTEM_COMMAND = "system_command"
    INTERNET_ACCESS = "internet_access"


class PermissionManager:
    """Manages permissions for sensitive operations."""
    
    def __init__(self, config_path: str = "config/permissions.json"):
        """Initialize permission manager with config file."""
        self.config_path = config_path
        self.permissions: Dict[str, PermissionLevel] = {}
        self.temp_permissions: Dict[str, tuple[PermissionLevel, datetime]] = {}
        self.load_permissions()
    
    def load_permissions(self):
        """Load permissions from config file."""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    data = json.load(f)
                    self.permissions = {
                        k: PermissionLevel[v] for k, v in data.items()
                    }
            except Exception as e:
                print(f"Error loading permissions: {e}")
                self._set_default_permissions()
        else:
            self._set_default_permissions()
    
    def _set_default_permissions(self):
        """Set default restrictive permissions."""
        self.permissions = {
            OperationType.FILE_READ.value: PermissionLevel.REQUIRE_CONFIRMATION,
            OperationType.FILE_WRITE.value: PermissionLevel.REQUIRE_CONFIRMATION,
            OperationType.FILE_DELETE.value: PermissionLevel.DENY,
            OperationType.APP_LAUNCH.value: PermissionLevel.REQUIRE_CONFIRMATION,
            OperationType.SYSTEM_COMMAND.value: PermissionLevel.DENY,
        }
    
    def save_permissions(self):
        """Save permissions to config file."""
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        import collections.abc
        def convert_sets(obj):
            if isinstance(obj, set):
                return list(obj)
            elif isinstance(obj, collections.abc.Mapping):
                return {k: convert_sets(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_sets(i) for i in obj]
            else:
                return obj
        with open(self.config_path, 'w') as f:
            data = {k: v.name for k, v in self.permissions.items()}
            json.dump(convert_sets(data), f, indent=2)
    
    def check_permission(self, operation: OperationType) -> PermissionLevel:
        """Check permission level for an operation."""
        # Check for expired temporary permissions
        self._cleanup_expired_permissions()
        
        op_name = operation.value
        if op_name in self.temp_permissions:
            perm, _ = self.temp_permissions[op_name]
            return perm
        
        return self.permissions.get(op_name, PermissionLevel.DENY)
    
    def set_permission(self, operation: OperationType, level: PermissionLevel, permanent: bool = True):
        """Set permission level for an operation."""
        op_name = operation.value
        self.permissions[op_name] = level
        if permanent:
            self.save_permissions()
    
    def grant_temporary_permission(self, operation: OperationType, duration_minutes: int = 5):
        """Grant temporary permission for a specific duration."""
        op_name = operation.value
        expiry = datetime.now() + timedelta(minutes=duration_minutes)
        self.temp_permissions[op_name] = (PermissionLevel.ALLOW, expiry)
    
    def _cleanup_expired_permissions(self):
        """Remove expired temporary permissions."""
        now = datetime.now()
        expired = [k for k, (_, expiry) in self.temp_permissions.items() if now > expiry]
        for k in expired:
            del self.temp_permissions[k]
