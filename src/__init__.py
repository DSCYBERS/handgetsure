"""
Hand Gesture Control System
A real-time gesture recognition system using Google MediaPipe.
"""

__version__ = "1.0.0"
__author__ = "Hand Gesture Control Team"
__description__ = "Dynamic Gesture-Based Live System Control Using Google MediaPipe"

# Import core modules that don't require display
from .camera import CameraManager
from .hand_detector import HandDetector, HandData
from .gesture_recognizer import GestureRecognizer, GestureResult, GestureType
from .config import ConfigManager

# Display-dependent modules - import only when explicitly requested
# These are not imported automatically to avoid display environment issues
# Import them manually in your code when display is available:
# from src.command_mapper import CommandMapper
# from src.visualizer import Visualizer

__all__ = [
    'CameraManager',
    'HandDetector', 
    'HandData',
    'GestureRecognizer', 
    'GestureResult', 
    'GestureType',
    'ConfigManager'
]

# Helper function to check display availability
def is_display_available():
    """Check if display environment is available for GUI modules."""
    import os
    return 'DISPLAY' in os.environ or os.name == 'nt'

# Helper function to safely import display modules
def import_display_modules():
    """Safely import display-dependent modules if available."""
    try:
        if is_display_available():
            from .command_mapper import CommandMapper
            from .visualizer import Visualizer
            return CommandMapper, Visualizer
        else:
            return None, None
    except ImportError:
        return None, None