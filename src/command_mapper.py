"""
Command Mapping Module
Maps recognized gestures to system commands using PyAutoGUI.
"""

import pyautogui
import subprocess
import platform
import time
from typing import Dict, Callable, Any, Optional
from enum import Enum
import logging
from .gesture_recognizer import GestureType

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Disable PyAutoGUI failsafe for smoother operation
pyautogui.FAILSAFE = False


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
            gesture: Recognized gesture type
            hand_center: Hand center coordinates for cursor control
            **kwargs: Additional parameters
            
        Returns:
            bool: True if command executed successfully
        """
        # Check cooldown
        current_time = time.time()
        if current_time - self.last_command_time < self.command_cooldown:
            return False
        
        try:
            # Handle mouse control specially
            if gesture == GestureType.INDEX_POINT and hand_center and self.enable_mouse_control:
                self._control_mouse_cursor(hand_center)
                return True
            
            # Execute mapped command
            if gesture in self.gesture_commands:
                command_func = self.gesture_commands[gesture]
                success = command_func()
                
                if success:
                    self.last_command_time = current_time
                    logger.info(f"Executed command for gesture: {gesture.value}")
                
                return success
            
            return False
            
        except Exception as e:
            logger.error(f"Error executing command for {gesture.value}: {e}")
            return False
    
    def _control_mouse_cursor(self, hand_center: tuple) -> bool:
        """Control mouse cursor based on hand position."""
        if not self.enable_mouse_control:
            return False
        
        try:
            # Convert normalized coordinates to screen coordinates
            screen_width, screen_height = pyautogui.size()
            target_x = int(hand_center[0] * screen_width)
            target_y = int(hand_center[1] * screen_height)
            
            # Get current cursor position
            current_x, current_y = pyautogui.position()
            
            # Apply smoothing
            smooth_x = int(current_x + (target_x - current_x) * self.cursor_smoothing)
            smooth_y = int(current_y + (target_y - current_y) * self.cursor_smoothing)
            
            # Move cursor
            pyautogui.moveTo(smooth_x, smooth_y, duration=0.1)
            return True
            
        except Exception as e:
            logger.error(f"Error controlling mouse cursor: {e}")
            return False
    
    # Volume control commands
    def _volume_up(self) -> bool:
        """Increase system volume."""
        try:
            if self.os_type == "windows":
                pyautogui.press("volumeup")
            elif self.os_type == "darwin":  # macOS
                subprocess.run(["osascript", "-e", "set volume output volume (output volume of (get volume settings) + 10)"])
            elif self.os_type == "linux":
                subprocess.run(["amixer", "set", "Master", "5%+"])
            return True
        except Exception as e:
            logger.error(f"Volume up error: {e}")
            return False
    
    def _volume_down(self) -> bool:
        """Decrease system volume."""
        try:
            if self.os_type == "windows":
                pyautogui.press("volumedown")
            elif self.os_type == "darwin":  # macOS
                subprocess.run(["osascript", "-e", "set volume output volume (output volume of (get volume settings) - 10)"])
            elif self.os_type == "linux":
                subprocess.run(["amixer", "set", "Master", "5%-"])
            return True
        except Exception as e:
            logger.error(f"Volume down error: {e}")
            return False
    
    # Media control commands
    def _play_pause(self) -> bool:
        """Toggle play/pause for media."""
        try:
            pyautogui.press("playpause")
            return True
        except Exception as e:
            logger.error(f"Play/pause error: {e}")
            return False
    
    def _next_track(self) -> bool:
        """Skip to next track."""
        try:
            pyautogui.press("nexttrack")
            return True
        except Exception as e:
            logger.error(f"Next track error: {e}")
            return False
    
    def _previous_track(self) -> bool:
        """Go to previous track."""
        try:
            pyautogui.press("prevtrack")
            return True
        except Exception as e:
            logger.error(f"Previous track error: {e}")
            return False
    
    # Presentation control commands
    def _presentation_next(self) -> bool:
        """Next slide in presentation."""
        try:
            pyautogui.press("right")
            return True
        except Exception as e:
            logger.error(f"Presentation next error: {e}")
            return False
    
    def _presentation_previous(self) -> bool:
        """Previous slide in presentation."""
        try:
            pyautogui.press("left")
            return True
        except Exception as e:
            logger.error(f"Presentation previous error: {e}")
            return False
    
    # Mouse control commands
    def _enable_mouse_control(self) -> bool:
        """Enable/disable mouse control mode."""
        self.mouse_control_active = not self.mouse_control_active
        logger.info(f"Mouse control: {'enabled' if self.mouse_control_active else 'disabled'}")
        return True
    
    def _mouse_click(self) -> bool:
        """Perform mouse click."""
        try:
            pyautogui.click()
            return True
        except Exception as e:
            logger.error(f"Mouse click error: {e}")
            return False
    
    # Browser control commands
    def _browser_scroll_up(self) -> bool:
        """Scroll up in browser."""
        try:
            pyautogui.scroll(3)
            return True
        except Exception as e:
            logger.error(f"Browser scroll up error: {e}")
            return False
    
    def _browser_scroll_down(self) -> bool:
        """Scroll down in browser."""
        try:
            pyautogui.scroll(-3)
            return True
        except Exception as e:
            logger.error(f"Browser scroll down error: {e}")
            return False
    
    # System shortcut commands
    def _take_screenshot(self) -> bool:
        """Take a screenshot."""
        try:
            if self.os_type == "windows":
                pyautogui.hotkey("win", "shift", "s")
            elif self.os_type == "darwin":  # macOS
                pyautogui.hotkey("cmd", "shift", "4")
            elif self.os_type == "linux":
                pyautogui.hotkey("shift", "printscreen")
            return True
        except Exception as e:
            logger.error(f"Screenshot error: {e}")
            return False
    
    def _alt_tab(self) -> bool:
        """Switch between windows."""
        try:
            if self.os_type == "darwin":  # macOS
                pyautogui.hotkey("cmd", "tab")
            else:
                pyautogui.hotkey("alt", "tab")
            return True
        except Exception as e:
            logger.error(f"Alt+Tab error: {e}")
            return False
    
    # Configuration methods
    def add_custom_mapping(self, gesture: GestureType, command_func: Callable) -> None:
        """Add custom gesture to command mapping."""
        self.gesture_commands[gesture] = command_func
        logger.info(f"Added custom mapping for {gesture.value}")
    
    def remove_mapping(self, gesture: GestureType) -> None:
        """Remove gesture mapping."""
        if gesture in self.gesture_commands:
            del self.gesture_commands[gesture]
            logger.info(f"Removed mapping for {gesture.value}")
    
    def set_command_cooldown(self, cooldown: float) -> None:
        """Set minimum time between commands."""
        self.command_cooldown = max(0.1, cooldown)
        logger.info(f"Command cooldown set to {self.command_cooldown}s")
    
    def get_available_mappings(self) -> Dict[str, str]:
        """Get list of available gesture mappings."""
        mappings = {}
        for gesture, func in self.gesture_commands.items():
            mappings[gesture.value] = func.__name__.replace("_", " ").title()
        return mappings
    
    def enable_mouse_control_mode(self, enable: bool) -> None:
        """Enable or disable mouse control."""
        self.enable_mouse_control = enable
        logger.info(f"Mouse control {'enabled' if enable else 'disabled'}")
    
    def enable_system_commands_mode(self, enable: bool) -> None:
        """Enable or disable system commands."""
        self.enable_system_commands = enable
        logger.info(f"System commands {'enabled' if enable else 'disabled'}")


# Utility functions for custom commands
def create_keyboard_shortcut(keys: list) -> Callable:
    """
    Create a custom keyboard shortcut command.
    
    Args:
        keys: List of keys for the shortcut
        
    Returns:
        Callable: Function that executes the shortcut
    """
    def shortcut_command():
        try:
            pyautogui.hotkey(*keys)
            return True
        except Exception as e:
            logger.error(f"Keyboard shortcut error: {e}")
            return False
    
    return shortcut_command


def create_system_command(command: str) -> Callable:
    """
    Create a custom system command.
    
    Args:
        command: System command to execute
        
    Returns:
        Callable: Function that executes the command
    """
    def system_command():
        try:
            subprocess.run(command.split(), capture_output=True)
            return True
        except Exception as e:
            logger.error(f"System command error: {e}")
            return False
    
    return system_command


if __name__ == "__main__":
    # Test the command mapper
    print("Testing Command Mapper...")
    
    mapper = CommandMapper()
    
    # Test available mappings
    mappings = mapper.get_available_mappings()
    print("Available gesture mappings:")
    for gesture, command in mappings.items():
        print(f"  {gesture}: {command}")
    
    # Test custom mapping
    custom_command = create_keyboard_shortcut(["ctrl", "c"])
    mapper.add_custom_mapping(GestureType.THUMBS_DOWN, custom_command)
    
    print(f"Operating system: {mapper.os_type}")
    print("Command mapper test completed!")