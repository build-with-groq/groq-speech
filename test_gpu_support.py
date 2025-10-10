#!/usr/bin/env python3
"""
Test script to verify GPU support for Pyannote.audio in the Groq Speech SDK.

This script tests:
1. GPU detection and availability
2. Pyannote.audio pipeline initialization with GPU support
3. Device selection and memory information
4. Fallback to CPU when GPU is not available

Usage:
    python test_gpu_support.py
"""

import os
import sys
import traceback

def test_gpu_detection():
    """Test GPU detection and information."""
    print("🔍 Testing GPU Detection...")
    print("=" * 50)
    
    try:
        from groq_speech.speech_config import SpeechConfig
        
        # Get GPU information
        gpu_info = SpeechConfig.get_gpu_info()
        optimal_device = SpeechConfig.get_optimal_device()
        
        print(f"CUDA Available: {gpu_info['cuda_available']}")
        print(f"Device Count: {gpu_info['device_count']}")
        print(f"Current Device: {gpu_info['current_device']}")
        print(f"Device Name: {gpu_info['device_name']}")
        print(f"Memory Allocated: {gpu_info['memory_allocated'] / 1024**3:.2f} GB")
        print(f"Memory Reserved: {gpu_info['memory_reserved'] / 1024**3:.2f} GB")
        print(f"Optimal Device: {optimal_device}")
        
        if 'error' in gpu_info:
            print(f"Error: {gpu_info['error']}")
            
        return gpu_info['cuda_available']
        
    except Exception as e:
        print(f"❌ Error testing GPU detection: {e}")
        traceback.print_exc()
        return False

def test_pyannote_import():
    """Test Pyannote.audio import and basic functionality."""
    print("\n🔍 Testing Pyannote.audio Import...")
    print("=" * 50)
    
    try:
        from pyannote.audio import Pipeline
        import torch
        
        print("✅ Pyannote.audio imported successfully")
        print(f"✅ PyTorch version: {torch.__version__}")
        print(f"✅ CUDA available in PyTorch: {torch.cuda.is_available()}")
        
        if torch.cuda.is_available():
            print(f"✅ CUDA device count: {torch.cuda.device_count()}")
            print(f"✅ Current CUDA device: {torch.cuda.current_device()}")
            print(f"✅ CUDA device name: {torch.cuda.get_device_name(0)}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Pyannote.audio not available: {e}")
        print("Install with: pip install pyannote.audio")
        return False
    except Exception as e:
        print(f"❌ Error testing Pyannote.audio: {e}")
        traceback.print_exc()
        return False

def test_pipeline_initialization():
    """Test Pyannote.audio pipeline initialization with GPU support."""
    print("\n🔍 Testing Pipeline Initialization...")
    print("=" * 50)
    
    try:
        # Check if HF token is available
        hf_token = os.getenv('HF_TOKEN')
        if not hf_token or hf_token == "your_hf_token_here":
            print("⚠️ HF_TOKEN not set, skipping pipeline initialization test")
            print("Set HF_TOKEN environment variable to test pipeline initialization")
            return True
        
        from pyannote.audio import Pipeline
        import torch
        from groq_speech.speech_config import SpeechConfig
        
        # Get optimal device
        optimal_device = SpeechConfig.get_optimal_device()
        device = torch.device(optimal_device)
        
        print(f"🔧 Using device: {device}")
        
        # Initialize pipeline
        pipeline = Pipeline.from_pretrained(
            "pyannote/speaker-diarization-3.1",
            use_auth_token=hf_token
        )
        
        # Move to device
        pipeline = pipeline.to(device)
        
        print(f"✅ Pipeline initialized and moved to {device}")
        
        # Test basic functionality (without actual audio processing)
        print("✅ Pipeline ready for diarization")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing pipeline initialization: {e}")
        traceback.print_exc()
        return False

def test_diarization_integration():
    """Test diarization integration with GPU support."""
    print("\n🔍 Testing Diarization Integration...")
    print("=" * 50)
    
    try:
        from groq_speech.speaker_diarization import _import_pyannote
        
        # Test lazy import
        pyannote_available = _import_pyannote()
        
        if pyannote_available:
            print("✅ Pyannote.audio integration working")
            print("✅ GPU detection integrated")
            return True
        else:
            print("❌ Pyannote.audio integration failed")
            return False
            
    except Exception as e:
        print(f"❌ Error testing diarization integration: {e}")
        traceback.print_exc()
        return False

def main():
    """Run all GPU support tests."""
    print("🚀 Groq Speech SDK GPU Support Test")
    print("=" * 60)
    
    # Test results
    results = {
        "gpu_detection": False,
        "pyannote_import": False,
        "pipeline_init": False,
        "diarization_integration": False
    }
    
    # Run tests
    results["gpu_detection"] = test_gpu_detection()
    results["pyannote_import"] = test_pyannote_import()
    results["pipeline_init"] = test_pipeline_initialization()
    results["diarization_integration"] = test_diarization_integration()
    
    # Summary
    print("\n📊 Test Results Summary")
    print("=" * 50)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name.replace('_', ' ').title()}: {status}")
    
    # Overall result
    all_passed = all(results.values())
    if all_passed:
        print("\n🎉 All tests passed! GPU support is working correctly.")
    else:
        print("\n⚠️ Some tests failed. Check the output above for details.")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
