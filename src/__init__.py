"""
Hand Gesture Control System
A real-time gesture recognition system using Google MediaPipe.
"""

__version__ = "1.0.0"
__author__ = "Hand Gesture Control Team"
__description__ = "Dynamic Gesture-Based Live System Control Using Google MediaPipe"

from .camera import CameraManager
from .hand_detector import HandDetector, HandData
from .gesture_recognizer import GestureRecognizer, GestureResult, GestureType
from .config import ConfigManager

# Conditional imports for display-dependent modules
try:
    from .command_mapper import CommandMapper
    from .visualizer import Visualizer
    _DISPLAY_MODULES_AVAILABLE = True
except ImportError as e:
    # Create placeholder classes for headless environments
    CommandMapper = None
    Visualizer = None
    _DISPLAY_MODULES_AVAILABLE = False

__all__ = [
    'CameraManager',
    'HandDetector', 
    'HandData',
    'GestureRecognizer', 
    'GestureResult', 
    'GestureType',
    'ConfigManager'
]

# Only add display modules to __all__ if they're available
if _DISPLAY_MODULES_AVAILABLE:
    __all__.extend(['CommandMapper', 'Visualizer'])