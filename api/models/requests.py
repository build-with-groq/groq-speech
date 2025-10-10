"""
Request models for the Groq Speech API.
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator
from enum import Enum


class AudioFormat(str, Enum):
    """Supported audio formats."""
    WAV = "wav"
    MP3 = "mp3"
    FLAC = "flac"
    WEBM = "webm"
    M4A = "m4a"


class RecognitionMode(str, Enum):
    """Recognition modes."""
    SINGLE = "single"
    CONTINUOUS = "continuous"
    STREAMING = "streaming"


class RecognitionRequest(BaseModel):
    """Request model for speech recognition."""
    
    # Audio data (base64 encoded or file path)
    audio_data: Optional[str] = Field(None, description="Base64 encoded audio data")
    audio_url: Optional[str] = Field(None, description="URL to audio file")
    audio_file: Optional[str] = Field(None, description="Local file path")
    
    # Recognition settings
    language: Optional[str] = Field("en-US", description="Language code for recognition")
    mode: RecognitionMode = Field(RecognitionMode.SINGLE, description="Recognition mode")
    
    # Audio format
    format: AudioFormat = Field(AudioFormat.WAV, description="Audio format")
    sample_rate: Optional[int] = Field(16000, description="Audio sample rate")
    channels: Optional[int] = Field(1, description="Number of audio channels")
    
    # Recognition options
    enable_semantic_segmentation: bool = Field(False, description="Enable semantic segmentation")
    enable_language_identification: bool = Field(False, description="Enable language identification")
    timeout: Optional[float] = Field(30.0, description="Recognition timeout in seconds")
    
    # Custom settings
    custom_settings: Optional[Dict[str, Any]] = Field(None, description="Custom recognition settings")
    
    @validator('audio_data', 'audio_url', 'audio_file')
    def validate_audio_source(cls, v, values):
        """Ensure at least one audio source is provided."""
        if not any([values.get('audio_data'), values.get('audio_url'), values.get('audio_file')]):
            raise ValueError("At least one audio source must be provided")
        return v
    
    @validator('language')
    def validate_language(cls, v):
        """Validate language code format."""
        if v and not v.replace('-', '').isalnum():
            raise ValueError("Invalid language code format")
        return v
    
    @validator('sample_rate')
    def validate_sample_rate(cls, v):
        """Validate sample rate."""
        if v and (v < 8000 or v > 48000):
            raise ValueError("Sample rate must be between 8000 and 48000 Hz")
        return v
    
    @validator('channels')
    def validate_channels(cls, v):
        """Validate channel count."""
        if v and v not in [1, 2]:
            raise ValueError("Channels must be 1 (mono) or 2 (stereo)")
        return v


class AudioUploadRequest(BaseModel):
    """Request model for audio file upload."""
    
    filename: str = Field(..., description="Audio file name")
    content_type: str = Field(..., description="Audio file MIME type")
    file_size: int = Field(..., description="File size in bytes")
    
    # Recognition settings (same as RecognitionRequest)
    language: Optional[str] = Field("en-US", description="Language code for recognition")
    enable_semantic_segmentation: bool = Field(False, description="Enable semantic segmentation")
    enable_language_identification: bool = Field(False, description="Enable language identification")
    timeout: Optional[float] = Field(30.0, description="Recognition timeout in seconds")
    
    @validator('content_type')
    def validate_content_type(cls, v):
        """Validate audio content type."""
        valid_types = [
            'audio/wav', 'audio/mp3', 'audio/flac', 
            'audio/webm', 'audio/m4a', 'audio/mpeg'
        ]
        if v not in valid_types:
            raise ValueError(f"Unsupported content type: {v}")
        return v
    
    @validator('file_size')
    def validate_file_size(cls, v):
        """Validate file size (max 100MB)."""
        max_size = 100 * 1024 * 1024  # 100MB
        if v > max_size:
            raise ValueError(f"File size exceeds maximum limit of {max_size} bytes")
        return v


class StreamingRequest(BaseModel):
    """Request model for streaming recognition."""
    
    # Connection settings
    session_id: Optional[str] = Field(None, description="Session ID for tracking")
    client_id: Optional[str] = Field(None, description="Client identifier")
    
    # Recognition settings
    language: Optional[str] = Field("en-US", description="Language code for recognition")
    enable_semantic_segmentation: bool = Field(False, description="Enable semantic segmentation")
    enable_language_identification: bool = Field(False, description="Enable language identification")
    
    # Audio settings
    sample_rate: Optional[int] = Field(16000, description="Audio sample rate")
    channels: Optional[int] = Field(1, description="Number of audio channels")
    chunk_size: Optional[int] = Field(1024, description="Audio chunk size")
    
    # Streaming options
    buffer_size: Optional[int] = Field(4096, description="Audio buffer size")
    silence_timeout: Optional[float] = Field(1.0, description="Silence timeout in seconds")
    phrase_timeout: Optional[float] = Field(3.0, description="Phrase timeout in seconds")
    
    @validator('session_id')
    def validate_session_id(cls, v):
        """Validate session ID format."""
        if v and not v.replace('-', '').replace('_', '').isalnum():
            raise ValueError("Session ID can only contain alphanumeric characters, hyphens, and underscores")
        return v


class BatchRequest(BaseModel):
    """Request model for batch recognition."""
    
    # Audio files
    audio_files: List[str] = Field(..., description="List of audio file paths or URLs")
    
    # Recognition settings
    language: Optional[str] = Field("en-US", description="Language code for recognition")
    enable_semantic_segmentation: bool = Field(False, description="Enable semantic segmentation")
    enable_language_identification: bool = Field(False, description="Enable language identification")
    
    # Batch options
    max_concurrent: Optional[int] = Field(5, description="Maximum concurrent recognitions")
    timeout_per_file: Optional[float] = Field(30.0, description="Timeout per file in seconds")
    
    @validator('audio_files')
    def validate_audio_files(cls, v):
        """Validate audio files list."""
        if not v:
            raise ValueError("At least one audio file must be provided")
        if len(v) > 100:
            raise ValueError("Maximum 100 files allowed per batch")
        return v
    
    @validator('max_concurrent')
    def validate_max_concurrent(cls, v):
        """Validate max concurrent limit."""
        if v and (v < 1 or v > 20):
            raise ValueError("Max concurrent must be between 1 and 20")
        return v 