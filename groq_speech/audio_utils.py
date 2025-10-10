"""
Audio format utilities for Groq Speech SDK.

This module provides centralized audio format conversion and processing utilities
that are used across different components (CLI, API, UI) to ensure consistency
and eliminate code duplication.

Key Features:
- Base64 audio decoding with format detection
- WAV and raw PCM format handling
- Audio data validation and conversion
- Consistent error handling across all consumers

ARCHITECTURE:
- Centralized audio processing logic
- Format-agnostic conversion utilities
- Consistent error handling and logging
- Reusable across CLI, API, and UI components

USAGE EXAMPLES:
    # Decode base64 audio data
    audio_array, sample_rate = AudioFormatUtils.decode_base64_audio(base64_data)
    
    # Detect audio format
    format_type = AudioFormatUtils.detect_audio_format(audio_bytes)
    
    # Convert to numpy array
    audio_array = AudioFormatUtils.convert_to_numpy(audio_bytes, sample_rate=16000)
"""

import base64
import io
import tempfile
import os
from typing import Tuple
import numpy as np
import soundfile as sf

from .logging_utils import get_logger

logger = get_logger(__name__)


class AudioFormatUtils:
    """Centralized audio format conversion utilities."""
    
    @staticmethod
    def decode_base64_audio(base64_data: str) -> Tuple[np.ndarray, int]:
        """
        Decode base64 audio data to numpy array and sample rate.
        
        This method handles both WAV and raw PCM formats, automatically detecting
        the format and converting to the appropriate numpy array representation.
        
        Args:
            base64_data: Base64-encoded audio data
            
        Returns:
            Tuple of (audio_array, sample_rate) where:
            - audio_array: numpy array of float32 audio samples
            - sample_rate: integer sample rate in Hz
            
        Raises:
            ValueError: If audio data cannot be decoded
            RuntimeError: If audio format is not supported
        """
        try:
            audio_bytes = base64.b64decode(base64_data)
            return AudioFormatUtils._decode_audio_bytes(audio_bytes)
        except Exception as e:
            logger.error(f"Failed to decode base64 audio data: {e}")
            raise ValueError(f"Invalid base64 audio data: {e}")
    
    @staticmethod
    def decode_audio_bytes(audio_bytes: bytes) -> Tuple[np.ndarray, int]:
        """
        Decode raw audio bytes to numpy array and sample rate.
        
        This method handles both WAV and raw PCM formats, automatically detecting
        the format and converting to the appropriate numpy array representation.
        
        Args:
            audio_bytes: Raw audio data bytes
            
        Returns:
            Tuple of (audio_array, sample_rate) where:
            - audio_array: numpy array of float32 audio samples
            - sample_rate: integer sample rate in Hz
            
        Raises:
            ValueError: If audio data cannot be decoded
            RuntimeError: If audio format is not supported
        """
        return AudioFormatUtils._decode_audio_bytes(audio_bytes)
    
    @staticmethod
    def _decode_audio_bytes(audio_bytes: bytes) -> Tuple[np.ndarray, int]:
        """
        Internal method to decode audio bytes with format detection.
        
        Args:
            audio_bytes: Raw audio data bytes
            
        Returns:
            Tuple of (audio_array, sample_rate)
        """
        # Try to decode as WAV file first (proper audio format)
        try:
            audio_array_float, sample_rate = sf.read(io.BytesIO(audio_bytes))
            logger.debug(f"Decoded as WAV: {len(audio_array_float)} samples, {sample_rate}Hz")
            logger.debug(f"Audio range: {audio_array_float.min():.4f} to {audio_array_float.max():.4f}")
            return audio_array_float, sample_rate
        except Exception as e:
            logger.debug(f"Not a WAV file, decoding as raw PCM: {e}")
            # Fallback to raw PCM int16 (standard behavior for frontend audio data)
            audio_array = np.frombuffer(audio_bytes, dtype=np.int16)
            audio_array_float = audio_array.astype(np.float32) / 32768.0
            sample_rate = 16000
            logger.debug(f"Decoded as raw PCM: {len(audio_array)} samples, {sample_rate}Hz")
            logger.debug(f"Audio range: {audio_array_float.min():.4f} to {audio_array_float.max():.4f}")
            return audio_array_float, sample_rate
    
    @staticmethod
    def detect_audio_format(audio_bytes: bytes) -> str:
        """
        Detect the format of audio data.
        
        Args:
            audio_bytes: Raw audio data bytes
            
        Returns:
            String indicating the detected format: 'wav', 'pcm', or 'unknown'
        """
        try:
            # Try to read as WAV
            sf.read(io.BytesIO(audio_bytes))
            return 'wav'
        except Exception:
            # Assume raw PCM if WAV fails
            return 'pcm'
    
    @staticmethod
    def convert_to_numpy(audio_bytes: bytes, sample_rate: int = 16000) -> np.ndarray:
        """
        Convert audio bytes to numpy array with specified sample rate.
        
        This method is used for raw PCM data where the sample rate is known.
        
        Args:
            audio_bytes: Raw audio data bytes
            sample_rate: Sample rate in Hz (default: 16000)
            
        Returns:
            numpy array of float32 audio samples
        """
        audio_array = np.frombuffer(audio_bytes, dtype=np.int16)
        audio_array_float = audio_array.astype(np.float32) / 32768.0
        logger.debug(f"Converted to numpy: {len(audio_array)} samples, {sample_rate}Hz")
        return audio_array_float
    
    @staticmethod
    def convert_list_to_numpy(audio_data: list, sample_rate: int = 16000) -> np.ndarray:
        """
        Convert list of audio samples to numpy array.
        
        This method is used for microphone data received as JSON arrays.
        
        Args:
            audio_data: List of audio samples (typically from JSON)
            sample_rate: Sample rate in Hz (default: 16000)
            
        Returns:
            numpy array of float32 audio samples
        """
        audio_array = np.array(audio_data, dtype=np.float32)
        logger.debug(f"Converted list to numpy: {len(audio_array)} samples, {sample_rate}Hz")
        return audio_array
    
    @staticmethod
    def save_audio_to_temp_file(audio_array: np.ndarray, sample_rate: int, 
                               suffix: str = ".wav") -> str:
        """
        Save audio array to a temporary file.
        
        This method is used for diarization processing which requires file input.
        
        Args:
            audio_array: numpy array of audio samples
            sample_rate: Sample rate in Hz
            suffix: File suffix (default: ".wav")
            
        Returns:
            Path to the temporary file
        """
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as temp_file:
            temp_path = temp_file.name
            sf.write(temp_path, audio_array, sample_rate)
            logger.debug(f"Saved audio to temp file: {temp_path}")
            return temp_path
    
    @staticmethod
    def cleanup_temp_file(file_path: str) -> None:
        """
        Clean up a temporary file.
        
        Args:
            file_path: Path to the file to delete
        """
        try:
            if os.path.exists(file_path):
                os.unlink(file_path)
                logger.debug(f"Cleaned up temp file: {file_path}")
        except Exception as e:
            logger.warning(f"Failed to cleanup temp file {file_path}: {e}")
    
    @staticmethod
    def validate_audio_data(audio_array: np.ndarray, sample_rate: int) -> bool:
        """
        Validate audio data for processing.
        
        Args:
            audio_array: numpy array of audio samples
            sample_rate: Sample rate in Hz
            
        Returns:
            True if audio data is valid, False otherwise
        """
        if len(audio_array) == 0:
            logger.warning("Audio data is empty")
            return False
        
        if sample_rate <= 0:
            logger.warning(f"Invalid sample rate: {sample_rate}")
            return False
        
        if not np.isfinite(audio_array).all():
            logger.warning("Audio data contains non-finite values")
            return False
        
        logger.debug(f"Audio data validation passed: {len(audio_array)} samples, {sample_rate}Hz")
        return True
    
    @staticmethod
    def get_audio_info(audio_array: np.ndarray, sample_rate: int) -> dict:
        """
        Get information about audio data.
        
        Args:
            audio_array: numpy array of audio samples
            sample_rate: Sample rate in Hz
            
        Returns:
            Dictionary with audio information
        """
        duration = len(audio_array) / sample_rate
        return {
            "samples": len(audio_array),
            "sample_rate": sample_rate,
            "duration": duration,
            "duration_minutes": duration / 60,
            "min_value": float(audio_array.min()),
            "max_value": float(audio_array.max()),
            "rms": float(np.sqrt(np.mean(audio_array ** 2))),
            "is_valid": AudioFormatUtils.validate_audio_data(audio_array, sample_rate)
        }
