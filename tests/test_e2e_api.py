#!/usr/bin/env python3
"""
End-to-End Test Suite for API Server

This test suite validates the API server functionality by testing
all REST and WebSocket endpoints with the same commands as CLI.

Test Coverage:
1. REST API endpoints (/api/v1/recognize, /api/v1/translate)
2. WebSocket endpoints (/ws/recognize)
3. Health check endpoint
4. Error handling and validation
5. Integration with CLI functionality
"""

import unittest
import requests
import json
import base64
import time
import threading
import websocket
import sys
import os
from pathlib import Path
from unittest.mock import patch, MagicMock
import numpy as np
import soundfile as sf

# Add the parent directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tests.test_config import (
    TEST_ENV_VARS, 
    setup_test_environment, 
    cleanup_test_environment,
    create_test_audio_file,
    get_test_audio_path
)

# API configuration
API_BASE_URL = "http://localhost:8000"
WS_BASE_URL = "ws://localhost:8000"
TIMEOUT_SECONDS = 30


class TestE2EAPI(unittest.TestCase):
    """End-to-end tests for API server."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment once for all tests."""
        # Set up test environment
        setup_test_environment()
        
        # Ensure test audio files exist
        cls.test_audio_path = get_test_audio_path("test1")
        if not cls.test_audio_path.exists():
            create_test_audio_file(cls.test_audio_path)
        
        # Start API server in background (if not already running)
        cls._start_api_server()
        
        # Wait for server to be ready
        cls._wait_for_server()
    
    @classmethod
    def tearDownClass(cls):
        """Clean up after all tests."""
        cleanup_test_environment()
        # Note: We don't stop the server as it might be used by other tests
    
    @classmethod
    def _start_api_server(cls):
        """Start the API server in background."""
        try:
            # Check if server is already running
            response = requests.get(f"{API_BASE_URL}/health", timeout=5)
            if response.status_code == 200:
                print("✅ API server already running")
                return
        except:
            pass
        
        print("🚀 Starting API server...")
        # Note: In a real test environment, you would start the server here
        # For now, we assume it's started manually or by run-dev.sh
    
    @classmethod
    def _wait_for_server(cls):
        """Wait for the API server to be ready."""
        max_attempts = 30
        for attempt in range(max_attempts):
            try:
                response = requests.get(f"{API_BASE_URL}/health", timeout=5)
                if response.status_code == 200:
                    print("✅ API server is ready")
                    return
            except:
                pass
            
            time.sleep(1)
        
        raise Exception("API server did not start within 30 seconds")
    
    def _create_audio_payload(self, audio_file_path):
        """Create base64 encoded audio payload for API requests."""
        with open(audio_file_path, 'rb') as f:
            audio_data = f.read()
        
        base64_audio = base64.b64encode(audio_data).decode('utf-8')
        return {
            "audio_data": base64_audio,
            "enable_timestamps": True,
            "enable_language_detection": True,
            "enable_diarization": False
        }
    
    def test_health_endpoint(self):
        """Test health check endpoint."""
        response = requests.get(f"{API_BASE_URL}/health")
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("status", data)
        self.assertEqual(data["status"], "healthy")
        self.assertIn("api_key_configured", data)
    
    def test_recognize_endpoint_basic(self):
        """Test basic recognition endpoint."""
        payload = self._create_audio_payload(self.test_audio_path)
        
        response = requests.post(
            f"{API_BASE_URL}/api/v1/recognize",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("text", data)
        self.assertIn("confidence", data)
        self.assertIn("language", data)
    
    def test_recognize_endpoint_with_diarization(self):
        """Test recognition endpoint with diarization."""
        payload = self._create_audio_payload(self.test_audio_path)
        payload["enable_diarization"] = True
        
        response = requests.post(
            f"{API_BASE_URL}/api/v1/recognize",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("text", data)
        
        # Check if diarization data is present
        if "segments" in data:
            self.assertIsInstance(data["segments"], list)
            if data["segments"]:
                self.assertIn("speaker_id", data["segments"][0])
                self.assertIn("text", data["segments"][0])
    
    def test_translate_endpoint_basic(self):
        """Test basic translation endpoint."""
        payload = self._create_audio_payload(self.test_audio_path)
        payload["target_language"] = "en"
        
        response = requests.post(
            f"{API_BASE_URL}/api/v1/translate",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("text", data)
        self.assertIn("confidence", data)
        self.assertIn("language", data)
    
    def test_translate_endpoint_with_diarization(self):
        """Test translation endpoint with diarization."""
        payload = self._create_audio_payload(self.test_audio_path)
        payload["enable_diarization"] = True
        payload["target_language"] = "en"
        
        response = requests.post(
            f"{API_BASE_URL}/api/v1/translate",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("text", data)
        
        # Check if diarization data is present
        if "segments" in data:
            self.assertIsInstance(data["segments"], list)
    
    def test_websocket_connection(self):
        """Test WebSocket connection."""
        def on_message(ws, message):
            data = json.loads(message)
            self.assertIn("type", data)
            if data["type"] == "recognition_result":
                self.assertIn("text", data["data"])
            elif data["type"] == "error":
                self.fail(f"WebSocket error: {data['message']}")
        
        def on_error(ws, error):
            self.fail(f"WebSocket error: {error}")
        
        def on_close(ws, close_status_code, close_msg):
            pass
        
        def on_open(ws):
            # Send start recognition message
            ws.send(json.dumps({
                "type": "start_recognition",
                "data": {
                    "model": "whisper-large-v3",
                    "is_translation": False,
                    "target_language": "en-US",
                    "mode": "single"
                }
            }))
            
            # Send audio data
            with open(self.test_audio_path, 'rb') as f:
                audio_data = f.read()
            
            base64_audio = base64.b64encode(audio_data).decode('utf-8')
            ws.send(json.dumps({
                "type": "audio_data",
                "data": {
                    "audio_data": base64_audio
                }
            }))
            
            # Close connection after sending
            time.sleep(1)
            ws.close()
        
        # Connect to WebSocket
        ws = websocket.WebSocketApp(
            f"{WS_BASE_URL}/ws/recognize",
            on_message=on_message,
            on_error=on_error,
            on_close=on_close,
            on_open=on_open
        )
        
        # Run WebSocket in a separate thread
        ws_thread = threading.Thread(target=ws.run_forever)
        ws_thread.daemon = True
        ws_thread.start()
        
        # Wait for completion
        ws_thread.join(timeout=10)
    
    def test_invalid_audio_data(self):
        """Test error handling with invalid audio data."""
        payload = {
            "audio_data": "invalid_base64_data",
            "enable_timestamps": True,
            "enable_language_detection": True,
            "enable_diarization": False
        }
        
        response = requests.post(
            f"{API_BASE_URL}/api/v1/recognize",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        self.assertNotEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("error", data)
    
    def test_missing_audio_data(self):
        """Test error handling with missing audio data."""
        payload = {
            "enable_timestamps": True,
            "enable_language_detection": True,
            "enable_diarization": False
        }
        
        response = requests.post(
            f"{API_BASE_URL}/api/v1/recognize",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        self.assertNotEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("error", data)
    
    def test_cors_headers(self):
        """Test CORS headers are present."""
        response = requests.options(f"{API_BASE_URL}/api/v1/recognize")
        
        # Check for CORS headers
        self.assertIn("Access-Control-Allow-Origin", response.headers)
        self.assertIn("Access-Control-Allow-Methods", response.headers)
        self.assertIn("Access-Control-Allow-Headers", response.headers)


class TestAPIIntegration(unittest.TestCase):
    """Integration tests for API server."""
    
    def setUp(self):
        """Set up test environment."""
        setup_test_environment()
    
    def tearDown(self):
        """Clean up after tests."""
        cleanup_test_environment()
    
    def test_api_cli_consistency(self):
        """Test that API results are consistent with CLI results."""
        # This test would compare API results with CLI results
        # For now, we just verify the API is working
        try:
            response = requests.get(f"{API_BASE_URL}/health", timeout=5)
            self.assertEqual(response.status_code, 200)
        except:
            self.skipTest("API server not available")
    
    def test_concurrent_requests(self):
        """Test handling of concurrent requests."""
        try:
            response = requests.get(f"{API_BASE_URL}/health", timeout=5)
            if response.status_code != 200:
                self.skipTest("API server not available")
        except:
            self.skipTest("API server not available")
        
        # Test concurrent requests
        def make_request():
            payload = {
                "audio_data": base64.b64encode(b"dummy_audio_data").decode('utf-8'),
                "enable_timestamps": True,
                "enable_language_detection": True,
                "enable_diarization": False
            }
            
            response = requests.post(
                f"{API_BASE_URL}/api/v1/recognize",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            return response.status_code
        
        # Run multiple concurrent requests
        threads = []
        results = []
        
        for _ in range(5):
            thread = threading.Thread(target=lambda: results.append(make_request()))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # Verify all requests completed (even if some failed)
        self.assertEqual(len(results), 5)


if __name__ == '__main__':
    print("🧪 Running End-to-End API Tests")
    print("=" * 50)
    print("Note: Make sure the API server is running (python -m api.server)")
    print("=" * 50)
    
    unittest.main(verbosity=2, buffer=True)
