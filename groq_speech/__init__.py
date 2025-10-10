"""
Groq Speech SDK - Real-time speech recognition and synthesis.

This module provides a comprehensive Python SDK for Groq's speech services,
enabling real-time speech-to-text and text-to-speech capabilities with
advanced AI-powered models.

ARCHITECTURE OVERVIEW:
1. CORE COMPONENTS
   - SpeechConfig: Configuration management for speech services
   - SpeechRecognizer: Main speech recognition engine
   - ResultReason: Recognition result status and categorization

2. CONFIGURATION SYSTEM
   - Config: Centralized configuration management
   - Environment-based configuration with defaults

3. ERROR HANDLING
   - Comprehensive exception hierarchy
   - Detailed error context and debugging
   - User-friendly error messages

KEY FEATURES:
- Real-time speech recognition with Groq's AI models
- Support for both transcription and translation
- Configurable audio processing and optimization
- Comprehensive error handling and debugging
- Environment-based configuration management
- Audio device enumeration and selection
- File-based and microphone-based audio processing
- Performance monitoring and timing metrics
- Event-driven architecture for real-time applications

USAGE EXAMPLES:
    # Basic speech recognition
    from groq_speech import SpeechConfig, SpeechRecognizer

    recognizer = SpeechRecognizer(api_key="your-api-key")
    result = recognizer.recognize_audio_data(audio_data)

    # Translation to English
    recognizer = SpeechRecognizer(api_key="your-api-key", translation_target_language="en")
    result = recognizer.translate_audio_data(audio_data)

    # Continuous recognition
    recognizer.start_continuous_recognition()
    # ... handle events ...
    recognizer.stop_continuous_recognition()

    # Diarization
    from groq_speech import Diarizer

    diarizer = Diarizer()
    result = diarizer.diarize("audio.wav", "transcription")

    # Configuration management
    from groq_speech import Config

    api_key = Config.get_api_key()
"""

from .speech_config import SpeechConfig
from .speech_recognizer import SpeechRecognizer, SpeechRecognitionResult
from .result_reason import ResultReason, CancellationReason
from .speaker_diarization import DiarizationConfig, SpeakerSegment, DiarizationResult, Diarizer
from .audio_utils import AudioFormatUtils
from .exceptions import (
    GroqSpeechException,
    ConfigurationError,
    APIError,
    AudioError,
    DiarizationError,
    VADError
)

# SDK version information
__version__ = "1.0.0"

# Public API exports
# These are the main classes and functions that users should import
__all__ = [
    "SpeechConfig",  # Speech recognition configuration
    "SpeechRecognizer",  # Main speech recognition engine
    "SpeechRecognitionResult",  # Recognition result objects
    "ResultReason",  # Recognition result status
    "CancellationReason",  # Error categorization
    "DiarizationConfig",  # Speaker diarization config
    "SpeakerSegment",  # Individual speaker segment
    "DiarizationResult",  # Complete diarization result
    "Diarizer",  # Simplified diarizer (replaces SpeakerDiarizer and EnhancedDiarizer)
    "AudioFormatUtils",  # Audio format conversion utilities
    # Exception classes
    "GroqSpeechException",  # Base exception
    "ConfigurationError",  # Configuration errors
    "APIError",  # API communication errors
    "AudioError",  # Audio processing errors
    "DiarizationError",  # Diarization errors
    "VADError",  # Voice Activity Detection errors
]
