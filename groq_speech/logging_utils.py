"""
Structured logging utilities for Groq Speech SDK.

This module provides consistent logging across all components with support for:
- Verbose mode control via environment variables
- Structured logging with timestamps and component identification
- Different log levels (DEBUG, INFO, WARNING, ERROR)
- Colored output for better readability
"""

import os
import sys
from datetime import datetime
from typing import Optional, Any, Dict
from enum import Enum

class LogLevel(Enum):
    """Log levels in order of severity."""
    DEBUG = 0
    INFO = 1
    WARNING = 2
    ERROR = 3

class ComponentLogger:
    """Structured logger for different components."""
    
    def __init__(self, component_name: str, min_level: LogLevel = LogLevel.INFO):
        self.component_name = component_name
        self.min_level = min_level
        self.verbose = self._is_verbose_enabled()
        
        # Colors for different log levels
        self.colors = {
            LogLevel.DEBUG: '\033[36m',    # Cyan
            LogLevel.INFO: '\033[32m',     # Green
            LogLevel.WARNING: '\033[33m',  # Yellow
            LogLevel.ERROR: '\033[31m',    # Red
        }
        self.reset_color = '\033[0m'
    
    def _is_verbose_enabled(self) -> bool:
        """Check if verbose logging is enabled via environment variables."""
        return (
            os.getenv('GROQ_VERBOSE', 'false').lower() in ('true', '1', 'yes') or
            os.getenv('GROQ_LOG_LEVEL', '').upper() == 'DEBUG'
        )
    
    def _should_log(self, level: LogLevel) -> bool:
        """Check if we should log at the given level."""
        if not self.verbose and level == LogLevel.DEBUG:
            return False
        return level.value >= self.min_level.value
    
    def _format_message(self, level: LogLevel, message: str, data: Optional[Dict[str, Any]] = None, **kwargs) -> str:
        """Format log message with timestamp, component, and level."""
        timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]
        level_name = level.name
        color = self.colors.get(level, '')
        reset = self.reset_color
        
        # Format additional context if provided
        context = ""
        if data or kwargs:
            context_parts = []
            if data:
                for key, value in data.items():
                    if isinstance(value, (list, tuple)):
                        value = f"[{', '.join(map(str, value))}]"
                    context_parts.append(f"{key}={value}")
            if kwargs:
                for key, value in kwargs.items():
                    if isinstance(value, (list, tuple)):
                        value = f"[{', '.join(map(str, value))}]"
                    context_parts.append(f"{key}={value}")
            context = f" | {' '.join(context_parts)}"
        
        return f"{color}[{timestamp}] [{self.component_name}] [{level_name}]{reset} {message}{context}"
    
    def debug(self, message: str, data: Optional[Dict[str, Any]] = None, **kwargs):
        """Log debug message (only in verbose mode)."""
        if self._should_log(LogLevel.DEBUG):
            print(self._format_message(LogLevel.DEBUG, message, data, **kwargs), file=sys.stdout)
    
    def info(self, message: str, data: Optional[Dict[str, Any]] = None, **kwargs):
        """Log info message."""
        if self._should_log(LogLevel.INFO):
            print(self._format_message(LogLevel.INFO, message, data, **kwargs), file=sys.stdout)
    
    def warning(self, message: str, data: Optional[Dict[str, Any]] = None, **kwargs):
        """Log warning message."""
        if self._should_log(LogLevel.WARNING):
            print(self._format_message(LogLevel.WARNING, message, data, **kwargs), file=sys.stderr)
    
    def error(self, message: str, data: Optional[Dict[str, Any]] = None, **kwargs):
        """Log error message."""
        if self._should_log(LogLevel.ERROR):
            print(self._format_message(LogLevel.ERROR, message, data, **kwargs), file=sys.stderr)
    
    def success(self, message: str, data: Optional[Dict[str, Any]] = None, **kwargs):
        """Log success message (info level with success emoji)."""
        if self._should_log(LogLevel.INFO):
            print(self._format_message(LogLevel.INFO, f"✅ {message}", data, **kwargs), file=sys.stdout)
    
    def processing(self, message: str, data: Optional[Dict[str, Any]] = None, **kwargs):
        """Log processing message (info level with processing emoji)."""
        if self._should_log(LogLevel.INFO):
            print(self._format_message(LogLevel.INFO, f"🔄 {message}", data, **kwargs), file=sys.stdout)

    def dataFlow(self, source: str, destination: str, data: Dict[str, Any], description: str):
        """Log data flow between components (info level with data flow emoji)."""
        if self._should_log(LogLevel.INFO):
            flow_data = {
                "source": source,
                "destination": destination,
                "description": description,
                **data
            }
            print(self._format_message(LogLevel.INFO, f"📊 Data Flow: {source} -> {destination} | {description}", flow_data), file=sys.stdout)

# Global loggers for different components
api_logger = ComponentLogger("API")
sdk_logger = ComponentLogger("SDK")
diarization_logger = ComponentLogger("DIARIZATION")
vad_logger = ComponentLogger("VAD")
audio_logger = ComponentLogger("AUDIO")

def get_logger(component_name: str) -> ComponentLogger:
    """Get a logger for a specific component."""
    return ComponentLogger(component_name)

# Convenience functions for backward compatibility
def log_debug(message: str, verbose: bool = False, component: str = "GENERAL", **kwargs):
    """Debug logging with backward compatibility."""
    if verbose:
        logger = ComponentLogger(component)
        logger.debug(message, **kwargs)

def log_info(message: str, component: str = "GENERAL", **kwargs):
    """Info logging with backward compatibility."""
    logger = ComponentLogger(component)
    logger.info(message, **kwargs)

def log_warning(message: str, component: str = "GENERAL", **kwargs):
    """Warning logging with backward compatibility."""
    logger = ComponentLogger(component)
    logger.warning(message, **kwargs)

def log_error(message: str, component: str = "GENERAL", **kwargs):
    """Error logging with backward compatibility."""
    logger = ComponentLogger(component)
    logger.error(message, **kwargs)

def log_success(message: str, component: str = "GENERAL", **kwargs):
    """Success logging with backward compatibility."""
    logger = ComponentLogger(component)
    logger.success(message, **kwargs)
