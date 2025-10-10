"""
Exception hierarchy for Groq Speech SDK.

This module provides a comprehensive exception hierarchy for the Groq Speech SDK,
enabling consistent error handling and providing clear error context for debugging
and user feedback.

ARCHITECTURE OVERVIEW:
1. EXCEPTION HIERARCHY
   - Base exception for all SDK errors
   - Specific exception types for different error categories
   - Consistent error context and messaging

2. ERROR CATEGORIES
   - Configuration errors: Invalid settings or missing credentials
   - API errors: Communication with Groq API
   - Audio errors: Audio processing and format issues
   - Diarization errors: Speaker diarization specific issues
   - VAD errors: Voice Activity Detection issues

3. ERROR CONTEXT
   - Detailed error messages with context
   - Error codes for programmatic handling
   - Suggested solutions and recovery strategies

KEY FEATURES:
- Hierarchical exception structure
- Consistent error messaging
- Error context and debugging information
- Recovery suggestions
- Programmatic error handling support

USAGE EXAMPLES:
    try:
        result = recognizer.recognize_file("audio.wav")
    except APIError as e:
        print(f"API Error: {e}")
        print(f"Error Code: {e.error_code}")
        print(f"Suggested Fix: {e.suggestion}")
    except AudioError as e:
        print(f"Audio Error: {e}")
        print(f"File: {e.file_path}")
"""

from typing import Optional, Dict, Any


class GroqSpeechException(Exception):
    """
    Base exception for all Groq Speech SDK errors.
    
    This is the root exception class that all other SDK exceptions inherit from.
    It provides common functionality for error context, suggestions, and debugging.
    """
    
    def __init__(
        self, 
        message: str, 
        error_code: Optional[str] = None,
        suggestion: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize Groq Speech exception.
        
        Args:
            message: Human-readable error message
            error_code: Machine-readable error code
            suggestion: Suggested fix or recovery action
            context: Additional context information
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.suggestion = suggestion
        self.context = context or {}
    
    def __str__(self) -> str:
        """String representation with context."""
        base_msg = self.message
        if self.error_code:
            base_msg = f"[{self.error_code}] {base_msg}"
        if self.suggestion:
            base_msg = f"{base_msg}\nSuggestion: {self.suggestion}"
        return base_msg


class ConfigurationError(GroqSpeechException):
    """
    Exception raised for configuration-related errors.
    
    This includes missing API keys, invalid configuration values,
    and environment setup issues.
    """
    
    def __init__(
        self, 
        message: str, 
        config_key: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize configuration error.
        
        Args:
            message: Error message
            config_key: Configuration key that caused the error
            **kwargs: Additional arguments for base exception
        """
        super().__init__(message, **kwargs)
        self.config_key = config_key


class APIError(GroqSpeechException):
    """
    Exception raised for Groq API communication errors.
    
    This includes network issues, API rate limits, authentication failures,
    and service unavailability.
    """
    
    def __init__(
        self, 
        message: str, 
        status_code: Optional[int] = None,
        api_endpoint: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize API error.
        
        Args:
            message: Error message
            status_code: HTTP status code from API
            api_endpoint: API endpoint that failed
            **kwargs: Additional arguments for base exception
        """
        super().__init__(message, **kwargs)
        self.status_code = status_code
        self.api_endpoint = api_endpoint


class AudioError(GroqSpeechException):
    """
    Exception raised for audio processing errors.
    
    This includes unsupported audio formats, corrupted audio files,
    audio processing failures, and audio quality issues.
    """
    
    def __init__(
        self, 
        message: str, 
        file_path: Optional[str] = None,
        audio_format: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize audio error.
        
        Args:
            message: Error message
            file_path: Path to audio file that caused the error
            audio_format: Audio format that caused the error
            **kwargs: Additional arguments for base exception
        """
        super().__init__(message, **kwargs)
        self.file_path = file_path
        self.audio_format = audio_format


class DiarizationError(GroqSpeechException):
    """
    Exception raised for speaker diarization errors.
    
    This includes Pyannote.audio failures, speaker detection issues,
    and diarization processing errors.
    """
    
    def __init__(
        self, 
        message: str, 
        diarization_step: Optional[str] = None,
        speaker_count: Optional[int] = None,
        **kwargs
    ):
        """
        Initialize diarization error.
        
        Args:
            message: Error message
            diarization_step: Step in diarization pipeline that failed
            speaker_count: Number of speakers detected (if any)
            **kwargs: Additional arguments for base exception
        """
        super().__init__(message, **kwargs)
        self.diarization_step = diarization_step
        self.speaker_count = speaker_count


class VADError(GroqSpeechException):
    """
    Exception raised for Voice Activity Detection errors.
    
    This includes VAD model loading failures, audio analysis errors,
    and VAD processing issues.
    """
    
    def __init__(
        self, 
        message: str, 
        vad_type: Optional[str] = None,
        audio_duration: Optional[float] = None,
        **kwargs
    ):
        """
        Initialize VAD error.
        
        Args:
            message: Error message
            vad_type: Type of VAD that failed (Silero, WebRTC, RMS)
            audio_duration: Duration of audio being processed
            **kwargs: Additional arguments for base exception
        """
        super().__init__(message, **kwargs)
        self.vad_type = vad_type
        self.audio_duration = audio_duration


# Convenience functions for common error scenarios
def create_configuration_error(
    config_key: str, 
    message: Optional[str] = None
) -> ConfigurationError:
    """Create a configuration error with standard message."""
    if not message:
        message = f"Configuration error for '{config_key}'. Please check your settings."
    
    suggestion = f"Verify that '{config_key}' is properly configured in your environment or .env file."
    
    return ConfigurationError(
        message=message,
        config_key=config_key,
        error_code="CONFIG_ERROR",
        suggestion=suggestion
    )


def create_api_error(
    message: str,
    status_code: Optional[int] = None,
    api_endpoint: Optional[str] = None
) -> APIError:
    """Create an API error with standard context."""
    suggestion = "Check your API key, network connection, and try again."
    if status_code == 401:
        suggestion = "Check your API key and ensure it's valid."
    elif status_code == 429:
        suggestion = "Rate limit exceeded. Please wait and try again."
    elif status_code == 500:
        suggestion = "Service temporarily unavailable. Please try again later."
    
    return APIError(
        message=message,
        status_code=status_code,
        api_endpoint=api_endpoint,
        error_code="API_ERROR",
        suggestion=suggestion
    )


def create_audio_error(
    message: str,
    file_path: Optional[str] = None,
    audio_format: Optional[str] = None
) -> AudioError:
    """Create an audio error with standard context."""
    suggestion = "Check that the audio file is valid and in a supported format (WAV, MP3, etc.)."
    if audio_format:
        suggestion = f"Audio format '{audio_format}' is not supported. Please convert to WAV format."
    
    return AudioError(
        message=message,
        file_path=file_path,
        audio_format=audio_format,
        error_code="AUDIO_ERROR",
        suggestion=suggestion
    )


def create_diarization_error(
    message: str,
    diarization_step: Optional[str] = None,
    speaker_count: Optional[int] = None
) -> DiarizationError:
    """Create a diarization error with standard context."""
    suggestion = "Check your HF_TOKEN and ensure Pyannote.audio is properly installed."
    if diarization_step == "speaker_detection":
        suggestion = "Speaker detection failed. Check audio quality and try with clearer audio."
    elif diarization_step == "grouping":
        suggestion = "Speaker grouping failed. Try adjusting diarization parameters."
    
    return DiarizationError(
        message=message,
        diarization_step=diarization_step,
        speaker_count=speaker_count,
        error_code="DIARIZATION_ERROR",
        suggestion=suggestion
    )


def create_vad_error(
    message: str,
    vad_type: Optional[str] = None,
    audio_duration: Optional[float] = None
) -> VADError:
    """Create a VAD error with standard context."""
    suggestion = "Voice Activity Detection failed. Check audio quality and try again."
    if vad_type == "Silero":
        suggestion = "Silero VAD failed. Falling back to WebRTC VAD or RMS-based detection."
    elif vad_type == "WebRTC":
        suggestion = "WebRTC VAD failed. Using RMS-based voice activity detection."
    
    return VADError(
        message=message,
        vad_type=vad_type,
        audio_duration=audio_duration,
        error_code="VAD_ERROR",
        suggestion=suggestion
    )
