"""Memory management system for persisting conversations and learning about the user."""
import json
import os
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from pathlib import Path


class ConversationIndex:
    """Index for fast conversation retrieval and search."""
    
    def __init__(self, index_file: Path):
        """Initialize conversation index.
        
        Args:
            index_file: Path to index JSON file
        """
        self.index_file = index_file
        self.index = self._load_index()
    
    def _load_index(self) -> Dict:
        """Load index from file or create new."""
        if self.index_file.exists():
            try:
                with open(self.index_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return {"conversations": {}, "keywords": {}}
        return {"conversations": {}, "keywords": {}}
    
    def _save_index(self):
        """Save index to file."""
        with open(self.index_file, 'w') as f:
            json.dump(self.index, f, indent=2)
    
    def add_conversation(self, session_id: str, keywords: List[str], timestamp: str, message_count: int):
        """Add conversation to index.
        
        Args:
            session_id: Session ID
            keywords: List of keywords from the conversation
            timestamp: Timestamp of conversation
            message_count: Number of messages
        """
        self.index["conversations"][session_id] = {
            "timestamp": timestamp,
            "message_count": message_count,
            "keywords": keywords
        }
        
        # Index keywords for fast lookup
        for keyword in keywords:
            if keyword not in self.index["keywords"]:
                self.index["keywords"][keyword] = []
            if session_id not in self.index["keywords"][keyword]:
                self.index["keywords"][keyword].append(session_id)
        
        self._save_index()
    
    def search_by_keywords(self, keywords: List[str]) -> List[str]:
        """Get conversations matching keywords.
        
        Args:
            keywords: Keywords to search for
            
        Returns:
            List of session IDs
        """
        matching_sessions = {}
        
        for keyword in keywords:
            keyword_lower = keyword.lower()
            # Direct match
            if keyword_lower in self.index["keywords"]:
                for session_id in self.index["keywords"][keyword_lower]:
                    matching_sessions[session_id] = matching_sessions.get(session_id, 0) + 1
            
            # Partial match
            for indexed_keyword in self.index["keywords"]:
                if keyword_lower in indexed_keyword or indexed_keyword in keyword_lower:
                    for session_id in self.index["keywords"][indexed_keyword]:
                        matching_sessions[session_id] = matching_sessions.get(session_id, 0) + 0.5
        
        # Sort by relevance
        sorted_sessions = sorted(matching_sessions.items(), key=lambda x: x[1], reverse=True)
        return [session_id for session_id, _ in sorted_sessions]



class MemoryManager:
    """Manages conversation history persistence and memory retrieval."""
    
    def __init__(self, memory_dir: str = "memory"):
        """Initialize memory manager.
        
        Args:
            memory_dir: Directory to store conversation and profile files
        """
        self.memory_dir = Path(memory_dir)
        self.memory_dir.mkdir(exist_ok=True)
        self.conversations_dir = self.memory_dir / "conversations"
        self.conversations_dir.mkdir(exist_ok=True)
        self.profile_file = self.memory_dir / "user_profile.json"
        self.current_session_file = self.memory_dir / "current_session.json"
        self.index_file = self.memory_dir / "conversation_index.json"
        self.index = ConversationIndex(self.index_file)
    
    def save_conversation(self, conversation_history: List[Dict], session_id: Optional[str] = None) -> str:
        """Save conversation history to file.
        
        Args:
            conversation_history: List of message dicts with role and content
            session_id: Optional session ID, generates timestamp if not provided
            
        Returns:
            The session ID/filename
        """
        if not session_id:
            session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        file_path = self.conversations_dir / f"{session_id}.json"
        
        conversation_data = {
            "timestamp": datetime.now().isoformat(),
            "session_id": session_id,
            "messages": conversation_history,
            "message_count": len(conversation_history)
        }
        
        with open(file_path, 'w') as f:
            json.dump(conversation_data, f, indent=2)
        
        # Extract keywords and add to index
        keywords = self._extract_keywords(conversation_history)
        self.index.add_conversation(
            session_id,
            keywords,
            conversation_data["timestamp"],
            len(conversation_history)
        )
        
        return session_id
    
    def _extract_keywords(self, messages: List[Dict]) -> List[str]:
        """Extract keywords from conversation.
        
        Args:
            messages: List of messages
            
        Returns:
            List of keywords
        """
        keywords = set()
        
        for msg in messages:
            content = msg.get("content", "").lower()
            
            # Extract important words (nouns, verbs, topics)
            important_words = [
                "python", "code", "help", "learn", "project", "question",
                "error", "problem", "solution", "idea", "discuss", "explain",
                "how", "what", "why", "when", "where", "about", "like",
                "build", "create", "develop", "design", "plan", "work"
            ]
            
            for word in important_words:
                if word in content:
                    keywords.add(word)
            
            # Also extract 2-3 word phrases
            words = content.split()
            for i in range(len(words) - 1):
                phrase = f"{words[i]} {words[i+1]}"
                if len(phrase) > 5 and len(phrase) < 50:
                    keywords.add(phrase)
        
        return list(keywords)[:20]  # Limit to 20 keywords
    
    
    def load_conversation(self, session_id: str) -> Optional[List[Dict]]:
        """Load a saved conversation.
        
        Args:
            session_id: Session ID/filename to load
            
        Returns:
            List of message dicts or None if not found
        """
        file_path = self.conversations_dir / f"{session_id}.json"
        
        if not file_path.exists():
            return None
        
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                return data.get("messages", [])
        except (json.JSONDecodeError, IOError):
            return None
    
    def save_current_session(self, conversation_history: List[Dict]):
        """Save current session for quick resumption.
        
        Args:
            conversation_history: Current conversation history
        """
        session_data = {
            "timestamp": datetime.now().isoformat(),
            "messages": conversation_history,
            "message_count": len(conversation_history)
        }
        
        with open(self.current_session_file, 'w') as f:
            json.dump(session_data, f, indent=2)
    
    def load_current_session(self) -> Optional[List[Dict]]:
        """Load the last session.
        
        Returns:
            List of message dicts or None if no session exists
        """
        if not self.current_session_file.exists():
            return None
        
        try:
            with open(self.current_session_file, 'r') as f:
                data = json.load(f)
                return data.get("messages", [])
        except (json.JSONDecodeError, IOError):
            return None
    
    def list_conversations(self, limit: int = 10) -> List[Dict]:
        """List recent conversations.
        
        Args:
            limit: Maximum number of conversations to return
            
        Returns:
            List of conversation metadata
        """
        conversations = []
        
        # Get all JSON files sorted by modification time (newest first)
        conversation_files = sorted(
            self.conversations_dir.glob("*.json"),
            key=lambda x: x.stat().st_mtime,
            reverse=True
        )[:limit]
        
        for file_path in conversation_files:
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    if not isinstance(data, dict):
                        print(f"Warning: Conversation file {file_path} does not contain a dict. Skipping.")
                        continue
                    conversations.append({
                        "session_id": data.get("session_id", file_path.stem),
                        "timestamp": data.get("timestamp"),
                        "message_count": data.get("message_count", 0)
                    })
            except (json.JSONDecodeError, IOError, AttributeError) as e:
                print(f"Error reading conversation file {file_path}: {e}")
                continue
        
        return conversations
    
    def get_conversation_summary(self, session_id: str) -> Optional[Dict]:
        """Get a summary of a conversation.
        
        Args:
            session_id: Session ID to summarize
            
        Returns:
            Summary dict with key information
        """
        file_path = self.conversations_dir / f"{session_id}.json"
        
        if not file_path.exists():
            return None
        
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                messages = data.get("messages", [])
                
                # Extract first user message and last assistant message
                first_user = None
                last_assistant = None
                
                for msg in messages:
                    if msg.get("role") == "user" and not first_user:
                        first_user = msg.get("content", "")[:100]
                    if msg.get("role") == "assistant":
                        last_assistant = msg.get("content", "")[:100]
                
                return {
                    "session_id": session_id,
                    "timestamp": data.get("timestamp"),
                    "message_count": len(messages),
                    "first_message": first_user,
                    "last_response": last_assistant
                }
        except (json.JSONDecodeError, IOError):
            return None
    
    def search_conversations(self, keyword: str, limit: int = 5) -> List[Dict]:
        """Search conversations for a keyword.
        
        Args:
            keyword: Keyword to search for (case-insensitive)
            limit: Maximum number of results
            
        Returns:
            List of matching conversation summaries
        """
        results = []
        keyword_lower = keyword.lower()
        
        for file_path in self.conversations_dir.glob("*.json"):
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    messages = data.get("messages", [])
                    
                    # Check if keyword appears in any message
                    for msg in messages:
                        if keyword_lower in msg.get("content", "").lower():
                            summary = {
                                "session_id": data.get("session_id", file_path.stem),
                                "timestamp": data.get("timestamp"),
                                "message_count": len(messages),
                                "matched_content": msg.get("content", "")[:100]
                            }
                            results.append(summary)
                            break  # Only add once per conversation
                    
                    if len(results) >= limit:
                        break
            except (json.JSONDecodeError, IOError):
                continue
        
        return results
    
    def save_user_profile(self, profile: Dict):
        """Save user profile information.
        
        Args:
            profile: Profile dictionary with learned information
        """
        with open(self.profile_file, 'w') as f:
            json.dump(profile, f, indent=2)
    
    def load_user_profile(self) -> Dict:
        """Load user profile information.
        
        Returns:
            Profile dictionary or empty dict if none exists
        """
        if not self.profile_file.exists():
            return {}
        
        try:
            with open(self.profile_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}
    
    def clear_memory(self, confirm: bool = False) -> bool:
        """Clear all memory (conversations and profile).
        
        Args:
            confirm: Must be True to actually clear memory
            
        Returns:
            True if cleared, False otherwise
        """
        if not confirm:
            return False
        
        try:
            # Delete conversation files
            for file_path in self.conversations_dir.glob("*.json"):
                file_path.unlink()
            
            # Delete current session
            if self.current_session_file.exists():
                self.current_session_file.unlink()
            
            # Delete profile
            if self.profile_file.exists():
                self.profile_file.unlink()
            
            # Delete index
            if self.index_file.exists():
                self.index_file.unlink()
            
            self.index = ConversationIndex(self.index_file)
            return True
        except Exception:
            return False
    
    def get_relevant_conversations(self, query: str, limit: int = 3) -> List[Dict]:
        """Get past conversations relevant to current query.
        
        Args:
            query: Current user query
            limit: Maximum conversations to return
            
        Returns:
            List of relevant past conversations with summaries
        """
        # Extract keywords from query
        query_lower = query.lower()
        keywords = []
        
        important_words = [
            "python", "code", "help", "learn", "project", "question",
            "error", "problem", "solution", "idea", "discuss", "explain",
            "how", "what", "why", "when", "where", "about", "like",
            "build", "create", "develop", "design", "plan", "work"
        ]
        
        for word in important_words:
            if word in query_lower:
                keywords.append(word)
        
        if not keywords:
            # If no keywords, get most recent conversations
            convs = self.list_conversations(limit=limit)
            return convs
        
        # Search for conversations with matching keywords
        matching_sessions = self.index.search_by_keywords(keywords)
        
        results = []
        for session_id in matching_sessions[:limit]:
            summary = self.get_conversation_summary(session_id)
            if summary:
                results.append(summary)
        
        return results
    
    def get_conversation_context(self, session_id: str, max_messages: int = 5) -> str:
        """Get a formatted context string from a conversation.
        
        Args:
            session_id: Session ID to get context from
            max_messages: Maximum messages to include (recent ones)
            
        Returns:
            Formatted conversation context
        """
        conversation = self.load_conversation(session_id)
        if not conversation:
            return ""
        
        # Get the last N messages
        recent_messages = conversation[-max_messages:]
        
        context = f"Previous conversation from {self.get_conversation_summary(session_id)['timestamp']}:\n"
        for msg in recent_messages:
            role = msg.get("role", "").upper()
            content = msg.get("content", "")[:200]  # Limit length
            context += f"{role}: {content}\n"
        
        return context
