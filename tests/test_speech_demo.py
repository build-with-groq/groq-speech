#!/usr/bin/env python3
"""
Test suite for speech_demo.py functionality.

This test suite ensures that:
1. All argument combinations work correctly
2. Argument validation works as expected
3. The correct processing functions are called
4. Enhanced diarization is used appropriately
"""

import unittest
import sys
import os
from unittest.mock import patch, MagicMock
from pathlib import Path

# Add the parent directory to the path to import groq_speech
sys.path.insert(0, str(Path(__file__).parent.parent))

from examples.speech_demo import (
    validate_environment,
    process_audio_file,
    process_audio_file_enhanced,
    process_microphone_basic,
    process_microphone_enhanced,
    process_microphone_single,
    main,
)


class TestSpeechDemoArguments(unittest.TestCase):
    """Test argument parsing and validation in speech_demo.py."""

    def setUp(self):
        """Set up test environment."""
        # Mock environment variables
        self.env_patcher = patch.dict(
            os.environ, {"GROQ_API_KEY": "test_key", "HF_TOKEN": "test_hf_token"}
        )
        self.env_patcher.start()

    def tearDown(self):
        """Clean up after tests."""
        self.env_patcher.stop()

    @patch("examples.speech_demo.validate_environment")
    @patch("examples.speech_demo.SpeechConfig")
    @patch("examples.speech_demo.SpeechRecognizer")
    @patch("examples.speech_demo.process_audio_file_enhanced")
    def test_file_processing_defaults_to_enhanced(
        self, mock_process, mock_recognizer, mock_config, mock_validate
    ):
        """Test that file processing defaults to enhanced diarization."""
        # Mock successful initialization
        mock_validate.return_value = True
        mock_config_instance = MagicMock()
        mock_config.return_value = mock_config_instance
        mock_recognizer_instance = MagicMock()
        mock_recognizer.return_value = mock_recognizer_instance
        mock_process.return_value = MagicMock()

        # Test with just --file (should use enhanced diarization)
        with patch("sys.argv", ["speech_demo.py", "--file", "test.wav"]):
            with patch("sys.exit") as mock_exit:
                main()
                mock_exit.assert_not_called()

        # Should call enhanced processing
        mock_process.assert_called_once_with(
            "test.wav", "transcription", mock_recognizer_instance
        )

    @patch("examples.speech_demo.validate_environment")
    @patch("examples.speech_demo.SpeechConfig")
    @patch("examples.speech_demo.SpeechRecognizer")
    @patch("examples.speech_demo.process_audio_file_enhanced")
    def test_file_processing_with_translation(
        self, mock_process, mock_recognizer, mock_config, mock_validate
    ):
        """Test that file processing with translation works."""
        # Mock successful initialization
        mock_validate.return_value = True
        mock_config_instance = MagicMock()
        mock_config.return_value = mock_config_instance
        mock_recognizer_instance = MagicMock()
        mock_recognizer.return_value = mock_recognizer_instance
        mock_process.return_value = MagicMock()

        # Test with --file and --operation translation
        with patch(
            "sys.argv",
            ["speech_demo.py", "--file", "test.wav", "--operation", "translation"],
        ):
            with patch("sys.exit") as mock_exit:
                main()
                mock_exit.assert_not_called()

        # Should call enhanced processing with translation
        mock_process.assert_called_once_with(
            "test.wav", "translation", mock_recognizer_instance
        )

    @patch("examples.speech_demo.validate_environment")
    @patch("examples.speech_demo.SpeechConfig")
    @patch("examples.speech_demo.SpeechRecognizer")
    @patch("examples.speech_demo.process_microphone_single")
    def test_microphone_single_mode(
        self, mock_process, mock_recognizer, mock_config, mock_validate
    ):
        """Test that single microphone mode uses single processing."""
        # Mock successful initialization
        mock_validate.return_value = True
        mock_config_instance = MagicMock()
        mock_config.return_value = mock_config_instance
        mock_recognizer_instance = MagicMock()
        mock_recognizer.return_value = mock_recognizer_instance
        mock_process.return_value = MagicMock()

        # Test with --microphone-mode single (should use single processing)
        with patch("sys.argv", ["speech_demo.py", "--microphone-mode", "single"]):
            with patch("sys.exit") as mock_exit:
                main()
                mock_exit.assert_not_called()

        # Should call single microphone processing
        mock_process.assert_called_once_with("transcription", mock_recognizer_instance)

    @patch("examples.speech_demo.validate_environment")
    @patch("examples.speech_demo.SpeechConfig")
    @patch("examples.speech_demo.SpeechRecognizer")
    @patch("examples.speech_demo.process_microphone_basic")
    def test_microphone_continuous_mode(
        self, mock_process, mock_recognizer, mock_config, mock_validate
    ):
        """Test that continuous microphone mode uses continuous processing."""
        # Mock successful initialization
        mock_validate.return_value = True
        mock_config_instance = MagicMock()
        mock_config.return_value = mock_config_instance
        mock_recognizer_instance = MagicMock()
        mock_recognizer.return_value = mock_recognizer_instance
        mock_process.return_value = MagicMock()

        # Test with --microphone-mode continuous (should use continuous processing)
        with patch("sys.argv", ["speech_demo.py", "--microphone-mode", "continuous"]):
            with patch("sys.exit") as mock_exit:
                main()
                mock_exit.assert_not_called()

        # Should call continuous microphone processing
        mock_process.assert_called_once_with("transcription", mock_recognizer_instance)

    @patch("examples.speech_demo.validate_environment")
    @patch("examples.speech_demo.SpeechConfig")
    @patch("examples.speech_demo.SpeechRecognizer")
    @patch("examples.speech_demo.process_microphone_enhanced")
    def test_microphone_processing_with_diarization(
        self, mock_process, mock_recognizer, mock_config, mock_validate
    ):
        """Test that microphone processing with diarization uses enhanced processing."""
        # Mock successful initialization
        mock_validate.return_value = True
        mock_config_instance = MagicMock()
        mock_config.return_value = mock_config_instance
        mock_recognizer_instance = MagicMock()
        mock_recognizer.return_value = mock_recognizer_instance
        mock_process.return_value = MagicMock()

        # Test with --microphone-mode single and --diarize true
        with patch(
            "sys.argv",
            ["speech_demo.py", "--microphone-mode", "single", "--diarize", "true"],
        ):
            with patch("sys.exit") as mock_exit:
                main()
                mock_exit.assert_not_called()

        # Should call enhanced microphone processing
        mock_process.assert_called_once_with("transcription", mock_recognizer_instance)

    @patch("examples.speech_demo.validate_environment")
    @patch("examples.speech_demo.SpeechConfig")
    @patch("examples.speech_demo.SpeechRecognizer")
    @patch("examples.speech_demo.process_microphone_enhanced")
    def test_microphone_continuous_with_translation_and_diarization(
        self, mock_process, mock_recognizer, mock_config, mock_validate
    ):
        """Test the specific combination: continuous microphone + translation + diarization."""
        # Mock successful initialization
        mock_validate.return_value = True
        mock_config_instance = MagicMock()
        mock_config.return_value = mock_config_instance
        mock_recognizer_instance = MagicMock()
        mock_recognizer.return_value = mock_recognizer_instance
        mock_process.return_value = MagicMock()

        # Test the specific combination mentioned by user
        with patch(
            "sys.argv",
            [
                "speech_demo.py",
                "--microphone-mode",
                "continuous",
                "--operation",
                "translation",
                "--diarize",
                "true",
            ],
        ):
            with patch("sys.exit") as mock_exit:
                main()
                mock_exit.assert_not_called()

        # Should call enhanced microphone processing with translation
        mock_process.assert_called_once_with("translation", mock_recognizer_instance)

    def test_argument_validation_no_input(self):
        """Test that error is raised when no input is specified."""
        with patch("sys.argv", ["speech_demo.py"]):
            with patch("sys.exit") as mock_exit:
                with patch(
                    "examples.speech_demo.argparse.ArgumentParser.error"
                ) as mock_error:
                    main()
                    mock_error.assert_called_with(
                        "Either --file or --microphone-mode must be specified"
                    )

    def test_argument_validation_both_inputs(self):
        """Test that error is raised when both file and microphone are specified."""
        with patch(
            "sys.argv",
            ["speech_demo.py", "--file", "test.wav", "--microphone-mode", "single"],
        ):
            with patch("sys.exit") as mock_exit:
                with patch(
                    "examples.speech_demo.argparse.ArgumentParser.error"
                ) as mock_error:
                    main()
                    mock_error.assert_called_with(
                        "Cannot specify both --file and --microphone-mode"
                    )

    def test_operation_defaults_to_transcription(self):
        """Test that operation defaults to transcription when not specified."""
        with patch("sys.argv", ["speech_demo.py", "--file", "test.wav"]):
            with patch("examples.speech_demo.validate_environment") as mock_validate:
                with patch("examples.speech_demo.SpeechConfig") as mock_config:
                    with patch(
                        "examples.speech_demo.SpeechRecognizer"
                    ) as mock_recognizer:
                        with patch(
                            "examples.speech_demo.process_audio_file_enhanced"
                        ) as mock_process:
                            mock_validate.return_value = True
                            mock_config_instance = MagicMock()
                            mock_config.return_value = mock_config_instance
                            mock_recognizer_instance = MagicMock()
                            mock_recognizer.return_value = mock_recognizer_instance
                            mock_process.return_value = MagicMock()

                            main()

                            # Should default to transcription
                            mock_process.assert_called_once_with(
                                "test.wav", "transcription", mock_recognizer_instance
                            )

    def test_diarize_defaults_to_false(self):
        """Test that diarize defaults to False when not specified."""
        with patch("sys.argv", ["speech_demo.py", "--microphone-mode", "single"]):
            with patch("examples.speech_demo.validate_environment") as mock_validate:
                with patch("examples.speech_demo.SpeechConfig") as mock_config:
                    with patch(
                        "examples.speech_demo.SpeechRecognizer"
                    ) as mock_recognizer:
                        with patch(
                            "examples.speech_demo.process_microphone_basic"
                        ) as mock_process:
                            mock_validate.return_value = True
                            mock_config_instance = MagicMock()
                            mock_config.return_value = mock_config_instance
                            mock_recognizer_instance = MagicMock()
                            mock_recognizer.return_value = mock_recognizer_instance
                            mock_process.return_value = MagicMock()

                            main()

                            # Should use basic processing (no diarization)
                            mock_process.assert_called_once_with(
                                "transcription", mock_recognizer_instance
                            )


class TestSpeechDemoFunctions(unittest.TestCase):
    """Test individual functions in speech_demo.py."""

    def setUp(self):
        """Set up test environment."""
        self.env_patcher = patch.dict(
            os.environ, {"GROQ_API_KEY": "test_key", "HF_TOKEN": "test_hf_token"}
        )
        self.env_patcher.start()

    def tearDown(self):
        """Clean up after tests."""
        self.env_patcher.stop()

    def test_validate_environment_success(self):
        """Test environment validation with all required variables."""
        with patch.dict(
            os.environ, {"GROQ_API_KEY": "test_key", "HF_TOKEN": "test_hf_token"}
        ):
            result = validate_environment()
            self.assertTrue(result)

    def test_validate_environment_missing_groq_key(self):
        """Test environment validation with missing GROQ_API_KEY."""
        with patch.dict(os.environ, {"HF_TOKEN": "test_hf_token"}, clear=True):
            result = validate_environment()
            self.assertFalse(result)

    def test_validate_environment_missing_hf_token(self):
        """Test environment validation with missing HF_TOKEN."""
        with patch.dict(os.environ, {"GROQ_API_KEY": "test_key"}, clear=True):
            result = validate_environment()
            self.assertTrue(result)  # HF_TOKEN is optional but recommended


class TestSpeechDemoIntegration(unittest.TestCase):
    """Integration tests for speech_demo.py."""

    def setUp(self):
        """Set up test environment."""
        self.env_patcher = patch.dict(
            os.environ, {"GROQ_API_KEY": "test_key", "HF_TOKEN": "test_hf_token"}
        )
        self.env_patcher.start()

    def tearDown(self):
        """Clean up after tests."""
        self.env_patcher.stop()

    @patch("examples.speech_demo.validate_environment")
    @patch("examples.speech_demo.SpeechConfig")
    @patch("examples.speech_demo.SpeechRecognizer")
    def test_complete_workflow_file_transcription(
        self, mock_recognizer, mock_config, mock_validate
    ):
        """Test complete workflow for file transcription."""
        # Mock all dependencies
        mock_validate.return_value = True
        mock_config_instance = MagicMock()
        mock_config.return_value = mock_config_instance
        mock_recognizer_instance = MagicMock()
        mock_recognizer.return_value = mock_recognizer_instance

        # Mock the enhanced processing function
        with patch("examples.speech_demo.process_audio_file_enhanced") as mock_process:
            mock_result = MagicMock()
            mock_result.segments = [MagicMock()]
            mock_result.num_speakers = 2
            mock_process.return_value = mock_result

            # Test the workflow
            with patch("sys.argv", ["speech_demo.py", "--file", "test.wav"]):
                with patch("sys.exit") as mock_exit:
                    main()
                    mock_exit.assert_not_called()

            # Verify the workflow
            mock_validate.assert_called_once()
            mock_config.assert_called_once()
            mock_recognizer.assert_called_once_with(mock_config_instance)
            mock_process.assert_called_once_with(
                "test.wav", "transcription", mock_recognizer_instance
            )

    @patch("examples.speech_demo.validate_environment")
    @patch("examples.speech_demo.SpeechConfig")
    @patch("examples.speech_demo.SpeechRecognizer")
    def test_complete_workflow_microphone_continuous_translation_diarization(
        self, mock_recognizer, mock_config, mock_validate
    ):
        """Test complete workflow for continuous microphone with translation and diarization."""
        # Mock all dependencies
        mock_validate.return_value = True
        mock_config_instance = MagicMock()
        mock_config.return_value = mock_config_instance
        mock_recognizer_instance = MagicMock()
        mock_recognizer.return_value = mock_recognizer_instance

        # Mock the enhanced microphone processing function
        with patch("examples.speech_demo.process_microphone_enhanced") as mock_process:
            mock_result = MagicMock()
            mock_result.segments = [MagicMock()]
            mock_result.num_speakers = 1
            mock_process.return_value = mock_result

            # Test the specific combination mentioned by user
            with patch(
                "sys.argv",
                [
                    "speech_demo.py",
                    "--microphone-mode",
                    "continuous",
                    "--operation",
                    "translation",
                    "--diarize",
                    "true",
                ],
            ):
                with patch("sys.exit") as mock_exit:
                    main()
                    mock_exit.assert_not_called()

            # Verify the workflow
            mock_validate.assert_called_once()
            mock_config.assert_called_once()
            mock_recognizer.assert_called_once_with(mock_config_instance)
            mock_process.assert_called_once_with(
                "translation", mock_recognizer_instance
            )


if __name__ == "__main__":
    unittest.main()
