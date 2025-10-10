#!/usr/bin/env python3
"""
Clean Speech Demo - Leveraging SDK's Internal Capabilities.

This demo shows how the SDK now handles all complexity internally,
providing a clean, simple interface for consumers.

Key Improvements:
1. No fallback logic in consumer code - SDK handles it internally
2. No manual audio preprocessing - AudioProcessor handles it
3. No complex error handling - SDK provides consistent responses
4. Clean, simple API calls with minimal consumer code

Usage:
    python speech_demo.py --file audio.wav
    python speech_demo.py --file audio.wav --diarize
    python speech_demo.py --microphone-mode single
    python speech_demo.py --microphone-mode continuous --diarize
"""

import argparse
import sys
import os
from pathlib import Path
import time
import warnings

# Add the parent directory to the path to import groq_speech
sys.path.insert(0, str(Path(__file__).parent.parent))

from groq_speech.speech_recognizer import SpeechRecognizer
from groq_speech.speech_config import SpeechConfig


def configure_warnings(verbose: bool = False):
    """Configure warning display based on verbose mode."""
    if not verbose:
        # Suppress PyTorch/TorchAudio deprecation warnings in production mode
        warnings.filterwarnings("ignore", category=UserWarning, module="torchaudio")
        warnings.filterwarnings("ignore", category=UserWarning, module="pyannote")
        warnings.filterwarnings("ignore", category=UserWarning, module="speechbrain")
        warnings.filterwarnings("ignore", message=".*torchaudio.*")
        warnings.filterwarnings("ignore", message=".*TorchCodec.*")
    else:
        # Show all warnings in verbose mode
        warnings.resetwarnings()


def _trim_silence_from_end(audio_data, sample_rate, silence_threshold=0.01, min_silence_duration=0.5):
    """
    Trim silence from the end of audio data to improve processing quality.
    
    Args:
        audio_data: Audio data as numpy array
        sample_rate: Sample rate of the audio
        silence_threshold: RMS threshold below which audio is considered silence
        min_silence_duration: Minimum duration of silence to trim (seconds)
        
    Returns:
        Trimmed audio data
    """
    import numpy as np
    
    if len(audio_data) == 0:
        return audio_data
    
    # Calculate RMS for each 0.1 second window
    window_size = int(sample_rate * 0.1)  # 0.1 second windows
    min_silence_samples = int(sample_rate * min_silence_duration)
    
    # Find the last non-silent window
    last_non_silent = len(audio_data)
    
    for i in range(len(audio_data) - window_size, 0, -window_size):
        window = audio_data[i:i + window_size]
        rms = np.sqrt(np.mean(window**2))
        
        if rms > silence_threshold:
            last_non_silent = i + window_size
            break
    
    # Ensure we don't trim too much (keep at least 0.5 seconds)
    min_keep_samples = int(sample_rate * 0.5)
    if last_non_silent < min_keep_samples:
        last_non_silent = min_keep_samples
    
    return audio_data[:last_non_silent]


def validate_environment(enable_diarization: bool = False):
    """Validate the environment configuration."""
    print("🔧 Validating Environment Configuration")
    print("=" * 50)

    # Check required environment variables
    required_vars = ["GROQ_API_KEY"]
    missing_vars = []

    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)

    if missing_vars:
        print(f"❌ Missing required environment variables: {missing_vars}")
        print("Please set these in your .env file")
        return False

    # Only check HF_TOKEN if diarization is needed
    if enable_diarization:
        hf_token = SpeechConfig.get_hf_token()
        if not hf_token:
            print("⚠️  HF_TOKEN not configured - Limited diarization capability")
            print("💡 For full speaker diarization, configure HF_TOKEN:")
            print("   1. Get token from: https://huggingface.co/settings/tokens")
            print("   2. Accept license: https://huggingface.co/pyannote/speaker-diarization-3.1")
            print("   3. Update groq_speech/.env with: HF_TOKEN=your_actual_token_here")
        else:
            print("✅ HF_TOKEN configured - Full Pyannote.audio diarization enabled")
    else:
        print("ℹ️  Diarization not requested - Skipping HF_TOKEN validation")

    print("✅ Environment validation passed")
    return True


async def process_audio_file(audio_file: str, mode: str, recognizer: SpeechRecognizer, enable_diarization: bool = True):
    """
    Process audio file - NOW ULTRA SIMPLE!
    
    The SDK now handles:
    - Fallback logic internally
    - Audio preprocessing automatically
    - Error handling consistently
    - Format conversion seamlessly
    """
    print(f"\n📁 Processing Audio File: {audio_file}")
    print("=" * 60)
    
    if enable_diarization:
        print("🎭 Diarization Pipeline: Pyannote.audio FIRST, then Groq API per segment")
    else:
        print("🎯 Direct Pipeline: Groq API processing without diarization")

    if not os.path.exists(audio_file):
        print(f"❌ Audio file not found: {audio_file}")
        return None

    # ULTRA SIMPLE API CALLS - SDK handles EVERYTHING internally!
    try:
        is_translation = (mode == "translation")
        result = await recognizer.process_file(audio_file, enable_diarization=enable_diarization, is_translation=is_translation)
        return result

    except Exception as e:
        print(f"❌ File processing failed: {e}")
        return None


async def process_microphone_single(mode: str, recognizer: SpeechRecognizer, enable_diarization: bool = False):
    """Simple single-shot microphone recording - SDK handles complexity internally."""
    print(f"\n🎤 Single Microphone {mode.title()}")
    print("=" * 50)
    print("💡 Press Ctrl+C to stop recording and process audio")

    try:
        import pyaudio
        import numpy as np

        # Audio recording parameters
        CHUNK = 8192
        FORMAT = pyaudio.paFloat32
        CHANNELS = 1
        RATE = 16000

        print("🎤 Recording started - speak naturally...")
        print("💡 Press Ctrl+C when you want to stop recording and process the audio")

        p = pyaudio.PyAudio()
        stream = p.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK,
        )

        all_frames = []
        print("🎤 Recording... Press Ctrl+C to stop")

        # Simple visual feedback
        last_visual_update = time.time()
        visual_update_interval = 1.0

        try:
            # Simple recording loop
            while True:
                data = stream.read(CHUNK)
                all_frames.append(data)
                
                # Simple visual feedback
                current_time = time.time()
                if current_time - last_visual_update >= visual_update_interval:
                    duration = len(all_frames) * CHUNK / RATE
                    estimated_size_mb = (len(all_frames) * CHUNK * 4) / (1024 * 1024)
                    print(f"\r🎤 Recording... {duration:.1f}s | {estimated_size_mb:.1f}MB", end="", flush=True)
                    last_visual_update = current_time

        except KeyboardInterrupt:
            print("\n🛑 Recording stopped by user, processing audio...")
            
            if not all_frames:
                print("❌ No audio recorded")
                return None

            # Convert all audio to numpy array
            audio_data = np.frombuffer(b"".join(all_frames), dtype=np.float32)
            total_duration = len(audio_data) / RATE
            print(f"📊 Total recording: {total_duration:.1f}s ({len(audio_data)} samples)")

            # SIMPLE API CALL - SDK handles everything!
            if enable_diarization:
                # For diarization, we need to save to a temporary file and use process_file
                import tempfile
                import soundfile as sf
                
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                    temp_path = temp_file.name
                    sf.write(temp_path, audio_data, RATE)
                
                try:
                    is_translation = (mode == "translation")
                    # Process with diarization - let it complete even if interrupted
                    try:
                        result = await recognizer.process_file(temp_path, enable_diarization=True, is_translation=is_translation)
                    except KeyboardInterrupt:
                        # If interrupted during processing, let it complete and show results
                        print("\n🛑 Processing interrupted by user, but letting diarization complete...")
                        result = await recognizer.process_file(temp_path, enable_diarization=True, is_translation=is_translation)
                finally:
                    # Clean up temporary file
                    try:
                        os.unlink(temp_path)
                    except:
                        pass
            else:
                # For non-diarization, use chunked audio data processing
                is_translation = (mode == "translation")
                result = recognizer.recognize_audio_data_chunked(audio_data, RATE, is_translation=is_translation)

            if result:
                if hasattr(result, "text") and result.text:
                    print(f"✅ {mode.title()} completed successfully!")
                    return result
                elif hasattr(result, "segments") and result.segments:
                    print(f"✅ {mode.title()} completed successfully!")
                    print(f"🎭 Speakers detected: {result.num_speakers}")
                    print(f"📊 Total segments: {len(result.segments)}")
                    return result
                else:
                    print(f"❌ {mode.title()} failed - no text or segments detected")
                    return None
            else:
                print(f"❌ {mode.title()} failed - no result")
                return None

        finally:
            stream.stop_stream()
            stream.close()
            p.terminate()

    except ImportError:
        print("❌ PyAudio not available. Install with: pip install pyaudio")
        return None
    except Exception as e:
        print(f"❌ Single microphone processing failed: {e}")
        return None


async def process_microphone_continuous(mode: str, recognizer: SpeechRecognizer, enable_diarization: bool = False):
    """Continuous microphone transcription - SDK handles VAD and chunking internally."""
    print(f"\n🎤 Continuous Microphone {mode.title()}")
    print("=" * 50)
    print("💡 Press Ctrl+C to stop")

    try:
        import pyaudio
        import numpy as np
        import tempfile
        import threading
        import queue

        # Audio recording parameters
        CHUNK = 8192
        FORMAT = pyaudio.paFloat32
        CHANNELS = 1
        RATE = 16000
        MAX_DURATION_SECONDS = 390  # 6.5 minutes

        print(f"🎤 Recording continuously...")
        print("💡 Press Ctrl+C to stop")

        p = pyaudio.PyAudio()
        stream = p.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK,
        )

        accumulated_audio = []
        last_visual_update = time.time()
        visual_update_interval = 0.5

        try:
            while True:
                data = stream.read(CHUNK, exception_on_overflow=False)
                accumulated_audio.append(data)
                
                # Convert current audio to numpy for VAD analysis
                audio_bytes = b"".join(accumulated_audio)
                audio_array = np.frombuffer(audio_bytes, dtype=np.float32)
                duration = len(audio_array) / RATE
                
                # Visual feedback using SDK method
                current_time = time.time()
                if current_time - last_visual_update >= visual_update_interval:
                    audio_level = recognizer.get_audio_level(audio_array[-RATE:])  # Last 1 second
                    level_bars = "█" * int(audio_level * 20) + "░" * (20 - int(audio_level * 20))
                    print(f"\r🎤 Listening... [{level_bars}] {audio_level:.2f} | {duration:.1f}s | {len(audio_bytes)/1024/1024:.1f}MB", end="", flush=True)
                    last_visual_update = current_time
                
                # Check if we should create a chunk using SDK method
                should_create, reason = recognizer.should_create_chunk(
                    audio_array, RATE, MAX_DURATION_SECONDS
                )
                
                if should_create:
                    print(f"\n🔄 Chunk created: {reason}")
                    
                    # Trim silence from the end of the chunk for better processing
                    trimmed_audio = _trim_silence_from_end(audio_array, RATE)
                    if len(trimmed_audio) < RATE:  # Less than 1 second of audio
                        print(f"⚠️  Chunk too short after silence trimming ({len(trimmed_audio)/RATE:.1f}s), skipping...")
                        accumulated_audio = []
                        continue
                    
                    print(f"📊 Processing trimmed chunk: {len(trimmed_audio)/RATE:.1f}s (trimmed from {len(audio_array)/RATE:.1f}s)")
                    
                    # SIMPLE API CALL - SDK handles everything!
                    if enable_diarization:
                        # For diarization, we need to save to a temporary file and use process_file
                        import tempfile
                        import soundfile as sf
                        
                        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                            temp_path = temp_file.name
                            sf.write(temp_path, trimmed_audio, RATE)
                        
                        try:
                            is_translation = (mode == "translation")
                            # Process with diarization - let it complete even if interrupted
                            result = await recognizer.process_file(temp_path, enable_diarization=True, is_translation=is_translation)
                        finally:
                            # Clean up temporary file
                            try:
                                os.unlink(temp_path)
                            except:
                                pass
                    else:
                        # For non-diarization, use chunked audio data processing
                        is_translation = (mode == "translation")
                        result = recognizer.recognize_audio_data_chunked(trimmed_audio, RATE, is_translation=is_translation)

                    if result:
                        if hasattr(result, "text") and result.text:
                            print(f"✅ {mode.title()}: {result.text}")
                        elif hasattr(result, "segments") and result.segments:
                            print(f"✅ {mode.title()}: Diarization completed")
                            print(f"🎭 Speakers: {result.num_speakers}, Segments: {len(result.segments)}")
                            
                            # Display individual speaker segments with their text
                            for i, segment in enumerate(result.segments):
                                speaker = segment.speaker_id
                                text = getattr(segment, 'text', '') or getattr(segment, 'transcription', '') or '[No text]'
                                if text and text.strip():
                                    print(f"🎤 {speaker}: {text}")
                                else:
                                    print(f"🎤 {speaker}: [No text detected]")
                    
                    # Reset accumulated audio
                    accumulated_audio = []

        except KeyboardInterrupt:
            print("\n🛑 Stopping continuous recognition...")
            
            # Process any remaining audio
            if accumulated_audio:
                print("🔄 Processing final chunk...")
                audio_bytes = b"".join(accumulated_audio)
                audio_array = np.frombuffer(audio_bytes, dtype=np.float32)
                
                # SIMPLE API CALL - SDK handles everything!
                if enable_diarization:
                    # For diarization, we need to save to a temporary file and use process_file
                    import tempfile
                    import soundfile as sf
                    
                    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                        temp_path = temp_file.name
                        sf.write(temp_path, audio_array, RATE)
                    
                    try:
                        is_translation = (mode == "translation")
                        # Process with diarization - let it complete even if interrupted
                        try:
                            result = await recognizer.process_file(temp_path, enable_diarization=True, is_translation=is_translation)
                        except KeyboardInterrupt:
                            # If interrupted during processing, let it complete and show results
                            print("\n🛑 Processing interrupted by user, but letting diarization complete...")
                            result = await recognizer.process_file(temp_path, enable_diarization=True, is_translation=is_translation)
                    finally:
                        # Clean up temporary file
                        try:
                            os.unlink(temp_path)
                        except:
                            pass
                else:
                    # For non-diarization, use direct audio data processing
                    is_translation = (mode == "translation")
                    result = recognizer.recognize_audio_data(audio_array, RATE, is_translation=is_translation)

                if result:
                    if hasattr(result, "text") and result.text:
                        print(f"✅ Final {mode.title()}: {result.text}")
                    elif hasattr(result, "segments") and result.segments:
                        print(f"✅ Final {mode.title()}: Diarization completed")
                        print(f"🎭 Speakers: {result.num_speakers}, Segments: {len(result.segments)}")
                        
                        # Display individual speaker segments with their text
                        for i, segment in enumerate(result.segments):
                            speaker = segment.speaker_id
                            text = getattr(segment, 'text', '') or getattr(segment, 'transcription', '') or '[No text]'
                            if text and text.strip():
                                print(f"🎤 {speaker}: {text}")
                            else:
                                print(f"🎤 {speaker}: [No text detected]")
            
            print("✅ Continuous processing completed successfully!")
            return None

        finally:
            try:
                stream.stop_stream()
                stream.close()
                p.terminate()
            except:
                pass

    except ImportError:
        print("❌ PyAudio not available. Install with: pip install pyaudio")
        return None
    except Exception as e:
        print(f"❌ Continuous microphone processing failed: {e}")
        return None


async def main():
    """Main function - NOW ULTRA SIMPLE!"""
    parser = argparse.ArgumentParser(
        description="Clean Speech Demo - Leveraging SDK's Internal Capabilities",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
EXAMPLES:
    # File-based transcription (SDK handles all complexity internally)
    python speech_demo.py --file audio.wav
    
    # File-based translation with diarization
    python speech_demo.py --file audio.wav --operation translation --diarize
    
    # Microphone single mode
    python speech_demo.py --microphone-mode single
    
    # Microphone continuous mode
    python speech_demo.py --microphone-mode continuous --diarize
        """,
    )

    parser.add_argument(
        "--operation",
        choices=["transcription", "translation"],
        default="transcription",
        help="Operation: transcription or translation",
    )

    parser.add_argument(
        "--microphone-mode",
        choices=["single", "continuous"],
        help="Microphone mode: single or continuous",
    )

    parser.add_argument(
        "--file",
        type=str,
        help="Audio file path for recognition",
    )

    parser.add_argument(
        "--diarize",
        action="store_true",
        help="Enable speaker diarization",
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose debug logging",
    )

    args = parser.parse_args()
    
    # Configure warning display
    configure_warnings(args.verbose)

    # Validate arguments
    if not args.file and not args.microphone_mode:
        parser.error("Either --file or --microphone-mode must be specified")

    if args.file and args.microphone_mode:
        parser.error("Cannot specify both --file and --microphone-mode")

    # Validate environment
    if not validate_environment(args.diarize):
        sys.exit(1)

    # Create speech recognizer - SIMPLE!
    try:
        speech_config = SpeechConfig()
        
        # Configure translation if requested
        if args.operation == "translation":
            speech_config.enable_translation = True
            speech_config.set_translation_target_language("en")
            print("🔀 Translation mode enabled (target: English)")
        
        recognizer = SpeechRecognizer(speech_config)
        print("✅ Speech recognizer initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize speech recognizer: {e}")
        sys.exit(1)

    # Process based on arguments - SIMPLE API CALLS!
    try:
        if args.file:
            result = await process_audio_file(args.file, args.operation, recognizer, args.diarize)
        else:  # microphone
            if args.microphone_mode == "single":
                result = await process_microphone_single(args.operation, recognizer, args.diarize)
            else:  # continuous
                result = await process_microphone_continuous(args.operation, recognizer, args.diarize)

        if result:
            print(f"\n✅ Processing completed successfully!")
            if hasattr(result, "segments"):
                print(f"🎭 Speakers: {result.num_speakers}")
                print(f"📊 Speaker Segment Groups: {len(result.segments)}")
                for i, segment in enumerate(result.segments):
                    speaker = segment.speaker_id
                    text = getattr(segment, "text", "") or "[No text]"
                    print(f"\n🎤 {speaker}:")
                    print(f"      {text}")
            elif hasattr(result, "text"):
                print(f"📝 Text: {result.text}")
        elif args.microphone_mode == "continuous":
            # Continuous mode returns None by design
            print(f"\n✅ Continuous processing completed successfully!")
        else:
            print(f"\n❌ Processing failed")
            sys.exit(1)

    except KeyboardInterrupt:
        # Only exit if we're not in the middle of processing recorded audio
        # The microphone functions handle their own KeyboardInterrupt during recording
        print(f"\n🛑 Processing interrupted by user")
        # Don't exit immediately - let the microphone functions handle their own KeyboardInterrupt
        # and show results if processing was completed
        if result:
            print(f"\n✅ Processing completed successfully!")
            if hasattr(result, "segments"):
                print(f"🎭 Speakers: {result.num_speakers}")
                print(f"📊 Speaker Segment Groups: {len(result.segments)}")
                for i, segment in enumerate(result.segments):
                    speaker = segment.speaker_id
                    text = getattr(segment, "text", "") or "[No text]"
                    print(f"\n🎤 {speaker}:")
                    print(f"      {text}")
            elif hasattr(result, "text"):
                print(f"📝 Text: {result.text}")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    import asyncio
    try:
        exit(asyncio.run(main()))
    except KeyboardInterrupt:
        print(f"\n🛑 Processing interrupted by user")
        exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        exit(1)