"""
Configuration Module
Manages system settings and gesture mappings for the hand gesture control system.
"""

import json
import os
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class CameraConfig:
    """Camera configuration settings."""
    camera_index: int = 0
    frame_width: int = 640
    frame_height: int = 480
    fps: int = 30
    auto_exposure: bool = True
    brightness: float = 0.5
    contrast: float = 0.5


@dataclass
class HandDetectionConfig:
    """Hand detection configuration settings."""
    max_num_hands: int = 2
    min_detection_confidence: float = 0.7
    min_tracking_confidence: float = 0.5
    static_image_mode: bool = False


@dataclass
class GestureRecognitionConfig:
    """Gesture recognition configuration settings."""
    motion_buffer_size: int = 10
    min_stability_frames: int = 3
    pinch_threshold: float = 0.03
    swipe_threshold: float = 0.1
    gesture_cooldown: float = 0.5


@dataclass
class VisualizationConfig:
    """Visualization configuration settings."""
    show_landmarks: bool = True
    show_connections: bool = True
    show_gesture_info: bool = True
    show_confidence: bool = True
    show_motion_trail: bool = False
    show_fps: bool = True
    window_name: str = "Hand Gesture Control"


@dataclass
class CommandConfig:
    """Command execution configuration settings."""
    enable_mouse_control: bool = True
    enable_system_commands: bool = True
    command_cooldown: float = 0.5
    mouse_smoothing: float = 0.3
    volume_step: int = 5
    scroll_sensitivity: int = 3


@dataclass
class SystemConfig:
    """Overall system configuration."""
    camera: CameraConfig
    hand_detection: HandDetectionConfig
    gesture_recognition: GestureRecognitionConfig
    visualization: VisualizationConfig
    commands: CommandConfig
    debug_mode: bool = False
    log_level: str = "INFO"


class ConfigManager:
    """Manages system configuration and settings persistence."""
    
    DEFAULT_CONFIG_PATH = "config/settings.json"
    GESTURE_MAPPINGS_PATH = "config/gesture_mappings.json"
    
    def __init__(self, config_dir: str = "config"):
        """
        Initialize configuration manager.
        
        Args:
            config_dir: Directory to store configuration files
        """
        self.config_dir = config_dir
        self.config_path = os.path.join(config_dir, "settings.json")
        self.mappings_path = os.path.join(config_dir, "gesture_mappings.json")
        
        # Ensure config directory exists
        os.makedirs(config_dir, exist_ok=True)
        
        # Load or create default configuration
        self.config = self._load_or_create_config()
        self.gesture_mappings = self._load_or_create_mappings()
        
        logger.info(f"Configuration manager initialized with config dir: {config_dir}")
    
    def _load_or_create_config(self) -> SystemConfig:
        """Load configuration from file or create default."""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    config_dict = json.load(f)
                return self._dict_to_config(config_dict)
            except Exception as e:
                logger.warning(f"Failed to load config: {e}. Using defaults.")
        
        # Create default configuration
        config = SystemConfig(
            camera=CameraConfig(),
            hand_detection=HandDetectionConfig(),
            gesture_recognition=GestureRecognitionConfig(),
            visualization=VisualizationConfig(),
            commands=CommandConfig()
        )
        
        self.save_config(config)
        return config
    
    def _load_or_create_mappings(self) -> Dict[str, Dict[str, Any]]:
        """Load gesture mappings from file or create default."""
        if os.path.exists(self.mappings_path):
            try:
                with open(self.mappings_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load mappings: {e}. Using defaults.")
        
        # Create default gesture mappings
        mappings = self._create_default_mappings()
        self.save_gesture_mappings(mappings)
        return mappings
    
    def _create_default_mappings(self) -> Dict[str, Dict[str, Any]]:
        """Create default gesture to command mappings."""
        return {
            "volume_control": {
                "open_palm": {
                    "action": "volume_up",
                    "description": "Increase volume",
                    "enabled": True
                },
                "fist": {
                    "action": "volume_down",
                    "description": "Decrease volume",
                    "enabled": True
                }
            },
            "media_control": {
                "thumbs_up": {
                    "action": "play_pause",
                    "description": "Play/Pause media",
                    "enabled": True
                },
                "swipe_left": {
                    "action": "next_track",
                    "description": "Next track",
                    "enabled": True
                },
                "swipe_right": {
                    "action": "previous_track",
                    "description": "Previous track",
                    "enabled": True
                }
            },
            "presentation_control": {
                "swipe_up": {
                    "action": "next_slide",
                    "description": "Next slide",
                    "enabled": True
                },
                "swipe_down": {
                    "action": "previous_slide",
                    "description": "Previous slide",
                    "enabled": True
                }
            },
            "mouse_control": {
                "index_point": {
                    "action": "mouse_cursor",
                    "description": "Control mouse cursor",
                    "enabled": True
                },
                "pinch": {
                    "action": "mouse_click",
                    "description": "Mouse click",
                    "enabled": True
                }
            },
            "browser_control": {
                "peace_sign": {
                    "action": "scroll_up",
                    "description": "Scroll up",
                    "enabled": True
                },
                "rock_sign": {
                    "action": "scroll_down",
                    "description": "Scroll down",
                    "enabled": True
                }
            },
            "system_shortcuts": {
                "ok_sign": {
                    "action": "screenshot",
                    "description": "Take screenshot",
                    "enabled": True
                },
                "stop_sign": {
                    "action": "alt_tab",
                    "description": "Switch windows",
                    "enabled": True
                }
            }
        }
    
    def _dict_to_config(self, config_dict: Dict[str, Any]) -> SystemConfig:
        """Convert dictionary to SystemConfig object."""
        return SystemConfig(
            camera=CameraConfig(**config_dict.get("camera", {})),
            hand_detection=HandDetectionConfig(**config_dict.get("hand_detection", {})),
            gesture_recognition=GestureRecognitionConfig(**config_dict.get("gesture_recognition", {})),
            visualization=VisualizationConfig(**config_dict.get("visualization", {})),
            commands=CommandConfig(**config_dict.get("commands", {})),
            debug_mode=config_dict.get("debug_mode", False),
            log_level=config_dict.get("log_level", "INFO")
        )
    
    def _config_to_dict(self, config: SystemConfig) -> Dict[str, Any]:
        """Convert SystemConfig object to dictionary."""
        return {
            "camera": asdict(config.camera),
            "hand_detection": asdict(config.hand_detection),
            "gesture_recognition": asdict(config.gesture_recognition),
            "visualization": asdict(config.visualization),
            "commands": asdict(config.commands),
            "debug_mode": config.debug_mode,
            "log_level": config.log_level
        }
    
    def save_config(self, config: Optional[SystemConfig] = None) -> bool:
        """
        Save configuration to file.
        
        Args:
            config: Configuration to save (uses current if None)
            
        Returns:
            bool: True if saved successfully
        """
        try:
            if config:
                self.config = config
            
            config_dict = self._config_to_dict(self.config)
            
            with open(self.config_path, 'w') as f:
                json.dump(config_dict, f, indent=4)
            
            logger.info("Configuration saved successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
            return False
    
    def save_gesture_mappings(self, mappings: Optional[Dict[str, Dict[str, Any]]] = None) -> bool:
        """
        Save gesture mappings to file.
        
        Args:
            mappings: Mappings to save (uses current if None)
            
        Returns:
            bool: True if saved successfully
        """
        try:
            if mappings:
                self.gesture_mappings = mappings
            
            with open(self.mappings_path, 'w') as f:
                json.dump(self.gesture_mappings, f, indent=4)
            
            logger.info("Gesture mappings saved successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save gesture mappings: {e}")
            return False
    
    def get_config(self) -> SystemConfig:
        """Get current configuration."""
        return self.config
    
    def get_gesture_mappings(self) -> Dict[str, Dict[str, Any]]:
        """Get current gesture mappings."""
        return self.gesture_mappings
    
    def update_camera_config(self, **kwargs) -> None:
        """Update camera configuration parameters."""
        for key, value in kwargs.items():
            if hasattr(self.config.camera, key):
                setattr(self.config.camera, key, value)
                logger.info(f"Updated camera.{key} = {value}")
    
    def update_hand_detection_config(self, **kwargs) -> None:
        """Update hand detection configuration parameters."""
        for key, value in kwargs.items():
            if hasattr(self.config.hand_detection, key):
                setattr(self.config.hand_detection, key, value)
                logger.info(f"Updated hand_detection.{key} = {value}")
    
    def update_gesture_recognition_config(self, **kwargs) -> None:
        """Update gesture recognition configuration parameters."""
        for key, value in kwargs.items():
            if hasattr(self.config.gesture_recognition, key):
                setattr(self.config.gesture_recognition, key, value)
                logger.info(f"Updated gesture_recognition.{key} = {value}")
    
    def update_visualization_config(self, **kwargs) -> None:
        """Update visualization configuration parameters."""
        for key, value in kwargs.items():
            if hasattr(self.config.visualization, key):
                setattr(self.config.visualization, key, value)
                logger.info(f"Updated visualization.{key} = {value}")
    
    def update_command_config(self, **kwargs) -> None:
        """Update command configuration parameters."""
        for key, value in kwargs.items():
            if hasattr(self.config.commands, key):
                setattr(self.config.commands, key, value)
                logger.info(f"Updated commands.{key} = {value}")
    
    def enable_gesture_mapping(self, category: str, gesture: str, enabled: bool = True) -> bool:
        """
        Enable or disable a gesture mapping.
        
        Args:
            category: Gesture category (e.g., "volume_control")
            gesture: Gesture name (e.g., "open_palm")
            enabled: Enable or disable the mapping
            
        Returns:
            bool: True if updated successfully
        """
        try:
            if category in self.gesture_mappings and gesture in self.gesture_mappings[category]:
                self.gesture_mappings[category][gesture]["enabled"] = enabled
                logger.info(f"{'Enabled' if enabled else 'Disabled'} {category}.{gesture}")
                return True
            else:
                logger.warning(f"Gesture mapping not found: {category}.{gesture}")
                return False
        except Exception as e:
            logger.error(f"Failed to update gesture mapping: {e}")
            return False
    
    def add_custom_gesture_mapping(self, category: str, gesture: str, action: str, description: str) -> bool:
        """
        Add a custom gesture mapping.
        
        Args:
            category: Gesture category
            gesture: Gesture name
            action: Action to perform
            description: Human-readable description
            
        Returns:
            bool: True if added successfully
        """
        try:
            if category not in self.gesture_mappings:
                self.gesture_mappings[category] = {}
            
            self.gesture_mappings[category][gesture] = {
                "action": action,
                "description": description,
                "enabled": True,
                "custom": True
            }
            
            logger.info(f"Added custom gesture mapping: {category}.{gesture} -> {action}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add custom gesture mapping: {e}")
            return False
    
    def get_enabled_mappings(self) -> Dict[str, str]:
        """
        Get all enabled gesture mappings.
        
        Returns:
            Dict[str, str]: Mapping of gesture names to actions
        """
        enabled_mappings = {}
        
        for category, gestures in self.gesture_mappings.items():
            for gesture, config in gestures.items():
                if config.get("enabled", True):
                    enabled_mappings[gesture] = config["action"]
        
        return enabled_mappings
    
    def reset_to_defaults(self) -> None:
        """Reset configuration to defaults."""
        self.config = SystemConfig(
            camera=CameraConfig(),
            hand_detection=HandDetectionConfig(),
            gesture_recognition=GestureRecognitionConfig(),
            visualization=VisualizationConfig(),
            commands=CommandConfig()
        )
        
        self.gesture_mappings = self._create_default_mappings()
        
        self.save_config()
        self.save_gesture_mappings()
        
        logger.info("Configuration reset to defaults")
    
    def export_config(self, export_path: str) -> bool:
        """
        Export current configuration to a file.
        
        Args:
            export_path: Path to export configuration
            
        Returns:
            bool: True if exported successfully
        """
        try:
            export_data = {
                "config": self._config_to_dict(self.config),
                "gesture_mappings": self.gesture_mappings
            }
            
            with open(export_path, 'w') as f:
                json.dump(export_data, f, indent=4)
            
            logger.info(f"Configuration exported to {export_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to export configuration: {e}")
            return False
    
    def import_config(self, import_path: str) -> bool:
        """
        Import configuration from a file.
        
        Args:
            import_path: Path to import configuration from
            
        Returns:
            bool: True if imported successfully
        """
        try:
            with open(import_path, 'r') as f:
                import_data = json.load(f)
            
            if "config" in import_data:
                self.config = self._dict_to_config(import_data["config"])
            
            if "gesture_mappings" in import_data:
                self.gesture_mappings = import_data["gesture_mappings"]
            
            self.save_config()
            self.save_gesture_mappings()
            
            logger.info(f"Configuration imported from {import_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to import configuration: {e}")
            return False


if __name__ == "__main__":
    # Test the configuration manager
    print("Testing Configuration Manager...")
    
    # Create test config directory
    test_config_dir = "test_config"
    config_manager = ConfigManager(test_config_dir)
    
    # Test configuration access
    config = config_manager.get_config()
    print(f"Camera resolution: {config.camera.frame_width}x{config.camera.frame_height}")
    print(f"Max hands: {config.hand_detection.max_num_hands}")
    
    # Test configuration update
    config_manager.update_camera_config(frame_width=800, frame_height=600)
    config_manager.update_hand_detection_config(max_num_hands=1)
    
    # Test gesture mappings
    mappings = config_manager.get_enabled_mappings()
    print(f"Enabled mappings: {len(mappings)}")
    
    # Test custom mapping
    config_manager.add_custom_gesture_mapping("test", "custom_gesture", "test_action", "Test action")
    
    # Test save/load
    config_manager.save_config()
    config_manager.save_gesture_mappings()
    
    print("Configuration manager test completed!")
    
    # Cleanup
    import shutil
    shutil.rmtree(test_config_dir, ignore_errors=True)