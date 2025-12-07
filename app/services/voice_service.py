"""Voice Service - Speech Recognition and Text-to-Speech."""
import logging
import speech_recognition as sr
import pyttsx3
import io
import wave
from typing import Optional

logger = logging.getLogger(__name__)


class VoiceService:
    """Handle speech recognition and text-to-speech conversion."""

    def __init__(self):
        """Initialize voice service with recognizer and TTS engine."""
        self.recognizer = sr.Recognizer()
        self.tts_engine = pyttsx3.init()
        self.tts_engine.setProperty('rate', 150)  # Words per minute
        self.tts_engine.setProperty('volume', 0.9)  # Volume (0.0 to 1.0)
        logger.info('VoiceService initialized')

    def transcribe_audio(self, audio_data: bytes) -> Optional[str]:
        """Convert audio bytes to text using Google Speech Recognition.
        
        Args:
            audio_data: Audio data in bytes format
            
        Returns:
            Transcribed text or None if recognition fails
        """
        try:
            # Convert bytes to audio data
            audio = sr.AudioData(audio_data, 16000, 2)
            
            # Use Google Speech Recognition
            text = self.recognizer.recognize_google(audio, language='en-US')
            logger.info(f'Transcribed: {text}')
            return text
            
        except sr.UnknownValueError:
            logger.warning('Could not understand audio')
            return None
        except sr.RequestError as e:
            logger.error(f'Speech recognition error: {str(e)}')
            return None
        except Exception as e:
            logger.error(f'Error in transcribe_audio: {str(e)}')
            return None

    def text_to_speech(self, text: str) -> Optional[bytes]:
        """Convert text to speech audio bytes.
        
        Args:
            text: Text to convert to speech
            
        Returns:
            Audio bytes or None if conversion fails
        """
        try:
            # Create temporary file-like object
            audio_buffer = io.BytesIO()
            
            # Configure TTS engine for the conversion
            self.tts_engine.save_to_file(text, 'temp_audio.wav')
            self.tts_engine.runAndWait()
            
            # Read the generated file
            with open('temp_audio.wav', 'rb') as audio_file:
                audio_bytes = audio_file.read()
            
            logger.info(f'Generated speech for: {text[:50]}...')
            return audio_bytes
            
        except Exception as e:
            logger.error(f'Error in text_to_speech: {str(e)}')
            return None

    def record_audio(self, duration: int = 5) -> Optional[bytes]:
        """Record audio from microphone.
        
        Args:
            duration: Recording duration in seconds
            
        Returns:
            Audio bytes or None if recording fails
        """
        try:
            with sr.Microphone() as source:
                logger.info('Recording audio...')
                audio = self.recognizer.listen(source, timeout=duration)
                return audio.get_wav_data()
                
        except sr.RequestError:
            logger.error('Microphone not available')
            return None
        except Exception as e:
            logger.error(f'Error in record_audio: {str(e)}')
            return None

    def get_audio_level(self, audio_data: bytes) -> float:
        """Calculate audio level from audio bytes.
        
        Args:
            audio_data: Audio data in bytes
            
        Returns:
            Audio level as float (0.0 to 1.0)
        """
        try:
            import numpy as np
            # Convert bytes to numpy array
            audio_array = np.frombuffer(audio_data, dtype=np.int16)
            # Calculate RMS (Root Mean Square) level
            rms_level = np.sqrt(np.mean(audio_array ** 2))
            # Normalize to 0.0-1.0 range
            return min(1.0, rms_level / 32768.0)
        except Exception as e:
            logger.error(f'Error calculating audio level: {str(e)}')
            return 0.0

    def set_voice_properties(self, rate: int = 150, volume: float = 0.9) -> None:
        """Set TTS voice properties.
        
        Args:
            rate: Words per minute (50-300)
            volume: Volume level (0.0-1.0)
        """
        try:
            self.tts_engine.setProperty('rate', max(50, min(300, rate)))
            self.tts_engine.setProperty('volume', max(0.0, min(1.0, volume)))
            logger.info(f'Voice properties set: rate={rate}, volume={volume}')
        except Exception as e:
            logger.error(f'Error setting voice properties: {str(e)}')
