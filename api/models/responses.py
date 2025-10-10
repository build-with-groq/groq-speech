"""
Response models for the Groq Speech API.
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class RecognitionStatus(str, Enum):
    """Recognition result status."""
    SUCCESS = "success"
    ERROR = "error"
    TIMEOUT = "timeout"
    NO_MATCH = "no_match"
    CANCELED = "canceled"


class RecognitionResponse(BaseModel):
    """Response model for speech recognition."""
    
    # Recognition result
    text: str = Field(..., description="Recognized text")
    confidence: float = Field(..., description="Confidence score (0.0 to 1.0)")
    language: Optional[str] = Field(None, description="Detected language")
    status: RecognitionStatus = Field(RecognitionStatus.SUCCESS, description="Recognition status")
    
    # Timing information
    processing_time: float = Field(..., description="Processing time in seconds")
    audio_duration: Optional[float] = Field(None, description="Audio duration in seconds")
    
    # Metadata
    recognition_id: Optional[str] = Field(None, description="Unique recognition ID")
    session_id: Optional[str] = Field(None, description="Session ID")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Recognition timestamp")
    
    # Error information
    error_message: Optional[str] = Field(None, description="Error message if status is error")
    error_code: Optional[str] = Field(None, description="Error code if status is error")
    
    # Additional information
    segments: Optional[List[Dict[str, Any]]] = Field(None, description="Audio segments information")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class StreamingResponse(BaseModel):
    """Response model for streaming recognition."""
    
    # Stream information
    stream_id: str = Field(..., description="Unique stream ID")
    session_id: Optional[str] = Field(None, description="Session ID")
    
    # Recognition result
    text: str = Field(..., description="Recognized text")
    confidence: float = Field(..., description="Confidence score")
    language: Optional[str] = Field(None, description="Detected language")
    is_final: bool = Field(False, description="Whether this is a final result")
    
    # Timing
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Recognition timestamp")
    audio_offset: Optional[float] = Field(None, description="Audio offset in seconds")
    
    # Status
    status: RecognitionStatus = Field(RecognitionStatus.SUCCESS, description="Recognition status")
    
    # Error information
    error_message: Optional[str] = Field(None, description="Error message if status is error")
    error_code: Optional[str] = Field(None, description="Error code if status is error")


class ErrorResponse(BaseModel):
    """Error response model."""
    
    error: str = Field(..., description="Error message")
    error_code: str = Field(..., description="Error code")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Error timestamp")
    request_id: Optional[str] = Field(None, description="Request ID for tracking")
    
    # HTTP status information
    status_code: int = Field(..., description="HTTP status code")
    status_text: str = Field(..., description="HTTP status text")


class HealthResponse(BaseModel):
    """Health check response model."""
    
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Health check timestamp")
    
    # Service information
    uptime: float = Field(..., description="Service uptime in seconds")
    memory_usage: Optional[float] = Field(None, description="Memory usage in MB")
    cpu_usage: Optional[float] = Field(None, description="CPU usage percentage")
    
    # Dependencies
    dependencies: Dict[str, str] = Field(default_factory=dict, description="Dependency status")
    
    # Configuration
    config: Optional[Dict[str, Any]] = Field(None, description="Service configuration")


class StatusResponse(BaseModel):
    """Status response model."""
    
    # Service status
    service: str = Field(..., description="Service name")
    version: str = Field(..., description="Service version")
    status: str = Field(..., description="Service status")
    
    # Performance metrics
    total_requests: int = Field(..., description="Total requests processed")
    successful_requests: int = Field(..., description="Successful requests")
    failed_requests: int = Field(..., description="Failed requests")
    average_response_time: float = Field(..., description="Average response time in seconds")
    
    # Current load
    active_connections: int = Field(..., description="Active WebSocket connections")
    active_sessions: int = Field(..., description="Active recognition sessions")
    queue_size: int = Field(..., description="Request queue size")
    
    # System information
    system_info: Dict[str, Any] = Field(default_factory=dict, description="System information")
    
    # Timestamp
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Status timestamp")


class BatchResponse(BaseModel):
    """Response model for batch recognition."""
    
    # Batch information
    batch_id: str = Field(..., description="Unique batch ID")
    total_files: int = Field(..., description="Total number of files")
    processed_files: int = Field(..., description="Number of processed files")
    successful_files: int = Field(..., description="Number of successful recognitions")
    failed_files: int = Field(..., description="Number of failed recognitions")
    
    # Results
    results: List[RecognitionResponse] = Field(..., description="Recognition results")
    
    # Timing
    start_time: datetime = Field(..., description="Batch start time")
    end_time: Optional[datetime] = Field(None, description="Batch end time")
    total_processing_time: Optional[float] = Field(None, description="Total processing time")
    
    # Status
    status: str = Field(..., description="Batch status (processing, completed, failed)")
    progress: float = Field(..., description="Progress percentage (0.0 to 1.0)")
    
    # Error information
    errors: Optional[List[Dict[str, Any]]] = Field(None, description="Batch errors")


class WebSocketMessage(BaseModel):
    """WebSocket message model."""
    
    # Message information
    message_type: str = Field(..., description="Message type")
    message_id: Optional[str] = Field(None, description="Unique message ID")
    session_id: Optional[str] = Field(None, description="Session ID")
    
    # Payload
    data: Optional[Dict[str, Any]] = Field(None, description="Message payload")
    error: Optional[Dict[str, Any]] = Field(None, description="Error information")
    
    # Timing
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Message timestamp")
    
    # Metadata
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata") 