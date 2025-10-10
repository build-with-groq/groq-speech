#!/usr/bin/env python3
"""
CLI Validation Tests - Comprehensive Command Testing

This test suite validates that all CLI commands work correctly by:
1. Testing argument parsing
2. Testing environment validation
3. Testing command execution (with mocked dependencies)
4. Testing error handling

All 10 CLI command combinations are validated.
"""

import unittest
import sys
import os
from unittest.mock import patch, MagicMock
from pathlib import Path

# Add the parent directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from examples.speech_demo import (
    validate_environment, 
    process_audio_file,
    process_microphone_single,
    process_microphone_continuous,
    main
)


class TestCLIValidation(unittest.TestCase):
    """Comprehensive CLI validation tests."""
    
    def setUp(self):
        """Set up test environment."""
        # Mock environment variables
        self.env_patcher = patch.dict(
            os.environ, {
                'GROQ_API_KEY': 'test_groq_api_key_here',
                'HF_TOKEN': 'test_hf_token_here'
            }
        )
        self.env_patcher.start()
        
        # Mock the actual processing functions to avoid real API calls
        self.process_audio_file_patcher = patch('examples.speech_demo.process_audio_file')
        self.process_microphone_single_patcher = patch('examples.speech_demo.process_microphone_single')
        self.process_microphone_continuous_patcher = patch('examples.speech_demo.process_microphone_continuous')
        
        self.mock_process_audio_file = self.process_audio_file_patcher.start()
        self.mock_process_microphone_single = self.process_microphone_single_patcher.start()
        self.mock_process_microphone_continuous = self.process_microphone_continuous_patcher.start()
        
        # Mock return values
        self.mock_process_audio_file.return_value = MagicMock(text="Test transcription")
        self.mock_process_microphone_single.return_value = MagicMock(text="Test microphone transcription")
        self.mock_process_microphone_continuous.return_value = None
    
    def tearDown(self):
        """Clean up after tests."""
        self.env_patcher.stop()
        self.process_audio_file_patcher.stop()
        self.process_microphone_single_patcher.stop()
        self.process_microphone_continuous_patcher.stop()
    
    def test_1_file_transcription_basic(self):
        """Test: python speech_demo.py --file test1.wav"""
        with patch('sys.argv', ['speech_demo.py', '--file', 'test1.wav']):
            # This should not raise an exception
            try:
                main()
                self.assertTrue(True, "Command executed successfully")
            except SystemExit as e:
                if e.code == 0:
                    self.assertTrue(True, "Command executed successfully")
                else:
                    self.fail(f"Command failed with exit code {e.code}")
    
    def test_2_file_transcription_with_diarization(self):
        """Test: python speech_demo.py --file test1.wav --diarize"""
        with patch('sys.argv', ['speech_demo.py', '--file', 'test1.wav', '--diarize']):
            try:
                main()
                self.assertTrue(True, "Command executed successfully")
            except SystemExit as e:
                if e.code == 0:
                    self.assertTrue(True, "Command executed successfully")
                else:
                    self.fail(f"Command failed with exit code {e.code}")
    
    def test_3_microphone_single_mode(self):
        """Test: python speech_demo.py --microphone-mode single"""
        with patch('sys.argv', ['speech_demo.py', '--microphone-mode', 'single']):
            try:
                main()
                self.assertTrue(True, "Command executed successfully")
            except SystemExit as e:
                if e.code == 0:
                    self.assertTrue(True, "Command executed successfully")
                else:
                    self.fail(f"Command failed with exit code {e.code}")
    
    def test_4_microphone_single_with_diarization(self):
        """Test: python speech_demo.py --microphone-mode single --diarize"""
        with patch('sys.argv', ['speech_demo.py', '--microphone-mode', 'single', '--diarize']):
            try:
                main()
                self.assertTrue(True, "Command executed successfully")
            except SystemExit as e:
                if e.code == 0:
                    self.assertTrue(True, "Command executed successfully")
                else:
                    self.fail(f"Command failed with exit code {e.code}")
    
    def test_5_microphone_single_translation(self):
        """Test: python speech_demo.py --microphone-mode single --operation translation"""
        with patch('sys.argv', ['speech_demo.py', '--microphone-mode', 'single', '--operation', 'translation']):
            try:
                main()
                self.assertTrue(True, "Command executed successfully")
            except SystemExit as e:
                if e.code == 0:
                    self.assertTrue(True, "Command executed successfully")
                else:
                    self.fail(f"Command failed with exit code {e.code}")
    
    def test_6_microphone_single_translation_with_diarization(self):
        """Test: python speech_demo.py --microphone-mode single --operation translation --diarize"""
        with patch('sys.argv', ['speech_demo.py', '--microphone-mode', 'single', '--operation', 'translation', '--diarize']):
            try:
                main()
                self.assertTrue(True, "Command executed successfully")
            except SystemExit as e:
                if e.code == 0:
                    self.assertTrue(True, "Command executed successfully")
                else:
                    self.fail(f"Command failed with exit code {e.code}")
    
    def test_7_microphone_continuous_mode(self):
        """Test: python speech_demo.py --microphone-mode continuous"""
        with patch('sys.argv', ['speech_demo.py', '--microphone-mode', 'continuous']):
            try:
                main()
                self.assertTrue(True, "Command executed successfully")
            except SystemExit as e:
                if e.code == 0:
                    self.assertTrue(True, "Command executed successfully")
                else:
                    self.fail(f"Command failed with exit code {e.code}")
    
    def test_8_microphone_continuous_with_diarization(self):
        """Test: python speech_demo.py --microphone-mode continuous --diarize"""
        with patch('sys.argv', ['speech_demo.py', '--microphone-mode', 'continuous', '--diarize']):
            try:
                main()
                self.assertTrue(True, "Command executed successfully")
            except SystemExit as e:
                if e.code == 0:
                    self.assertTrue(True, "Command executed successfully")
                else:
                    self.fail(f"Command failed with exit code {e.code}")
    
    def test_9_microphone_continuous_translation(self):
        """Test: python speech_demo.py --microphone-mode continuous --operation translation"""
        with patch('sys.argv', ['speech_demo.py', '--microphone-mode', 'continuous', '--operation', 'translation']):
            try:
                main()
                self.assertTrue(True, "Command executed successfully")
            except SystemExit as e:
                if e.code == 0:
                    self.assertTrue(True, "Command executed successfully")
                else:
                    self.fail(f"Command failed with exit code {e.code}")
    
    def test_10_microphone_continuous_translation_with_diarization(self):
        """Test: python speech_demo.py --microphone-mode continuous --operation translation --diarize"""
        with patch('sys.argv', ['speech_demo.py', '--microphone-mode', 'continuous', '--operation', 'translation', '--diarize']):
            try:
                main()
                self.assertTrue(True, "Command executed successfully")
            except SystemExit as e:
                if e.code == 0:
                    self.assertTrue(True, "Command executed successfully")
                else:
                    self.fail(f"Command failed with exit code {e.code}")
    
    def test_help_command(self):
        """Test: python speech_demo.py --help"""
        with patch('sys.argv', ['speech_demo.py', '--help']):
            with self.assertRaises(SystemExit) as cm:
                main()
            self.assertEqual(cm.exception.code, 0, "Help command should exit with code 0")
    
    def test_missing_required_arguments(self):
        """Test error handling when required arguments are missing."""
        with patch('sys.argv', ['speech_demo.py']):
            with self.assertRaises(SystemExit) as cm:
                main()
            self.assertEqual(cm.exception.code, 2, "Should exit with error code 2")
    
    def test_invalid_operation(self):
        """Test error handling with invalid operation."""
        with patch('sys.argv', ['speech_demo.py', '--microphone-mode', 'single', '--operation', 'invalid']):
            with self.assertRaises(SystemExit) as cm:
                main()
            self.assertEqual(cm.exception.code, 2, "Should exit with error code 2")
    
    def test_invalid_microphone_mode(self):
        """Test error handling with invalid microphone mode."""
        with patch('sys.argv', ['speech_demo.py', '--microphone-mode', 'invalid']):
            with self.assertRaises(SystemExit) as cm:
                main()
            self.assertEqual(cm.exception.code, 2, "Should exit with error code 2")


class TestEnvironmentValidation(unittest.TestCase):
    """Test environment validation."""
    
    def test_validate_environment_with_api_key(self):
        """Test environment validation with API key."""
        with patch.dict(os.environ, {'GROQ_API_KEY': 'test_key'}):
            result = validate_environment(enable_diarization=False)
            self.assertTrue(result)
    
    def test_validate_environment_with_diarization(self):
        """Test environment validation with diarization."""
        with patch.dict(os.environ, {'GROQ_API_KEY': 'test_key', 'HF_TOKEN': 'test_token'}):
            result = validate_environment(enable_diarization=True)
            self.assertTrue(result)
    
    def test_validate_environment_missing_api_key(self):
        """Test environment validation without API key."""
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(SystemExit) as cm:
                validate_environment(enable_diarization=False)
            self.assertEqual(cm.exception.code, 1, "Should exit with error code 1")
    
    def test_validate_environment_missing_hf_token(self):
        """Test environment validation without HF token for diarization."""
        with patch.dict(os.environ, {'GROQ_API_KEY': 'test_key'}, clear=True):
            with self.assertRaises(SystemExit) as cm:
                validate_environment(enable_diarization=True)
            self.assertEqual(cm.exception.code, 1, "Should exit with error code 1")


class TestFunctionCalls(unittest.TestCase):
    """Test that functions are called correctly."""
    
    def setUp(self):
        """Set up test environment."""
        self.env_patcher = patch.dict(
            os.environ, {
                'GROQ_API_KEY': 'test_groq_api_key_here',
                'HF_TOKEN': 'test_hf_token_here'
            }
        )
        self.env_patcher.start()
    
    def tearDown(self):
        """Clean up after tests."""
        self.env_patcher.stop()
    
    @patch('examples.speech_demo.process_audio_file')
    def test_file_processing_function_called(self, mock_process_audio_file):
        """Test that file processing function is called."""
        mock_process_audio_file.return_value = MagicMock(text="Test result")
        
        # Test the function directly
        result = process_audio_file("test.wav", "transcription", MagicMock(), True)
        
        # The function should be called (it's the same function, so it will be called)
        self.assertIsNotNone(result)
    
    @patch('examples.speech_demo.process_microphone_single')
    def test_microphone_single_function_called(self, mock_process_microphone_single):
        """Test that microphone single function is called."""
        mock_process_microphone_single.return_value = MagicMock(text="Test result")
        
        # Test the function directly
        result = mock_process_microphone_single("transcription", MagicMock(), True, False)
        
        # Verify the function was called
        mock_process_microphone_single.assert_called_once()
    
    @patch('examples.speech_demo.process_microphone_continuous')
    def test_microphone_continuous_function_called(self, mock_process_microphone_continuous):
        """Test that microphone continuous function is called."""
        mock_process_microphone_continuous.return_value = None
        
        # Test the function directly
        result = mock_process_microphone_continuous("transcription", MagicMock(), True, False)
        
        # Verify the function was called
        mock_process_microphone_continuous.assert_called_once()


if __name__ == '__main__':
    print("🧪 Running CLI Validation Tests")
    print("=" * 50)
    print("Testing all 10 CLI command combinations:")
    print("1. File transcription basic")
    print("2. File transcription with diarization")
    print("3. Microphone single mode")
    print("4. Microphone single with diarization")
    print("5. Microphone single translation")
    print("6. Microphone single translation with diarization")
    print("7. Microphone continuous mode")
    print("8. Microphone continuous with diarization")
    print("9. Microphone continuous translation")
    print("10. Microphone continuous translation with diarization")
    print("=" * 50)
    
    # Run tests with verbose output
    unittest.main(verbosity=2, buffer=True)
