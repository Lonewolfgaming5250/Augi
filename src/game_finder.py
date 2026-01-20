"""Game file finder for discovering installed games."""
import os
import sys
from typing import Dict, List, Optional
from pathlib import Path


class GameFinder:
    """Finds and catalogs installed games on the system."""
    
    # Common game file extensions
    GAME_EXTENSIONS = {'.exe', '.bat', '.cmd', '.lnk'}
    
    # Known game platforms and directories
    GAME_SEARCH_PATHS = [
        r"C:\Program Files\Steam\steamapps\common",
        r"C:\Program Files (x86)\Steam\steamapps\common",
        r"C:\Program Files\Epic Games",
        r"C:\Program Files (x86)\Epic Games",
        r"C:\Program Files\GOG Galaxy\Games",
        r"C:\Program Files (x86)\GOG Galaxy\Games",
        r"C:\Program Files\Origin Games",
        r"C:\Program Files (x86)\Origin Games",
        r"C:\Users\{user}\AppData\Local\Programs\Epic Games",
        r"C:\Games",
        os.path.expanduser(r"~\Games"),
    ]
    
    # Keywords that indicate a directory is a game
    GAME_INDICATORS = [
        'game', 'games', 'steam', 'epic', 'origin', 'gog', 'bethesda',
        'ubisoft', 'rockstar', 'activision', 'blizzard', 'ea', 'ea sports'
    ]
    
    # Keywords to exclude (not actual games)
    EXCLUDE_KEYWORDS = [
        'uninstall', 'installer', 'setup', 'helper', 'launcher', 'config',
        'redist', 'vcredist', 'runtime', 'update', 'patch', 'demo'
    ]
    
    def __init__(self):
        """Initialize game finder."""
        self.games: Dict[str, str] = {}
        self.game_paths: Dict[str, str] = {}
    
    def find_games(self, limit: int = 50, scan_depth: int = 3) -> Dict[str, str]:
        """Find installed games on the system.
        
        Args:
            limit: Maximum number of games to find
            scan_depth: Maximum directory depth to scan
            
        Returns:
            Dictionary of {game_name: full_path}
        """
        if sys.platform != 'win32':
            return {}
        
        self.games = {}
        search_paths = self._expand_search_paths()
        
        for search_path in search_paths:
            if len(self.games) >= limit:
                break
            
            if not os.path.exists(search_path):
                continue
            
            try:
                self._scan_directory(search_path, limit, scan_depth)
            except (PermissionError, OSError):
                continue
        
        return self.games
    
    def _expand_search_paths(self) -> List[str]:
        """Expand search paths with current user directory."""
        expanded = []
        current_user = os.getenv('USERNAME', 'User')
        
        for path in self.GAME_SEARCH_PATHS:
            expanded_path = path.replace('{user}', current_user)
            expanded.append(expanded_path)
        
        return expanded
    
    def _scan_directory(self, root_path: str, limit: int, max_depth: int, current_depth: int = 0):
        """Recursively scan directory for game files.
        
        Args:
            root_path: Directory to scan
            limit: Maximum games to find
            max_depth: Maximum depth to scan
            current_depth: Current recursion depth
        """
        if current_depth > max_depth or len(self.games) >= limit:
            return
        
        try:
            for item in os.listdir(root_path):
                if len(self.games) >= limit:
                    break
                
                item_path = os.path.join(root_path, item)
                
                # Skip if it's excluded
                if any(exclude in item.lower() for exclude in self.EXCLUDE_KEYWORDS):
                    continue
                
                # Check if it's a file
                if os.path.isfile(item_path):
                    if item.endswith('.exe'):
                        game_name = item[:-4].lower()
                        
                        # Check if looks like a game executable
                        if self._is_likely_game(game_name, root_path):
                            if game_name not in self.games:
                                self.games[game_name] = item_path
                
                # Recursively scan subdirectories
                elif os.path.isdir(item_path):
                    self._scan_directory(item_path, limit, max_depth, current_depth + 1)
        
        except (PermissionError, OSError):
            pass
    
    def _is_likely_game(self, filename: str, directory: str) -> bool:
        """Determine if a file is likely a game executable.
        
        Args:
            filename: Name of the executable (without .exe)
            directory: Directory containing the file
            
        Returns:
            True if likely a game, False otherwise
        """
        # Check if directory or filename contains game indicators
        dir_path = directory.lower()
        
        is_in_game_dir = any(indicator in dir_path for indicator in self.GAME_INDICATORS)
        is_game_named = any(indicator in filename for indicator in self.GAME_INDICATORS)
        
        # Exclude common non-game executables
        if any(exclude in filename for exclude in self.EXCLUDE_KEYWORDS):
            return False
        
        # Very short names are often system files
        if len(filename) <= 2:
            return False
        
        return is_in_game_dir or is_game_named
    
    def search_game(self, game_name: str) -> Optional[str]:
        """Search for a specific game.
        
        Args:
            game_name: Name of the game to search for
            
        Returns:
            Path to the game executable if found, None otherwise
        """
        # First check already found games
        game_name_lower = game_name.lower()
        
        for name, path in self.games.items():
            if game_name_lower in name or name in game_name_lower:
                return path
        
        # If not found, do a targeted search
        return self._targeted_game_search(game_name)
    
    def _targeted_game_search(self, game_name: str) -> Optional[str]:
        """Perform a targeted search for a game by name."""
        search_paths = self._expand_search_paths()
        game_name_lower = game_name.lower()
        
        for search_path in search_paths:
            if not os.path.exists(search_path):
                continue
            
            try:
                for root, dirs, files in os.walk(search_path):
                    for file in files:
                        if file.endswith('.exe'):
                            file_name = file[:-4].lower()
                            if game_name_lower in file_name or file_name in game_name_lower:
                                full_path = os.path.join(root, file)
                                return full_path
            except (PermissionError, OSError):
                continue
        
        return None
    
    def get_popular_games(self) -> List[str]:
        """Get list of popular/installed games found.
        
        Returns:
            Sorted list of game names
        """
        return sorted(self.games.keys())
    
    def get_game_info(self, game_name: str) -> Optional[Dict]:
        """Get information about a game.
        
        Args:
            game_name: Name of the game
            
        Returns:
            Dictionary with game info or None
        """
        path = self.search_game(game_name)
        
        if path and os.path.exists(path):
            return {
                'name': game_name,
                'path': path,
                'executable': os.path.basename(path),
                'size': os.path.getsize(path),
                'directory': os.path.dirname(path)
            }
        
        return None
