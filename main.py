#!/usr/bin/env python3
"""
Main Application
Orchestrates all modules for the hand gesture control system.
"""

import cv2
import time
import signal
import sys
import threading
from typing import List, Optional
import logging
import os

# Configure logging first
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def validate_startup_requirements():
    """Validate requirements before starting the application."""
    logger.info("🔍 Validating startup requirements...")
    
    try:
        from requirements_manager import validate_critical_requirements_only, get_requirements_manager
        
        if not validate_critical_requirements_only():
            manager = get_requirements_manager()
            manager.print_validation_errors()
            manager.print_missing_packages_help()
            
            print("\n🚫 STARTUP BLOCKED")
            print("❌ Critical requirements not satisfied")
            print("💡 Run the installer: python install.py")
            print("💡 Or install manually: pip install -r requirements.txt")
            sys.exit(1)
        
        logger.info("✅ Startup requirements satisfied")
        
    except ImportError as e:
        logger.error(f"❌ Requirements manager not available: {e}")
        print("\n� REQUIREMENTS VALIDATION FAILED")
        print("❌ Unable to validate requirements")
        print("� Ensure you're running from the project directory")
        print("💡 Run: python install.py")
        sys.exit(1)

# Validate requirements before importing other modules
validate_startup_requirements()

# Import core modules that don't require display
try:
    # Import core modules directly to avoid __init__.py issues
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    
    from src.camera import CameraManager
    from src.hand_detector import HandDetector, HandData
    from src.gesture_recognizer import GestureRecognizer, GestureResult, GestureType
    from src.config import ConfigManager
    
    logger.info("Core modules imported successfully")
    
    # Try to import display-dependent modules
    DISPLAY_AVAILABLE = False
    CommandMapper = None
    Visualizer = None
    
    # Check if display is available
    if 'DISPLAY' in os.environ or os.name == 'nt':  # Windows doesn't need DISPLAY
        try:
            from src.command_mapper import CommandMapper
            from src.visualizer import Visualizer
            DISPLAY_AVAILABLE = True
            logger.info("Display modules imported successfully - full GUI mode available")
        except Exception as e:
            logger.warning(f"Display modules not available: {e}")
            logger.info("Running in headless mode - core functionality only")
    else:
        logger.info("No display environment detected - running in headless mode")
        
except ImportError as e:
    logger.error(f"Failed to import required modules: {e}")
    print("❌ Error: Missing required dependencies. Please run: pip install -r requirements.txt")
    sys.exit(1)


class HandGestureControlSystem:
    """Main application class for hand gesture control system."""
    
    def __init__(self, config_dir: str = "config"):
        """
        Initialize the hand gesture control system.
        
        Args:
            config_dir: Directory containing configuration files
        """
        logger.info("Initializing Hand Gesture Control System...")
        
        # Load configuration
        self.config_manager = ConfigManager(config_dir)
        self.config = self.config_manager.get_config()
        
        # MANDATORY CAMERA CHECK - Camera is required for this tool
        if not self._check_camera_availability():
            logger.error("❌ CAMERA REQUIRED: This tool requires a working camera to function")
            print("\n" + "="*60)
            print("🚫 CAMERA ACCESS REQUIRED")
            print("="*60)
            print("❌ This hand gesture tool requires a working camera to operate.")
            print("📹 Please ensure you have:")
            print("   • A camera connected to your system")
            print("   • Camera drivers properly installed")
            print("   • Camera permissions granted")
            print("   • No other applications using the camera")
            print("\n💡 To test your camera:")
            print("   • On Windows: Open Camera app")
            print("   • On Linux: Run 'cheese' or 'v4l2-ctl --list-devices'")
            print("   • On macOS: Open Photo Booth")
            print("\n🔧 Once your camera is working, restart this application.")
            print("="*60)
            sys.exit(1)
        
        # Initialize system state
        self.running = False
        self.paused = False
        self.show_help = False
        
        # Initialize modules
        self._initialize_modules()
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        logger.info("Hand Gesture Control System initialized successfully")
    
    def _initialize_modules(self) -> None:
        """Initialize all system modules."""
        try:
            # Camera manager
            self.camera = CameraManager(
                camera_index=self.config.camera.camera_index,
                frame_width=self.config.camera.frame_width,
                frame_height=self.config.camera.frame_height
            )
            
            # Hand detector
            self.hand_detector = HandDetector(
                max_num_hands=self.config.hand_detection.max_num_hands,
                min_detection_confidence=self.config.hand_detection.min_detection_confidence,
                min_tracking_confidence=self.config.hand_detection.min_tracking_confidence
            )
            
            # Gesture recognizer
            self.gesture_recognizer = GestureRecognizer(
                motion_buffer_size=self.config.gesture_recognition.motion_buffer_size
            )
            
            # Initialize display-dependent modules if available
            if DISPLAY_AVAILABLE:
                # Command mapper
                self.command_mapper = CommandMapper(
                    enable_mouse_control=self.config.commands.enable_mouse_control,
                    enable_system_commands=self.config.commands.enable_system_commands
                )
                self.command_mapper.set_command_cooldown(self.config.commands.command_cooldown)
                
                # Visualizer
                self.visualizer = Visualizer(
                    window_name=self.config.visualization.window_name,
                    show_landmarks=self.config.visualization.show_landmarks,
                    show_connections=self.config.visualization.show_connections,
                    show_gesture_info=self.config.visualization.show_gesture_info,
                    show_confidence=self.config.visualization.show_confidence,
                    show_motion_trail=self.config.visualization.show_motion_trail
                )
                logger.info("All modules initialized successfully (full mode)")
            else:
                self.command_mapper = None
                self.visualizer = None
                logger.info("Core modules initialized successfully (headless mode)")
            
        except Exception as e:
            logger.error(f"Failed to initialize modules: {e}")
            raise
    
    def _check_camera_availability(self) -> bool:
        """
        Check if camera is available and working.
        
        Returns:
            bool: True if camera is available, False otherwise
        """
        logger.info("🔍 Checking camera availability...")
        
        # Try to access multiple camera indices (0, 1, 2)
        for camera_index in range(3):
            try:
                logger.info(f"Testing camera index {camera_index}...")
                cap = cv2.VideoCapture(camera_index)
                
                if cap.isOpened():
                    # Try to read a frame to verify camera is actually working
                    ret, frame = cap.read()
                    cap.release()
                    
                    if ret and frame is not None:
                        logger.info(f"✅ Camera {camera_index} is available and working")
                        # Update config to use this working camera
                        self.config.camera.camera_index = camera_index
                        return True
                    else:
                        logger.warning(f"⚠️ Camera {camera_index} opened but cannot read frames")
                else:
                    logger.warning(f"⚠️ Cannot open camera {camera_index}")
                    
                cap.release()
                
            except Exception as e:
                logger.warning(f"⚠️ Error testing camera {camera_index}: {e}")
                
        logger.error("❌ No working camera found")
        return False
    
    def start(self) -> None:
        """Start the hand gesture control system."""
        logger.info("Starting Hand Gesture Control System...")
        
        # Double-check camera before starting (additional safety)
        logger.info("🔍 Performing final camera verification...")
        if not self._check_camera_availability():
            logger.error("❌ CRITICAL: Camera became unavailable before starting")
            print("\n🚫 CAMERA ERROR: Camera was detected during initialization but is no longer available!")
            print("💡 Please check if another application is using the camera and try again.")
            return
        
        # Start camera
        if not self.camera.start_camera():
            logger.error("❌ CRITICAL: Failed to start camera - Tool cannot function without camera")
            print("\n🚫 CAMERA STARTUP FAILED")
            print("❌ The camera could not be started. This tool requires camera access to function.")
            print("💡 Please ensure:")
            print("   • Camera is not being used by another application")
            print("   • Camera drivers are properly installed")
            print("   • You have camera permissions")
            return
        
        self.running = True
        
        try:
            self._main_loop()
        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt")
        except Exception as e:
            logger.error(f"Unexpected error in main loop: {e}")
        finally:
            self.stop()
    
    def _main_loop(self) -> None:
        """Main processing loop."""
        logger.info("Entering main processing loop...")
        
        # Performance tracking
        frame_count = 0
        start_time = time.time()
        
        while self.running:
            # Capture frame
            success, bgr_frame, rgb_frame = self.camera.get_processed_frame()
            
            if not success or bgr_frame is None or rgb_frame is None:
                logger.warning("Failed to capture frame")
                continue
            
            # Skip processing if paused
            if self.paused:
                self._display_paused_frame(bgr_frame)
                continue
            
            # Process frame
            hands_data, gesture_results = self._process_frame(rgb_frame)
            
            # Execute commands
            self._execute_commands(gesture_results)
            
            # Visualize results
            self._visualize_frame(bgr_frame, hands_data, gesture_results)
            
            # Handle user input
            if not self._handle_user_input():
                break
            
            # Update frame counter
            frame_count += 1
            
            # Log performance every 100 frames
            if frame_count % 100 == 0:
                elapsed_time = time.time() - start_time
                fps = frame_count / elapsed_time
                logger.info(f"Processing FPS: {fps:.2f}")
        
        logger.info("Exited main processing loop")
    
    def _process_frame(self, rgb_frame) -> tuple:
        """
        Process a single frame for hand detection and gesture recognition.
        
        Args:
            rgb_frame: RGB frame for processing
            
        Returns:
            tuple: (hands_data, gesture_results)
        """
        # Detect hands
        hands_data = self.hand_detector.detect_hands(rgb_frame)
        
        # Recognize gestures
        gesture_results = []
        for hand_data in hands_data:
            gesture_result = self.gesture_recognizer.recognize_gesture(hand_data)
            gesture_results.append(gesture_result)
        
        return hands_data, gesture_results
    
    def _execute_commands(self, gesture_results: List[GestureResult]) -> None:
        """
        Execute commands based on recognized gestures.
        
        Args:
            gesture_results: List of gesture recognition results
        """
        for result in gesture_results:
            if result.gesture != GestureType.UNKNOWN and result.confidence > 0.5:
                self.command_mapper.execute_command(
                    result.gesture,
                    hand_center=result.hand_center
                )
    
    def _visualize_frame(self, bgr_frame, hands_data: List[HandData], gesture_results: List[GestureResult]):
        """
        Create visualization of the current frame.
        
        Args:
            bgr_frame: BGR frame for visualization
            hands_data: Detected hands data
            gesture_results: Gesture recognition results
            
        Returns:
            Annotated frame
        """
        # Prepare additional info
        additional_info = {
            "Hands": len(hands_data),
            "Mode": "Mouse Control" if self.command_mapper.enable_mouse_control else "Gesture Control",
            "Status": "PAUSED" if self.paused else "RUNNING"
        }
        
        # Add camera info
        camera_info = self.camera.get_camera_info()
        camera_res = f"{camera_info.get('width', 'N/A')}x{camera_info.get('height', 'N/A')}"
        additional_info.update({
            "Camera": camera_res
        })
        
        # Create annotated frame
        annotated_frame = self.visualizer.draw_frame(
            bgr_frame, hands_data, gesture_results, additional_info
        )
        
        # Add help overlay if requested
        if self.show_help:
            annotated_frame = self._draw_help_overlay(annotated_frame)
        
        # Display frame
        self.visualizer.display_frame(annotated_frame)
        
        return annotated_frame
    
    def _display_paused_frame(self, bgr_frame) -> None:
        """Display frame when system is paused."""
        # Add pause overlay
        overlay = bgr_frame.copy()
        cv2.rectangle(overlay, (0, 0), (bgr_frame.shape[1], bgr_frame.shape[0]), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.5, bgr_frame, 0.5, 0, bgr_frame)
        
        # Add pause text
        text = "PAUSED - Press SPACE to resume"
        text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 1, 2)[0]
        text_x = (bgr_frame.shape[1] - text_size[0]) // 2
        text_y = (bgr_frame.shape[0] + text_size[1]) // 2
        
        cv2.putText(bgr_frame, text, (text_x, text_y),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
        self.visualizer.display_frame(bgr_frame)
    
    def _draw_help_overlay(self, frame):
        """Draw help overlay on frame."""
        overlay = frame.copy()
        cv2.rectangle(overlay, (50, 50), (frame.shape[1] - 50, frame.shape[0] - 50), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.8, frame, 0.2, 0, frame)
        
        help_text = [
            "HAND GESTURE CONTROL SYSTEM - HELP",
            "",
            "KEYBOARD CONTROLS:",
            "  ESC - Exit application",
            "  SPACE - Pause/Resume",
            "  H - Toggle this help",
            "  L - Toggle landmarks",
            "  C - Toggle connections",
            "  I - Toggle gesture info",
            "  T - Toggle motion trail",
            "",
            "GESTURE CONTROLS:",
            "  Open Palm - Volume Up",
            "  Fist - Volume Down",
            "  Thumbs Up - Play/Pause",
            "  Index Point - Mouse Control",
            "  Pinch - Mouse Click",
            "  Peace Sign - Scroll Up",
            "  Rock Sign - Scroll Down",
            "  Swipe Left/Right - Next/Prev Track",
            "  Swipe Up/Down - Next/Prev Slide",
            "  OK Sign - Screenshot",
            "  Stop Sign - Alt+Tab",
            "",
            "Press H again to close this help"
        ]
        
        y_start = 80
        for i, line in enumerate(help_text):
            y = y_start + i * 25
            if y > frame.shape[0] - 100:
                break
            
            font_scale = 0.7 if line.startswith(" ") else 0.8
            color = (200, 200, 200) if line.startswith(" ") else (255, 255, 255)
            thickness = 1 if line.startswith(" ") else 2
            
            cv2.putText(frame, line, (80, y),
                       cv2.FONT_HERSHEY_SIMPLEX, font_scale, color, thickness)
        
        return frame
    
    def _handle_user_input(self) -> bool:
        """
        Handle user keyboard input.
        
        Returns:
            bool: True to continue, False to exit
        """
        key = cv2.waitKey(1) & 0xFF
        
        if key == 27:  # ESC key
            logger.info("Exit requested by user")
            return False
        
        # Handle other keys
        self._process_key_input(key)
        return True
    
    def _process_key_input(self, key: int) -> None:
        """Process individual key inputs."""
        if key == ord(' '):  # Space key
            self.paused = not self.paused
            logger.info(f"System {'paused' if self.paused else 'resumed'}")
        elif key == ord('h') or key == ord('H'):
            self.show_help = not self.show_help
        else:
            self._handle_display_toggles(key)
            self._handle_system_commands(key)
    
    def _handle_display_toggles(self, key: int) -> None:
        """Handle display toggle keys."""
        if key == ord('l') or key == ord('L'):
            self.visualizer.toggle_landmarks()
            logger.info("Toggled landmarks display")
        elif key == ord('c') or key == ord('C'):
            self.visualizer.toggle_connections()
            logger.info("Toggled connections display")
        elif key == ord('i') or key == ord('I'):
            self.visualizer.toggle_gesture_info()
            logger.info("Toggled gesture info display")
        elif key == ord('t') or key == ord('T'):
            self.visualizer.toggle_motion_trail()
            logger.info("Toggled motion trail display")
    
    def _handle_system_commands(self, key: int) -> None:
        """Handle system command keys."""
        if key == ord('m') or key == ord('M'):
            self._toggle_mouse_control()
        elif key == ord('s') or key == ord('S'):
            self._save_configuration()
    
    def _toggle_mouse_control(self) -> None:
        """Toggle mouse control mode."""
        current_state = self.command_mapper.enable_mouse_control
        self.command_mapper.enable_mouse_control_mode(not current_state)
        logger.info(f"Mouse control {'enabled' if not current_state else 'disabled'}")
    
    def _save_configuration(self) -> None:
        """Save current configuration."""
        self.config_manager.save_config()
        logger.info("Configuration saved")
    
    def stop(self) -> None:
        """Stop the hand gesture control system."""
        logger.info("Stopping Hand Gesture Control System...")
        
        self.running = False
        
        # Stop camera
        self.camera.stop_camera()
        
        # Close detector
        self.hand_detector.close()
        
        # Close visualizer
        self.visualizer.close()
        
        # Destroy all OpenCV windows
        cv2.destroyAllWindows()
        
        logger.info("Hand Gesture Control System stopped")
    
    def _signal_handler(self, signum, frame):
        """Handle system signals for graceful shutdown."""
        logger.info(f"Received signal {signum}, shutting down...")
        self.running = False
    
    def get_system_status(self) -> dict:
        """Get current system status."""
        return {
            "running": self.running,
            "paused": self.paused,
            "camera_active": self.camera.is_active,
            "config": self.config_manager.get_config()
        }


def main():
    """Main entry point."""
    print("=" * 60)
    print("🤚 DYNAMIC GESTURE-BASED LIVE SYSTEM CONTROL 🤚")
    print("Using Google MediaPipe Hand Recognition")
    print("=" * 60)
    print("⚠️  CAMERA REQUIRED: This tool requires a working camera")
    print("📹 Ensure your camera is connected and accessible")
    print("=" * 60)
    print()
    
    try:
        # Create and start the system
        system = HandGestureControlSystem()
        
        print("🎉 Camera verified successfully!")
        print("Starting system... Press ESC to exit, H for help")
        print("Make sure your hands are visible to the camera!")
        print()
        
        system.start()
        
    except KeyboardInterrupt:
        print("\nShutdown requested by user")
    except Exception as e:
        logger.error(f"System error: {e}")
        print(f"Error: {e}")
    finally:
        print("\nThank you for using Hand Gesture Control System!")


if __name__ == "__main__":
    main()