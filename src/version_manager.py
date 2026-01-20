"""Version management system for tracking Augi updates and releases."""
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


class VersionManager:
    """Manages version history, changelog, and deployment tracking."""
    
    def __init__(self, version_file: str = "version.json"):
        """Initialize version manager.
        
        Args:
            version_file: Path to version tracking file
        """
        self.version_file = Path(version_file)
        self.changelog_dir = Path("changelog")
        self.changelog_dir.mkdir(exist_ok=True)
        self.current_version = self._load_version()
    
    def _load_version(self) -> Dict:
        """Load current version info."""
        if self.version_file.exists():
            try:
                with open(self.version_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return self._create_default_version()
        return self._create_default_version()
    
    def _create_default_version(self) -> Dict:
        """Create default version info."""
        return {
            "version": "2.0.0",
            "release_date": datetime.now().isoformat(),
            "status": "stable",
            "features": [
                "Chat interface",
                "Memory and conversation persistence",
                "User profile learning",
                "6 personality profiles",
                "Internet search with permissions",
                "Voice support (TTS/STT)",
                "Conversation recall and context",
                "Streamlit web app"
            ],
            "last_updated": datetime.now().isoformat(),
            "deployed_to": []
        }
    
    def _save_version(self):
        """Save version info to file."""
        with open(self.version_file, 'w') as f:
            json.dump(self.current_version, f, indent=2)
    
    def create_release(self, version: str, features: List[str], 
                      bug_fixes: List[str] = None, notes: str = "") -> Dict:
        """Create a new release version.
        
        Args:
            version: Version number (e.g., "2.1.0")
            features: List of new features
            bug_fixes: List of bug fixes
            notes: Release notes
            
        Returns:
            Release info dict
        """
        release_info = {
            "version": version,
            "release_date": datetime.now().isoformat(),
            "status": "beta",
            "features": features,
            "bug_fixes": bug_fixes or [],
            "notes": notes,
            "changelog_file": f"{version}.json"
        }
        
        # Save changelog entry
        changelog_file = self.changelog_dir / f"{version}.json"
        with open(changelog_file, 'w') as f:
            json.dump(release_info, f, indent=2)
        
        # Update current version
        self.current_version = release_info
        self.current_version["last_updated"] = datetime.now().isoformat()
        self._save_version()
        
        return release_info
    
    def mark_deployed(self, platform: str, url: str = None) -> Dict:
        """Mark current version as deployed.
        
        Args:
            platform: Platform name (e.g., "streamlit_cloud", "heroku", "railway")
            url: Optional deployment URL
            
        Returns:
            Updated version info
        """
        deployment = {
            "platform": platform,
            "url": url,
            "deployed_date": datetime.now().isoformat(),
            "version": self.current_version.get("version")
        }
        
        if "deployed_to" not in self.current_version:
            self.current_version["deployed_to"] = []
        
        self.current_version["deployed_to"].append(deployment)
        self.current_version["status"] = "production"
        self._save_version()
        
        return deployment
    
    def get_changelog(self, version: str = None) -> Optional[Dict]:
        """Get changelog for a specific version.
        
        Args:
            version: Version number or None for latest
            
        Returns:
            Changelog dict or None
        """
        if not version:
            version = self.current_version.get("version")
        
        changelog_file = self.changelog_dir / f"{version}.json"
        if changelog_file.exists():
            try:
                with open(changelog_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return None
        return None
    
    def list_releases(self) -> List[Dict]:
        """List all releases in order.
        
        Returns:
            List of release dicts
        """
        releases = []
        
        for changelog_file in sorted(self.changelog_dir.glob("*.json"), reverse=True):
            try:
                with open(changelog_file, 'r') as f:
                    releases.append(json.load(f))
            except (json.JSONDecodeError, IOError):
                continue
        
        return releases
    
    def get_deployment_status(self) -> Dict:
        """Get current deployment status across platforms.
        
        Returns:
            Deployment status dict
        """
        deployments = {}
        
        for deployment in self.current_version.get("deployed_to", []):
            platform = deployment.get("platform")
            deployments[platform] = {
                "url": deployment.get("url"),
                "version": deployment.get("version"),
                "deployed_date": deployment.get("deployed_date")
            }
        
        return deployments
    
    def format_changelog_text(self) -> str:
        """Format current changelog as readable text.
        
        Returns:
            Formatted changelog text
        """
        v = self.current_version
        text = f"""
# Version {v.get('version')} - {v.get('status').upper()}

**Released:** {v.get('release_date')}
**Last Updated:** {v.get('last_updated')}

## Features
"""
        for feature in v.get('features', []):
            text += f"- {feature}\n"
        
        if v.get('bug_fixes'):
            text += "\n## Bug Fixes\n"
            for fix in v.get('bug_fixes'):
                text += f"- {fix}\n"
        
        if v.get('notes'):
            text += f"\n## Notes\n{v.get('notes')}\n"
        
        if v.get('deployed_to'):
            text += "\n## Deployed To\n"
            for deployment in v.get('deployed_to'):
                platform = deployment.get('platform')
                url = deployment.get('url')
                date = deployment.get('deployed_date')
                text += f"- **{platform}**: {url or 'N/A'} ({date})\n"
        
        return text
