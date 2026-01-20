"""Main entry point for Personal AI Assistant."""
import os
from dotenv import load_dotenv
from src.ai_assistant import PersonalAIAssistant


def main():
    """Main function to run the AI assistant."""
    # Load environment variables
    load_dotenv()
    
    # Check for API key
    if not os.getenv('ANTHROPIC_API_KEY'):
        print("⚠️  Error: ANTHROPIC_API_KEY not found in environment variables")
        print("Please set your API key: set ANTHROPIC_API_KEY=your-key-here")
        return
    
    # Get wake word settings
    wake_word = os.getenv('WAKE_WORD', 'augi').lower()
    enable_wake_word = os.getenv('ENABLE_WAKE_WORD', 'true').lower() == 'true'
    
    # Get personality setting
    personality = os.getenv('PERSONALITY', 'friendly').lower()
    
    # Get learning and memory settings
    enable_learning = os.getenv('ENABLE_LEARNING', 'true').lower() == 'true'
    load_last_session = os.getenv('LOAD_LAST_SESSION', 'false').lower() == 'true'
    
    # Get voice settings
    enable_voice = os.getenv('ENABLE_VOICE', 'false').lower() == 'true'
    
    # Initialize and run assistant
    assistant = PersonalAIAssistant(
        wake_word=wake_word, 
        enable_wake_word=enable_wake_word, 
        personality=personality,
        enable_learning=enable_learning,
        load_last_session=load_last_session,
        enable_voice=enable_voice
    )
    assistant.chat()


if __name__ == "__main__":
    main()
