"""Main AI Assistant with Claude integration."""
import os
import re
from typing import Optional
from anthropic import Anthropic
from .permission_manager import PermissionManager, OperationType
from .file_manager import FileManager
from .app_launcher import AppLauncher
from .game_finder import GameFinder
from .web_searcher import WebSearcher
from .personality import PersonalityManager, PersonalityType
from .memory_manager import MemoryManager
from .user_profile import UserProfileManager
from .voice_manager import VoiceManager, SimpleVoiceManager
from .device_diagnostic import DeviceDiagnostic



class PersonalAIAssistant:
    """Personal AI assistant with file and app access capabilities."""

    def set_user_location(self, location: str):
        """Set the user's location for context-aware responses."""
        if hasattr(self.user_profile, 'profile'):
            self.user_profile.profile['location'] = location
        else:
            self.user_profile.location = location

    def get_user_location(self) -> str:
        """Get the user's location if known."""
        if hasattr(self.user_profile, 'profile') and 'location' in self.user_profile.profile:
            return self.user_profile.profile['location']
        elif hasattr(self.user_profile, 'location'):
            return self.user_profile.location
        return None

    def _extract_search_query(self, message: str) -> str:
        """Extract a search query from the assistant's message."""
        # Simple heuristic: look for quoted text or after 'search for', 'look up', etc.
        import re
        # Try to extract quoted text
        quoted = re.findall(r'"([^"]+)"|\'([^\']+)\'', message)
        if quoted:
            # quoted is a list of tuples, get the first non-empty
            for tup in quoted[0]:
                if tup:
                    return tup.strip()
        # Try to extract after common search phrases
        patterns = [
            r'search(?:ing)?(?: the internet)?(?: for)? ([^.!?\n]+)',
            r'look(?:ing)? up ([^.!?\n]+)',
            r'find(?:ing)? ([^.!?\n]+)',
        ]
        for pattern in patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                query = match.group(1).strip()
                # Clean up the query
                query = query.replace("internet", "").replace("online", "").strip()
                return query
        # Fallback: return the whole message if it looks like a question
        if message.strip().endswith('?'):
            return message.strip()
        return None

    def run_device_diagnostic(self) -> str:
        """Run a full device diagnostic and return a summary."""
        diag = DeviceDiagnostic()
        results = {}
        try:
            results['os'] = diag.check_os()
            results['hardware'] = diag.check_hardware()
            results['disk'] = diag.check_disk()
            results['memory'] = diag.check_memory()
            results['network'] = diag.check_network()
            results['python'] = diag.check_python()
            results['env'] = diag.check_env()
        except Exception as e:
            return f"Device diagnostic failed: {e}"
        summary = ["Device Diagnostic Results:"]
        for k, v in results.items():
            summary.append(f"- {k.capitalize()}: {v}")
        return "\n".join(summary)

    def _get_user_profile_context(self):
        """Return a summary of learned user info for prompt injection."""
        location = self.get_user_location()
        summary = None
        if hasattr(self.user_profile, "get_learning_summary"):
            summary = self.user_profile.get_learning_summary()
        context_parts = []
        if location:
            context_parts.append(f"User location: {location}")
        if summary:
            context_parts.append(summary)
        return "\n".join(context_parts) if context_parts else ""
    """Personal AI assistant with file and app access capabilities."""

    def _should_perform_internet_search(self, message: str) -> bool:
        """Detect if the assistant's response suggests an internet search is needed."""
        keywords = [
            "search the internet",
            "look up",
            "find online",
            "let me search",
            "let me look up",
            "let me check online",
        ]
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in keywords)

    def chat(self):
        """Run an interactive chat loop with the AI assistant."""
        print("\nWelcome to your Personal AI Assistant! Type 'exit' to quit.\n")
        while True:
            try:
                user_input = input("You: ").strip()
                if user_input.lower() in ("exit", "quit"):
                    print("\nGoodbye! 👋")
                    break
                response = self.process_user_input(user_input)
                if response:
                    print(f"Augi: {response}")
            except (KeyboardInterrupt, EOFError):
                print("\nGoodbye! 👋")
                break
    
    def __init__(self, wake_word: str = "ai", enable_wake_word: bool = True, personality: str = "friendly", 
                 enable_learning: bool = True, load_last_session: bool = False, enable_voice: bool = False):
        """Initialize AI assistant.
        
        Args:
            wake_word: The word or phrase needed to activate the assistant
            enable_wake_word: Whether to require wake word activation
            personality: Personality type (professional, friendly, witty, helpful, tech_savvy, casual)
            enable_learning: Whether to learn and remember information about the user
            load_last_session: Whether to load the last conversation session
            enable_voice: Whether to enable voice input/output
        """
        self.wake_word = wake_word.lower()
        self.client = Anthropic()
        self.pm = PermissionManager()
        self.file_manager = FileManager(self.pm)
        self.app_launcher = AppLauncher(self.pm)
        self.game_finder = GameFinder()
        self.web_searcher = WebSearcher()
        self.personality_manager = PersonalityManager(PersonalityType[personality.upper()])
        # Set the base system prompt and include personality
        base_prompt = "You are Augi, a helpful personal AI assistant with access to file operations, app launching, and internet search capabilities."
        personality_addition = self.personality_manager.profile.system_prompt_addition
        self.system_prompt = f"{base_prompt}\n\n{personality_addition}"
        
        # Memory and learning systems
        self.memory_manager = MemoryManager()
        self.enable_learning = enable_learning
        # Self-repair functionality removed
        
        # Load user profile
        profile_data = self.memory_manager.load_user_profile()
        self.user_profile = UserProfileManager(profile_data)
        
        # Voice support
        self.voice_enabled = enable_voice
        if enable_voice:
            try:
                self.voice_manager = VoiceManager(enable_tts=True, enable_stt=True)
            except Exception:
                # Fallback to simple voice (TTS only)
                self.voice_manager = SimpleVoiceManager()
        else:
            self.voice_manager = None
        
        # Load conversation history from last session if available
        self.conversation_history = []
        self.session_file = None
        self._load_conversation_history()

    def _get_session_file_path(self):
        import os
        import datetime
        memory_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "memory", "conversations")
        os.makedirs(memory_dir, exist_ok=True)
        if self.session_file:
            return self.session_file
        # Use timestamp for new session
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.session_file = os.path.join(memory_dir, f"{timestamp}.json")
        return self.session_file

    def _load_conversation_history(self):
        import os
        import glob
        import json
        memory_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "memory", "conversations")
        os.makedirs(memory_dir, exist_ok=True)
        # Find the most recent session file
        session_files = sorted(glob.glob(os.path.join(memory_dir, "*.json")), reverse=True)
        if session_files:
            with open(session_files[0], "r", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                    # Handle dict with 'messages' key (Anthropic format)
                    if isinstance(data, dict) and "messages" in data:
                        messages = data["messages"]
                        if isinstance(messages, list):
                            self.conversation_history = messages
                        else:
                            self.conversation_history = []
                    # Handle list of dicts, each with 'messages' (flatten all messages)
                    elif isinstance(data, list) and all(isinstance(item, dict) for item in data):
                        all_msgs = []
                        for item in data:
                            if "messages" in item and isinstance(item["messages"], list):
                                all_msgs.extend(item["messages"])
                            elif "role" in item and "content" in item:
                                all_msgs.append(item)
                        self.conversation_history = all_msgs
                    # Handle list of messages (legacy format)
                    elif isinstance(data, list):
                        self.conversation_history = data
                    # Handle dict that is a single message
                    elif isinstance(data, dict) and "role" in data and "content" in data:
                        self.conversation_history = [data]
                    else:
                        self.conversation_history = []
                    self.session_file = session_files[0]
                except Exception:
                    self.conversation_history = []
        else:
            self.conversation_history = []

    def _save_conversation_history(self):
        import json
        session_file = self._get_session_file_path()
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
        with open(session_file, "w", encoding="utf-8") as f:
            json.dump(convert_sets(self.conversation_history), f, ensure_ascii=False, indent=2)

    # (Removed duplicate, keep only the properly indented process_user_input below)
    def process_user_input(self, user_input: str):
        # Allow user to set location with phrases like "my location is ..." or "i'm in ..."
        location_phrases = ["my location is ", "i'm in ", "i am in ", "i live in ", "i'm at ", "i am at "]
        for phrase in location_phrases:
            if user_input.lower().startswith(phrase):
                location = user_input[len(phrase):].strip().strip('.!')
                self.set_user_location(location)
                return f"Got it! I'll remember your location as {location}."

        # Device diagnostic command detection
        normalized_input = user_input.strip().lower()
        diagnostic_phrases = [
            "run diagnostic", "device diagnostic", "system diagnostic", "check my device", "check this computer", "run a health check", "run system check", "run hardware check", "run system diagnostic", "run device check"
        ]
        if any(phrase in normalized_input for phrase in diagnostic_phrases):
            return self.run_device_diagnostic()

        # If input is only the wake word, respond with a friendly greeting or prompt
        user_name = self.user_profile.get_preferred_name() if hasattr(self.user_profile, "get_preferred_name") else None
        if normalized_input == self.wake_word:
            if user_name:
                return f"{self.personality_manager.profile.greeting} Nice to see you, {user_name}!"
            return self.personality_manager.profile.greeting

        # Respond personally to "who are you" and similar questions
        who_phrases = [
            "who are you",
            "what are you",
            "who is augi",
            "what is augi",
            "tell me about yourself",
            "your name",
            "introduce yourself"
        ]
        if any(phrase in normalized_input for phrase in who_phrases):
            if user_name:
                return (
                    f"I'm Augi, your personal AI assistant! {self.personality_manager.profile.description}. "
                    f"It's great to talk with you, {user_name}. "
                    f"I can help you with files, launch apps, search the web, and have a {self.personality_manager.profile.response_style.lower()} conversation. "
                    f"Just ask me anything!"
                )
            return (
                f"I'm Augi, your personal AI assistant! {self.personality_manager.profile.description}. "
                f"I can help you with files, launch apps, search the web, and have a {self.personality_manager.profile.response_style.lower()} conversation. "
                f"Just ask me anything!"
            )

        # Append user input to conversation history
        self.conversation_history.append({
            "role": "user",
            "content": user_input
        })
        self._save_conversation_history()

        # Create enhanced prompt with user profile and current capabilities
        user_profile_context = self._get_user_profile_context()
        capabilities_info = self._get_capabilities_info()
        enhanced_system = f"{self.system_prompt}\n\n{user_profile_context}\n{capabilities_info}"

        # Get response from Claude
        response = self.client.messages.create(
            model="claude-opus-4-1",
            max_tokens=2048,
            system=enhanced_system,
            messages=self.conversation_history
        )

        assistant_message = response.content[0].text.strip()
        # Append assistant response to conversation history and save
        self.conversation_history.append({
            "role": "assistant",
            "content": assistant_message
        })
        self._save_conversation_history()

        # If the model returns a very short or generic response, offer a follow-up
        if len(assistant_message.split()) < 5:
            return self.personality_manager.profile.greeting + " How can I help you today?"

        # Check if AI wants to search the internet
        if self._should_perform_internet_search(assistant_message):
            # Always allow internet access, no confirmation needed
            search_query = self._extract_search_query(assistant_message)
            if search_query:
                search_results = self.internet_search(search_query, num_results=3)
                # Add search results to the response
        patterns = [
            r"search(?:ing)?\s+(?:for\s+)?([^.!?\n]+)",
            r"search(?:ing)?\s+the\s+internet\s+for\s+([^.!?\n]+)",
            r"look(?:ing)?\s+up\s+([^.!?\n]+)",
        ]

        for pattern in patterns:
            match = re.search(pattern, assistant_message, re.IGNORECASE)
            if match:
                query = match.group(1).strip()
                # Clean up the query
                query = query.replace("internet", "").replace("online", "").strip()
                if query:
                    return query

        # If no specific query found, extract a general topic
        return assistant_message
    
    def _get_capabilities_info(self) -> str:
        """Get current capabilities based on permissions."""
        perms = {
            OperationType.FILE_READ: self.pm.check_permission(OperationType.FILE_READ).name,
            OperationType.FILE_WRITE: self.pm.check_permission(OperationType.FILE_WRITE).name,
            OperationType.APP_LAUNCH: self.pm.check_permission(OperationType.APP_LAUNCH).name,
        }
        
        return f"""Current Permissions Status:
- File Reading: {perms[OperationType.FILE_READ]}
- File Writing: {perms[OperationType.FILE_WRITE]}
- App Launching: {perms[OperationType.APP_LAUNCH]}

Inform the user of permission restrictions when relevant."""
    
    def _process_file_operations(self, user_input: str, assistant_response: str):
        """Process any file operations based on conversation."""
        # This is a placeholder for more sophisticated file operation detection
        # In a real implementation, Claude would output structured commands
        pass
    
    def read_file_command(self, file_path: str) -> str:
        """Command to read a file."""
        return self.file_manager.read_file(file_path, self.request_user_confirmation)
    
    def write_file_command(self, file_path: str, content: str) -> bool:
        """Command to write a file."""
        return self.file_manager.write_file(file_path, content, self.request_user_confirmation)
    
    def launch_app_command(self, app_path: str) -> bool:
        """Command to launch an application."""
        return self.app_launcher.launch_app(app_path, request_confirmation=self.request_user_confirmation)
    
    def launch_app_by_name(self, app_name: str) -> bool:
        """Command to launch an application by name."""
        return self.app_launcher.launch_by_name(app_name, request_confirmation=self.request_user_confirmation)
    
    def list_available_apps(self, limit: int = 30) -> list:
        """Get list of available applications."""
        return self.app_launcher.list_available_apps(limit=limit)
    
    def search_app(self, app_name: str) -> Optional[str]:
        """Search for an application."""
        return self.app_launcher.search_app(app_name)
    
    def find_games(self, limit: int = 50) -> dict:
        """Find installed games on the system."""
        return self.game_finder.find_games(limit=limit)
    
    def search_game(self, game_name: str) -> Optional[str]:
        """Search for a specific game."""
        return self.game_finder.search_game(game_name)
    
    def get_available_games(self, limit: int = 30) -> list:
        """Get list of available games."""
        games = self.game_finder.find_games(limit=limit)
        return sorted(games.keys())[:limit]
    
    def internet_search(self, query: str, num_results: int = 5) -> str:
        """Search the internet."""
        return self.web_searcher.search_with_summary(query, num_results=num_results)
    
    def set_permission(self, operation_name: str, permission_level: str):
        """Set permission for an operation."""
        op = OperationType[operation_name.upper().replace(' ', '_')]
        from .permission_manager import PermissionLevel
        level = PermissionLevel[permission_level.upper()]
        self.pm.set_permission(op, level, permanent=True)
        return f"Permission updated: {operation_name} -> {permission_level}"
    
    def _check_wake_word(self, user_input: str) -> bool:
        """Check if user input contains the wake word."""
        input_lower = user_input.lower()
        return self.wake_word in input_lower
    
    def _extract_command_after_wake_word(self, user_input: str) -> str:
        """Extract the command part after the wake word."""
        input_lower = user_input.lower()
        wake_word_index = input_lower.find(self.wake_word)
        
        if wake_word_index != -1:
            # Remove the wake word and get the remaining text
            command = user_input[wake_word_index + len(self.wake_word):].strip()
            return command
        
        return user_input
    
    # _show_help method removed due to corruption and syntax error
