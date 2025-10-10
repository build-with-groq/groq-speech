"""
Speaker Diarization and Segmentation for Groq Speech services.

This module provides speaker diarization capabilities that integrate seamlessly
with the existing Groq Speech SDK. It uses Pyannote.audio for efficient
speaker segmentation and then processes each segment through Groq's API.

ARCHITECTURE OVERVIEW:
1. CORE COMPONENTS
   - SpeakerDiarizer: Main class for speaker diarization operations
   - DiarizationResult: Structured results with speaker information
   - SpeakerSegment: Individual speaker segment with metadata
   - AudioSegmenter: Audio segmentation and preprocessing

2. DIARIZATION PIPELINE
   - Voice Activity Detection (VAD)
   - Speaker embedding extraction
   - Speaker clustering and segmentation
   - Segment validation and optimization

3. GROQ INTEGRATION
   - Batch processing of speaker segments
   - Transcription with speaker labels
   - Confidence scoring and validation
   - Performance optimization

4. FEATURES
   - Real-time and batch diarization
   - Configurable speaker detection sensitivity
   - Automatic speaker labeling (Speaker A, Speaker B, etc.)
   - Integration with existing recognition pipeline

KEY FEATURES:
- Efficient speaker segmentation using Pyannote.audio
- Seamless integration with Groq transcription API
- Configurable diarization parameters
- Real-time and batch processing modes
- Speaker confidence scoring
- Automatic speaker labeling and identification
- Performance optimization and caching
- Error handling and recovery

USAGE EXAMPLES:
    # Basic diarization
    diarizer = SpeakerDiarizer()
    result = diarizer.diarize_audio(audio_data)

    # Batch processing with custom parameters
    config = DiarizationConfig(
        min_speakers=2,
        max_speakers=5,
        min_segment_duration=1.0
    )
    result = diarizer.diarize_audio(audio_data, config)

    # Integration with existing recognizer
    recognizer = SpeechRecognizer(speech_config)
    diarized_result = recognizer.recognize_with_diarization(audio_data)
"""

import asyncio
import concurrent.futures
from typing import List, Dict, Any, Optional, Tuple
import numpy as np

# Import structured logging
from .logging_utils import diarization_logger, log_debug, log_info, log_success, log_warning, log_error


# Legacy logging functions removed - using structured logging from logging_utils

# Lazy import Pyannote to avoid loading it when not needed
PYANNOTE_AVAILABLE = None
Pipeline = None
Annotation = None

def _import_pyannote():
    """Lazy import Pyannote.audio only when needed."""
    global PYANNOTE_AVAILABLE, Pipeline, Annotation
    
    if PYANNOTE_AVAILABLE is not None:
        return PYANNOTE_AVAILABLE
    
    try:
        from pyannote.audio import Pipeline
        from pyannote.core.annotation import Annotation
        import torch
        
        # Check GPU availability
        if torch.cuda.is_available():
            print("   🔧 CUDA available for Pyannote.audio GPU acceleration")
        else:
            print("   ℹ️ CUDA not available, using CPU for Pyannote.audio")
            
        PYANNOTE_AVAILABLE = True
        return True
    except ImportError:
        PYANNOTE_AVAILABLE = False
        print(
            "Warning: Pyannote.audio not available. Install with: pip install pyannote.audio"
        )

        # Create a fallback Annotation class for when Pyannote is not available
        class Annotation:
            def itertracks(self, yield_label=False):
                return []
        
        return False


# DiarizationError removed - using standard exceptions


class DiarizationConfig:
    """
    Configuration for speaker diarization operations.

    CRITICAL: This class provides configurable parameters for the diarization
    pipeline, allowing users to tune the behavior for their specific use cases:

    1. Speaker Detection: Minimum and maximum number of speakers
    2. Segment Control: Duration thresholds and overlap settings
    3. Quality Settings: Confidence thresholds and validation parameters
    4. Performance: Batch processing and caching options
    5. Optimization: New advanced settings for better output quality
    """

    def __init__(
        self,
        min_speakers: int = 1,
        max_speakers: int = 5,
        min_segment_duration: float = 2.0,
        max_segment_duration: float = 30.0,
        confidence_threshold: float = 0.7,
        # New optimization parameters
        silence_threshold: float = 0.8,
        speaker_change_sensitivity: float = 0.7,
        max_segments_per_chunk: int = 8,
        chunk_strategy: str = "adaptive",
        min_chunk_duration: float = 15.0,
        max_chunk_duration: float = 30.0,
        overlap_duration: float = 2.0,
        enable_cross_chunk_persistence: bool = True,
        speaker_similarity_threshold: float = 0.85,
        enable_adaptive_merging: bool = True,
        merge_time_threshold: float = 1.5,
        enable_context_awareness: bool = True,
    ):
        """
        Initialize diarization configuration.

        Args:
            min_speakers: Minimum number of speakers to detect
            max_speakers: Maximum number of speakers to detect
            min_segment_duration: Minimum segment duration in seconds
            max_segment_duration: Maximum segment duration in seconds
            confidence_threshold: Minimum confidence for segment inclusion
            silence_threshold: Silence detection sensitivity (0.1-1.0)
            speaker_change_sensitivity: Speaker change detection sensitivity (0.1-1.0)
            max_segments_per_chunk: Maximum segments per audio chunk
            chunk_strategy: Chunking strategy ('fixed', 'adaptive', 'conversation_aware')
            min_chunk_duration: Minimum chunk duration in seconds
            max_chunk_duration: Maximum chunk duration in seconds
            overlap_duration: Overlap between chunks in seconds
            enable_cross_chunk_persistence: Enable speaker persistence across chunks
            speaker_similarity_threshold: Threshold for speaker matching (0.5-1.0)
            enable_adaptive_merging: Enable intelligent segment merging
            merge_time_threshold: Time threshold for merging segments
            enable_context_awareness: Enable conversation flow analysis
        """
        # Legacy parameters
        self.min_speakers = min_speakers
        self.max_speakers = max_speakers
        self.min_segment_duration = min_segment_duration
        self.max_segment_duration = max_segment_duration
        self.confidence_threshold = confidence_threshold

        # New optimization parameters
        self.silence_threshold = silence_threshold
        self.speaker_change_sensitivity = speaker_change_sensitivity
        self.max_segments_per_chunk = max_segments_per_chunk
        self.chunk_strategy = chunk_strategy
        self.min_chunk_duration = min_chunk_duration
        self.max_chunk_duration = max_chunk_duration
        self.overlap_duration = overlap_duration
        self.enable_cross_chunk_persistence = enable_cross_chunk_persistence
        self.speaker_similarity_threshold = speaker_similarity_threshold
        self.enable_adaptive_merging = enable_adaptive_merging
        self.merge_time_threshold = merge_time_threshold
        self.enable_context_awareness = enable_context_awareness

    @classmethod
    def from_environment(cls) -> "DiarizationConfig":
        """Create configuration from environment variables."""
        from .speech_config import SpeechConfig

        config_dict = SpeechConfig.get_diarization_config()

        return cls(
            min_speakers=config_dict["max_speakers"],
            max_speakers=config_dict["max_speakers"],
            min_segment_duration=config_dict["min_segment_duration"],
            max_segment_duration=30.0,  # Default max duration
            confidence_threshold=0.7,  # Default confidence
            silence_threshold=config_dict["silence_threshold"],
            speaker_change_sensitivity=0.7,  # Default sensitivity
            max_segments_per_chunk=config_dict["max_segments_per_chunk"],
            chunk_strategy=config_dict["chunk_strategy"],
            min_chunk_duration=15.0,  # Default min chunk duration
            max_chunk_duration=30.0,  # Default max chunk duration
            overlap_duration=2.0,  # Default overlap duration
            enable_cross_chunk_persistence=True,  # Default persistence
            speaker_similarity_threshold=0.85,  # Default similarity threshold
            enable_adaptive_merging=True,  # Default adaptive merging
            merge_time_threshold=1.5,  # Default merge threshold
            enable_context_awareness=True,  # Default context awareness
        )

    def validate(self) -> bool:
        """Validate configuration parameters."""
        errors = []

        if self.min_speakers < 1:
            errors.append("min_speakers must be at least 1")

        if self.max_speakers < self.min_speakers:
            errors.append("max_speakers must be greater than or equal to min_speakers")

        if self.min_segment_duration < 0.5:
            errors.append("min_segment_duration must be at least 0.5 seconds")

        if self.max_segment_duration < self.min_segment_duration:
            errors.append(
                "max_segment_duration must be greater than min_segment_duration"
            )

        if self.confidence_threshold < 0.0 or self.confidence_threshold > 1.0:
            errors.append("confidence_threshold must be between 0.0 and 1.0")

        if self.silence_threshold < 0.1 or self.silence_threshold > 1.0:
            errors.append("silence_threshold must be between 0.1 and 1.0")

        if (
            self.speaker_change_sensitivity < 0.1
            or self.speaker_change_sensitivity > 1.0
        ):
            errors.append("speaker_change_sensitivity must be between 0.1 and 1.0")

        if self.max_segments_per_chunk < 1:
            errors.append("max_segments_per_chunk must be at least 1")

        if self.chunk_strategy not in ["fixed", "adaptive", "conversation_aware"]:
            errors.append(
                "chunk_strategy must be 'fixed', 'adaptive', or 'conversation_aware'"
            )

        if self.min_chunk_duration < 5.0:
            errors.append("min_chunk_duration must be at least 5.0 seconds")

        if self.max_chunk_duration < self.min_chunk_duration:
            errors.append("max_chunk_duration must be greater than min_chunk_duration")

        if self.overlap_duration < 0.0:
            errors.append("overlap_duration must be non-negative")

        if (
            self.speaker_similarity_threshold < 0.5
            or self.speaker_similarity_threshold > 1.0
        ):
            errors.append("speaker_similarity_threshold must be between 0.5 and 1.0")

        if self.merge_time_threshold < 0.0:
            errors.append("merge_time_threshold must be non-negative")

        if errors:
            print("DiarizationConfig validation errors:")
            for error in errors:
                print(f"  ❌ {error}")
            return False

        return True

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            "min_speakers": self.min_speakers,
            "max_speakers": self.max_speakers,
            "min_segment_duration": self.min_segment_duration,
            "max_segment_duration": self.max_segment_duration,
            "confidence_threshold": self.confidence_threshold,
            "silence_threshold": self.silence_threshold,
            "speaker_change_sensitivity": self.speaker_change_sensitivity,
            "max_segments_per_chunk": self.max_segments_per_chunk,
            "chunk_strategy": self.chunk_strategy,
            "min_chunk_duration": self.min_chunk_duration,
            "max_chunk_duration": self.max_chunk_duration,
            "overlap_duration": self.overlap_duration,
            "enable_cross_chunk_persistence": self.enable_cross_chunk_persistence,
            "speaker_similarity_threshold": self.speaker_similarity_threshold,
            "enable_adaptive_merging": self.enable_adaptive_merging,
            "merge_time_threshold": self.merge_time_threshold,
            "enable_context_awareness": self.enable_context_awareness,
        }

    def __str__(self) -> str:
        """String representation of configuration."""
        config_str = f"DiarizationConfig(\n"
        config_str += f"  Speakers: {self.min_speakers}-{self.max_speakers}\n"
        config_str += (
            f"  Segments: {self.min_segment_duration}s-{self.max_segment_duration}s\n"
        )
        config_str += f"  Chunking: {self.chunk_strategy} ({self.min_chunk_duration}s-{self.max_chunk_duration}s)\n"
        config_str += f"  Quality: silence={self.silence_threshold}, sensitivity={self.speaker_change_sensitivity}\n"
        config_str += f"  Persistence: {self.enable_cross_chunk_persistence}\n"
        config_str += f"  Merging: {self.enable_adaptive_merging} (threshold: {self.merge_time_threshold}s)\n"
        config_str += f"  Context: {self.enable_context_awareness}\n"
        config_str += ")"
        return config_str


class SpeakerSegment:
    """
    Represents a single speaker segment with metadata.

    CRITICAL: This class encapsulates all information about a speaker segment,
    including timing, speaker identification, and transcription data:

    1. Segment Information: Start/end times and duration
    2. Speaker Data: Speaker ID and confidence scores
    3. Audio Content: Raw audio data and processed text
    4. Metadata: Quality metrics and processing information
    """

    def __init__(
        self,
        start_time: float,
        end_time: float,
        speaker_id: str,
        confidence: float = 1.0,
        audio_data: Optional[np.ndarray] = None,
        text: str = "",
        language: str = "",
        transcription_confidence: float = 0.0,
    ):
        """
        Initialize speaker segment.

        Args:
            start_time: Segment start time in seconds
            end_time: Segment end time in seconds
            speaker_id: Unique identifier for the speaker
            confidence: Speaker detection confidence (0.0 to 1.0)
            audio_data: Raw audio data for this segment
            text: Transcribed text from this segment
            language: Detected language of the speech
            transcription_confidence: Confidence of the transcription
        """
        self.start_time = start_time
        self.end_time = end_time
        self.speaker_id = speaker_id
        self.confidence = confidence
        self.audio_data = audio_data
        self.text = text
        self.language = language
        self.transcription_confidence = transcription_confidence

    @property
    def duration(self) -> float:
        """Get segment duration in seconds."""
        return self.end_time - self.start_time

    @property
    def is_valid(self) -> bool:
        """Check if segment is valid (positive duration, reasonable confidence)."""
        return self.duration > 0 and self.confidence >= 0.0 and self.confidence <= 1.0

    def __str__(self) -> str:
        """String representation for debugging."""
        return f"SpeakerSegment(speaker={self.speaker_id}, time={self.start_time:.2f}-{self.end_time:.2f}, text='{self.text[:50]}...')"

    def to_dict(self) -> Dict[str, Any]:
        """Convert segment to dictionary for serialization."""
        return {
            "start_time": self.start_time,
            "end_time": self.end_time,
            "speaker_id": self.speaker_id,
            "confidence": self.confidence,
            "text": self.text,
            "language": self.language,
            "transcription_confidence": self.transcription_confidence,
            "duration": self.duration,
        }


class DiarizationResult:
    """
    Result of speaker diarization operation.

    CRITICAL: This class provides a comprehensive view of the diarization
    results, including all speaker segments and metadata:

    1. Speaker Segments: All detected speaker segments with timing
    2. Speaker Mapping: Mapping of speaker IDs to labels
    3. Quality Metrics: Overall diarization quality and confidence
    4. Processing Information: Timing and performance data
    """

    def __init__(
        self,
        segments: List[SpeakerSegment],
        speaker_mapping: Dict[str, str],
        total_duration: float,
        num_speakers: int,
        overall_confidence: float = 0.0,
        processing_time: float = 0.0,
        error_details: Optional[str] = None,
    ):
        """
        Initialize diarization result.

        Args:
            segments: List of detected speaker segments
            speaker_mapping: Mapping of speaker IDs to human-readable labels
            total_duration: Total duration of the audio in seconds
            num_speakers: Number of unique speakers detected
            overall_confidence: Overall confidence of the diarization
            processing_time: Time taken to process the audio
            error_details: Details of any errors that occurred
        """
        self.segments = segments
        self.speaker_mapping = speaker_mapping
        self.total_duration = total_duration
        self.num_speakers = num_speakers
        self.overall_confidence = overall_confidence
        self.processing_time = processing_time
        self.error_details = error_details

    @property
    def is_successful(self) -> bool:
        """Check if diarization was successful."""
        return self.error_details is None and len(self.segments) > 0

    @property
    def speaker_labels(self) -> List[str]:
        """Get list of unique speaker labels."""
        return list(self.speaker_mapping.values())

    def get_segments_by_speaker(self, speaker_id: str) -> List[SpeakerSegment]:
        """Get all segments for a specific speaker."""
        return [seg for seg in self.segments if seg.speaker_id == speaker_id]

    def get_transcript(self, include_speaker_labels: bool = True) -> str:
        """Get full transcript with optional speaker labels."""
        if not self.segments:
            return ""

        transcript_lines = []
        for segment in sorted(self.segments, key=lambda x: x.start_time):
            if include_speaker_labels:
                speaker_label = self.speaker_mapping.get(
                    segment.speaker_id, segment.speaker_id
                )
                transcript_lines.append(f"[{speaker_label}] {segment.text}")
            else:
                transcript_lines.append(segment.text)

        return "\n".join(transcript_lines)

    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary for serialization."""
        return {
            "segments": [seg.to_dict() for seg in self.segments],
            "speaker_mapping": self.speaker_mapping,
            "total_duration": self.total_duration,
            "num_speakers": self.num_speakers,
            "overall_confidence": self.overall_confidence,
            "processing_time": self.processing_time,
            "error_details": self.error_details,
            "is_successful": self.is_successful,
        }

    def __str__(self) -> str:
        """String representation for debugging."""
        if self.is_successful:
            return f"DiarizationResult({self.num_speakers} speakers, {len(self.segments)} segments, {self.total_duration:.2f}s)"
        else:
            return f"DiarizationResult(FAILED: {self.error_details})"


class AudioSegmenter:
    """
    Handles audio segmentation and preprocessing for diarization.

    CRITICAL: This class manages the audio processing pipeline for speaker
    diarization, ensuring optimal audio quality and format compatibility:

    1. Audio Preprocessing: Format conversion and quality optimization
    2. Segment Extraction: Extract individual speaker segments
    3. Audio Validation: Ensure segments meet quality requirements
    4. Format Conversion: Convert to formats compatible with Groq API
    """

    def __init__(self, sample_rate: int = 16000, channels: int = 1):
        """
        Initialize audio segmenter.

        Args:
            sample_rate: Target sample rate for audio processing
            channels: Number of audio channels (1 for mono, 2 for stereo)
        """
        self.sample_rate = sample_rate
        self.channels = channels

    def extract_segment_audio(
        self, full_audio: np.ndarray, segment: SpeakerSegment
    ) -> np.ndarray:
        """
        Extract audio data for a specific segment.

        Args:
            full_audio: Complete audio data
            segment: Speaker segment with timing information

        Returns:
            Audio data for the specified segment
        """
        start_sample = int(segment.start_time * self.sample_rate)
        end_sample = int(segment.end_time * self.sample_rate)

        # Ensure bounds are within audio length
        start_sample = max(0, start_sample)
        end_sample = min(len(full_audio), end_sample)

        if start_sample >= end_sample:
            return np.array([])

        return full_audio[start_sample:end_sample]

    def preprocess_audio(self, audio_data: np.ndarray) -> np.ndarray:
        """
        Preprocess audio data for optimal diarization.

        Args:
            audio_data: Input audio data

        Returns:
            Preprocessed audio data
        """
        # Convert to mono if stereo
        if len(audio_data.shape) > 1 and audio_data.shape[1] > 1:
            audio_data = np.mean(audio_data, axis=1)

        # Ensure float32 format with range [-1, 1]
        if audio_data.dtype != np.float32:
            if audio_data.dtype == np.int16:
                audio_data = audio_data.astype(np.float32) / 32768.0
            elif audio_data.dtype == np.int32:
                audio_data = audio_data.astype(np.float32) / 2147483648.0
            else:
                audio_data = audio_data.astype(np.float32)

        # Normalize audio levels
        if np.max(np.abs(audio_data)) > 0:
            audio_data = audio_data / np.max(np.abs(audio_data)) * 0.95

        return audio_data

    def validate_segment(
        self, segment: SpeakerSegment, min_duration: float = 0.5
    ) -> bool:
        """
        Validate if a segment meets quality requirements.

        Args:
            segment: Speaker segment to validate
            min_duration: Minimum required duration

        Returns:
            True if segment is valid, False otherwise
        """
        return (
            segment.is_valid
            and segment.duration >= min_duration
            and segment.confidence > 0.0
        )




# Simplified Diarizer class that combines both basic and enhanced functionality
class Diarizer:
    """Simplified diarizer that provides enhanced functionality by default."""
    
    def __init__(self, config: Optional[DiarizationConfig] = None):
        self.config = config or DiarizationConfig()
        # Direct implementation without base diarizer
        self.max_concurrent_requests = 5  # Limit concurrent API calls
    
    async def _transcribe_audio_async(self, speech_recognizer, audio_chunk: np.ndarray, mode: str, group_idx: int, verbose: bool = False) -> Tuple[Optional[SpeakerSegment], int]:
        """
        Async wrapper for transcribing a single audio chunk.
        
        Args:
            speech_recognizer: SpeechRecognizer instance
            audio_chunk: Audio data to transcribe
            mode: 'transcription' or 'translation'
            group_idx: Group index for logging
            verbose: Verbose logging
            
        Returns:
            Tuple of (SpeakerSegment or None, group_idx)
        """
        try:
            # Run the synchronous transcription in a thread pool
            loop = asyncio.get_event_loop()
            with concurrent.futures.ThreadPoolExecutor() as executor:
                if mode == "translation":
                    result = await loop.run_in_executor(
                        executor, speech_recognizer.translate_audio_data, audio_chunk
                    )
                else:
                    result = await loop.run_in_executor(
                        executor, speech_recognizer.recognize_audio_data, audio_chunk
                    )
            
            if result and result.text:
                log_debug(f"✅ Group {group_idx+1}: {result.text}", verbose)
                return result, group_idx
            else:
                log_debug(f"⚠️ Group {group_idx+1}: No text detected", verbose)
                return None, group_idx
                
        except Exception as e:
            log_debug(f"❌ Group {group_idx+1} transcription failed: {e}", verbose)
            return None, group_idx
    
    async def _process_segments_parallel(self, grouped_segments: List[Dict], audio_file: str, mode: str, 
                                       speech_recognizer, verbose: bool = False) -> Tuple[List[SpeakerSegment], Dict[str, str]]:
        """
        Process all speaker segments in parallel using asyncio.
        
        Args:
            grouped_segments: List of grouped speaker segments
            audio_file: Path to audio file
            mode: 'transcription' or 'translation'
            speech_recognizer: SpeechRecognizer instance
            verbose: Verbose logging
            
        Returns:
            List of SpeakerSegment objects
        """
        diarization_logger.info(f"🚀 Processing {len(grouped_segments)} speaker groups in parallel...")
        
        # Create speaker mapping
        speaker_mapping = {}
        speaker_counter = 0
        
        # Prepare tasks for parallel execution
        tasks = []
        group_data = []
        
        for group_idx, group in enumerate(grouped_segments):
            log_debug(f"Preparing group {group_idx+1}/{len(grouped_segments)}: "
                      f"{len(group['segments'])} segments, {group['total_duration']:.1f}s, {group['total_size_mb']:.1f}MB", verbose)
            
            # Map Pyannote speaker labels to consistent IDs
            if group['speaker'] not in speaker_mapping:
                speaker_counter += 1
                speaker_mapping[group['speaker']] = f"SPEAKER_{speaker_counter-1:02d}"
            
            speaker_id = speaker_mapping[group['speaker']]
            
            # Extract combined audio chunk for this speaker group
            combined_chunk = self._extract_audio_chunk(
                audio_file, group['start_time'], group['end_time']
            )
            
            if combined_chunk is None:
                print(f"      ⚠️ Skipping group {group_idx+1} - audio extraction failed")
                continue
            
            # Create async task for this group (don't await here!)
            task = self._transcribe_audio_async(
                speech_recognizer, combined_chunk, mode, group_idx, verbose
            )
            tasks.append(task)
            group_data.append({
                'group': group,
                'speaker_id': speaker_id,
                'group_idx': group_idx
            })
        
        if not tasks:
            return [], speaker_mapping
        
        # Execute all tasks in parallel with concurrency limit
        semaphore = asyncio.Semaphore(self.max_concurrent_requests)
        
        async def limited_transcribe(coro, group_info):
            async with semaphore:
                transcription_result, group_idx = await coro
                return transcription_result, group_info
        
        # Run all tasks with concurrency control
        limited_tasks = [
            limited_transcribe(task, group_data[i]) 
            for i, task in enumerate(tasks)
        ]
        
        # Convert coroutines to Tasks for proper cancellation handling
        task_objects = [asyncio.create_task(coro) for coro in limited_tasks]
        
        # Wait for all tasks to complete with proper cancellation handling
        try:
            results = await asyncio.gather(*task_objects, return_exceptions=True)
        except KeyboardInterrupt:
            # For KeyboardInterrupt, let the tasks complete naturally and return results
            print("   🛑 KeyboardInterrupt detected, letting parallel processing complete...")
            # Wait for all tasks to complete (don't cancel them)
            results = await asyncio.gather(*task_objects, return_exceptions=True)
        except asyncio.CancelledError:
            # Cancel all tasks if the operation is cancelled
            for task in task_objects:
                if not task.done():
                    task.cancel()
            # Wait for cancellation to complete
            await asyncio.gather(*task_objects, return_exceptions=True)
            raise
        except Exception as e:
            # Cancel all tasks on any other error
            for task in task_objects:
                if not task.done():
                    task.cancel()
            raise
        
        # Process results and create segments
        segments = []
        for result_tuple in results:
            if isinstance(result_tuple, Exception):
                log_debug(f"❌ Task failed: {result_tuple}", verbose)
                continue
            
            # result_tuple is (transcription_result, group_info)
            transcription_result, group_info = result_tuple
            if isinstance(transcription_result, Exception):
                log_debug(f"❌ Group {group_info['group_idx']+1} failed: {transcription_result}", verbose)
                continue
            
            if transcription_result and hasattr(transcription_result, 'text') and transcription_result.text:
                # Create speaker segment with accurate transcription
                segment = SpeakerSegment(
                    start_time=group_info['group']['start_time'],
                    end_time=group_info['group']['end_time'],
                    speaker_id=group_info['speaker_id'],
                    text=transcription_result.text,
                    confidence=transcription_result.confidence
                )
                segments.append(segment)
        
        diarization_logger.success(f"Parallel processing completed: {len(segments)} segments processed")
        return segments, speaker_mapping
    
    async def _get_partial_results(self, grouped_segments: List[Dict], audio_file: str, mode: str, 
                                 speech_recognizer, verbose: bool = False) -> Tuple[List[SpeakerSegment], Dict[str, str]]:
        """
        Get partial results when diarization is interrupted.
        This method tries to process as many segments as possible before interruption.
        """
        print("   🔍 Attempting to get partial results...")
        
        # Create speaker mapping
        speaker_mapping = {}
        speaker_counter = 0
        
        for group in grouped_segments:
            if group['speaker'] not in speaker_mapping:
                speaker_counter += 1
                speaker_mapping[group['speaker']] = f"SPEAKER_{speaker_counter-1:02d}"
        
        # Try to process segments one by one (not in parallel) to get partial results
        segments = []
        for group_idx, group in enumerate(grouped_segments):
            try:
                # Extract audio chunk for this speaker group
                combined_chunk = self._extract_audio_chunk(
                    audio_file, group['start_time'], group['end_time']
                )
                
                if combined_chunk is None:
                    continue
                
                # Process this segment
                speaker_id = speaker_mapping[group['speaker']]
                result, _ = await self._transcribe_audio_async(
                    speech_recognizer, combined_chunk, mode, group_idx, verbose
                )
                
                if result and result.text:
                    segment = SpeakerSegment(
                        start_time=group['start_time'],
                        end_time=group['end_time'],
                        speaker_id=speaker_id,
                        text=result.text,
                        confidence=result.confidence
                    )
                    segments.append(segment)
                    print(f"   ✅ Processed segment {group_idx+1}/{len(grouped_segments)}: {result.text[:50]}...")
                
            except Exception as e:
                print(f"   ⚠️ Failed to process segment {group_idx+1}: {e}")
                continue
        
        print(f"   📊 Partial results: {len(segments)} segments processed")
        return segments, speaker_mapping
    
    async def diarize(self, audio_file: str, mode: str, speech_recognizer=None, verbose: bool = False) -> DiarizationResult:
        """
        Perform diarization with enhanced functionality by default.

        Args:
            audio_file: Path to audio file
            mode: 'transcription' or 'translation'
            speech_recognizer: SpeechRecognizer instance for transcription

        Returns:
            DiarizationResult with speaker-separated transcription
        """
        try:
            # Use the enhanced diarization method directly
            return await self.diarize_with_accurate_transcription(
                audio_file, mode, speech_recognizer, verbose
            )
        except Exception as e:
            print(f"Diarization failed: {e}")
            # Create a minimal result
            segment = SpeakerSegment(
                start_time=0.0,
                end_time=1.0,
                speaker_id="SPEAKER_00",
                confidence=0.5,
                text="[Diarization failed]"
            )
            return DiarizationResult(
                segments=[segment],
                speaker_mapping={"SPEAKER_00": "Speaker 1"},
                total_duration=1.0,
                num_speakers=1,
                overall_confidence=0.5
            )
    
    async def diarize_with_accurate_transcription(self, audio_file: str, mode: str, 
                                          speech_recognizer=None, verbose: bool = False) -> "DiarizationResult":
        """
        CORRECT PIPELINE: Pyannote.audio FIRST, then Groq API per segment.
        
        This is the proper approach:
        1. Pyannote.audio detects speaker segments and timestamps
        2. Audio is split into speaker-specific chunks
        3. Each chunk is sent to Groq API for accurate transcription
        4. Perfect speaker attribution with accurate text
        
        Args:
            audio_file: Path to audio file
            mode: 'transcription' or 'translation'
            speech_recognizer: SpeechRecognizer instance for Groq API calls
            
        Returns:
            DiarizationResult with accurate speaker-specific transcriptions
        """
        print("🎭 Running CORRECT diarization pipeline...")
        print("   1. Pyannote.audio → Speaker detection")
        print("   2. Audio chunking → Speaker-specific segments") 
        print("   3. Groq API → Accurate transcription per segment")
        
        try:
            # Step 1: Pyannote.audio for speaker detection
            print("   🔍 Step 1: Detecting speakers with Pyannote.audio...")
            
            # Get HF token from Config
            from .speech_config import SpeechConfig
            hf_token = SpeechConfig.get_hf_token()
            
            if not hf_token or hf_token == "your_hf_token_here":
                raise ValueError("HF_TOKEN not configured for Pyannote.audio")
            
            # Initialize Pyannote pipeline with GPU support
            from pyannote.audio import Pipeline
            import torch
            
            # Get optimal device using SpeechConfig utility
            optimal_device = SpeechConfig.get_optimal_device()
            device = torch.device(optimal_device)
            
            # Get GPU info for logging
            gpu_info = SpeechConfig.get_gpu_info()
            if gpu_info["cuda_available"]:
                print(f"   🔧 Using GPU: {gpu_info['device_name']} (Device {gpu_info['current_device']})")
                print(f"   📊 GPU Memory: {gpu_info['memory_allocated'] / 1024**3:.2f}GB allocated, {gpu_info['memory_reserved'] / 1024**3:.2f}GB reserved")
            else:
                print(f"   🔧 Using CPU (GPU not available)")
            
            # Load the pretrained pipeline
            pipeline = Pipeline.from_pretrained(
                "pyannote/speaker-diarization-3.1",
                use_auth_token=hf_token
            )
            
            # Move the pipeline to the optimal device
            pipeline = pipeline.to(device)
            print(f"   ✅ Pipeline loaded and moved to {device}")
            
            # Run diarization to get speaker segments
            diarization = pipeline(audio_file)
            
            # Extract speaker segments with timestamps
            speaker_segments = []
            for turn, _, speaker in diarization.itertracks(yield_label=True):
                speaker_segments.append({
                    'start': turn.start,
                    'end': turn.end,
                    'speaker': speaker,
                    'duration': turn.end - turn.start
                })
            
            print(f"   ✅ Detected {len(speaker_segments)} speaker segments")
            
            if not speaker_segments:
                print("   ⚠️ No speaker segments detected, creating single speaker")
                # Get audio duration for single speaker
                import soundfile as sf
                audio_data, sample_rate = sf.read(audio_file)
                duration = len(audio_data) / sample_rate
                
                speaker_segments = [{
                    'start': 0.0,
                    'end': duration,
                    'speaker': 'SPEAKER_1'
                }]
            
            # Step 2: Smart grouping of consecutive segments by speaker with 24MB limit
            print("   🔍 Step 2: Smart grouping of speaker segments...")
            
            if not speech_recognizer:
                raise ValueError("SpeechRecognizer required for transcription")
            
            # Group consecutive segments by speaker with 24MB size limit
            grouped_segments = self._group_segments_by_speaker_with_size_limit(
                speaker_segments, audio_file
            )
            
            print(f"   📊 Grouped {len(speaker_segments)} segments into {len(grouped_segments)} groups")
            
            # Process all grouped segments in parallel
            try:
                segments, speaker_mapping = await self._process_segments_parallel(
                    grouped_segments, audio_file, mode, speech_recognizer, verbose
                )
            except KeyboardInterrupt:
                # Handle KeyboardInterrupt - let processing complete and return results
                print("   ⚠️ Diarization interrupted by user, but letting processing complete...")
                # The parallel processing should have already completed most tasks
                # Just return what we have
                segments, speaker_mapping = await self._get_partial_results(
                    grouped_segments, audio_file, mode, speech_recognizer, verbose
                )
            
            if not segments:
                raise ValueError("No segments could be transcribed")
            
            # Create final result
            result = DiarizationResult(
                segments=segments,
                speaker_mapping=speaker_mapping,
                total_duration=grouped_segments[-1]['end_time'] if grouped_segments else 0.0,
                num_speakers=len(speaker_mapping),
                overall_confidence=sum(s.confidence for s in segments) / len(segments) if segments else 0.0
            )
            
            print(f"   ✅ Diarization completed: {len(segments)} groups, {len(speaker_mapping)} speakers")
            return result
            
        except KeyboardInterrupt:
            # If interrupted, try to return partial results if we have any
            print(f"   ⚠️ Diarization interrupted by user")
            if 'segments' in locals() and segments:
                print(f"   📊 Returning partial results: {len(segments)} segments processed")
                result = DiarizationResult(
                    segments=segments,
                    speaker_mapping=speaker_mapping if 'speaker_mapping' in locals() else {},
                    total_duration=grouped_segments[-1]['end_time'] if grouped_segments else 0.0,
                    num_speakers=len(speaker_mapping) if 'speaker_mapping' in locals() else 0,
                    overall_confidence=sum(s.confidence for s in segments) / len(segments) if segments else 0.0
                )
                return result
            else:
                print(f"   ❌ No partial results available")
                raise
        except Exception as e:
            print(f"   ❌ Diarization failed: {e}")
            raise
    
    def _group_segments_by_speaker_with_size_limit(self, speaker_segments, audio_file):
        """Group consecutive segments by speaker with 24MB size limit."""
        if not speaker_segments:
            return []
        
        # Sort segments by start time
        sorted_segments = sorted(speaker_segments, key=lambda x: x['start'])
        
        grouped = []
        current_group = None
        
        for segment in sorted_segments:
            if current_group is None or current_group['speaker'] != segment['speaker']:
                # Start new group
                if current_group:
                    grouped.append(current_group)
                
                current_group = {
                    'speaker': segment['speaker'],
                    'segments': [segment],
                    'start_time': segment['start'],
                    'end_time': segment['end'],
                    'total_duration': segment['end'] - segment['start']
                }
            else:
                # Add to current group
                current_group['segments'].append(segment)
                current_group['end_time'] = segment['end']
                current_group['total_duration'] = current_group['end_time'] - current_group['start_time']
            
            # Check size limit (24MB = ~6.5 minutes at 16kHz)
            estimated_duration_minutes = current_group['total_duration'] / 60
            if estimated_duration_minutes > 6.5:
                # Group is too large, finalize it and start new one
                grouped.append(current_group)
                current_group = None
        
        # Add final group
        if current_group:
            grouped.append(current_group)
        
        # Calculate size estimates for each group
        for group in grouped:
            group['total_size_mb'] = (group['total_duration'] * 16000 * 4) / (1024 * 1024)  # Rough estimate
        
        return grouped
    
    def _extract_audio_chunk(self, audio_file, start_time, end_time):
        """Extract audio chunk from file."""
        try:
            import soundfile as sf
            audio_data, sample_rate = sf.read(audio_file)
            
            start_sample = int(start_time * sample_rate)
            end_sample = int(end_time * sample_rate)
            
            chunk = audio_data[start_sample:end_sample]
            
            # Convert to mono if stereo
            if len(chunk.shape) > 1:
                chunk = chunk[:, 0]
            
            # Resample to 16kHz if needed
            if sample_rate != 16000:
                from scipy import signal
                chunk = signal.resample(chunk, int(len(chunk) * 16000 / sample_rate))
            
            # Apply noise filtering for better transcription quality
            try:
                from .vad_service import VADService, VADConfig
                vad_service = VADService(VADConfig())
                chunk = vad_service._apply_noise_filtering(chunk, 16000)
            except Exception as e:
                # Continue without noise filtering if it fails
                pass
            
            return chunk
            
        except Exception as e:
            print(f"      ❌ Audio extraction failed: {e}")
            return None
