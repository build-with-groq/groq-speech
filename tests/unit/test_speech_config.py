"""
Unit tests for SpeechConfig class.
"""

import unittest
import os
from unittest.mock import patch, MagicMock
from groq_speech.speech_config import SpeechConfig
from groq_speech.property_id import PropertyId
from groq_speech.exceptions import ConfigurationError, APIKeyError


class TestSpeechConfig(unittest.TestCase):
    """Test cases for SpeechConfig class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.valid_api_key = "gsk_test123456789"
        self.test_region = "us-east-1"
        self.test_endpoint = "https://custom.groq.com"
        self.test_host = "custom.groq.com"
        self.test_token = "test_auth_token"
    
    def test_init_with_api_key(self):
        """Test initialization with API key."""
        config = SpeechConfig(api_key=self.valid_api_key)
        
        self.assertEqual(config.api_key, self.valid_api_key)
        self.assertEqual(config.region, "us-east-1")
        self.assertIsNone(config.endpoint)
        self.assertIsNone(config.host)
        self.assertIsNone(config.authorization_token)
        self.assertEqual(config.speech_recognition_language, "en-US")
        self.assertIsNone(config.endpoint_id)
    
    def test_init_with_authorization_token(self):
        """Test initialization with authorization token."""
        config = SpeechConfig(authorization_token=self.test_token)
        
        self.assertIsNone(config.api_key)
        self.assertEqual(config.authorization_token, self.test_token)
        self.assertEqual(config.region, "us-east-1")
    
    def test_init_with_custom_region(self):
        """Test initialization with custom region."""
        config = SpeechConfig(api_key=self.valid_api_key, region="eu-west-1")
        
        self.assertEqual(config.region, "eu-west-1")
    
    def test_init_with_custom_endpoint(self):
        """Test initialization with custom endpoint."""
        config = SpeechConfig(api_key=self.valid_api_key, endpoint=self.test_endpoint)
        
        self.assertEqual(config.endpoint, self.test_endpoint)
    
    def test_init_with_custom_host(self):
        """Test initialization with custom host."""
        config = SpeechConfig(api_key=self.valid_api_key, host=self.test_host)
        
        self.assertEqual(config.host, self.test_host)
    
    def test_init_without_credentials(self):
        """Test initialization without API key or token."""
        with self.assertRaises(ValueError) as context:
            SpeechConfig()
        
        self.assertIn("API key or authorization token must be provided", str(context.exception))
    
    def test_init_with_both_api_key_and_token(self):
        """Test initialization with both API key and token."""
        config = SpeechConfig(
            api_key=self.valid_api_key,
            authorization_token=self.test_token
        )
        
        self.assertEqual(config.api_key, self.valid_api_key)
        self.assertEqual(config.authorization_token, self.test_token)
    
    def test_set_property(self):
        """Test setting configuration properties."""
        config = SpeechConfig(api_key=self.valid_api_key)
        
        config.set_property(PropertyId.Speech_SegmentationStrategy, "Semantic")
        config.set_property(PropertyId.Speech_LogFilename, "/tmp/speech.log")
        
        self.assertEqual(
            config.get_property(PropertyId.Speech_SegmentationStrategy),
            "Semantic"
        )
        self.assertEqual(
            config.get_property(PropertyId.Speech_LogFilename),
            "/tmp/speech.log"
        )
    
    def test_get_property_not_set(self):
        """Test getting property that hasn't been set."""
        config = SpeechConfig(api_key=self.valid_api_key)
        
        result = config.get_property(PropertyId.Speech_SegmentationStrategy)
        
        self.assertEqual(result, "")
    
    def test_set_speech_recognition_language(self):
        """Test setting speech recognition language."""
        config = SpeechConfig(api_key=self.valid_api_key)
        
        config.set_speech_recognition_language("de-DE")
        
        self.assertEqual(config.speech_recognition_language, "de-DE")
    
    def test_set_endpoint_id(self):
        """Test setting endpoint ID."""
        config = SpeechConfig(api_key=self.valid_api_key)
        
        config.set_endpoint_id("custom-endpoint-123")
        
        self.assertEqual(config.endpoint_id, "custom-endpoint-123")
    
    def test_get_authorization_headers_with_api_key(self):
        """Test getting authorization headers with API key."""
        config = SpeechConfig(api_key=self.valid_api_key)
        
        headers = config.get_authorization_headers()
        
        self.assertIn("Authorization", headers)
        self.assertEqual(headers["Authorization"], f"Bearer {self.valid_api_key}")
    
    def test_get_authorization_headers_with_token(self):
        """Test getting authorization headers with token."""
        config = SpeechConfig(authorization_token=self.test_token)
        
        headers = config.get_authorization_headers()
        
        self.assertIn("Authorization", headers)
        self.assertEqual(headers["Authorization"], f"Bearer {self.test_token}")
    
    def test_get_authorization_headers_without_credentials(self):
        """Test getting authorization headers without credentials."""
        config = SpeechConfig(api_key=self.valid_api_key)
        config.api_key = None
        config.authorization_token = None
        
        with self.assertRaises(ValueError) as context:
            config.get_authorization_headers()
        
        self.assertIn("No authorization credentials available", str(context.exception))
    
    def test_get_base_url_with_endpoint(self):
        """Test getting base URL with custom endpoint."""
        config = SpeechConfig(api_key=self.valid_api_key, endpoint=self.test_endpoint)
        
        base_url = config.get_base_url()
        
        self.assertEqual(base_url, self.test_endpoint)
    
    def test_get_base_url_with_host(self):
        """Test getting base URL with custom host."""
        config = SpeechConfig(api_key=self.valid_api_key, host=self.test_host)
        
        base_url = config.get_base_url()
        
        self.assertEqual(base_url, f"https://{self.test_host}")
    
    def test_get_base_url_default(self):
        """Test getting default base URL."""
        config = SpeechConfig(api_key=self.valid_api_key)
        
        base_url = config.get_base_url()
        
        self.assertEqual(base_url, "https://api.groq.com/openai/v1")
    
    def test_validate_success(self):
        """Test successful validation."""
        config = SpeechConfig(api_key=self.valid_api_key)
        
        # Should not raise any exception
        config.validate()
    
    def test_validate_without_credentials(self):
        """Test validation without credentials."""
        config = SpeechConfig(api_key=self.valid_api_key)
        config.api_key = None
        config.authorization_token = None
        
        with self.assertRaises(ValueError) as context:
            config.validate()
        
        self.assertIn("API key or authorization token must be provided", str(context.exception))
    
    def test_validate_with_invalid_api_key_format(self):
        """Test validation with invalid API key format."""
        config = SpeechConfig(api_key="invalid_key")
        
        with self.assertRaises(ValueError) as context:
            config.validate()
        
        self.assertIn("Invalid API key format", str(context.exception))
    
    def test_default_properties_set(self):
        """Test that default properties are set during initialization."""
        config = SpeechConfig(api_key=self.valid_api_key)
        
        # Check that default properties are set
        self.assertEqual(
            config.get_property(PropertyId.Speech_SegmentationStrategy),
            "Silence"
        )
        self.assertEqual(
            config.get_property(PropertyId.Speech_LogFilename),
            ""
        )
        self.assertEqual(
            config.get_property(PropertyId.Speech_ServiceConnection_LogFilename),
            ""
        )
    
    def test_property_overwrite(self):
        """Test that properties can be overwritten."""
        config = SpeechConfig(api_key=self.valid_api_key)
        
        # Set custom property
        config.set_property(PropertyId.Speech_SegmentationStrategy, "Semantic")
        
        # Verify it was set
        self.assertEqual(
            config.get_property(PropertyId.Speech_SegmentationStrategy),
            "Semantic"
        )
        
        # Overwrite it
        config.set_property(PropertyId.Speech_SegmentationStrategy, "Silence")
        
        # Verify it was overwritten
        self.assertEqual(
            config.get_property(PropertyId.Speech_SegmentationStrategy),
            "Silence"
        )
    
    def test_multiple_properties(self):
        """Test setting and getting multiple properties."""
        config = SpeechConfig(api_key=self.valid_api_key)
        
        properties = {
            PropertyId.Speech_SegmentationStrategy: "Semantic",
            PropertyId.Speech_LogFilename: "/tmp/speech.log",
            PropertyId.Speech_ServiceConnection_LogFilename: "/tmp/connection.log"
        }
        
        # Set all properties
        for prop_id, value in properties.items():
            config.set_property(prop_id, value)
        
        # Verify all properties
        for prop_id, expected_value in properties.items():
            self.assertEqual(config.get_property(prop_id), expected_value)
    
    def test_empty_string_property(self):
        """Test setting property with empty string."""
        config = SpeechConfig(api_key=self.valid_api_key)
        
        config.set_property(PropertyId.Speech_LogFilename, "")
        
        self.assertEqual(config.get_property(PropertyId.Speech_LogFilename), "")
    
    def test_none_property(self):
        """Test setting property with None value."""
        config = SpeechConfig(api_key=self.valid_api_key)
        
        config.set_property(PropertyId.Speech_LogFilename, None)
        
        self.assertEqual(config.get_property(PropertyId.Speech_LogFilename), "")
    
    def test_unicode_property(self):
        """Test setting property with Unicode characters."""
        config = SpeechConfig(api_key=self.valid_api_key)
        
        unicode_value = "测试日志.log"
        config.set_property(PropertyId.Speech_LogFilename, unicode_value)
        
        self.assertEqual(config.get_property(PropertyId.Speech_LogFilename), unicode_value)


if __name__ == "__main__":
    unittest.main() 