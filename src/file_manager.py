"""File system operations with permission checking."""
import os
from pathlib import Path
from typing import Optional
from .permission_manager import PermissionManager, OperationType, PermissionLevel


class FileManager:
    """Manages file operations with permission checks."""
    
    def __init__(self, permission_manager: PermissionManager):
        """Initialize file manager with permission manager."""
        self.pm = permission_manager
    
    def read_file(self, file_path: str, request_confirmation: callable = None) -> Optional[str]:
        """Read file with permission check."""
        perm = self.pm.check_permission(OperationType.FILE_READ)
        
        if perm == PermissionLevel.DENY:
            return "[ERROR] File reading is not permitted"
        
        if perm == PermissionLevel.REQUIRE_CONFIRMATION:
            if request_confirmation:
                if not request_confirmation(f"Allow reading file: {file_path}?"):
                    return "[DENIED] User rejected file read permission"
            else:
                return "[ERROR] Confirmation required but no confirmation handler provided"
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            return f"[ERROR] Failed to read file: {str(e)}"
    
    def write_file(self, file_path: str, content: str, request_confirmation: callable = None) -> bool:
        """Write file with permission check."""
        perm = self.pm.check_permission(OperationType.FILE_WRITE)
        
        if perm == PermissionLevel.DENY:
            print("[ERROR] File writing is not permitted")
            return False
        
        if perm == PermissionLevel.REQUIRE_CONFIRMATION:
            if request_confirmation:
                if not request_confirmation(f"Allow writing to file: {file_path}?"):
                    print("[DENIED] User rejected file write permission")
                    return False
            else:
                print("[ERROR] Confirmation required but no confirmation handler provided")
                return False
        
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except Exception as e:
            print(f"[ERROR] Failed to write file: {str(e)}")
            return False
    
    def delete_file(self, file_path: str, request_confirmation: callable = None) -> bool:
        """Delete file with permission check."""
        perm = self.pm.check_permission(OperationType.FILE_DELETE)
        
        if perm == PermissionLevel.DENY:
            print("[ERROR] File deletion is not permitted")
            return False
        
        if perm == PermissionLevel.REQUIRE_CONFIRMATION:
            if request_confirmation:
                if not request_confirmation(f"Delete file: {file_path}?"):
                    print("[DENIED] User rejected file delete permission")
                    return False
            else:
                print("[ERROR] Confirmation required but no confirmation handler provided")
                return False
        
        try:
            os.remove(file_path)
            return True
        except Exception as e:
            print(f"[ERROR] Failed to delete file: {str(e)}")
            return False
    
    def list_directory(self, dir_path: str) -> Optional[list]:
        """List directory contents."""
        try:
            path = Path(dir_path)
            if path.is_dir():
                items = []
                for item in path.iterdir():
                    items.append({
                        'name': item.name,
                        'type': 'dir' if item.is_dir() else 'file',
                        'size': item.stat().st_size if item.is_file() else None
                    })
                return items
            return None
        except Exception as e:
            return None
