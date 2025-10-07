"""
Visualization Module
Handles display of live camera feed with hand landmarks and gesture information.
"""

import cv2
import numpy as np
from typing import List, Dict, Optional, Tuple
import time
import logging
from .hand_detector import HandData
from .gesture_recognizer import GestureResult, GestureType

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Visualizer:
    """Handles visualization of hand tracking and gesture recognition."""
    
    # Color constants (BGR format for OpenCV)
    COLORS = {
        'landmark': (0, 255, 0),        # Green for landmarks
        'connection': (255, 0, 0),      # Blue for connections
        'text': (255, 255, 255),        # White for text
        'gesture_box': (0, 0, 255),     # Red for gesture info box
        'confidence_bar': (0, 255, 255), # Yellow for confidence bar
        'hand_center': (255, 0, 255),   # Magenta for hand center
        'motion_trail': (0, 165, 255),  # Orange for motion trail
    }
    
    # Hand landmark connections for drawing skeleton
    HAND_CONNECTIONS = [
        # Thumb
        (0, 1), (1, 2), (2, 3), (3, 4),
        # Index finger
        (0, 5), (5, 6), (6, 7), (7, 8),
        # Middle finger
        (0, 9), (9, 10), (10, 11), (11, 12),
        # Ring finger
        (0, 13), (13, 14), (14, 15), (15, 16),
        # Pinky
        (0, 17), (17, 18), (18, 19), (19, 20),
        # Palm
        (5, 9), (9, 13), (13, 17)
    ]
    
    def __init__(self, window_name: str = "Hand Gesture Control", 
                 show_landmarks: bool = True,
                 show_connections: bool = True,
                 show_gesture_info: bool = True,
                 show_confidence: bool = True,
                 show_motion_trail: bool = False):
        """
        Initialize visualizer.
        
        Args:
            window_name: Name of the display window
            show_landmarks: Show hand landmarks
            show_connections: Show connections between landmarks
            show_gesture_info: Show gesture recognition info
            show_confidence: Show confidence bars
            show_motion_trail: Show motion trail for hand movement
        """
        self.window_name = window_name
        self.show_landmarks = show_landmarks
        self.show_connections = show_connections
        self.show_gesture_info = show_gesture_info
        self.show_confidence = show_confidence
        self.show_motion_trail = show_motion_trail
        
        # Motion trail for visualization
        self.motion_trail = []
        self.max_trail_length = 20
        
        # FPS calculation
        self.fps_counter = 0
        self.fps_time = time.time()
        self.current_fps = 0
        
        # Window settings
        self.window_created = False
        
        logger.info("Visualizer initialized")
    
    def create_window(self):
        """Create display window."""
        if not self.window_created:
            cv2.namedWindow(self.window_name, cv2.WINDOW_AUTOSIZE)
            self.window_created = True
    
    def draw_frame(self, frame: np.ndarray, 
                   hands_data: List[HandData], 
                   gesture_results: List[GestureResult],
                   additional_info: Dict = None) -> np.ndarray:
        """
        Draw complete visualization on frame.
        
        Args:
            frame: Input BGR frame
            hands_data: List of detected hands
            gesture_results: List of gesture recognition results
            additional_info: Additional information to display
            
        Returns:
            np.ndarray: Annotated frame
        """
        # Make a copy to avoid modifying original
        annotated_frame = frame.copy()
        
        # Draw hand landmarks and connections
        if hands_data:
            for i, hand_data in enumerate(hands_data):
                gesture_result = gesture_results[i] if i < len(gesture_results) else None
                self._draw_hand(annotated_frame, hand_data, gesture_result)
        
        # Draw UI elements
        self._draw_ui_overlay(annotated_frame, gesture_results, additional_info)
        
        # Update FPS
        self._update_fps()
        
        return annotated_frame
    
    def _draw_hand(self, frame: np.ndarray, hand_data: HandData, gesture_result: Optional[GestureResult]):
        """Draw hand landmarks, connections, and gesture info."""
        frame_height, frame_width = frame.shape[:2]
        
        # Convert landmarks to pixel coordinates
        landmark_points = []
        for landmark in hand_data.landmarks:
            x = int(landmark.x * frame_width)
            y = int(landmark.y * frame_height)
            landmark_points.append((x, y))
        
        # Draw connections
        if self.show_connections:
            self._draw_hand_connections(frame, landmark_points)
        
        # Draw landmarks
        if self.show_landmarks:
            self._draw_hand_landmarks(frame, landmark_points, hand_data)
        
        # Draw hand center and motion trail
        if gesture_result:
            hand_center_pixel = (
                int(gesture_result.hand_center[0] * frame_width),
                int(gesture_result.hand_center[1] * frame_height)
            )
            
            # Draw hand center
            cv2.circle(frame, hand_center_pixel, 8, self.COLORS['hand_center'], -1)
            
            # Update and draw motion trail
            if self.show_motion_trail:
                self._update_motion_trail(hand_center_pixel)
                self._draw_motion_trail(frame)
            
            # Draw gesture-specific visualizations
            self._draw_gesture_overlay(frame, gesture_result, landmark_points)
    
    def _draw_hand_connections(self, frame: np.ndarray, landmark_points: List[Tuple[int, int]]):
        """Draw connections between hand landmarks."""
        for start_idx, end_idx in self.HAND_CONNECTIONS:
            if start_idx < len(landmark_points) and end_idx < len(landmark_points):
                start_point = landmark_points[start_idx]
                end_point = landmark_points[end_idx]
                cv2.line(frame, start_point, end_point, self.COLORS['connection'], 2)
    
    def _draw_hand_landmarks(self, frame: np.ndarray, landmark_points: List[Tuple[int, int]], hand_data: HandData):
        """Draw hand landmarks with different styles for different parts."""
        # Draw regular landmarks
        for i, point in enumerate(landmark_points):
            if i in [4, 8, 12, 16, 20]:  # Finger tips
                cv2.circle(frame, point, 6, self.COLORS['landmark'], -1)
                cv2.circle(frame, point, 8, (255, 255, 255), 1)
            else:
                cv2.circle(frame, point, 4, self.COLORS['landmark'], -1)
        
        # Draw handedness label
        wrist_point = landmark_points[0]
        cv2.putText(frame, hand_data.handedness, 
                   (wrist_point[0] - 30, wrist_point[1] - 20),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, self.COLORS['text'], 1)
    
    def _draw_gesture_overlay(self, frame: np.ndarray, gesture_result: GestureResult, landmark_points: List[Tuple[int, int]]):
        """Draw gesture-specific overlays."""
        # Draw gesture-specific visualizations
        if gesture_result.gesture == GestureType.PINCH:
            # Draw line between thumb and index for pinch
            thumb_tip = landmark_points[4]
            index_tip = landmark_points[8]
            cv2.line(frame, thumb_tip, index_tip, (0, 255, 255), 3)
        
        elif gesture_result.gesture == GestureType.OK_SIGN:
            # Draw circle for OK sign
            thumb_tip = landmark_points[4]
            index_tip = landmark_points[8]
            center = ((thumb_tip[0] + index_tip[0]) // 2, (thumb_tip[1] + index_tip[1]) // 2)
            radius = int(np.sqrt((thumb_tip[0] - index_tip[0])**2 + (thumb_tip[1] - index_tip[1])**2) / 2)
            cv2.circle(frame, center, radius, (0, 255, 255), 2)
        
        elif gesture_result.gesture in [GestureType.SWIPE_LEFT, GestureType.SWIPE_RIGHT, 
                                       GestureType.SWIPE_UP, GestureType.SWIPE_DOWN]:
            # Draw arrow for swipe gestures
            self._draw_swipe_arrow(frame, gesture_result.gesture, gesture_result.hand_center)
    
    def _draw_swipe_arrow(self, frame: np.ndarray, gesture: GestureType, hand_center: Tuple[float, float]):
        """Draw directional arrow for swipe gestures."""
        frame_height, frame_width = frame.shape[:2]
        center_x = int(hand_center[0] * frame_width)
        center_y = int(hand_center[1] * frame_height)
        
        arrow_length = 50
        arrow_directions = {
            GestureType.SWIPE_LEFT: (-arrow_length, 0),
            GestureType.SWIPE_RIGHT: (arrow_length, 0),
            GestureType.SWIPE_UP: (0, -arrow_length),
            GestureType.SWIPE_DOWN: (0, arrow_length)
        }
        
        if gesture in arrow_directions:
            dx, dy = arrow_directions[gesture]
            end_point = (center_x + dx, center_y + dy)
            
            # Draw arrow line
            cv2.arrowedLine(frame, (center_x, center_y), end_point, 
                           (0, 255, 255), 4, tipLength=0.3)
    
    def _update_motion_trail(self, hand_center: Tuple[int, int]):
        """Update motion trail for hand movement."""
        self.motion_trail.append(hand_center)
        
        # Keep only recent points
        if len(self.motion_trail) > self.max_trail_length:
            self.motion_trail.pop(0)
    
    def _draw_motion_trail(self, frame: np.ndarray):
        """Draw motion trail."""
        if len(self.motion_trail) < 2:
            return
        
        # Draw trail with fading effect
        for i in range(1, len(self.motion_trail)):
            # Calculate alpha based on recency
            alpha = i / len(self.motion_trail)
            thickness = int(alpha * 4) + 1
            
            cv2.line(frame, self.motion_trail[i-1], self.motion_trail[i], 
                    self.COLORS['motion_trail'], thickness)
    
    def _draw_ui_overlay(self, frame: np.ndarray, gesture_results: List[GestureResult], additional_info: Dict = None):
        """Draw UI overlay with gesture info and system status."""
        frame_height, frame_width = frame.shape[:2]
        
        # Draw gesture information panel
        if self.show_gesture_info and gesture_results:
            self._draw_gesture_panel(frame, gesture_results)
        
        # Draw FPS counter
        fps_text = f"FPS: {self.current_fps:.1f}"
        cv2.putText(frame, fps_text, (frame_width - 100, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, self.COLORS['text'], 1)
        
        # Draw additional info if provided
        if additional_info:
            self._draw_additional_info(frame, additional_info)
        
        # Draw instructions
        self._draw_instructions(frame)
    
    def _draw_gesture_panel(self, frame: np.ndarray, gesture_results: List[GestureResult]):
        """Draw gesture information panel."""
        frame_height, frame_width = frame.shape[:2]
        panel_width = 300
        panel_height = 150
        panel_x = 10
        panel_y = 10
        
        # Draw panel background
        overlay = frame.copy()
        cv2.rectangle(overlay, (panel_x, panel_y), 
                     (panel_x + panel_width, panel_y + panel_height),
                     (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
        
        # Draw panel border
        cv2.rectangle(frame, (panel_x, panel_y), 
                     (panel_x + panel_width, panel_y + panel_height),
                     self.COLORS['gesture_box'], 2)
        
        # Draw gesture information
        y_offset = panel_y + 25
        for i, result in enumerate(gesture_results[:2]):  # Show max 2 hands
            # Gesture name
            gesture_name = result.gesture.value.replace('_', ' ').title()
            text = f"Hand {i+1}: {gesture_name}"
            cv2.putText(frame, text, (panel_x + 10, y_offset),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, self.COLORS['text'], 1)
            
            # Confidence bar
            if self.show_confidence:
                bar_width = int(result.confidence * 200)
                bar_y = y_offset + 10
                cv2.rectangle(frame, (panel_x + 10, bar_y), 
                             (panel_x + 10 + bar_width, bar_y + 10),
                             self.COLORS['confidence_bar'], -1)
                
                # Confidence text
                conf_text = f"{result.confidence:.2f}"
                cv2.putText(frame, conf_text, (panel_x + 220, y_offset),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, self.COLORS['text'], 1)
            
            y_offset += 60
    
    def _draw_additional_info(self, frame: np.ndarray, info: Dict):
        """Draw additional system information."""
        frame_height, frame_width = frame.shape[:2]
        
        y_start = frame_height - 100
        for i, (key, value) in enumerate(info.items()):
            text = f"{key}: {value}"
            cv2.putText(frame, text, (10, y_start + i * 20),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, self.COLORS['text'], 1)
    
    def _draw_instructions(self, frame: np.ndarray):
        """Draw basic usage instructions."""
        frame_height, frame_width = frame.shape[:2]
        
        instructions = [
            "ESC: Exit",
            "SPACE: Toggle pause",
            "H: Toggle help"
        ]
        
        for i, instruction in enumerate(instructions):
            cv2.putText(frame, instruction, (frame_width - 150, frame_height - 60 + i * 20),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, self.COLORS['text'], 1)
    
    def _update_fps(self):
        """Update FPS calculation."""
        self.fps_counter += 1
        current_time = time.time()
        
        if current_time - self.fps_time >= 1.0:
            self.current_fps = self.fps_counter / (current_time - self.fps_time)
            self.fps_counter = 0
            self.fps_time = current_time
    
    def display_frame(self, frame: np.ndarray) -> int:
        """
        Display frame in window.
        
        Args:
            frame: Frame to display
            
        Returns:
            int: Key pressed by user (-1 if no key)
        """
        if not self.window_created:
            self.create_window()
        
        cv2.imshow(self.window_name, frame)
        return cv2.waitKey(1) & 0xFF
    
    def close(self):
        """Close visualization window and cleanup."""
        if self.window_created:
            cv2.destroyWindow(self.window_name)
            self.window_created = False
        logger.info("Visualizer closed")
    
    # Configuration methods
    def toggle_landmarks(self):
        """Toggle landmark display."""
        self.show_landmarks = not self.show_landmarks
    
    def toggle_connections(self):
        """Toggle connection display."""
        self.show_connections = not self.show_connections
    
    def toggle_gesture_info(self):
        """Toggle gesture info display."""
        self.show_gesture_info = not self.show_gesture_info
    
    def toggle_motion_trail(self):
        """Toggle motion trail display."""
        self.show_motion_trail = not self.show_motion_trail
        if not self.show_motion_trail:
            self.motion_trail.clear()
    
    def set_colors(self, color_dict: Dict[str, Tuple[int, int, int]]):
        """Set custom colors for visualization elements."""
        for key, color in color_dict.items():
            if key in self.COLORS:
                self.COLORS[key] = color


if __name__ == "__main__":
    # Test the visualizer
    print("Testing Visualizer...")
    
    visualizer = Visualizer()
    
    # Create test frame
    test_frame = np.zeros((480, 640, 3), dtype=np.uint8)
    
    # Draw test UI
    annotated_frame = visualizer.draw_frame(test_frame, [], [], {"Test": "Value"})
    
    print(f"Test frame shape: {annotated_frame.shape}")
    print("Visualizer test completed!")
    
    visualizer.close()