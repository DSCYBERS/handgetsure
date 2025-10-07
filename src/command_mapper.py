"""
Command Mapping Module
Maps recognized gestures to system commands using PyAutoGUI.
"""

import subprocess
import platform
import time
import os
from typing import Dict, Callable, Any, Optional
from enum import Enum
import logging
from .gesture_recognizer import GestureType

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try to import PyAutoGUI with display check
PYAUTOGUI_AVAILABLE = False
pyautogui = None

def check_display_environment():
    """Check if display environment is available."""
    return 'DISPLAY' in os.environ or os.name == 'nt'

def init_pyautogui():
    """Initialize PyAutoGUI if display is available."""
    global PYAUTOGUI_AVAILABLE, pyautogui
    
    if not check_display_environment():
        logger.warning("No display environment available - PyAutoGUI commands will be simulated")
        return False
    
    try:
        import pyautogui as pg
        # Disable PyAutoGUI failsafe for smoother operation
        pg.FAILSAFE = False
        pyautogui = pg
        PYAUTOGUI_AVAILABLE = True
        logger.info("PyAutoGUI initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize PyAutoGUI: {e}")
        return False

# Initialize on import
init_pyautogui()


def safe_pyautogui_call(func_name, *args, **kwargs):
    """Safely call PyAutoGUI functions with fallback."""
    if PYAUTOGUI_AVAILABLE and pyautogui:
        try:
            func = getattr(pyautogui, func_name)
            return func(*args, **kwargs)
        except Exception as e:
            logger.warning(f"PyAutoGUI {func_name} failed: {e}")
            return False
    else:
        logger.info(f"Simulating PyAutoGUI {func_name}({args}, {kwargs}) - display not available")
        return True


class CommandType(Enum):
    """Types of system commands."""
    VOLUME_CONTROL = "volume_control"
    MEDIA_CONTROL = "media_control"
    PRESENTATION_CONTROL = "presentation_control"
    MOUSE_CONTROL = "mouse_control"
    KEYBOARD_SHORTCUT = "keyboard_shortcut"
    SYSTEM_COMMAND = "system_command"
    BROWSER_CONTROL = "browser_control"
    WINDOW_CONTROL = "window_control"


class CommandMapper:
    """Maps gestures to system commands and executes them."""
    
    def __init__(self, enable_mouse_control: bool = True, enable_system_commands: bool = True):
        """
        Initialize command mapper.
        
        Args:
            enable_mouse_control: Enable mouse cursor control
            enable_system_commands: Enable system-level commands
        """
        self.enable_mouse_control = enable_mouse_control
        self.enable_system_commands = enable_system_commands
        self.last_command_time = 0
        self.command_cooldown = 0.5  # Minimum time between commands (seconds)
        self.os_type = platform.system().lower()
        
        # Initialize gesture to command mapping
        self.gesture_commands = self._initialize_default_mappings()
        
        # Track mouse control state
        self.mouse_control_active = False
        self.cursor_smoothing = 0.3  # Smoothing factor for cursor movement
        
        logger.info(f"Command mapper initialized for {self.os_type}")
    
    def _initialize_default_mappings(self) -> Dict[GestureType, Callable]:
        """Initialize default gesture to command mappings."""
        return {
            # Volume control
            GestureType.OPEN_PALM: self._volume_up,
            GestureType.FIST: self._volume_down,
            
            # Media control
            GestureType.THUMBS_UP: self._play_pause,
            GestureType.SWIPE_LEFT: self._next_track,
            GestureType.SWIPE_RIGHT: self._previous_track,
            
            # Presentation control
            GestureType.SWIPE_UP: self._presentation_next,
            GestureType.SWIPE_DOWN: self._presentation_previous,
            
            # Mouse control
            GestureType.INDEX_POINT: self._enable_mouse_control,
            GestureType.PINCH: self._mouse_click,
            
            # Browser control
            GestureType.PEACE_SIGN: self._browser_scroll_up,
            GestureType.ROCK_SIGN: self._browser_scroll_down,
            
            # System shortcuts
            GestureType.OK_SIGN: self._take_screenshot,
            GestureType.STOP_SIGN: self._alt_tab,
        }
    
    def execute_command(self, gesture: GestureType, hand_center: tuple = None, **kwargs) -> bool:
        """
        Execute command for recognized gesture.
        
        Args:
            gesture: The recognized gesture type
            hand_center: Normalized hand center coordinates (x, y)
            **kwargs: Additional parameters
            
        Returns:
            bool: True if command executed successfully
        """
        # Check command cooldown
        current_time = time.time()
        if current_time - self.last_command_time < self.command_cooldown:
            return False
        
        # Get command function
        command_func = self.gesture_commands.get(gesture)
        if not command_func:
            logger.warning(f"No command mapped for gesture: {gesture}")
            return False
        
        # Execute command
        try:
            success = command_func(hand_center=hand_center, **kwargs)
            if success:
                self.last_command_time = current_time
                logger.info(f"Executed command for gesture: {gesture}")
            return success
        except Exception as e:
            logger.error(f"Error executing command for {gesture}: {e}")
            return False
    
    def control_mouse_cursor(self, hand_center: tuple) -> bool:
        """Control mouse cursor using hand position."""
        if not self.enable_mouse_control or not hand_center:
            return False
        
        try:
            # Convert normalized coordinates to screen coordinates
            if PYAUTOGUI_AVAILABLE and pyautogui:
                screen_width, screen_height = pyautogui.size()
                current_x, current_y = pyautogui.position()
            else:
                screen_width, screen_height = 1920, 1080  # Default resolution
                current_x, current_y = screen_width // 2, screen_height // 2
            
            target_x = int(hand_center[0] * screen_width)
            target_y = int(hand_center[1] * screen_height)
            
            # Apply smoothing
            smooth_x = int(current_x + (target_x - current_x) * self.cursor_smoothing)
            smooth_y = int(current_y + (target_y - current_y) * self.cursor_smoothing)
            
            # Move cursor
            safe_pyautogui_call("moveTo", smooth_x, smooth_y, duration=0.1)
            return True
            
        except Exception as e:
            logger.error(f"Error controlling mouse cursor: {e}")
            return False
    
    # Volume control commands
    def _volume_up(self, **kwargs) -> bool:
        """Increase system volume."""
        try:
            if self.os_type == "windows":
                safe_pyautogui_call("press", "volumeup")
            elif self.os_type == "darwin":  # macOS
                subprocess.run(["osascript", "-e", "set volume output volume (output volume of (get volume settings) + 10)"])
            elif self.os_type == "linux":
                subprocess.run(["amixer", "set", "Master", "5%+"])
            logger.info("Volume increased")
            return True
        except Exception as e:
            logger.error(f"Volume up error: {e}")
            return False
    
    def _volume_down(self, **kwargs) -> bool:
        """Decrease system volume."""
        try:
            if self.os_type == "windows":
                safe_pyautogui_call("press", "volumedown")
            elif self.os_type == "darwin":  # macOS
                subprocess.run(["osascript", "-e", "set volume output volume (output volume of (get volume settings) - 10)"])
            elif self.os_type == "linux":
                subprocess.run(["amixer", "set", "Master", "5%-"])
            logger.info("Volume decreased")
            return True
        except Exception as e:
            logger.error(f"Volume down error: {e}")
            return False
    
    # Media control commands
    def _play_pause(self, **kwargs) -> bool:
        """Toggle play/pause for media."""
        try:
            safe_pyautogui_call("press", "playpause")
            logger.info("Play/pause toggled")
            return True
        except Exception as e:
            logger.error(f"Play/pause error: {e}")
            return False
    
    def _next_track(self, **kwargs) -> bool:
        """Skip to next track."""
        try:
            safe_pyautogui_call("press", "nexttrack")
            logger.info("Next track")
            return True
        except Exception as e:
            logger.error(f"Next track error: {e}")
            return False
    
    def _previous_track(self, **kwargs) -> bool:
        """Go to previous track."""
        try:
            safe_pyautogui_call("press", "prevtrack")
            logger.info("Previous track")
            return True
        except Exception as e:
            logger.error(f"Previous track error: {e}")
            return False
    
    # Presentation control commands
    def _presentation_next(self, **kwargs) -> bool:
        """Go to next slide in presentation."""
        try:
            safe_pyautogui_call("press", "right")
            logger.info("Next slide")
            return True
        except Exception as e:
            logger.error(f"Next slide error: {e}")
            return False
    
    def _presentation_previous(self, **kwargs) -> bool:
        """Go to previous slide in presentation."""
        try:
            safe_pyautogui_call("press", "left")
            logger.info("Previous slide")
            return True
        except Exception as e:
            logger.error(f"Previous slide error: {e}")
            return False
    
    # Mouse control commands
    def _enable_mouse_control(self, **kwargs) -> bool:
        """Toggle mouse control mode."""
        self.mouse_control_active = not self.mouse_control_active
        logger.info(f"Mouse control: {'enabled' if self.mouse_control_active else 'disabled'}")
        return True
    
    def _mouse_click(self, **kwargs) -> bool:
        """Perform mouse click."""
        try:
            safe_pyautogui_call("click")
            logger.info("Mouse clicked")
            return True
        except Exception as e:
            logger.error(f"Mouse click error: {e}")
            return False
    
    # Browser control commands
    def _browser_scroll_up(self, **kwargs) -> bool:
        """Scroll up in browser."""
        try:
            safe_pyautogui_call("scroll", 3)
            logger.info("Scrolled up")
            return True
        except Exception as e:
            logger.error(f"Scroll up error: {e}")
            return False
    
    def _browser_scroll_down(self, **kwargs) -> bool:
        """Scroll down in browser."""
        try:
            safe_pyautogui_call("scroll", -3)
            logger.info("Scrolled down")
            return True
        except Exception as e:
            logger.error(f"Scroll down error: {e}")
            return False
    
    # System commands
    def _take_screenshot(self, **kwargs) -> bool:
        """Take a screenshot."""
        try:
            if self.os_type == "windows":
                safe_pyautogui_call("hotkey", "win", "shift", "s")
            elif self.os_type == "darwin":  # macOS
                safe_pyautogui_call("hotkey", "cmd", "shift", "4")
            else:  # Linux
                safe_pyautogui_call("hotkey", "shift", "printscreen")
            logger.info("Screenshot taken")
            return True
        except Exception as e:
            logger.error(f"Screenshot error: {e}")
            return False
    
    def _alt_tab(self, **kwargs) -> bool:
        """Switch between applications."""
        try:
            if self.os_type == "darwin":  # macOS
                safe_pyautogui_call("hotkey", "cmd", "tab")
            else:  # Windows/Linux
                safe_pyautogui_call("hotkey", "alt", "tab")
            logger.info("Application switched")
            return True
        except Exception as e:
            logger.error(f"Alt+Tab error: {e}")
            return False
    
    # Configuration methods
    def set_command_cooldown(self, cooldown: float) -> None:
        """Set minimum time between commands."""
        self.command_cooldown = max(0.1, cooldown)
        logger.info(f"Command cooldown set to {self.command_cooldown}s")
    
    def add_custom_command(self, gesture: GestureType, command_func: Callable) -> None:
        """Add custom command mapping."""
        self.gesture_commands[gesture] = command_func
        logger.info(f"Custom command added for {gesture}")
    
    def remove_command(self, gesture: GestureType) -> None:
        """Remove command mapping."""
        if gesture in self.gesture_commands:
            del self.gesture_commands[gesture]
            logger.info(f"Command removed for {gesture}")
    
    def execute_custom_hotkey(self, keys: list) -> bool:
        """Execute custom hotkey combination."""
        try:
            safe_pyautogui_call("hotkey", *keys)
            logger.info(f"Hotkey executed: {'+'.join(keys)}")
            return True
        except Exception as e:
            logger.error(f"Hotkey error: {e}")
            return False
    
    def get_available_gestures(self) -> list:
        """Get list of available gesture mappings."""
        return list(self.gesture_commands.keys())
    
    def is_command_available(self, gesture: GestureType) -> bool:
        """Check if command is available for gesture."""
        return gesture in self.gesture_commands