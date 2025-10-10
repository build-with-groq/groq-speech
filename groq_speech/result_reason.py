"""
Result reason enums for Groq Speech services.

This module provides enumeration classes that define the possible outcomes
and states of speech recognition operations. These enums are essential for
understanding what happened during recognition and handling different
scenarios.

ARCHITECTURE OVERVIEW:
1. RESULT REASON ENUMERATION
   - Defines all possible speech recognition outcomes
   - Provides consistent status reporting across the system
   - Enables proper error handling and user feedback

2. CANCELLATION REASON ENUMERATION
   - Categorizes different types of recognition failures
   - Enables specific error handling and recovery
   - Provides detailed feedback for debugging and user support

3. SYSTEM INTEGRATION
   - Used throughout the speech recognition pipeline
   - Integrated with event system and result objects
   - Provides consistent status reporting

KEY FEATURES:
- Comprehensive coverage of all recognition outcomes
- Clear categorization of success and failure states
- Detailed cancellation reasons for error handling
- Consistent enum values for system integration
- Easy extensibility for future status types

USAGE EXAMPLES:
    # Check recognition result status
    if result.reason == ResultReason.RecognizedSpeech:
        print(f"Recognized: {result.text}")

    # Handle cancellation with specific reason
    if result.reason == ResultReason.Canceled:
        if result.cancellation_details.reason == CancellationReason.NetworkError:
            print("Network error occurred")

    # Check session state
    if result.reason == ResultReason.SessionStarted:
        print("Recognition session started")
"""

from enum import Enum


class ResultReason(Enum):
    """
    Enumeration of speech recognition result reasons.

    CRITICAL: This enum defines all possible outcomes of speech recognition
    operations. It's the primary way the system communicates the status
    and result of recognition attempts to applications and users.

    The ResultReason values are used throughout the system to:
    1. Indicate recognition success or failure
    2. Provide session lifecycle information
    3. Enable proper error handling and recovery
    4. Support continuous recognition workflows
    5. Guide user interface behavior and feedback

    Each reason has specific implications for:
    - Application behavior and user experience
    - Error handling and recovery strategies
    - Resource management and cleanup
    - Performance monitoring and analytics
    """

    # Successful recognition
    # This indicates that speech was successfully
    # recognized and transcribed
    RecognizedSpeech = "RecognizedSpeech"

    # No speech detected
    # This occurs when audio is present but no
    # recognizable speech is found
    NoMatch = "NoMatch"

    # Recognition was canceled
    # This indicates the recognition process was
    # interrupted or failed
    Canceled = "Canceled"

    # Recognition is in progress (for continuous recognition)
    # This is used during ongoing recognition to show progress
    Recognizing = "Recognizing"

    # Session started
    # This indicates the beginning of a recognition session
    SessionStarted = "SessionStarted"

    # Session stopped
    # This indicates the end of a recognition session
    SessionStopped = "SessionStopped"


class CancellationReason(Enum):
    """
    Enumeration of cancellation reasons for failed recognition.

    CRITICAL: This enum provides detailed information about why a speech
    recognition operation was canceled or failed. It's essential for:

    1. Error Diagnosis: Understanding what went wrong
    2. User Feedback: Providing meaningful error messages
    3. Recovery Strategies: Implementing appropriate retry logic
    4. Debugging: Identifying system or configuration issues
    5. Monitoring: Tracking failure patterns and system health

    Each cancellation reason requires different handling:
    - Network errors may benefit from retry logic
    - Service errors may indicate system issues
    - Invalid audio may require user guidance
    - Timeout errors may need configuration adjustment
    """

    # Error occurred during recognition
    # Generic error that doesn't fit other categories
    Error = "Error"

    # Recognition was canceled by user
    # User explicitly stopped the recognition process
    EndOfStream = "EndOfStream"

    # Recognition was canceled due to timeout
    # Operation exceeded configured time limits
    Timeout = "Timeout"

    # Recognition was canceled due to network issues
    # Network connectivity or API communication
    # problems
    NetworkError = "NetworkError"

    # Recognition was canceled due to service issues
    # Problems with the Groq speech recognition service
    ServiceError = "ServiceError"

    # Recognition was canceled due to invalid audio
    # Audio format, quality, or corruption issues
    InvalidAudio = "InvalidAudio"

    # Recognition was canceled due to language not supported
    # The detected language is not supported by the service
    LanguageNotSupported = "LanguageNotSupported"
