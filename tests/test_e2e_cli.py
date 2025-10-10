#!/usr/bin/env python3
"""
End-to-End Test Suite for CLI Commands

This test suite validates all CLI command combinations by running them
as subprocess calls and verifying the expected outputs and behaviors.

Test Coverage:
1. File processing (with/without diarization)
2. Microphone single mode (with/without diarization, with/without translation)
3. Microphone continuous mode (with/without diarization, with/without translation)
4. Error handling and validation
5. Environment variable requirements
"""

import unittest
import subprocess
import sys
import os
import tempfile
import time
import signal
import threading
from pathlib import Path
from unittest.mock import patch, MagicMock
import numpy as np
import soundfile as sf

# Add the parent directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Test configuration
TEST_AUDIO_FILE = "examples/test1.wav"
CLI_SCRIPT = "examples/speech_demo.py"
TIMEOUT_SECONDS = 30  # Timeout for CLI commands


class TestE2ECLI(unittest.TestCase):
    """End-to-end tests for CLI commands."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment once for all tests."""
        # Ensure we have test audio files
        cls.test_audio_path = Path(TEST_AUDIO_FILE)
        if not cls.test_audio_path.exists():
            # Create a test audio file if it doesn't exist
            cls._create_test_audio_file()
        
        # Set up environment variables for testing
        cls.original_env = os.environ.copy()
        os.environ.update({
            'GROQ_API_KEY': 'test_api_key_here',
            'HF_TOKEN': 'test_hf_token_here'
        })
    
    @classmethod
    def tearDownClass(cls):
        """Clean up after all tests."""
        # Restore original environment
        os.environ.clear()
        os.environ.update(cls.original_env)
    
    @classmethod
    def _create_test_audio_file(cls):
        """Create a test audio file for testing."""
        # Generate 3 seconds of test audio (16kHz, mono)
        sample_rate = 16000
        duration = 3.0
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        # Create a simple sine wave
        frequency = 440  # A4 note
        audio_data = 0.3 * np.sin(2 * np.pi * frequency * t)
        
        # Save as WAV file
        sf.write(cls.test_audio_path, audio_data, sample_rate)
        print(f"Created test audio file: {cls.test_audio_path}")
    
    def _run_cli_command(self, args, timeout=TIMEOUT_SECONDS):
        """Run a CLI command and return the result."""
        cmd = [sys.executable, CLI_SCRIPT] + args
        print(f"Running command: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=Path(__file__).parent.parent
            )
            return result
        except subprocess.TimeoutExpired:
            self.fail(f"Command timed out after {timeout} seconds: {' '.join(cmd)}")
        except Exception as e:
            self.fail(f"Command failed with exception: {e}")
    
    def _assert_successful_execution(self, result, expected_keywords=None):
        """Assert that the command executed successfully."""
        self.assertEqual(result.returncode, 0, 
                        f"Command failed with return code {result.returncode}\n"
                        f"STDOUT: {result.stdout}\nSTDERR: {result.stderr}")
        
        if expected_keywords:
            for keyword in expected_keywords:
                self.assertIn(keyword, result.stdout, 
                            f"Expected keyword '{keyword}' not found in output:\n{result.stdout}")
    
    def test_file_transcription_basic(self):
        """Test: python speech_demo.py --file test1.wav"""
        result = self._run_cli_command(["--file", TEST_AUDIO_FILE])
        
        self._assert_successful_execution(result, [
            "Processing Audio File",
            "Direct Pipeline",
            "Processing completed successfully",
            "Text:"
        ])
        
        # Should not contain diarization output
        self.assertNotIn("Diarization Pipeline", result.stdout)
        self.assertNotIn("Speakers:", result.stdout)
    
    def test_file_transcription_with_diarization(self):
        """Test: python speech_demo.py --file test1.wav --diarize"""
        result = self._run_cli_command(["--file", TEST_AUDIO_FILE, "--diarize"])
        
        self._assert_successful_execution(result, [
            "Processing Audio File",
            "Diarization Pipeline",
            "Pyannote.audio",
            "Processing completed successfully",
            "Speakers:",
            "SPEAKER_"
        ])
    
    def test_microphone_single_mode(self):
        """Test: python speech_demo.py --microphone-mode single"""
        # Mock microphone input to avoid actual recording
        with patch('examples.speech_demo.process_microphone_single') as mock_process:
            mock_process.return_value = MagicMock(
                text="Test transcription",
                reason=MagicMock(),
                confidence=0.95
            )
            
            result = self._run_cli_command(["--microphone-mode", "single"])
            
            self._assert_successful_execution(result, [
                "Microphone Single Mode",
                "Processing completed successfully"
            ])
    
    def test_microphone_single_with_diarization(self):
        """Test: python speech_demo.py --microphone-mode single --diarize"""
        with patch('examples.speech_demo.process_microphone_single') as mock_process:
            # Mock diarization result
            mock_result = MagicMock()
            mock_result.text = "Test transcription"
            mock_result.num_speakers = 2
            mock_result.segments = [
                MagicMock(speaker_id="SPEAKER_00", text="Speaker 0 text"),
                MagicMock(speaker_id="SPEAKER_01", text="Speaker 1 text")
            ]
            mock_process.return_value = mock_result
            
            result = self._run_cli_command(["--microphone-mode", "single", "--diarize"])
            
            self._assert_successful_execution(result, [
                "Microphone Single Mode",
                "Processing completed successfully",
                "Speakers:",
                "SPEAKER_"
            ])
    
    def test_microphone_single_translation(self):
        """Test: python speech_demo.py --microphone-mode single --operation translation"""
        with patch('examples.speech_demo.process_microphone_single') as mock_process:
            mock_process.return_value = MagicMock(
                text="Test translation",
                reason=MagicMock(),
                confidence=0.95
            )
            
            result = self._run_cli_command([
                "--microphone-mode", "single", 
                "--operation", "translation"
            ])
            
            self._assert_successful_execution(result, [
                "Microphone Single Mode",
                "Translation Mode",
                "Processing completed successfully"
            ])
    
    def test_microphone_single_translation_with_diarization(self):
        """Test: python speech_demo.py --microphone-mode single --operation translation --diarize"""
        with patch('examples.speech_demo.process_microphone_single') as mock_process:
            # Mock diarization result for translation
            mock_result = MagicMock()
            mock_result.text = "Test translation"
            mock_result.num_speakers = 2
            mock_result.segments = [
                MagicMock(speaker_id="SPEAKER_00", text="Speaker 0 translation"),
                MagicMock(speaker_id="SPEAKER_01", text="Speaker 1 translation")
            ]
            mock_process.return_value = mock_result
            
            result = self._run_cli_command([
                "--microphone-mode", "single", 
                "--operation", "translation",
                "--diarize"
            ])
            
            self._assert_successful_execution(result, [
                "Microphone Single Mode",
                "Translation Mode",
                "Processing completed successfully",
                "Speakers:",
                "SPEAKER_"
            ])
    
    def test_microphone_continuous_mode(self):
        """Test: python speech_demo.py --microphone-mode continuous"""
        with patch('examples.speech_demo.process_microphone_continuous') as mock_process:
            mock_process.return_value = None  # Continuous mode doesn't return a result
            
            result = self._run_cli_command(["--microphone-mode", "continuous"])
            
            self._assert_successful_execution(result, [
                "Microphone Continuous Mode",
                "Processing completed successfully"
            ])
    
    def test_microphone_continuous_with_diarization(self):
        """Test: python speech_demo.py --microphone-mode continuous --diarize"""
        with patch('examples.speech_demo.process_microphone_continuous') as mock_process:
            mock_process.return_value = None
            
            result = self._run_cli_command([
                "--microphone-mode", "continuous", 
                "--diarize"
            ])
            
            self._assert_successful_execution(result, [
                "Microphone Continuous Mode",
                "Processing completed successfully"
            ])
    
    def test_microphone_continuous_translation(self):
        """Test: python speech_demo.py --microphone-mode continuous --operation translation"""
        with patch('examples.speech_demo.process_microphone_continuous') as mock_process:
            mock_process.return_value = None
            
            result = self._run_cli_command([
                "--microphone-mode", "continuous", 
                "--operation", "translation"
            ])
            
            self._assert_successful_execution(result, [
                "Microphone Continuous Mode",
                "Translation Mode",
                "Processing completed successfully"
            ])
    
    def test_microphone_continuous_translation_with_diarization(self):
        """Test: python speech_demo.py --microphone-mode continuous --operation translation --diarize"""
        with patch('examples.speech_demo.process_microphone_continuous') as mock_process:
            mock_process.return_value = None
            
            result = self._run_cli_command([
                "--microphone-mode", "continuous", 
                "--operation", "translation",
                "--diarize"
            ])
            
            self._assert_successful_execution(result, [
                "Microphone Continuous Mode",
                "Translation Mode",
                "Processing completed successfully"
            ])
    
    def test_missing_api_key(self):
        """Test error handling when API key is missing."""
        with patch.dict(os.environ, {}, clear=True):
            result = self._run_cli_command(["--file", TEST_AUDIO_FILE])
            
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("API key", result.stderr.lower())
    
    def test_missing_hf_token_for_diarization(self):
        """Test error handling when HF token is missing for diarization."""
        with patch.dict(os.environ, {"GROQ_API_KEY": "test_key"}, clear=True):
            result = self._run_cli_command(["--file", TEST_AUDIO_FILE, "--diarize"])
            
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("HF_TOKEN", result.stderr)
    
    def test_invalid_audio_file(self):
        """Test error handling with invalid audio file."""
        result = self._run_cli_command(["--file", "nonexistent.wav"])
        
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("not found", result.stderr.lower())
    
    def test_invalid_operation(self):
        """Test error handling with invalid operation."""
        result = self._run_cli_command([
            "--microphone-mode", "single", 
            "--operation", "invalid_operation"
        ])
        
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("invalid choice", result.stderr.lower())
    
    def test_help_output(self):
        """Test that help output is displayed correctly."""
        result = self._run_cli_command(["--help"])
        
        self.assertEqual(result.returncode, 0)
        self.assertIn("usage:", result.stdout.lower())
        self.assertIn("--file", result.stdout)
        self.assertIn("--microphone-mode", result.stdout)
        self.assertIn("--operation", result.stdout)
        self.assertIn("--diarize", result.stdout)


class TestE2EIntegration(unittest.TestCase):
    """Integration tests that verify the complete workflow."""
    
    def setUp(self):
        """Set up test environment."""
        self.original_env = os.environ.copy()
        os.environ.update({
            'GROQ_API_KEY': 'test_api_key_here',
            'HF_TOKEN': 'test_hf_token_here'
        })
    
    def tearDown(self):
        """Clean up after tests."""
        os.environ.clear()
        os.environ.update(self.original_env)
    
    def test_all_file_modes(self):
        """Test all file processing modes in sequence."""
        test_file = "examples/test1.wav"
        
        # Test basic transcription
        result = subprocess.run([
            sys.executable, CLI_SCRIPT, "--file", test_file
        ], capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 0)
        
        # Test transcription with diarization
        result = subprocess.run([
            sys.executable, CLI_SCRIPT, "--file", test_file, "--diarize"
        ], capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 0)
        
        # Test translation
        result = subprocess.run([
            sys.executable, CLI_SCRIPT, "--file", test_file, "--operation", "translation"
        ], capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 0)
        
        # Test translation with diarization
        result = subprocess.run([
            sys.executable, CLI_SCRIPT, "--file", test_file, 
            "--operation", "translation", "--diarize"
        ], capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 0)
    
    def test_environment_validation(self):
        """Test that environment validation works correctly."""
        # Test with valid environment
        result = subprocess.run([
            sys.executable, CLI_SCRIPT, "--file", "examples/test1.wav"
        ], capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 0)
        self.assertIn("Environment validation passed", result.stdout)
        
        # Test with missing API key
        with patch.dict(os.environ, {}, clear=True):
            result = subprocess.run([
                sys.executable, CLI_SCRIPT, "--file", "examples/test1.wav"
            ], capture_output=True, text=True, timeout=30)
            self.assertNotEqual(result.returncode, 0)


if __name__ == '__main__':
    # Set up test environment
    print("🧪 Running End-to-End CLI Tests")
    print("=" * 50)
    
    # Run tests with verbose output
    unittest.main(verbosity=2, buffer=True)
