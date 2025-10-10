# Groq Speech Library - Core Module

> **⚠️ Disclaimer**: This documents a **demonstrative solution** for educational purposes. This is not a formal SDK and should be used as a reference for learning.

This is the core module of the Groq Speech Library, providing speech recognition, translation, and speaker diarization capabilities with a clean, SOLID-principle-based architecture.

## Quick Start

```python
from groq_speech import SpeechRecognizer, SpeechConfig

# Basic usage
config = SpeechConfig()
recognizer = SpeechRecognizer(config)

# File processing (async)
result = await recognizer.recognize_file("audio.wav")
print(f"Recognized: {result.text}")

# With diarization (async)
result = await recognizer.recognize_file("audio.wav", enable_diarization=True)
if hasattr(result, 'segments'):
    for segment in result.segments:
        print(f"Speaker {segment.speaker_id}: {segment.text}")

# Translation (async)
result = await recognizer.translate_file("audio.wav")
print(f"Translated: {result.text}")
```

## Key Features

- **Real-time Processing**: Support for both file and streaming audio
- **Speaker Diarization**: Multi-speaker detection using Pyannote.audio
- **Voice Activity Detection**: Intelligent audio chunking and silence detection
- **Translation Support**: Automatic translation to target languages
- **Web Interface**: Modern React-based UI for testing and demonstration
- **REST API**: FastAPI backend with WebSocket support

## Table of Contents
1. [Quick Start](#quick-start)
2. [Critical Entry Points](#critical-entry-points)
3. [Architecture Overview](#architecture-overview)
4. [Data Flows](#data-flows)
5. [Configuration System](#configuration-system)
6. [Error Handling](#error-handling)
7. [Performance](#performance)
8. [API Reference](#api-reference)
9. [Migration Guide](#migration-guide)

## Quick Start

```python
from groq_speech import SpeechRecognizer, SpeechConfig

# Basic transcription
config = SpeechConfig()
recognizer = SpeechRecognizer(config)
result = recognizer.recognize_file("audio.wav")

# Translation to English
config.enable_translation = True
recognizer = SpeechRecognizer(config)
result = recognizer.translate_file("audio.wav")

# With speaker diarization
result = recognizer.recognize_file("audio.wav", enable_diarization=True)
```

## Core Classes

### 1. SpeechRecognizer (Primary Entry Point)
**Location**: `groq_speech.speech_recognizer.SpeechRecognizer`

The main class for all speech recognition operations:

```python
from groq_speech import SpeechRecognizer, SpeechConfig

config = SpeechConfig()
recognizer = SpeechRecognizer(config)

# File processing
result = recognizer.recognize_file("audio.wav", enable_diarization=True)
result = recognizer.translate_file("audio.wav", enable_diarization=False)

# Raw audio data processing
result = recognizer.recognize_audio_data(audio_data, sample_rate=16000)
result = recognizer.recognize_audio_data(audio_data, is_translation=True)

# Process file with diarization
result = recognizer.process_file("audio.wav", enable_diarization=True, is_translation=False)
```

**Key Public Methods**:
- `recognize_file(audio_file, enable_diarization=True)` - Process audio files
- `translate_file(audio_file, enable_diarization=True)` - Translate audio files
- `recognize_audio_data(audio_data, sample_rate=16000, is_translation=False)` - Process raw audio data
- `process_file(audio_file, enable_diarization=True, is_translation=False)` - Process files with full control

### 2. SpeechConfig (Configuration Management)
**Location**: `groq_speech.speech_config.SpeechConfig`

Configuration management for speech recognition:

```python
from groq_speech import SpeechConfig

# Create configuration
config = SpeechConfig()
config.api_key = "your-api-key"
config.enable_translation = True
config.set_translation_target_language("en")

# Use with recognizer
recognizer = SpeechRecognizer(config)
```

### 3. Result Objects (Data Access)
**Location**: `groq_speech.speech_recognizer.SpeechRecognitionResult`

Structured result data access:

```python
# Basic recognition result
result = recognizer.recognize_file("audio.wav")
print(f"Text: {result.text}")
print(f"Confidence: {result.confidence}")
print(f"Language: {result.language}")

# Diarization result
result = recognizer.recognize_file("audio.wav", enable_diarization=True)
if hasattr(result, 'segments'):
    print(f"Number of speakers: {result.num_speakers}")
    for segment in result.segments:
        print(f"Speaker {segment.speaker_id}: {segment.text}")
```

### 4. Speaker Diarization
**Location**: `groq_speech.speaker_diarization.SpeakerDiarizer`

Advanced speaker diarization using Pyannote.audio:

```python
from groq_speech import SpeakerDiarizer

diarizer = SpeakerDiarizer()
result = diarizer.diarize_with_accurate_transcription(
    audio_file="audio.wav",
    mode="transcription",
    speech_recognizer=recognizer
)
```

## Architecture Overview

The Library follows a **clean architecture with SOLID principles**:

### Core Components
- **SpeechRecognizer**: Main orchestrator class (Facade pattern)
- **SpeakerDiarizer**: Speaker diarization using Pyannote.audio
- **VADService**: Voice Activity Detection and audio chunking
- **SpeechConfig**: Configuration management

### Internal Services (Dependency Injection)
- **APIClient**: Groq API communication
- **AudioProcessor**: Audio preprocessing and optimization
- **ResponseParser**: API response parsing
- **EventManager**: Event-driven architecture

### Design Patterns
- **Facade Pattern**: SpeechRecognizer provides simple interface
- **Dependency Injection**: Services injected for testability
- **Single Responsibility**: Each class has one clear purpose
- **Interface Segregation**: Small, focused interfaces

## Data Flows

### 1. File Processing (No Diarization)
**Command**: `python speech_demo.py --file audio.wav`

```
User
  ↓
File Input (audio.wav)
  ↓
SpeechRecognizer.recognize_file(enable_diarization=False)
  ↓
AudioProcessor → GroqAPIClient → ResponseParser
  ↓
SpeechRecognitionResult
  ↓
User Response (transcribed text)
```

### 2. File Processing (With Diarization)
**Command**: `python speech_demo.py --file audio.wav --diarize`

```
User
  ↓
File Input (audio.wav)
  ↓
SpeechRecognizer.recognize_file(enable_diarization=True)
  ↓
DiarizationService → Pyannote.audio → Speaker Detection
  ↓
Smart Grouping (24MB chunks) → GroqAPIClient (per segment)
  ↓
DiarizationResult (with speaker attribution)
  ↓
User Response (speaker-separated transcriptions)
```

### 3. Microphone Single Mode
**Command**: `python speech_demo.py --microphone-mode single`

```
User
  ↓
Microphone Input (real-time recording)
  ↓
SpeechRecognizer.recognize_microphone()
  ↓
AudioProcessor → GroqAPIClient → ResponseParser
  ↓
SpeechRecognitionResult
  ↓
User Response (transcribed text)
```

### 4. Microphone Continuous Mode
**Command**: `python speech_demo.py --microphone-mode continuous`

```
User
  ↓
Microphone Input (continuous streaming)
  ↓
SpeechRecognizer.recognize_microphone() (continuous loop)
  ↓
AudioProcessor → VADService → Audio Chunking
  ↓
For each chunk: GroqAPIClient → ResponseParser
  ↓
SpeechRecognitionResult (per chunk)
  ↓
User Response (continuous transcriptions)
```

### 5. Translation Processing
**Command**: `python speech_demo.py --file audio.wav --operation translation`

```
User
  ↓
Audio Input → SpeechRecognizer.translate_file/translate_audio_data()
  ↓
GroqAPIClient (translation mode) → ResponseParser
  ↓
SpeechRecognitionResult (translated text)
  ↓
User Response (English translation)
```

## Configuration System

### Environment Variables
```bash
# Required
GROQ_API_KEY=your_api_key_here

# Optional
HF_TOKEN=your_huggingface_token_here  # For diarization
GROQ_MODEL_ID=whisper-large-v3        # Model selection
GROQ_TEMPERATURE=0.0                  # Model temperature
```

### Configuration Classes
- **SpeechConfig**: Speech recognition settings
- **DiarizationConfig**: Diarization parameters
- **VADConfig**: Voice Activity Detection settings

### Configuration Validation
```python
from groq_speech import SpeechConfig

# Get current settings
settings = SpeechConfig.get_diarization_config()
print(f"Chunk strategy: {settings['chunk_strategy']}")
```

## Error Handling

### Exception Hierarchy
```python
from groq_speech.exceptions import (
    GroqSpeechException,      # Base exception
    ConfigurationError,       # Configuration issues
    APIError,                 # API communication errors
    AudioError,               # Audio processing errors
    DiarizationError          # Diarization-specific errors
)

try:
    result = recognizer.recognize_file("audio.wav")
except APIError as e:
    print(f"API Error: {e}")
except AudioError as e:
    print(f"Audio Error: {e}")
```

### Fallback Mechanisms
- **Diarization Fallback**: Falls back to basic transcription if diarization fails
- **API Retry**: Automatic retry for transient API errors
- **Audio Processing**: Graceful handling of audio format issues
- **VAD Fallback**: Multiple VAD implementations with fallback chain

## Performance

### Big O Complexity
- **File Processing**: O(n) where n is audio length
- **Diarization**: O(n log n) due to Pyannote.audio processing
- **API Calls**: O(1) per chunk, O(k) total where k is number of chunks
- **Memory Usage**: O(1) for streaming, O(n) for file processing

### Optimization Features
- **Smart Grouping**: 24MB-optimized speaker segment grouping
- **Voice Activity Detection**: Intelligent silence detection
- **Caching**: Model and configuration caching
- **Retry Logic**: Automatic retry for transient errors
- **Parallel Processing**: Concurrent processing where applicable

### Thread Safety
The Library is designed to be thread-safe:
- **Thread-safe request tracking**
- **Lock-protected result collection**
- **Concurrent request management**
- **Safe configuration access**

### Memory Management
- **Efficient audio data handling**
- **Configurable processing modes**
- **Automatic cleanup of temporary data**
- **Streaming support for large files**

## API Reference

For detailed API documentation, see:
- [API_REFERENCE.md](API_REFERENCE.md) - Complete API reference

## Migration Guide

### Breaking Changes
- **AudioConfig removed**: Functionality moved to SpeechRecognizer
- **EnhancedDiarizer removed**: Consolidated into Diarizer
- **Multiple entry points**: Simplified to single SpeechRecognizer
- **Constructor parameters**: Simplified and standardized

### Migration Guide
```python
# Old way
from groq_speech import AudioConfig, EnhancedDiarizer
audio_config = AudioConfig()
diarizer = EnhancedDiarizer()

# New way
from groq_speech import SpeechRecognizer
recognizer = SpeechRecognizer()
# All functionality through SpeechRecognizer
```

## Future Enhancements

### Planned Features
1. **Real-time Streaming**: Optimize for live microphone input
2. **Speaker Persistence**: Maintain speaker identity across sessions
3. **Advanced Chunking**: Intelligent audio segmentation
4. **Performance Monitoring**: Real-time pipeline metrics

### Integration Opportunities
1. **Custom Models**: Support for other speaker detection models
2. **Multi-language**: Enhanced language support
3. **Cloud Processing**: Distributed processing capabilities
4. **API Extensions**: Additional Groq API features