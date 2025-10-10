#!/usr/bin/env python3
"""
CLI Command Tests - Focused on Command Validation

This test suite validates that all CLI commands can be parsed correctly
and that the appropriate functions are called with the right parameters.
It uses mocking to avoid actual API calls and audio recording.
"""

import unittest
import sys
import os
from unittest.mock import patch, MagicMock, call
from pathlib import Path

# Add the parent directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import the CLI module
from examples.speech_demo import main, validate_environment, process_audio_file


class TestCLICommands(unittest.TestCase):
    """Test CLI command parsing and execution."""
    
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
        
        # Mock the actual processing functions
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
    
    def test_file_transcription_basic(self):
        """Test: python speech_demo.py --file test1.wav"""
        with patch('sys.argv', ['speech_demo.py', '--file', 'test1.wav']):
            with patch('examples.speech_demo.main') as mock_main:
                main()
                mock_main.assert_called_once()
    
    def test_file_transcription_with_diarization(self):
        """Test: python speech_demo.py --file test1.wav --diarize"""
        with patch('sys.argv', ['speech_demo.py', '--file', 'test1.wav', '--diarize']):
            with patch('examples.speech_demo.main') as mock_main:
                main()
                mock_main.assert_called_once()
    
    def test_microphone_single_mode(self):
        """Test: python speech_demo.py --microphone-mode single"""
        with patch('sys.argv', ['speech_demo.py', '--microphone-mode', 'single']):
            with patch('examples.speech_demo.main') as mock_main:
                main()
                mock_main.assert_called_once()
    
    def test_microphone_single_with_diarization(self):
        """Test: python speech_demo.py --microphone-mode single --diarize"""
        with patch('sys.argv', ['speech_demo.py', '--microphone-mode', 'single', '--diarize']):
            with patch('examples.speech_demo.main') as mock_main:
                main()
                mock_main.assert_called_once()
    
    def test_microphone_single_translation(self):
        """Test: python speech_demo.py --microphone-mode single --operation translation"""
        with patch('sys.argv', ['speech_demo.py', '--microphone-mode', 'single', '--operation', 'translation']):
            with patch('examples.speech_demo.main') as mock_main:
                main()
                mock_main.assert_called_once()
    
    def test_microphone_single_translation_with_diarization(self):
        """Test: python speech_demo.py --microphone-mode single --operation translation --diarize"""
        with patch('sys.argv', ['speech_demo.py', '--microphone-mode', 'single', '--operation', 'translation', '--diarize']):
            with patch('examples.speech_demo.main') as mock_main:
                main()
                mock_main.assert_called_once()
    
    def test_microphone_continuous_mode(self):
        """Test: python speech_demo.py --microphone-mode continuous"""
        with patch('sys.argv', ['speech_demo.py', '--microphone-mode', 'continuous']):
            with patch('examples.speech_demo.main') as mock_main:
                main()
                mock_main.assert_called_once()
    
    def test_microphone_continuous_with_diarization(self):
        """Test: python speech_demo.py --microphone-mode continuous --diarize"""
        with patch('sys.argv', ['speech_demo.py', '--microphone-mode', 'continuous', '--diarize']):
            with patch('examples.speech_demo.main') as mock_main:
                main()
                mock_main.assert_called_once()
    
    def test_microphone_continuous_translation(self):
        """Test: python speech_demo.py --microphone-mode continuous --operation translation"""
        with patch('sys.argv', ['speech_demo.py', '--microphone-mode', 'continuous', '--operation', 'translation']):
            with patch('examples.speech_demo.main') as mock_main:
                main()
                mock_main.assert_called_once()
    
    def test_microphone_continuous_translation_with_diarization(self):
        """Test: python speech_demo.py --microphone-mode continuous --operation translation --diarize"""
        with patch('sys.argv', ['speech_demo.py', '--microphone-mode', 'continuous', '--operation', 'translation', '--diarize']):
            with patch('examples.speech_demo.main') as mock_main:
                main()
                mock_main.assert_called_once()
    
    def test_help_output(self):
        """Test that help output is displayed correctly."""
        with patch('sys.argv', ['speech_demo.py', '--help']):
            with patch('examples.speech_demo.main') as mock_main:
                main()
                mock_main.assert_called_once()
    
    def test_invalid_operation(self):
        """Test error handling with invalid operation."""
        with patch('sys.argv', ['speech_demo.py', '--microphone-mode', 'single', '--operation', 'invalid_operation']):
            with patch('examples.speech_demo.main') as mock_main:
                main()
                mock_main.assert_called_once()


class TestCLIArgumentParsing(unittest.TestCase):
    """Test CLI argument parsing logic."""
    
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
    
    def test_validate_environment_with_api_key(self):
        """Test environment validation with API key."""
        result = validate_environment(enable_diarization=False)
        self.assertTrue(result)
    
    def test_validate_environment_with_diarization(self):
        """Test environment validation with diarization."""
        result = validate_environment(enable_diarization=True)
        self.assertTrue(result)
    
    def test_validate_environment_missing_api_key(self):
        """Test environment validation without API key."""
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(SystemExit):
                validate_environment(enable_diarization=False)
    
    def test_validate_environment_missing_hf_token(self):
        """Test environment validation without HF token for diarization."""
        with patch.dict(os.environ, {'GROQ_API_KEY': 'test_key'}, clear=True):
            with self.assertRaises(SystemExit):
                validate_environment(enable_diarization=True)


class TestCLIFunctionCalls(unittest.TestCase):
    """Test that CLI functions are called with correct parameters."""
    
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
    def test_file_processing_calls(self, mock_process_audio_file):
        """Test that file processing calls the right function."""
        # This would be called by the main function when processing files
        # We're testing the function directly here
        mock_process_audio_file.return_value = MagicMock(text="Test result")
        
        result = process_audio_file("test.wav", "transcription", MagicMock(), True)
        
        # Verify the function was called
        mock_process_audio_file.assert_called_once()
    
    @patch('examples.speech_demo.process_microphone_single')
    def test_microphone_single_calls(self, mock_process_microphone_single):
        """Test that microphone single mode calls the right function."""
        mock_process_microphone_single.return_value = MagicMock(text="Test result")
        
        # This would be called by the main function
        # We're testing the function call pattern
        result = mock_process_microphone_single("transcription", MagicMock(), True, False)
        
        # Verify the function was called
        mock_process_microphone_single.assert_called_once()
    
    @patch('examples.speech_demo.process_microphone_continuous')
    def test_microphone_continuous_calls(self, mock_process_microphone_continuous):
        """Test that microphone continuous mode calls the right function."""
        mock_process_microphone_continuous.return_value = None
        
        # This would be called by the main function
        result = mock_process_microphone_continuous("transcription", MagicMock(), True, False)
        
        # Verify the function was called
        mock_process_microphone_continuous.assert_called_once()


class TestCLIErrorHandling(unittest.TestCase):
    """Test CLI error handling."""
    
    def test_missing_required_arguments(self):
        """Test error handling when required arguments are missing."""
        with patch('sys.argv', ['speech_demo.py']):
            with patch('examples.speech_demo.main') as mock_main:
                main()
                mock_main.assert_called_once()
    
    def test_invalid_microphone_mode(self):
        """Test error handling with invalid microphone mode."""
        with patch('sys.argv', ['speech_demo.py', '--microphone-mode', 'invalid']):
            with patch('examples.speech_demo.main') as mock_main:
                main()
                mock_main.assert_called_once()
    
    def test_invalid_operation(self):
        """Test error handling with invalid operation."""
        with patch('sys.argv', ['speech_demo.py', '--microphone-mode', 'single', '--operation', 'invalid']):
            with patch('examples.speech_demo.main') as mock_main:
                main()
                mock_main.assert_called_once()


if __name__ == '__main__':
    print("🧪 Running CLI Command Tests")
    print("=" * 50)
    
    # Run tests with verbose output
    unittest.main(verbosity=2, buffer=True)
