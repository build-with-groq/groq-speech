"""
FastAPI server for Groq Speech SDK.

Provides REST API endpoints for speech recognition and translation.
The API server acts as a bridge between the web interface and the core SDK,
using the same SpeechRecognizer class as the CLI interface.

Key Features:
- REST API endpoints for file processing
- Support for both transcription and translation
- Speaker diarization support
- Health check and monitoring endpoints

Architecture:
- Layer 2b: API Client (parallel to CLI Client)
- Uses same SpeechRecognizer as CLI
- Provides HTTP interface to Layer 3 (UI)
"""

import os
import sys
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Add the parent directory to the path to import the SDK
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables from project root .env.api
from dotenv import load_dotenv

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_path = os.path.join(project_root, ".env.api")
if os.path.exists(env_path):
    load_dotenv(env_path)
    print(f"✅ Loaded environment variables from {env_path}")
else:
    print(f"ℹ️  No .env.api file found at {env_path} - using environment variables from Docker/system")

# Check if required environment variables are set
print(f"🔍 GROQ_API_KEY: {'SET' if os.getenv('GROQ_API_KEY') else 'NOT SET'}")
print(f"🔍 HF_TOKEN: {'SET' if os.getenv('HF_TOKEN') else 'NOT SET'}")

# Import groq_speech after adding to path
from groq_speech import (
    SpeechConfig,
    SpeechRecognizer,
    ResultReason,
    AudioFormatUtils,
)
from groq_speech.vad_service import VADService, VADConfig
from groq_speech.logging_utils import api_logger


# Pydantic models for API requests/responses
class LogRequest(BaseModel):
    component: str
    level: str
    message: str
    data: Optional[Dict[str, Any]] = None
    timestamp: str

class RecognitionRequest(BaseModel):
    """Request model for speech recognition."""

    audio_data: Optional[str] = Field(None, description="Base64 encoded audio data")
    model: Optional[str] = Field(None, description="Groq model to use")
    target_language: Optional[str] = Field(
        "en", description="Target language for translation"
    )
    enable_timestamps: bool = Field(False, description="Enable word-level timestamps")
    enable_language_detection: bool = Field(
        True, description="Enable automatic language detection"
    )
    enable_diarization: bool = Field(False, description="Enable speaker diarization")


class RecognitionResponse(BaseModel):
    """Response model for speech recognition."""

    success: bool
    text: Optional[str] = None
    confidence: Optional[float] = None
    language: Optional[str] = None
    timestamps: Optional[List[Dict[str, Any]]] = None
    segments: Optional[List[Dict[str, Any]]] = None
    num_speakers: Optional[int] = None
    error: Optional[str] = None


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    timestamp: str
    version: str
    api_key_configured: bool

class VADRequest(BaseModel):
    """Request model for VAD operations."""
    audio_data: List[float]  # Float32Array as JSON list
    sample_rate: int = 16000
    max_duration_seconds: Optional[float] = None

class VADResponse(BaseModel):
    """Response model for VAD operations."""
    success: bool
    should_create_chunk: bool
    reason: str
    audio_level: float
    error: Optional[str] = None


# Global state - WebSocket functionality removed


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    api_logger.info("🚀 Starting Groq Speech API Server...")
    try:
        SpeechConfig.get_api_key()
        api_logger.success("API key validated")
    except ValueError as e:
        api_logger.error(f"API key error: {e}")
    yield
    api_logger.info("🛑 Shutting down Groq Speech API Server...")


# Create FastAPI app
app = FastAPI(
    title="Groq Speech API",
    description="REST API endpoints for Groq Speech SDK",
    version="1.0.0",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_speech_config(
    model: Optional[str] = None,
    is_translation: bool = False,
    target_language: str = "en",
    enable_timestamps: bool = False,
    enable_diarization: bool = False,
) -> SpeechConfig:
    """Create speech configuration using SDK factory methods."""
    if enable_diarization:
        return SpeechConfig.create_for_diarization(
            model=model,
            target_language=target_language,
            enable_timestamps=enable_timestamps,
            is_translation=is_translation
        )
    elif is_translation:
        return SpeechConfig.create_for_translation(
            model=model,
            target_language=target_language,
            enable_timestamps=enable_timestamps
        )
    else:
        return SpeechConfig.create_for_recognition(
            model=model,
            target_language=target_language,
            enable_timestamps=enable_timestamps
        )


@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint."""
    return {
        "message": "Groq Speech API Server",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
    }


@app.post("/api/v1/log")
async def log_frontend_message(request: LogRequest):
    """Receive logs from frontend and display them in terminal."""
    try:
        # Format the log message for terminal display
        timestamp = request.timestamp
        component = request.component
        level = request.level
        message = request.message
        data = request.data or {}
        
        # Create a formatted log message
        data_str = ""
        if data and len(data) > 0:
            data_str = " | " + " ".join([f"{k}={v}" for k, v in data.items()])
        
        formatted_message = f"[{timestamp}] [{component}] [{level}] {message}{data_str}"
        
        # Print to terminal with color coding
        if level == "ERROR":
            print(f"\033[0;31m[FRONTEND] {formatted_message}\033[0m")  # Red
        elif level == "WARNING":
            print(f"\033[1;33m[FRONTEND] {formatted_message}\033[0m")  # Yellow
        elif level == "INFO":
            print(f"\033[0;34m[FRONTEND] {formatted_message}\033[0m")  # Blue
        else:
            print(f"[FRONTEND] {formatted_message}")
        
        return {"status": "logged"}
    except Exception as e:
        print(f"[FRONTEND] Error processing log: {e}")
        return {"status": "error", "message": str(e)}

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    try:
        api_key_configured = bool(SpeechConfig.get_api_key())
    except ValueError:
        api_key_configured = False

    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        version="1.0.0",
        api_key_configured=api_key_configured,
    )

@app.post("/api/log")
async def frontend_log(request: dict):
    """Receive frontend logs and forward to terminal."""
    try:
        component = request.get("component", "UNKNOWN")
        level = request.get("level", "INFO")
        message = request.get("message", "")
        context = request.get("context", {})
        prefix = request.get("prefix", "")
        timestamp = request.get("timestamp", datetime.now().isoformat())
        
        # Format the log message for terminal output
        time_str = timestamp[11:23] if len(timestamp) > 23 else timestamp
        context_str = ""
        if context:
            context_str = " | " + " ".join([f"{k}={json.dumps(v)}" for k, v in context.items()])
        
        prefix_str = f"[{prefix}] " if prefix else ""
        formatted_message = f"[{time_str}] [FRONTEND-{component}] [{level}] {prefix_str}{message}{context_str}"
        
        # Print to terminal with color coding
        if level == "ERROR":
            print(f"\033[0;31m{formatted_message}\033[0m")  # Red
        elif level == "WARN":
            print(f"\033[1;33m{formatted_message}\033[0m")  # Yellow
        elif level == "DEBUG":
            print(f"\033[0;36m{formatted_message}\033[0m")  # Cyan
        else:
            print(f"\033[0;34m{formatted_message}\033[0m")  # Blue
            
        return {"status": "logged"}
    except Exception as e:
        print(f"Error processing frontend log: {e}")
        return {"status": "error", "message": str(e)}


@app.get("/api/v1/device-info")
async def get_device_info():
    """Get device information (CPU/GPU) for diarization processing."""
    try:
        gpu_info = SpeechConfig.get_gpu_info()
        
        device_type = "GPU" if gpu_info.get("cuda_available") else "CPU"
        device_name = gpu_info.get("device_name", "CPU")
        estimated_time = "30-60 seconds" if gpu_info.get("cuda_available") else "2-3 minutes"
        
        return {
            "device_type": device_type,
            "device_name": device_name,
            "cuda_available": gpu_info.get("cuda_available", False),
            "device_count": gpu_info.get("device_count", 0),
            "estimated_time": estimated_time,
            "memory_info": {
                "allocated_gb": gpu_info.get("memory_allocated", 0) / (1024**3) if gpu_info.get("cuda_available") else 0,
                "reserved_gb": gpu_info.get("memory_reserved", 0) / (1024**3) if gpu_info.get("cuda_available") else 0
            }
        }
    except Exception as e:
        print(f"Error getting device info: {e}")
        return {
            "device_type": "CPU",
            "device_name": "CPU",
            "cuda_available": False,
            "device_count": 0,
            "estimated_time": "2-3 minutes",
            "memory_info": {
                "allocated_gb": 0,
                "reserved_gb": 0
            }
        }



@app.post("/api/v1/recognize", response_model=RecognitionResponse)
async def recognize_speech(request: RecognitionRequest):
    """Recognize speech from audio data - EXACTLY like CLI file recognition."""
    try:
        if not request.audio_data:
            raise HTTPException(status_code=400, detail="Audio data is required")

        api_logger.info("🎤 REST API: Received audio data request", {
            "audio_length": len(request.audio_data),
            "enable_timestamps": request.enable_timestamps,
            "target_language": request.target_language,
            "enable_language_detection": request.enable_language_detection,
            "enable_diarization": request.enable_diarization,
            "model": request.model,
            "timestamp": datetime.now().isoformat()
        })
        
        api_logger.dataFlow("Frontend", "API", {
            "request_type": "recognition",
            "audio_data_length": len(request.audio_data),
            "enable_diarization": request.enable_diarization,
            "target_language": request.target_language
        }, "Audio data received from frontend")

        # Setup speech configuration using SDK factory
        speech_config = get_speech_config(
            model=request.model,
            is_translation=False,
            target_language=request.target_language,
            enable_timestamps=request.enable_timestamps,
            enable_diarization=request.enable_diarization,
        )

        # Create recognizer - EXACTLY like CLI
        recognizer = SpeechRecognizer(
            speech_config=speech_config,
            translation_target_language=request.target_language
        )

        # Decode audio data using SDK utilities
        audio_array_float, sample_rate = AudioFormatUtils.decode_base64_audio(request.audio_data)
        
        # Log audio information
        audio_info = AudioFormatUtils.get_audio_info(audio_array_float, sample_rate)
        api_logger.info("📊 Audio data decoded", audio_info)

        # Process based on diarization requirement
        if request.enable_diarization:
            # For diarization, save to temp file and use process_file
            print("🎭 Processing with diarization...")
            temp_path = AudioFormatUtils.save_audio_to_temp_file(audio_array_float, sample_rate)
            
            try:
                api_logger.dataFlow("API", "Groq API", {
                    "method": "process_file",
                    "file_path": temp_path,
                    "enable_diarization": True,
                    "is_translation": False,
                    "audio_samples": len(audio_array_float),
                    "sample_rate": sample_rate
                }, "Sending audio file to Groq API for diarization")
                
                result = await recognizer.process_file(temp_path, enable_diarization=True, is_translation=False)
                
                api_logger.dataFlow("Groq API", "API", {
                    "result_type": "diarization",
                    "has_segments": hasattr(result, 'segments') and result.segments is not None,
                    "segments_count": len(result.segments) if hasattr(result, 'segments') and result.segments else 0,
                    "has_text": hasattr(result, 'text') and result.text is not None,
                    "text_length": len(result.text) if hasattr(result, 'text') and result.text else 0
                }, "Received diarization result from Groq API")
            finally:
                # Clean up temporary file using SDK utility
                AudioFormatUtils.cleanup_temp_file(temp_path)
        else:
            # For non-diarization, use direct audio data processing
            print("🎤 Processing without diarization...")
            
            api_logger.dataFlow("API", "Groq API", {
                "method": "recognize_audio_data",
                "audio_samples": len(audio_array_float),
                "sample_rate": sample_rate,
                "enable_diarization": False,
                "is_translation": False
            }, "Sending audio data to Groq API for recognition")
            
            result = recognizer.recognize_audio_data(audio_array_float, sample_rate, is_translation=False)
            
            api_logger.dataFlow("Groq API", "API", {
                "result_type": "recognition",
                "has_text": hasattr(result, 'text') and result.text is not None,
                "text_length": len(result.text) if hasattr(result, 'text') and result.text else 0,
                "confidence": getattr(result, 'confidence', None),
                "reason": getattr(result, 'reason', None)
            }, "Received recognition result from Groq API")

        # Handle diarization result
        if hasattr(result, "segments") and result.segments:
            print(f"✅ Diarization successful: {len(result.segments)} segments, {result.num_speakers} speakers")
            
            # Convert segments to API format
            segments_data = []
            for segment in result.segments:
                segment_data = {
                    "speaker_id": segment.speaker_id,
                    "text": getattr(segment, 'text', '') or getattr(segment, 'transcription', '') or '[No text]',
                    "start_time": getattr(segment, 'start_time', 0),
                    "end_time": getattr(segment, 'end_time', 0)
                }
                segments_data.append(segment_data)

            return RecognitionResponse(
                success=True,
                text=None,  # No single text for diarization
                confidence=None,
                language=result.language if hasattr(result, 'language') else None,
                timestamps=None,
                segments=segments_data,
                num_speakers=result.num_speakers
            )

        # Handle regular recognition result
        elif result.reason == ResultReason.RecognizedSpeech:
            print(f"✅ Recognition successful: '{result.text}'")
            print(f"🎯 Confidence: {result.confidence}")
            print(f"🌍 Language: {result.language}")

            api_logger.dataFlow("API", "Frontend", {
                "response_type": "recognition",
                "text_length": len(result.text) if result.text else 0,
                "confidence": result.confidence,
                "language": result.language,
                "has_timestamps": hasattr(result, 'timestamps') and result.timestamps is not None
            }, "Sending recognition response to frontend")

            return RecognitionResponse(
                success=True,
                text=result.text,
                confidence=result.confidence,
                language=result.language,
                timestamps=(result.timestamps if request.enable_timestamps else None),
                segments=None,
                num_speakers=None
            )
        elif result.reason == ResultReason.NoMatch:
            print("❌ No speech detected in audio")
            return RecognitionResponse(success=False, error="No speech detected")
        else:
            print(f"❌ Recognition failed: {result.reason}")
            if hasattr(result, "cancellation_details") and result.cancellation_details:
                print(f"🔍 Cancellation details: {result.cancellation_details.error_details}")
            return RecognitionResponse(success=False, error="Recognition failed")

    except Exception as e:
        print(f"💥 Error in REST API recognition: {e}")
        import traceback
        traceback.print_exc()
        return RecognitionResponse(success=False, error=str(e))


@app.post("/api/v1/translate", response_model=RecognitionResponse)
async def translate_speech(request: RecognitionRequest):
    """Translate speech from audio data - EXACTLY like CLI file translation."""
    try:
        if not request.audio_data:
            raise HTTPException(status_code=400, detail="Audio data is required")

        print(f"🔀 Translation API: Received audio data request")
        print(f"📊 Audio data length: {len(request.audio_data)} characters")
        print(f"🎭 Enable diarization: {request.enable_diarization}")

        # Setup speech configuration for translation using SDK factory
        speech_config = get_speech_config(
            model=request.model,
            is_translation=True,
            target_language=request.target_language,
            enable_timestamps=request.enable_timestamps,
            enable_diarization=request.enable_diarization,
        )

        print(f"🔀 Translation mode enabled (target: {request.target_language})")

        # Create recognizer - EXACTLY like CLI (AFTER enabling translation)
        recognizer = SpeechRecognizer(
            speech_config=speech_config,
            translation_target_language=request.target_language
        )

        # Decode audio data using SDK utilities
        audio_array_float, sample_rate = AudioFormatUtils.decode_base64_audio(request.audio_data)
        
        # Log audio information
        audio_info = AudioFormatUtils.get_audio_info(audio_array_float, sample_rate)
        api_logger.info("📊 Audio data decoded for translation", audio_info)

        # Process based on diarization requirement
        if request.enable_diarization:
            # For diarization, save to temp file and use process_file
            print("🎭 Processing translation with diarization...")
            temp_path = AudioFormatUtils.save_audio_to_temp_file(audio_array_float, sample_rate)
            
            try:
                result = await recognizer.process_file(temp_path, enable_diarization=True, is_translation=True)
            finally:
                # Clean up temporary file using SDK utility
                AudioFormatUtils.cleanup_temp_file(temp_path)
        else:
            # For non-diarization, use direct audio data processing
            print("🔀 Processing translation without diarization...")
            result = recognizer.recognize_audio_data(audio_array_float, sample_rate, is_translation=True)

        # Handle diarization result
        if hasattr(result, "segments") and result.segments:
            print(f"✅ Translation diarization successful: {len(result.segments)} segments, {result.num_speakers} speakers")
            
            # Convert segments to API format
            segments_data = []
            for segment in result.segments:
                segment_data = {
                    "speaker_id": segment.speaker_id,
                    "text": getattr(segment, 'text', '') or getattr(segment, 'transcription', '') or '[No text]',
                    "start_time": getattr(segment, 'start_time', 0),
                    "end_time": getattr(segment, 'end_time', 0)
                }
                segments_data.append(segment_data)

            return RecognitionResponse(
                success=True,
                text=None,  # No single text for diarization
                confidence=None,
                language=result.language if hasattr(result, 'language') else None,
                timestamps=None,
                segments=segments_data,
                num_speakers=result.num_speakers
            )

        # Handle regular translation result
        elif result.reason == ResultReason.RecognizedSpeech:
            print(f"✅ Translation successful: '{result.text}'")
            return RecognitionResponse(
                success=True,
                text=result.text,
                confidence=result.confidence,
                language=result.language,
                timestamps=(result.timestamps if request.enable_timestamps else None),
                segments=None,
                num_speakers=None
            )
        elif result.reason == ResultReason.NoMatch:
            return RecognitionResponse(success=False, error="No speech detected")
        else:
            return RecognitionResponse(success=False, error="Translation failed")

    except Exception as e:
        print(f"💥 Error in REST API translation: {e}")
        import traceback
        traceback.print_exc()
        return RecognitionResponse(success=False, error=str(e))


@app.get("/api/v1/models")
async def get_available_models():
    """Get available Groq models."""
    models = [
        {
            "id": "whisper-large-v3",
            "name": "Whisper Large V3",
            "description": "High accuracy, slower processing",
        },
        {
            "id": "whisper-large-v3-turbo",
            "name": "Whisper Large V3 Turbo",
            "description": "Fast processing, good accuracy",
        },
    ]
    return {"models": models}


@app.post("/api/v1/recognize-microphone", response_model=RecognitionResponse)
async def recognize_microphone_single(request: dict):
    """Single microphone recognition - EXACTLY like speech_demo.py process_microphone_single."""
    try:
        # Extract audio data and parameters - EXACTLY like speech_demo.py
        audio_data = request.get("audio_data")  # Raw float32 array as list
        sample_rate = request.get("sample_rate", 16000)
        enable_diarization = request.get("enable_diarization", False)
        is_translation = request.get("is_translation", False)
        target_language = request.get("target_language", "en")
        
        if not audio_data:
            raise HTTPException(status_code=400, detail="Audio data is required")

        api_logger.info("🎤 SINGLE MIC: Processing microphone audio", {
            "audio_samples": len(audio_data),
            "sample_rate": sample_rate,
            "enable_diarization": enable_diarization,
            "is_translation": is_translation,
            "duration": len(audio_data) / sample_rate,
            "timestamp": datetime.now().isoformat()
        })

        # Convert list to numpy array - EXACTLY like speech_demo.py
        import numpy as np
        audio_array = np.array(audio_data, dtype=np.float32)
        
        print(f"📊 Microphone audio: {len(audio_array)} samples, {sample_rate}Hz")
        print(f"📊 Duration: {len(audio_array) / sample_rate:.2f} seconds")

        # Persist a debug copy of the captured microphone audio so we can
        # compare it with CLI captures when investigating quality issues.
        try:
            debug_dir = os.path.join(project_root, "debug_audio")
            os.makedirs(debug_dir, exist_ok=True)
            temp_path = AudioFormatUtils.save_audio_to_temp_file(audio_array, sample_rate)
            debug_filename = os.path.join(
                debug_dir,
                f"ui_mic_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav",
            )
            os.replace(temp_path, debug_filename)
            api_logger.info("💾 Saved debug UI microphone capture", {
                "path": debug_filename,
                "samples": len(audio_array),
                "sample_rate": sample_rate
            })
        except Exception as debug_error:
            api_logger.warning("⚠️ Failed to save UI microphone debug audio", {
                "error": str(debug_error)
            })

        # Log a short preview of the first samples for debugging
        try:
            preview_count = min(10, len(audio_array))
            preview_values = [float(x) for x in audio_array[:preview_count]]
            api_logger.debug("🔍 Audio sample preview", {
                "preview": preview_values,
                "preview_count": preview_count
            })
        except Exception as preview_error:
            api_logger.warning("⚠️ Failed to log audio sample preview", {
                "error": str(preview_error)
            })

        # DEBUG: Check audio data quality
        print(f"🔍 DEBUG: Audio array shape: {audio_array.shape}")
        print(f"🔍 DEBUG: Audio array dtype: {audio_array.dtype}")
        print(f"🔍 DEBUG: Audio array min/max: {audio_array.min():.6f} / {audio_array.max():.6f}")
        print(f"🔍 DEBUG: Audio array mean: {audio_array.mean():.6f}")
        print(f"🔍 DEBUG: Non-zero samples: {np.count_nonzero(audio_array)}")
        print(f"🔍 DEBUG: Audio array size in MB: {(len(audio_array) * 4) / (1024 * 1024):.2f}")
        
        # Check if audio has any actual content (not just silence)
        audio_rms = np.sqrt(np.mean(audio_array**2))
        print(f"🔍 DEBUG: Audio RMS level: {audio_rms:.6f}")
        
        if audio_rms < 0.001:
            print("⚠️ WARNING: Audio appears to be mostly silence or very quiet!")
        else:
            print("✅ Audio has detectable content")

        # Setup speech configuration using SDK factory
        speech_config = get_speech_config(
            model="whisper-large-v3-turbo",
            is_translation=is_translation,
            target_language=target_language,
            enable_diarization=enable_diarization,
        )

        # Create recognizer - EXACTLY like speech_demo.py
        recognizer = SpeechRecognizer(
            speech_config=speech_config,
            translation_target_language=target_language
        )

        # Process with groq_speech - EXACTLY like speech_demo.py process_microphone_single
        if enable_diarization:
            # For diarization, save to temp file and use process_file - EXACTLY like speech_demo.py
            temp_path = AudioFormatUtils.save_audio_to_temp_file(audio_array, sample_rate)
            
            try:
                result = await recognizer.process_file(temp_path, enable_diarization=True, is_translation=is_translation)
            finally:
                # Clean up temporary file using SDK utility
                AudioFormatUtils.cleanup_temp_file(temp_path)
        else:
            # For non-diarization, use chunked audio data processing - EXACTLY like speech_demo.py
            result = recognizer.recognize_audio_data_chunked(audio_array, sample_rate, is_translation=is_translation)

        # Return result - EXACTLY like speech_demo.py
        if hasattr(result, "text") and result.text:
            print(f"✅ Single microphone recognition successful: '{result.text}'")
            return RecognitionResponse(
                success=True,
                text=result.text,
                confidence=getattr(result, 'confidence', 0.0),
                language=getattr(result, 'language', 'Unknown')
            )
        elif hasattr(result, "segments") and result.segments:
            print(f"✅ Single microphone diarization successful: {result.num_speakers} speakers, {len(result.segments)} segments")
            
            # Convert segments to the format expected by frontend
            segments_data = []
            full_text_parts = []
            
            for segment in result.segments:
                segment_text = getattr(segment, 'text', '') or getattr(segment, 'transcription', '') or '[No text]'
                if segment_text and segment_text.strip() and segment_text != '[No text]':
                    full_text_parts.append(segment_text)
                
                segments_data.append({
                    "speaker_id": segment.speaker_id,
                    "text": segment_text,
                    "start_time": getattr(segment, 'start_time', 0.0),
                    "end_time": getattr(segment, 'end_time', 0.0)
                })
            
            # Combine all segment texts into main text
            combined_text = " ".join(full_text_parts) if full_text_parts else "[No speech detected]"
            
            return RecognitionResponse(
                success=True,
                text=combined_text,
                confidence=getattr(result, 'confidence', 0.95),
                language=getattr(result, 'language', 'Unknown'),
                segments=segments_data,
                num_speakers=result.num_speakers
            )
        else:
            return RecognitionResponse(success=False, error="No speech detected")

    except Exception as e:
        api_logger.error("Error processing single microphone recognition", {
            "error": str(e)
        })
        import traceback
        traceback.print_exc()
        return RecognitionResponse(success=False, error=str(e))


@app.post("/api/v1/recognize-microphone-continuous", response_model=RecognitionResponse)
async def recognize_microphone_continuous(request: dict):
    """Continuous microphone recognition - EXACTLY like speech_demo.py process_microphone_continuous."""
    try:
        # Extract audio data and parameters - EXACTLY like speech_demo.py
        audio_data = request.get("audio_data")  # Raw float32 array as list
        sample_rate = request.get("sample_rate", 16000)
        enable_diarization = request.get("enable_diarization", False)
        is_translation = request.get("is_translation", False)
        target_language = request.get("target_language", "en")
        
        if not audio_data:
            raise HTTPException(status_code=400, detail="Audio data is required")

        api_logger.info("🎤 CONTINUOUS MIC: Processing microphone audio chunk", {
            "audio_samples": len(audio_data),
            "sample_rate": sample_rate,
            "enable_diarization": enable_diarization,
            "is_translation": is_translation,
            "duration": len(audio_data) / sample_rate,
            "timestamp": datetime.now().isoformat()
        })

        # Convert list to numpy array - EXACTLY like speech_demo.py
        import numpy as np
        audio_array = np.array(audio_data, dtype=np.float32)
        
        print(f"📊 Continuous microphone chunk: {len(audio_array)} samples, {sample_rate}Hz")
        print(f"📊 Duration: {len(audio_array) / sample_rate:.2f} seconds")

        # Setup speech configuration using SDK factory
        speech_config = get_speech_config(
            model="whisper-large-v3-turbo",
            is_translation=is_translation,
            target_language=target_language,
            enable_diarization=enable_diarization,
        )

        # Create recognizer - EXACTLY like speech_demo.py
        recognizer = SpeechRecognizer(
            speech_config=speech_config,
            translation_target_language=target_language
        )

        # Process with groq_speech - EXACTLY like speech_demo.py process_microphone_continuous
        if enable_diarization:
            # For diarization, save to temp file and use process_file - EXACTLY like speech_demo.py
            temp_path = AudioFormatUtils.save_audio_to_temp_file(audio_array, sample_rate)
            
            try:
                result = await recognizer.process_file(temp_path, enable_diarization=True, is_translation=is_translation)
            finally:
                # Clean up temporary file using SDK utility
                AudioFormatUtils.cleanup_temp_file(temp_path)
        else:
            # For non-diarization, use direct audio data processing - EXACTLY like speech_demo.py
            result = recognizer.recognize_audio_data(audio_array, sample_rate, is_translation=is_translation)

        # Return result - EXACTLY like speech_demo.py
        if hasattr(result, "text") and result.text:
            print(f"✅ Continuous microphone recognition successful: '{result.text}'")
            return RecognitionResponse(
                success=True,
                text=result.text,
                confidence=getattr(result, 'confidence', 0.0),
                language=getattr(result, 'language', 'Unknown')
            )
        elif hasattr(result, "segments") and result.segments:
            print(f"✅ Continuous microphone diarization successful: {result.num_speakers} speakers, {len(result.segments)} segments")
            
            # Convert segments to the format expected by frontend
            segments_data = []
            full_text_parts = []
            
            for segment in result.segments:
                segment_text = getattr(segment, 'text', '') or getattr(segment, 'transcription', '') or '[No text]'
                if segment_text and segment_text.strip() and segment_text != '[No text]':
                    full_text_parts.append(segment_text)
                
                segments_data.append({
                    "speaker_id": segment.speaker_id,
                    "text": segment_text,
                    "start_time": getattr(segment, 'start_time', 0.0),
                    "end_time": getattr(segment, 'end_time', 0.0)
                })
            
            # Combine all segment texts into main text
            combined_text = " ".join(full_text_parts) if full_text_parts else "[No speech detected]"
            
            return RecognitionResponse(
                success=True,
                text=combined_text,
                confidence=getattr(result, 'confidence', 0.95),
                language=getattr(result, 'language', 'Unknown'),
                segments=segments_data,
                num_speakers=result.num_speakers
            )
        else:
            return RecognitionResponse(success=False, error="No speech detected")

    except Exception as e:
        api_logger.error("Error processing continuous microphone recognition", {
            "error": str(e)
        })
        import traceback
        traceback.print_exc()
        return RecognitionResponse(success=False, error=str(e))


@app.post("/api/v1/vad/should-create-chunk", response_model=VADResponse)
async def vad_should_create_chunk(request: VADRequest):
    """VAD endpoint to determine if a chunk should be created."""
    try:
        # Convert list to numpy array
        import numpy as np
        audio_array = np.array(request.audio_data, dtype=np.float32)
        
        # Create VAD service instance
        vad_config = VADConfig()
        vad_service = VADService(vad_config)
        
        # Determine if chunk should be created
        should_create, reason = vad_service.should_create_chunk(
            audio_array, 
            request.sample_rate, 
            request.max_duration_seconds
        )
        
        # Get audio level for visual feedback
        audio_level = vad_service.get_audio_level(audio_array)
        
        api_logger.info("🎤 VAD analysis completed", {
            "should_create_chunk": should_create,
            "reason": reason,
            "audio_level": audio_level,
            "audio_samples": len(audio_array),
            "sample_rate": request.sample_rate
        })
        
        return VADResponse(
            success=True,
            should_create_chunk=should_create,
            reason=reason,
            audio_level=audio_level
        )
        
    except Exception as e:
        api_logger.error(f"❌ VAD analysis failed: {e}")
        return VADResponse(
            success=False,
            should_create_chunk=False,
            reason="VAD analysis failed",
            audio_level=0.0,
            error=str(e)
        )


@app.post("/api/v1/vad/audio-level", response_model=VADResponse)
async def vad_get_audio_level(request: VADRequest):
    """VAD endpoint to get audio level for visual feedback."""
    try:
        # Convert list to numpy array
        import numpy as np
        audio_array = np.array(request.audio_data, dtype=np.float32)
        
        # Create VAD service instance
        vad_config = VADConfig()
        vad_service = VADService(vad_config)
        
        # Get audio level
        audio_level = vad_service.get_audio_level(audio_array)
        
        return VADResponse(
            success=True,
            should_create_chunk=False,
            reason="Audio level calculated",
            audio_level=audio_level
        )
        
    except Exception as e:
        api_logger.error(f"❌ Audio level calculation failed: {e}")
        return VADResponse(
            success=False,
            should_create_chunk=False,
            reason="Audio level calculation failed",
            audio_level=0.0,
            error=str(e)
        )


if __name__ == "__main__":
    # Environment variables already loaded from root .env.api at module level
    
    # Get API configuration from environment variables
    api_host = os.getenv("API_HOST", "0.0.0.0")
    api_port = int(os.getenv("API_PORT", "8000"))
    api_workers = int(os.getenv("API_WORKERS", "1"))
    api_log_level = os.getenv("API_LOG_LEVEL", "info").lower()
    
    print("🚀 Starting Groq Speech API Server...")
    print(f"📖 API Documentation: http://{api_host}:{api_port}/docs")
    print(f"🔍 Health Check: http://{api_host}:{api_port}/health")
    print(f"🌐 Server: {api_host}:{api_port}")
    print(f"👥 Workers: {api_workers}")

    uvicorn.run(
        "api.server:app", 
        host=api_host, 
        port=api_port, 
        workers=api_workers,
        reload=True, 
        log_level=api_log_level
    )
