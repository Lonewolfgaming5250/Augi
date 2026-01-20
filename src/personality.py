"""Personality system for the AI assistant."""
from enum import Enum
from typing import Dict, Optional


class PersonalityType(Enum):
    """Available personality types."""
    PROFESSIONAL = "professional"
    FRIENDLY = "friendly"
    WITTY = "witty"
    HELPFUL = "helpful"
    TECH_SAVVY = "tech_savvy"
    CASUAL = "casual"


class PersonalityProfile:
    """Defines a personality profile for the assistant."""
    
    def __init__(self, name: str, description: str, system_prompt_addition: str, 
                 greeting: str, farewell: str, response_style: str):
        """Initialize personality profile.
        
        Args:
            name: Personality name
            description: Description of the personality
            system_prompt_addition: Text to add to system prompt
            greeting: Greeting message
            farewell: Farewell message
            response_style: Description of response style
        """
        self.name = name
        self.description = description
        self.system_prompt_addition = system_prompt_addition
        self.greeting = greeting
        self.farewell = farewell
        self.response_style = response_style


class PersonalityManager:
    """Manages AI personality profiles."""
    
    PERSONALITIES: Dict[PersonalityType, PersonalityProfile] = {
        PersonalityType.PROFESSIONAL: PersonalityProfile(
            name="Professional",
            description="Formal, efficient, business-like",
            system_prompt_addition="""You are a professional AI assistant. Be formal, efficient, and business-like in your responses.
Focus on clarity, accuracy, and practical solutions. Use professional language and maintain a respectful tone.""",
            greeting="Good day. I'm ready to assist you with your tasks.",
            farewell="Thank you for using my services. Have a productive day.",
            response_style="Formal and straightforward"
        ),
        
        PersonalityType.FRIENDLY: PersonalityProfile(
            name="Friendly",
            description="Warm, approachable, conversational",
            system_prompt_addition="""You are a friendly, approachable AI assistant. Be warm and conversational in your responses.
Use a friendly tone, feel free to use casual language, and make the user feel valued. Show genuine interest in helping.""",
            greeting="Hey there! I'm here to help you out. What can I do for you?",
            farewell="Thanks for chatting with me! Feel free to come back anytime. Catch you later!",
            response_style="Warm and conversational"
        ),
        
        PersonalityType.WITTY: PersonalityProfile(
            name="Witty",
            description="Clever, humorous, entertaining",
            system_prompt_addition="""You are a witty and humorous AI assistant. Use clever wordplay, light humor, and entertaining responses.
Be entertaining while still being helpful. Make the interaction enjoyable and memorable.""",
            greeting="Well, hello there! Ready to have some fun while getting things done?",
            farewell="It's been a pleasure! May your code compile on the first try. Peace!",
            response_style="Clever and humorous"
        ),
        
        PersonalityType.HELPFUL: PersonalityProfile(
            name="Helpful",
            description="Focused on assistance, patient, educational",
            system_prompt_addition="""You are a genuinely helpful AI assistant. Be patient, thorough, and educational in your responses.
Explain things clearly, provide detailed guidance, and make sure the user understands. Focus on being truly useful.""",
            greeting="Hello! I'm here to help you with whatever you need. Don't hesitate to ask questions!",
            farewell="I hope I was able to help! Feel free to ask if you need anything else.",
            response_style="Patient and educational"
        ),
        
        PersonalityType.TECH_SAVVY: PersonalityProfile(
            name="Tech Savvy",
            description="Technical, knowledgeable, developer-focused",
            system_prompt_addition="""You are a tech-savvy AI assistant with deep technical knowledge. Use technical terminology appropriately,
reference programming concepts, and provide developer-friendly solutions. Be knowledgeable and precise.""",
            greeting="System initialized. Tech mode activated. What's on your agenda?",
            farewell="Process complete. Keep coding and debugging. Out.",
            response_style="Technical and developer-focused"
        ),
        
        PersonalityType.CASUAL: PersonalityProfile(
            name="Casual",
            description="Laid-back, relaxed, easygoing",
            system_prompt_addition="""You are a casual, laid-back AI assistant. Be relaxed and easygoing in your responses.
Use informal language, be chill about things, and create a low-pressure environment. Keep things simple and fun.""",
            greeting="Yo! What's up? I'm here to help with whatever you need.",
            farewell="Alright, catch you later! No stress, you got this!",
            response_style="Laid-back and casual"
        ),
    }
    
    def __init__(self, personality: PersonalityType = PersonalityType.FRIENDLY):
        """Initialize personality manager.
        
        Args:
            personality: Initial personality type
        """
        self.current_personality = personality
        self.profile = self.PERSONALITIES[personality]
    
    def set_personality(self, personality: PersonalityType) -> PersonalityProfile:
        """Set the current personality.
        
        Args:
            personality: Personality type to set
            
        Returns:
            The new personality profile
        """
        self.current_personality = personality
        self.profile = self.PERSONALITIES[personality]
        return self.profile
    
    def set_personality_by_name(self, name: str) -> Optional[PersonalityProfile]:
        """Set personality by name string.
        
        Args:
            name: Personality name (case-insensitive)
            
        Returns:
            The new personality profile or None if not found
        """
        try:
            personality = PersonalityType[name.upper()]
            return self.set_personality(personality)
        except KeyError:
            return None
    
    def get_system_prompt_addition(self) -> str:
        """Get system prompt addition for current personality.
        
        Returns:
            System prompt addition text
        """
        return self.profile.system_prompt_addition
    
    def get_greeting(self) -> str:
        """Get personalized greeting.
        
        Returns:
            Greeting message
        """
        return self.profile.greeting
    
    def get_farewell(self) -> str:
        """Get personalized farewell.
        
        Returns:
            Farewell message
        """
        return self.profile.farewell
    
    def list_personalities(self) -> Dict[str, str]:
        """Get list of available personalities.
        
        Returns:
            Dictionary of {name: description}
        """
        return {
            p.name.lower(): f"{p.name}: {p.description}"
            for p in self.PERSONALITIES.values()
        }
    
    def get_current_personality_name(self) -> str:
        """Get current personality name.
        
        Returns:
            Current personality name
        """
        return self.profile.name
    
    def get_current_personality_description(self) -> str:
        """Get current personality description.
        
        Returns:
            Current personality description
        """
        return self.profile.description
