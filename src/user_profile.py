"""User profile learning system for extracting and storing information about the user."""
import json
from typing import Dict, List, Set
from datetime import datetime


class UserProfileManager:
    """Extracts and maintains learned information about the user."""
    
    def __init__(self, profile_data: Dict = None):
        """Initialize user profile manager.
        
        Args:
            profile_data: Initial profile data (from memory manager)
        """
        self.profile = profile_data or self._create_empty_profile()
    
    def _create_empty_profile(self) -> Dict:
        """Create empty profile structure."""
        return {
            "created": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "preferred_name": None,
            "interests": set(),
            "skills": set(),
            "preferences": {},
            "hobbies": set(),
            "work_info": {},
            "favorite_apps": [],
            "favorite_games": [],
            "commonly_used_files": [],
            "learning_notes": {}
        }
    
    def extract_from_conversation(self, conversation_history: List[Dict]) -> Dict:
        """Extract learnable information from a conversation.
        
        Args:
            conversation_history: List of message dicts
            
        Returns:
            Extracted information as a dictionary
        """
        extracted = {
            "interests": set(),
            "skills": set(),
            "preferences": {},
            "mentions": set()
        }
        
        # Keywords that indicate interests
        interest_keywords = [
            "i like", "i love", "i enjoy", "interested in", "hobby",
            "passion", "fascinated", "enthusiast", "fan of", "into"
        ]
        
        # Keywords that indicate skills
        skill_keywords = [
            "i know", "i can", "i'm good at", "expertise", "skilled in",
            "experienced with", "proficient", "master", "expert"
        ]
        
        # Keywords that indicate preferences
        preference_keywords = [
            "prefer", "like to", "rather", "don't like", "hate",
            "dislike", "avoid"
        ]
        
        name_phrases = [
            "my name is ",
            "i am ",
            "i'm ",
            "call me ",
            "you can call me ",
            "people call me "
        ]
        for message in conversation_history:
            if message.get("role") == "user":
                content = message.get("content", "").strip()
                content_lower = content.lower()
                # Extract preferred name
                for phrase in name_phrases:
                    if phrase in content_lower:
                        idx = content_lower.find(phrase) + len(phrase)
                        name_candidate = content[idx:].split()[0].strip(". ,!?")
                        if name_candidate and name_candidate.isalpha() and len(name_candidate) > 1:
                            extracted["preferred_name"] = name_candidate.capitalize()
                # Extract interests
                for keyword in interest_keywords:
                    if keyword in content_lower:
                        parts = content_lower.split(keyword)
                        if len(parts) > 1:
                            interest = parts[1][:50].strip().split('.')[0].strip()
                            if interest and len(interest) > 2:
                                extracted["interests"].add(interest)
                # Extract skills
                for keyword in skill_keywords:
                    if keyword in content_lower:
                        parts = content_lower.split(keyword)
                        if len(parts) > 1:
                            skill = parts[1][:50].strip().split('.')[0].strip()
                            if skill and len(skill) > 2:
                                extracted["skills"].add(skill)
                # Extract mentions
                if "my" in content_lower or "i" in content_lower:
                    words = content_lower.split()
                    for i, word in enumerate(words):
                        if word in ["my", "i've", "i'm"] and i + 1 < len(words):
                            extracted["mentions"].add(words[i+1])
        return extracted
    
    def update_profile(self, extracted_info: Dict):
        """Update profile with newly extracted information.
        
        Args:
            extracted_info: Dictionary of extracted information
        """
        self.profile["last_updated"] = datetime.now().isoformat()
        
        # Merge preferred name
        if "preferred_name" in extracted_info and extracted_info["preferred_name"]:
            self.profile["preferred_name"] = extracted_info["preferred_name"]
        # Merge interests
        if "interests" in extracted_info:
            if not isinstance(self.profile["interests"], set):
                self.profile["interests"] = set(self.profile.get("interests", []))
            self.profile["interests"].update(extracted_info["interests"])
        # Merge skills
        if "skills" in extracted_info:
            if not isinstance(self.profile["skills"], set):
                self.profile["skills"] = set(self.profile.get("skills", []))
            self.profile["skills"].update(extracted_info["skills"])
        # Merge preferences
        if "preferences" in extracted_info:
            self.profile["preferences"].update(extracted_info["preferences"])
        def get_preferred_name(self) -> str:
            """Return the user's preferred name if known."""
            name = self.profile.get("preferred_name")
            if name and isinstance(name, str) and len(name) > 1:
                return name
            return None
    
    def add_interest(self, interest: str):
        """Manually add an interest.
        
        Args:
            interest: Interest to add
        """
        if not isinstance(self.profile["interests"], set):
            self.profile["interests"] = set(self.profile.get("interests", []))
        self.profile["interests"].add(interest)
        self.profile["last_updated"] = datetime.now().isoformat()
    
    def add_skill(self, skill: str):
        """Manually add a skill.
        
        Args:
            skill: Skill to add
        """
        if not isinstance(self.profile["skills"], set):
            self.profile["skills"] = set(self.profile.get("skills", []))
        self.profile["skills"].add(skill)
        self.profile["last_updated"] = datetime.now().isoformat()
    
    def set_preference(self, key: str, value):
        """Set a user preference.
        
        Args:
            key: Preference key
            value: Preference value
        """
        self.profile["preferences"][key] = value
        self.profile["last_updated"] = datetime.now().isoformat()
    
    def get_profile(self) -> Dict:
        """Get the current user profile.
        
        Returns:
            Profile dictionary
        """
        return self.profile
    
    def get_profile_summary(self) -> str:
        """Get a text summary of learned information.
        
        Returns:
            Human-readable profile summary
        """
        interests = list(self.profile.get("interests", []))[:5]
        skills = list(self.profile.get("skills", []))[:5]
        prefs = self.profile.get("preferences", {})
        
        summary_parts = []
        
        if interests:
            summary_parts.append(f"Interests: {', '.join(interests)}")
        
        if skills:
            summary_parts.append(f"Skills: {', '.join(skills)}")
        
        if prefs:
            pref_str = ", ".join([f"{k}: {v}" for k, v in list(prefs.items())[:3]])
            summary_parts.append(f"Preferences: {pref_str}")
        
        return "\n".join(summary_parts) if summary_parts else "No learned information yet."
    
    def get_context_for_system_prompt(self) -> str:
        """Get formatted context to include in system prompt.
        
        Returns:
            Formatted profile information for system prompt
        """
        interests = list(self.profile.get("interests", []))[:5]
        skills = list(self.profile.get("skills", []))[:5]
        
        context_parts = []
        
        if interests or skills:
            context_parts.append("What I know about you:")
            if interests:
                context_parts.append(f"- Interests: {', '.join(interests)}")
            if skills:
                context_parts.append(f"- Skills/Knowledge: {', '.join(skills)}")
        
        return "\n".join(context_parts) if context_parts else ""
    
    def to_json_serializable(self) -> Dict:
        """Convert profile to JSON-serializable format.
        
        Returns:
            Profile dict with sets converted to lists
        """
        profile_copy = self.profile.copy()
        
        # Convert sets to lists for JSON serialization
        for key in ["interests", "skills", "hobbies", "mentions"]:
            if isinstance(profile_copy.get(key), set):
                profile_copy[key] = list(profile_copy[key])
        
        return profile_copy
    
    def from_json_data(self, data: Dict):
        """Load profile from JSON data.
        
        Args:
            data: Profile data from JSON file
        """
        self.profile = data
        
        # Convert lists back to sets
        for key in ["interests", "skills", "hobbies"]:
            if key in self.profile and isinstance(self.profile[key], list):
                self.profile[key] = set(self.profile[key])
    
    def get_learning_summary(self) -> str:
        """Get a summary of what the AI has learned about the user.
        
        Returns:
            Summary string for display
        """
        summary = "📚 What I've learned about you:\n"
        
        interests = list(self.profile.get("interests", []))
        skills = list(self.profile.get("skills", []))
        prefs = self.profile.get("preferences", {})
        
        if interests:
            summary += f"• Interested in: {', '.join(interests[:3])}"
            if len(interests) > 3:
                summary += f" (+ {len(interests)-3} more)"
            summary += "\n"
        
        if skills:
            summary += f"• Skilled with: {', '.join(skills[:3])}"
            if len(skills) > 3:
                summary += f" (+ {len(skills)-3} more)"
            summary += "\n"
        
        if prefs:
            summary += f"• Preferences recorded: {len(prefs)}\n"
        
        if not (interests or skills or prefs):
            summary += "Tell me about yourself and I'll learn more!\n"
        
        return summary
