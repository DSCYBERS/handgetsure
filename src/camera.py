"""
Camera Module for Hand Gesture Recognition System
Handles video capture, frame preprocessing, and camera management.
"""

import cv2
import numpy as np
from typing import Optional, Tuple
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CameraManager:
    """Manages camera input and frame processing for gesture recognition."""
    
    def __init__(self, camera_index: int = 0, frame_width: int = 640, frame_height: int = 480):
        """
        Initialize camera manager.
        
        Args:
            camera_index: Index of camera device (0 for default)
            frame_width: Width of captured frames
            frame_height: Height of captured frames
        """
        self.camera_index = camera_index
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.cap = None
        self.is_active = False
        
    def start_camera(self) -> bool:
        """
        Start camera capture.
        
        Returns:
            bool: True if camera started successfully, False otherwise
        """
        try:
            self.cap = cv2.VideoCapture(self.camera_index)
            
            if not self.cap.isOpened():
                logger.error(f"Cannot open camera {self.camera_index}")
                return False
            
            # Set camera properties
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.frame_width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.frame_height)
            self.cap.set(cv2.CAP_PROP_FPS, 30)
            
            self.is_active = True
            logger.info(f"Camera {self.camera_index} started successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error starting camera: {e}")
            return False
    
    def stop_camera(self) -> None:
        """Stop camera capture and release resources."""
        if self.cap is not None:
            self.cap.release()
            self.is_active = False
            logger.info("Camera stopped")
    
    def get_frame(self) -> Tuple[bool, Optional[np.ndarray]]:
        """
        Capture a single frame from camera.
        
        Returns:
            Tuple[bool, Optional[np.ndarray]]: (success, frame)
                success: True if frame captured successfully
                frame: BGR frame as numpy array, None if failed
        """
        if not self.is_active or self.cap is None:
            return False, None
        
        ret, frame = self.cap.read()
        if not ret:
            logger.warning("Failed to capture frame")
            return False, None
        
        return True, frame
    
    def preprocess_frame(self, frame: np.ndarray) -> np.ndarray:
        """
        Preprocess frame for MediaPipe processing.
        
        Args:
            frame: Input BGR frame
            
        Returns:
            np.ndarray: RGB frame ready for MediaPipe
        """
        # Flip frame horizontally for mirror effect
        frame = cv2.flip(frame, 1)
        
        # Convert BGR to RGB for MediaPipe
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        return rgb_frame
    
    def get_processed_frame(self) -> Tuple[bool, Optional[np.ndarray], Optional[np.ndarray]]:
        """
        Get both original BGR frame and preprocessed RGB frame.
        
        Returns:
            Tuple[bool, Optional[np.ndarray], Optional[np.ndarray]]: 
                (success, bgr_frame, rgb_frame)
        """
        success, bgr_frame = self.get_frame()
        
        if not success or bgr_frame is None:
            return False, None, None
        
        rgb_frame = self.preprocess_frame(bgr_frame)
        
        return True, bgr_frame, rgb_frame
    
    def get_camera_info(self) -> dict:
        """
        Get camera information and properties.
        
        Returns:
            dict: Camera properties
        """
        if not self.is_active or self.cap is None:
            return {}
        
        return {
            'width': int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            'height': int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
            'fps': int(self.cap.get(cv2.CAP_PROP_FPS)),
            'camera_index': self.camera_index,
            'is_active': self.is_active
        }
    
    def __enter__(self):
        """Context manager entry."""
        self.start_camera()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop_camera()


# Utility functions
def list_available_cameras(max_cameras: int = 10) -> list:
    """
    List all available camera devices.
    
    Args:
        max_cameras: Maximum number of cameras to check
        
    Returns:
        list: List of available camera indices
    """
    available_cameras = []
    
    for i in range(max_cameras):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            available_cameras.append(i)
            cap.release()
    
    return available_cameras


def test_camera(camera_index: int = 0) -> bool:
    """
    Test if a specific camera is working.
    
    Args:
        camera_index: Index of camera to test
        
    Returns:
        bool: True if camera is working, False otherwise
    """
    try:
        with CameraManager(camera_index) as camera:
            if camera.is_active:
                success, _, _ = camera.get_processed_frame()
                return success
        return False
    except Exception as e:
        logger.error(f"Camera test failed: {e}")
        return False


if __name__ == "__main__":
    # Test the camera module
    print("Testing Camera Module...")
    
    # List available cameras
    cameras = list_available_cameras()
    print(f"Available cameras: {cameras}")
    
    if cameras:
        # Test default camera
        camera_index = cameras[0]
        print(f"Testing camera {camera_index}...")
        
        with CameraManager(camera_index) as camera:
            if camera.is_active:
                print(f"Camera info: {camera.get_camera_info()}")
                
                # Capture a few test frames
                for i in range(5):
                    success, bgr_frame, rgb_frame = camera.get_processed_frame()
                    if success:
                        print(f"Frame {i+1}: BGR shape {bgr_frame.shape}, RGB shape {rgb_frame.shape}")
                    else:
                        print(f"Failed to capture frame {i+1}")
                
                print("Camera test completed successfully!")
            else:
                print("Failed to start camera")
    else:
        print("No cameras available")