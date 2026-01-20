"""Application launcher with permission checking."""
import subprocess
import sys
import os
from typing import Optional, Dict, List
from pathlib import Path
from .permission_manager import PermissionManager, OperationType, PermissionLevel


class AppLauncher:
    """Launches applications with permission checks."""
    
    def __init__(self, permission_manager: PermissionManager):
        """Initialize app launcher with permission manager."""
        self.pm = permission_manager
    
    def launch_app(self, app_path: str, args: list = None, request_confirmation: callable = None) -> bool:
        """Launch application with permission check."""
        perm = self.pm.check_permission(OperationType.APP_LAUNCH)
        
        if perm == PermissionLevel.DENY:
            print("[ERROR] Application launching is not permitted")
            return False
        
        if perm == PermissionLevel.REQUIRE_CONFIRMATION:
            if request_confirmation:
                if not request_confirmation(f"Allow launching: {app_path}?"):
                    print("[DENIED] User rejected app launch permission")
                    return False
            else:
                # If no confirmation handler provided but confirmation is needed,
                # grant temporary permission and proceed
                print("[INFO] Granting temporary permission...")
                self.pm.grant_temporary_permission(OperationType.APP_LAUNCH, duration_minutes=5)
        
        try:
            cmd = [app_path]
            if args:
                cmd.extend(args)
            
            if sys.platform == 'win32':
                # Use shell=False for direct execution
                subprocess.Popen(cmd)
            else:
                subprocess.Popen(cmd)
            
            print(f"[SUCCESS] Launched: {app_path}")
            return True
        except Exception as e:
            print(f"[ERROR] Failed to launch app: {str(e)}")
            return False
    
    def launch_by_name(self, app_name: str, request_confirmation: callable = None) -> bool:
        """Launch application by name (Windows only)."""
        if sys.platform != 'win32':
            print("[ERROR] App launching by name is only supported on Windows")
            return False
        
        perm = self.pm.check_permission(OperationType.APP_LAUNCH)
        
        if perm == PermissionLevel.DENY:
            print("[ERROR] Application launching is not permitted")
            return False
        
        if perm == PermissionLevel.REQUIRE_CONFIRMATION:
            if request_confirmation:
                if not request_confirmation(f"Allow launching: {app_name}?"):
                    print("[DENIED] User rejected app launch permission")
                    return False
            else:
                print("[ERROR] Confirmation required but no confirmation handler provided")
                return False
        
        try:
            subprocess.Popen(f'start {app_name}', shell=True)
            return True
        except Exception as e:
            print(f"[ERROR] Failed to launch app: {str(e)}")
            return False
    
    def get_common_apps(self) -> dict:
        """Get paths to common applications (Windows specific)."""
        if sys.platform != 'win32':
            return {}
        
        common_apps = {
            'notepad': 'notepad.exe',
            'calculator': 'calc.exe',
            'paint': 'mspaint.exe',
            'wordpad': 'write.exe',
            'explorer': 'explorer.exe',
            'steam': self._find_steam(),
            'chrome': self._find_chrome(),
            'firefox': self._find_firefox(),
        }
        return {k: v for k, v in common_apps.items() if v}
    
    @staticmethod
    def _find_chrome() -> Optional[str]:
        """Find Chrome installation."""
        possible_paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        ]
        for path in possible_paths:
            if os.path.exists(path):
                return path
        return None
    
    @staticmethod
    def _find_firefox() -> Optional[str]:
        """Find Firefox installation."""
        possible_paths = [
            r"C:\Program Files\Mozilla Firefox\firefox.exe",
            r"C:\Program Files (x86)\Mozilla Firefox\firefox.exe",
        ]
        for path in possible_paths:
            if os.path.exists(path):
                return path
        return None
    
    @staticmethod
    def _find_steam() -> Optional[str]:
        """Find Steam installation."""
        possible_paths = [
            r"C:\Program Files\Steam\steam.exe",
            r"C:\Program Files (x86)\Steam\steam.exe",
        ]
        for path in possible_paths:
            if os.path.exists(path):
                return path
        return None
    
    def discover_installed_apps(self, limit: int = 50) -> Dict[str, str]:
        """Discover installed applications from common directories.
        
        Args:
            limit: Maximum number of apps to return
            
        Returns:
            Dictionary of {app_name: full_path}
        """
        if sys.platform != 'win32':
            return {}
        
        apps = {}
        search_paths = [
            r"C:\Program Files",
            r"C:\Program Files (x86)",
            os.path.expanduser(r"~\AppData\Local\Programs"),
            os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application"),
        ]
        
        for search_path in search_paths:
            if not os.path.exists(search_path):
                continue
            
            try:
                for root, dirs, files in os.walk(search_path):
                    if len(apps) >= limit:
                        return apps
                    
                    for file in files:
                        if len(apps) >= limit:
                            return apps
                        
                        if file.endswith('.exe'):
                            full_path = os.path.join(root, file)
                            app_name = file[:-4].lower()  # Remove .exe extension
                            
                            # Avoid duplicates and system files
                            if app_name not in apps and not self._is_system_file(app_name):
                                apps[app_name] = full_path
            except (PermissionError, OSError):
                # Skip directories we don't have permission to access
                continue
        
        return apps
    
    @staticmethod
    def _is_system_file(app_name: str) -> bool:
        """Check if app is a system file to skip."""
        system_keywords = [
            'uninstall', 'installer', 'setup', 'temp', 'system',
            'config', 'debug', 'test', 'helper', '.net', 'runtime'
        ]
        return any(keyword in app_name.lower() for keyword in system_keywords)
    
    def search_app(self, app_name: str) -> Optional[str]:
        """Search for an application by name.
        
        Args:
            app_name: Name of the application to search for
            
        Returns:
            Full path to the application if found, None otherwise
        """
        # First check common apps
        common_apps = self.get_common_apps()
        if app_name.lower() in common_apps:
            return common_apps[app_name.lower()]
        
        # Then search installed apps
        installed = self.discover_installed_apps(limit=100)
        for name, path in installed.items():
            if app_name.lower() in name.lower() or name.lower() in app_name.lower():
                return path
        
        return None
    
    def list_available_apps(self, limit: int = 30) -> List[str]:
        """List available applications.
        
        Args:
            limit: Maximum number of apps to list
            
        Returns:
            List of available application names
        """
        apps = self.get_common_apps()
        app_names = list(apps.keys())
        
        # Add discovered apps
        if len(app_names) < limit:
            discovered = self.discover_installed_apps(limit=limit - len(app_names))
            app_names.extend(discovered.keys())
        
        return sorted(app_names)[:limit]
