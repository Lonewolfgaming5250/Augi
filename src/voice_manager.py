"""Voice support for AI assistant - speech-to-text and text-to-speech."""
import os
import sys
from typing import Optional


class VoiceManager:
    """Manages voice input/output for the AI assistant."""
    
    def __init__(self, enable_tts: bool = True, enable_stt: bool = True):
        """Initialize voice manager.
        
        Args:
            enable_tts: Enable text-to-speech (speaking responses)
            enable_stt: Enable speech-to-text (voice commands)
        """
        self.enable_tts = enable_tts
        self.enable_stt = enable_stt
        self.tts_engine = None
        self.recognizer = None
        
        # Initialize TTS (text-to-speech) if enabled
        if enable_tts:
            try:
                import pyttsx3
                self.tts_engine = pyttsx3.init()
                self.tts_engine.setProperty('rate', 150)  # Speed
                self.tts_engine.setProperty('volume', 0.9)  # Volume
                print("✓ Text-to-speech initialized")
            except Exception as e:
                print(f"⚠ Text-to-speech unavailable: {e}")
                self.enable_tts = False
        
        # Initialize STT (speech-to-text) if enabled
        if enable_stt:
            try:
                import speech_recognition as sr
                self.recognizer = sr.Recognizer()
                # Try to use default microphone
                self.mic = sr.Microphone()
                print("✓ Speech recognition initialized")
            except Exception as e:
                print(f"⚠ Speech recognition unavailable: {e}")
                print("   Install: pip install SpeechRecognition pyaudio")
                self.enable_stt = False
    
    def speak(self, text: str) -> bool:
        """Speak text using text-to-speech.
        
        Args:
            text: Text to speak
            
        Returns:
            True if successful, False otherwise
        """
        if not self.enable_tts or not self.tts_engine:
            return False
        
        try:
            print(f"\n🔊 Speaking: {text[:100]}..." if len(text) > 100 else f"\n🔊 Speaking: {text}")
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
            return True
        except Exception as e:
            print(f"Error speaking: {e}")
            return False
    
    def listen(self, timeout: int = 10) -> Optional[str]:
        """Listen for voice input and convert to text.
        
        Args:
            timeout: Seconds to listen for
            
        Returns:
            Recognized text or None if failed
        """
        if not self.enable_stt or not self.recognizer:
            return None
        
        try:
            import speech_recognition as sr
            
            print("\n🎤 Listening..." if timeout <= 10 else "\n🎤 Listening (timeout in 30s)...")
            
            with self.mic as source:
                # Adjust for ambient noise
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                
                try:
                    # Listen for audio
                    audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=timeout)
                    print("🔄 Processing speech...")
                    
                    # Try to recognize using Google Speech Recognition (free, online but requires internet)
                    try:
                        text = self.recognizer.recognize_google(audio)
                        print(f"✓ Recognized: {text}")
                        return text
                    except sr.UnknownAudioException:
                        print("⚠ Could not understand audio")
                        return None
                    except sr.RequestError:
                        print("⚠ Internet required for speech recognition")
                        print("   (Google Speech-to-Text requires online connection)")
                        return None
                        
                except sr.WaitTimeoutError:
                    print("⚠ No speech detected (timeout)")
                    return None
                    
        except Exception as e:
            print(f"Error listening: {e}")
            return None
    
    def toggle_tts(self) -> bool:
        """Toggle text-to-speech on/off."""
        self.enable_tts = not self.enable_tts
        status = "enabled" if self.enable_tts else "disabled"
        print(f"🔊 Text-to-speech {status}")
        return self.enable_tts
    
    def toggle_stt(self) -> bool:
        """Toggle speech-to-text on/off."""
        self.enable_stt = not self.enable_stt
        status = "enabled" if self.enable_stt else "disabled"
        print(f"🎤 Speech-to-text {status}")
        return self.enable_stt
    
    def get_status(self) -> str:
        """Get current voice status."""
        tts_status = "✓ Enabled" if self.enable_tts else "✗ Disabled"
        stt_status = "✓ Enabled" if self.enable_stt else "✗ Disabled"
        return f"Text-to-Speech: {tts_status}\nSpeech-to-Text: {stt_status}"
    
    def is_available(self) -> bool:
        """Check if any voice features are available."""
        return self.enable_tts or self.enable_stt


class SimpleVoiceManager:
    """Fallback voice manager with just TTS (no STT dependencies)."""
    
    def __init__(self):
        """Initialize simple voice manager with TTS only."""
        self.tts_engine = None
        self.enable_tts = True
        self.enable_stt = False
        
        try:
            import pyttsx3
            self.tts_engine = pyttsx3.init()
            self.tts_engine.setProperty('rate', 150)
            self.tts_engine.setProperty('volume', 0.9)
            print("✓ Text-to-speech (output only) initialized")
        except Exception as e:
            print(f"⚠ Text-to-speech unavailable: {e}")
            self.enable_tts = False
    
    def speak(self, text: str) -> bool:
        """Speak text."""
        if not self.enable_tts or not self.tts_engine:
            return False
        
        try:
            print(f"\n🔊 Speaking: {text[:100]}..." if len(text) > 100 else f"\n🔊 Speaking: {text}")
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
            return True
        except Exception as e:
            print(f"Error speaking: {e}")
            return False
    
    def listen(self, timeout: int = 10) -> Optional[str]:
        """Listen not implemented in simple mode."""
        return None
    
    def toggle_tts(self) -> bool:
        """Toggle TTS."""
        self.enable_tts = not self.enable_tts
        status = "enabled" if self.enable_tts else "disabled"
        print(f"🔊 Text-to-speech {status}")
        return self.enable_tts
    
    def toggle_stt(self) -> bool:
        """STT not available."""
        print("⚠ Speech-to-text requires: pip install SpeechRecognition pyaudio")
        return False
    
    def get_status(self) -> str:
        """Get status."""
        tts_status = "✓ Enabled" if self.enable_tts else "✗ Disabled"
        return f"Text-to-Speech: {tts_status}\nSpeech-to-Text: ✗ Disabled (requires SpeechRecognition)"
    
    def is_available(self) -> bool:
        """Check availability."""
        return self.enable_tts
