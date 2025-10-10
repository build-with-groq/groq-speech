"""
Voice Activity Detection Service using Silero VAD.

This module provides internal VAD functionality for the Groq Speech SDK.
Consumers of the SDK don't need to know about this implementation.
"""

import numpy as np
from typing import List, Tuple, Optional
import threading
from dataclasses import dataclass
import scipy.signal
import time

# Lazy import to avoid loading VAD libraries unless needed
_silero_vad_model = None
_silero_vad_utils = None
_webrtc_vad = None
_vad_available = None
_vad_type = None

def _import_silero_vad():
    """Try to import Silero VAD."""
    try:
        from silero_vad import load_silero_vad
        model, utils = load_silero_vad()
        
        # Test the model to ensure it works
        import torch
        test_audio = torch.randn(16000)
        get_speech_timestamps = utils[0]
        timestamps = get_speech_timestamps(test_audio, model)
        
        return model, utils, "silero"
    except Exception as e:
        return None, None, None

def _import_webrtc_vad():
    """Try to import WebRTC VAD."""
    try:
        import webrtcvad
        vad = webrtcvad.Vad(1)  # Aggressiveness level 1 (0-3) - Medium sensitivity
        return vad, "webrtc"
    except Exception as e:
        return None, None

def _initialize_vad():
    """Initialize the best available VAD."""
    global _silero_vad_model, _silero_vad_utils, _webrtc_vad, _vad_available, _vad_type
    
    if _vad_available is not None:
        return _vad_available
    
    # Try Silero VAD first
    model, utils, vtype = _import_silero_vad()
    if vtype == "silero":
        _silero_vad_model = model
        _silero_vad_utils = utils
        _vad_type = "silero"
        _vad_available = True
        print("✅ Silero VAD loaded and tested successfully")
        return True
    
    # Fallback to WebRTC VAD
    vad, vtype = _import_webrtc_vad()
    if vtype == "webrtc":
        _webrtc_vad = vad
        _vad_type = "webrtc"
        _vad_available = True
        print("✅ WebRTC VAD loaded successfully")
        return True
    
    # No VAD available
    print("⚠️  No VAD libraries available")
    print("💡 Using fallback RMS-based voice activity detection")
    _vad_available = False
    _vad_type = "fallback"
    return False

@dataclass
class VADConfig:
    """Configuration for Voice Activity Detection."""
    threshold: float = 0.2  # Speech detection threshold (0.0-1.0) - Lowered for better sensitivity
    min_speech_duration_ms: int = 100  # Minimum speech duration in milliseconds - Reduced for better detection
    min_silence_duration_ms: int = 2000  # Minimum silence duration in milliseconds (2 seconds) - Much more sensitive
    max_silence_duration_ms: int = 5000  # Maximum silence before forcing chunk (5 seconds)
    sample_rate: int = 16000  # Audio sample rate
    enable_noise_filtering: bool = False  # Disable noise reduction to preserve speech content
    noise_reduction_strength: float = 0.3  # Noise reduction strength (0.0-1.0) - Much more conservative
    webrtc_aggressiveness: int = 0  # WebRTC VAD aggressiveness (0-3, 0 = least aggressive)
    max_chunk_size_mb: float = 20.0  # Maximum chunk size before forcing chunk (20MB to stay under 24MB)

@dataclass
class SpeechSegment:
    """Represents a detected speech segment."""
    start_sample: int
    end_sample: int
    start_time: float
    end_time: float
    duration: float
    confidence: float

class VADService:
    """
    Voice Activity Detection Service using Silero VAD.
    
    This service provides intelligent speech detection and chunking
    for continuous audio streams.
    """
    
    def __init__(self, config: Optional[VADConfig] = None):
        """
        Initialize VAD service.
        
        Args:
            config: VAD configuration, uses defaults if None
        """
        self.config = config or VADConfig()
        self._model = None
        self._get_speech_timestamps = None
        self._is_initialized = False
        self._lock = threading.Lock()
        self._vad_type = None
        self._silence_start_time = None  # Track when silence period started
        self._last_audio_time = None     # Track when we last had audio
        
    def _ensure_initialized(self) -> bool:
        """Ensure VAD model is loaded."""
        with self._lock:
            if self._is_initialized:
                return True
                
            if not _initialize_vad():
                self._vad_type = "fallback"
                return False
                
            try:
                # Access the global _vad_type
                global _vad_type
                if _vad_type == "silero":
                    self._model, utils = _silero_vad_model, _silero_vad_utils
                    self._get_speech_timestamps = utils[0]
                    self._vad_type = "silero"
                elif _vad_type == "webrtc":
                    self._model = _webrtc_vad
                    self._get_speech_timestamps = None  # WebRTC VAD doesn't use this
                    self._vad_type = "webrtc"
                else:
                    self._vad_type = "fallback"
                    return False
                    
                self._is_initialized = True
                return True
            except Exception as e:
                print(f"⚠️  Failed to initialize VAD: {e}")
                self._vad_type = "fallback"
                return False
    
    def _apply_noise_filtering(self, audio_data: np.ndarray, sample_rate: int) -> np.ndarray:
        """
        Apply noise reduction to audio data using multiple techniques.
        
        Args:
            audio_data: Audio data as numpy array
            sample_rate: Audio sample rate
            
        Returns:
            Noise-filtered audio data
        """
        if not self.config.enable_noise_filtering:
            return audio_data
            
        try:
            # Try to import noisereduce
            import noisereduce as nr
            
            # Apply noise reduction with more conservative settings
            filtered_audio = nr.reduce_noise(
                y=audio_data,
                sr=sample_rate,
                prop_decrease=self.config.noise_reduction_strength,
                stationary=False,  # Non-stationary noise (better for speech)
                use_tqdm=False
            )
            
            # Apply additional spectral gating to remove residual noise
            filtered_audio = self._apply_spectral_gating(filtered_audio, sample_rate)
            
            return filtered_audio.astype(audio_data.dtype)
            
        except ImportError:
            # Fallback to simple high-pass filter if noisereduce not available
            return self._apply_simple_noise_filter(audio_data, sample_rate)
        except Exception as e:
            print(f"⚠️  Noise filtering failed: {e}, using original audio")
            return audio_data
    
    def _apply_simple_noise_filter(self, audio_data: np.ndarray, sample_rate: int) -> np.ndarray:
        """
        Apply simple noise filtering using high-pass filter.
        
        Args:
            audio_data: Audio data as numpy array
            sample_rate: Audio sample rate
            
        Returns:
            Filtered audio data
        """
        try:
            # High-pass filter to remove low-frequency noise
            nyquist = sample_rate / 2
            cutoff = 80  # Hz - remove very low frequency noise
            normalized_cutoff = cutoff / nyquist
            
            # Design Butterworth high-pass filter
            b, a = scipy.signal.butter(4, normalized_cutoff, btype='high', analog=False)
            
            # Apply filter
            filtered_audio = scipy.signal.filtfilt(b, a, audio_data)
            
            return filtered_audio.astype(audio_data.dtype)
            
        except Exception as e:
            print(f"⚠️  Simple noise filtering failed: {e}, using original audio")
            return audio_data
    
    def _apply_spectral_gating(self, audio_data: np.ndarray, sample_rate: int) -> np.ndarray:
        """
        Apply spectral gating to remove residual noise.
        
        Args:
            audio_data: Audio data as numpy array
            sample_rate: Audio sample rate
            
        Returns:
            Spectrally gated audio data
        """
        try:
            # Calculate RMS energy
            rms = np.sqrt(np.mean(audio_data**2))
            
            # Only apply gating if audio is very quiet (likely noise)
            if rms < 0.01:  # Very quiet threshold
                # Apply gentle high-pass filter to remove low-frequency noise
                nyquist = sample_rate / 2
                cutoff = 100  # Hz - remove very low frequency noise
                normalized_cutoff = cutoff / nyquist
                
                # Design Butterworth high-pass filter
                b, a = scipy.signal.butter(2, normalized_cutoff, btype='high', analog=False)
                
                # Apply filter
                filtered_audio = scipy.signal.filtfilt(b, a, audio_data)
                
                return filtered_audio.astype(audio_data.dtype)
            else:
                return audio_data
                
        except Exception as e:
            print(f"⚠️  Spectral gating failed: {e}, using original audio")
            return audio_data
    
    def _detect_speech_segments(self, audio_data: np.ndarray, 
                             sample_rate: Optional[int] = None) -> List[SpeechSegment]:
        """
        Detect speech segments in audio data.
        
        Args:
            audio_data: Audio data as numpy array
            sample_rate: Audio sample rate, uses config default if None
            
        Returns:
            List of detected speech segments
        """
        if not self._ensure_initialized():
            return []
            
        sample_rate = sample_rate or self.config.sample_rate
        
        # Apply noise filtering before VAD analysis
        filtered_audio = self._apply_noise_filtering(audio_data, sample_rate)
        
        try:
            if self._vad_type == "silero":
                # Use Silero VAD
                speech_timestamps = self._get_speech_timestamps(
                    filtered_audio,
                    self._model,
                    threshold=self.config.threshold,
                    min_speech_duration_ms=self.config.min_speech_duration_ms,
                    min_silence_duration_ms=self.config.min_silence_duration_ms
                )
                
                # Convert to SpeechSegment objects
                segments = []
                for timestamp in speech_timestamps:
                    start_sample = timestamp['start']
                    end_sample = timestamp['end']
                    start_time = start_sample / sample_rate
                    end_time = end_sample / sample_rate
                    duration = end_time - start_time
                    confidence = timestamp.get('confidence', 0.5)
                    
                    segments.append(SpeechSegment(
                        start_sample=start_sample,
                        end_sample=end_sample,
                        start_time=start_time,
                        end_time=end_time,
                        duration=duration,
                        confidence=confidence
                    ))
                
                return segments
                
            elif self._vad_type == "webrtc":
                # Use WebRTC VAD with pre-filtering for very quiet audio
                import webrtcvad
                
                # WebRTC VAD requires 16-bit PCM audio
                if filtered_audio.dtype != np.int16:
                    # Convert float32 to int16
                    audio_int16 = (filtered_audio * 32767).astype(np.int16)
                else:
                    audio_int16 = filtered_audio
                
                # WebRTC VAD works on 10ms, 20ms, or 30ms frames
                frame_duration_ms = 20
                frame_size = int(sample_rate * frame_duration_ms / 1000)
                
                segments = []
                current_segment_start = None
                
                for i in range(0, len(audio_int16) - frame_size, frame_size):
                    frame = audio_int16[i:i + frame_size]
                    
                    # WebRTC VAD requires exactly the right frame size
                    if len(frame) != frame_size:
                        continue
                    
                    try:
                        # Pre-filter: Skip very quiet frames to reduce false positives
                        frame_rms = np.sqrt(np.mean((frame / 32767.0) ** 2))
                        if frame_rms < 0.01:  # Very quiet threshold
                            # Treat as silence regardless of VAD
                            if current_segment_start is not None:
                                # End current segment
                                end_sample = i + frame_size
                                start_time = current_segment_start / sample_rate
                                end_time = end_sample / sample_rate
                                duration = end_time - start_time
                                
                                if duration >= self.config.min_speech_duration_ms / 1000:
                                    segments.append(SpeechSegment(
                                        start_sample=current_segment_start,
                                        end_sample=end_sample,
                                        start_time=start_time,
                                        end_time=end_time,
                                        duration=duration,
                                        confidence=0.8
                                    ))
                                current_segment_start = None
                            continue
                        
                        is_speech = self._model.is_speech(frame.tobytes(), sample_rate)
                        
                        if is_speech and current_segment_start is None:
                            # Start of speech segment
                            current_segment_start = i
                        elif not is_speech and current_segment_start is not None:
                            # End of speech segment
                            end_sample = i + frame_size
                            start_time = current_segment_start / sample_rate
                            end_time = end_sample / sample_rate
                            duration = end_time - start_time
                            
                            # Only include segments longer than minimum duration
                            if duration >= self.config.min_speech_duration_ms / 1000:
                                segments.append(SpeechSegment(
                                    start_sample=current_segment_start,
                                    end_sample=end_sample,
                                    start_time=start_time,
                                    end_time=end_time,
                                    duration=duration,
                                    confidence=0.8  # WebRTC VAD doesn't provide confidence
                                ))
                            
                            current_segment_start = None
                    except Exception:
                        # Skip frames that cause errors
                        continue
                
                # Handle case where speech continues to end of audio
                if current_segment_start is not None:
                    end_sample = len(audio_int16)
                    start_time = current_segment_start / sample_rate
                    end_time = end_sample / sample_rate
                    duration = end_time - start_time
                    
                    if duration >= self.config.min_speech_duration_ms / 1000:
                        segments.append(SpeechSegment(
                            start_sample=current_segment_start,
                            end_sample=end_sample,
                            start_time=start_time,
                            end_time=end_time,
                            duration=duration,
                            confidence=0.8
                        ))
                
                return segments
            
            else:
                return []
            
        except Exception as e:
            print(f"⚠️  VAD detection failed: {e}")
            return []
    
    
    
    def should_create_chunk(self, audio_data: np.ndarray, 
                          sample_rate: Optional[int] = None,
                          max_duration_seconds: Optional[float] = None) -> Tuple[bool, str]:
        """
        Determine if a chunk should be created based on VAD analysis.
        
        Args:
            audio_data: Audio data as numpy array
            sample_rate: Audio sample rate, uses config default if None
            max_duration_seconds: Maximum duration before forcing chunk
            
        Returns:
            Tuple of (should_create, reason)
        """
        sample_rate = sample_rate or self.config.sample_rate
        duration_seconds = len(audio_data) / sample_rate
        
        # Calculate approximate size in MB (16kHz, 32-bit float = 4 bytes per sample)
        # 1 second = 16,000 samples = 64,000 bytes = 0.064 MB
        estimated_size_mb = (len(audio_data) * 4) / (1024 * 1024)
        
        # PRIORITY 1: Check if we're approaching 24MB limit (conservative threshold)
        if estimated_size_mb >= self.config.max_chunk_size_mb:
            return True, f"Approaching 24MB limit ({estimated_size_mb:.1f}MB)"
        
        # PRIORITY 2: Check if we've hit maximum duration
        if max_duration_seconds and duration_seconds >= max_duration_seconds:
            return True, f"Maximum duration reached ({duration_seconds:.1f}s)"
        
        # PRIORITY 3: Only check for silence if we're NOT approaching the size limit
        # This ensures we prioritize 24MB chunks over silence-based chunking
        if estimated_size_mb < 20.0:  # Only check silence if we're well under the 24MB limit
            # Analyze recent audio (last 5 seconds) for more stable silence detection
            recent_seconds = 5.0
            recent_samples = int(recent_seconds * sample_rate)
            recent_audio = audio_data[-recent_samples:] if len(audio_data) > recent_samples else audio_data
            
            # Get audio levels for recent audio
            recent_rms = np.sqrt(np.mean(recent_audio**2))
            recent_max = np.max(np.abs(recent_audio))
            current_time = time.time()
            
            # Much more conservative silence detection - only trigger on very quiet audio
            practical_silence_threshold = 0.003  # Very low threshold for conservative detection
            
            if recent_rms < practical_silence_threshold and recent_max < 0.01:
                # Recent audio is very quiet - start or continue silence tracking
                if self._silence_start_time is None:
                    self._silence_start_time = current_time
                    return False, f"Silence started (RMS: {recent_rms:.4f}, Max: {recent_max:.4f})"
                
                # Check if we've had enough silence (15 seconds)
                silence_duration = current_time - self._silence_start_time
                required_silence_seconds = 15.0  # 15 seconds of continuous silence required
                if silence_duration >= required_silence_seconds:
                    # Reset silence tracking for next chunk
                    self._silence_start_time = None
                    self._last_audio_time = None
                    return True, f"Silence detected ({silence_duration:.1f}s, RMS: {recent_rms:.4f})"
                
                return False, f"Silence continuing... ({silence_duration:.1f}s, RMS: {recent_rms:.4f})"
            
            else:
                # Recent audio detected - reset silence tracking
                if self._silence_start_time is not None:
                    self._silence_start_time = None
                self._last_audio_time = current_time
                return False, f"Audio detected (RMS: {recent_rms:.4f}, Max: {recent_max:.4f}, {duration_seconds:.1f}s, {estimated_size_mb:.1f}MB)"
        
        # If we're approaching the size limit, don't check for silence - just continue recording
        return False, f"Continuing to 24MB limit ({estimated_size_mb:.1f}MB, {duration_seconds:.1f}s)"
    
    def get_audio_level(self, audio_data: np.ndarray) -> float:
        """
        Get audio level (RMS) for visual feedback.
        
        Args:
            audio_data: Audio data as numpy array
            
        Returns:
            Audio level (0.0-1.0)
        """
        if len(audio_data) == 0:
            return 0.0
        
        rms = np.sqrt(np.mean(audio_data**2))
        # Normalize to 0-1 range (adjust based on typical audio levels)
        return min(rms * 10, 1.0)  # Scale factor may need adjustment

# VAD service is now initialized per SpeechRecognizer instance
# No global VAD service needed - each SpeechRecognizer creates its own VADService
