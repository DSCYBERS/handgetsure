"""
Hand Detection Module using Google MediaPipe
Handles hand landmark detection and tracking for gesture recognition.
"""

import mediapipe as mp
import numpy as np
from typing import List, Optional, NamedTuple, Dict
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class HandLandmark(NamedTuple):
    """Represents a single hand landmark with normalized coordinates."""
    x: float  # Normalized x coordinate (0-1)
    y: float  # Normalized y coordinate (0-1)
    z: float  # Normalized z coordinate (depth)


class HandData(NamedTuple):
    """Represents detected hand data with landmarks and metadata."""
    landmarks: List[HandLandmark]  # 21 hand landmarks
    handedness: str  # 'Left' or 'Right'
    confidence: float  # Detection confidence (0-1)


class HandDetector:
    """MediaPipe-based hand detector for real-time landmark extraction."""
    
    # MediaPipe hand landmark indices
    LANDMARK_NAMES = {
        0: 'WRIST',
        1: 'THUMB_CMC', 2: 'THUMB_MCP', 3: 'THUMB_IP', 4: 'THUMB_TIP',
        5: 'INDEX_FINGER_MCP', 6: 'INDEX_FINGER_PIP', 7: 'INDEX_FINGER_DIP', 8: 'INDEX_FINGER_TIP',
        9: 'MIDDLE_FINGER_MCP', 10: 'MIDDLE_FINGER_PIP', 11: 'MIDDLE_FINGER_DIP', 12: 'MIDDLE_FINGER_TIP',
        13: 'RING_FINGER_MCP', 14: 'RING_FINGER_PIP', 15: 'RING_FINGER_DIP', 16: 'RING_FINGER_TIP',
        17: 'PINKY_MCP', 18: 'PINKY_PIP', 19: 'PINKY_DIP', 20: 'PINKY_TIP'
    }
    
    # Finger tip and base indices for gesture recognition
    FINGER_TIPS = [4, 8, 12, 16, 20]  # Thumb, Index, Middle, Ring, Pinky tips
    FINGER_BASES = [3, 6, 10, 14, 18]  # Corresponding finger bases (for comparison)
    
    def __init__(self, 
                 max_num_hands: int = 2,
                 min_detection_confidence: float = 0.7,
                 min_tracking_confidence: float = 0.5):
        """
        Initialize hand detector.
        
        Args:
            max_num_hands: Maximum number of hands to detect
            min_detection_confidence: Minimum confidence for hand detection
            min_tracking_confidence: Minimum confidence for hand tracking
        """
        self.max_num_hands = max_num_hands
        self.min_detection_confidence = min_detection_confidence
        self.min_tracking_confidence = min_tracking_confidence
        
        # Initialize MediaPipe components
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        
        # Initialize hand detector
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=max_num_hands,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence
        )
        
        logger.info("Hand detector initialized successfully")
    
    def detect_hands(self, rgb_frame: np.ndarray) -> List[HandData]:
        """
        Detect hands in RGB frame and extract landmarks.
        
        Args:
            rgb_frame: Input frame in RGB format
            
        Returns:
            List[HandData]: List of detected hands with landmarks
        """
        try:
            # Process frame with MediaPipe
            results = self.hands.process(rgb_frame)
            detected_hands = []
            
            if results.multi_hand_landmarks and results.multi_handedness:
                for hand_landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
                    # Extract landmark coordinates
                    landmarks = []
                    for landmark in hand_landmarks.landmark:
                        landmarks.append(HandLandmark(
                            x=landmark.x,
                            y=landmark.y,
                            z=landmark.z
                        ))
                    
                    # Get handedness info
                    hand_label = handedness.classification[0].label
                    confidence = handedness.classification[0].score
                    
                    # Create HandData object
                    hand_data = HandData(
                        landmarks=landmarks,
                        handedness=hand_label,
                        confidence=confidence
                    )
                    
                    detected_hands.append(hand_data)
            
            return detected_hands
            
        except Exception as e:
            logger.error(f"Error in hand detection: {e}")
            return []
    
    def get_landmark_positions(self, hand_data: HandData, frame_width: int, frame_height: int) -> Dict[str, tuple]:
        """
        Convert normalized landmarks to pixel coordinates.
        
        Args:
            hand_data: HandData object with landmarks
            frame_width: Frame width in pixels
            frame_height: Frame height in pixels
            
        Returns:
            Dict[str, tuple]: Dictionary mapping landmark names to (x, y) pixel coordinates
        """
        positions = {}
        
        for i, landmark in enumerate(hand_data.landmarks):
            landmark_name = self.LANDMARK_NAMES.get(i, f"LANDMARK_{i}")
            x_pixel = int(landmark.x * frame_width)
            y_pixel = int(landmark.y * frame_height)
            positions[landmark_name] = (x_pixel, y_pixel)
        
        return positions
    
    def get_finger_states(self, hand_data: HandData) -> Dict[str, bool]:
        """
        Determine if each finger is extended or folded.
        
        Args:
            hand_data: HandData object with landmarks
            
        Returns:
            Dict[str, bool]: Dictionary mapping finger names to extended state
        """
        finger_states = {}
        landmarks = hand_data.landmarks
        
        # Check thumb (different logic due to thumb orientation)
        if hand_data.handedness == "Right":
            thumb_extended = landmarks[4].x > landmarks[3].x
        else:  # Left hand
            thumb_extended = landmarks[4].x < landmarks[3].x
        
        finger_states["thumb"] = thumb_extended
        
        # Check other fingers (compare tip with base)
        finger_names = ["index", "middle", "ring", "pinky"]
        for i, finger_name in enumerate(finger_names):
            tip_idx = self.FINGER_TIPS[i + 1]  # Skip thumb
            base_idx = self.FINGER_BASES[i + 1]
            
            # Finger is extended if tip is above base (lower y value)
            finger_extended = landmarks[tip_idx].y < landmarks[base_idx].y
            finger_states[finger_name] = finger_extended
        
        return finger_states
    
    def calculate_distances(self, hand_data: HandData) -> Dict[str, float]:
        """
        Calculate distances between key landmarks for gesture recognition.
        
        Args:
            hand_data: HandData object with landmarks
            
        Returns:
            Dict[str, float]: Dictionary of calculated distances
        """
        landmarks = hand_data.landmarks
        distances = {}
        
        # Distance between thumb tip and index tip
        thumb_tip = landmarks[4]
        index_tip = landmarks[8]
        distances["thumb_index"] = np.sqrt(
            (thumb_tip.x - index_tip.x)**2 + 
            (thumb_tip.y - index_tip.y)**2
        )
        
        # Distance between index tip and middle tip
        middle_tip = landmarks[12]
        distances["index_middle"] = np.sqrt(
            (index_tip.x - middle_tip.x)**2 + 
            (index_tip.y - middle_tip.y)**2
        )
        
        # Distance from wrist to middle finger tip (hand size reference)
        wrist = landmarks[0]
        distances["wrist_middle_tip"] = np.sqrt(
            (wrist.x - middle_tip.x)**2 + 
            (wrist.y - middle_tip.y)**2
        )
        
        return distances
    
    def get_hand_center(self, hand_data: HandData) -> tuple:
        """
        Calculate the center point of the hand.
        
        Args:
            hand_data: HandData object with landmarks
            
        Returns:
            tuple: (x, y) normalized coordinates of hand center
        """
        landmarks = hand_data.landmarks
        
        # Use average of all landmark positions
        center_x = sum(landmark.x for landmark in landmarks) / len(landmarks)
        center_y = sum(landmark.y for landmark in landmarks) / len(landmarks)
        
        return (center_x, center_y)
    
    def close(self):
        """Clean up MediaPipe resources."""
        if hasattr(self, 'hands'):
            self.hands.close()
        logger.info("Hand detector closed")


# Utility functions
def visualize_landmarks(frame: np.ndarray, hand_data: HandData, frame_width: int, frame_height: int) -> np.ndarray:
    """
    Draw hand landmarks on frame for visualization.
    
    Args:
        frame: Input BGR frame
        hand_data: HandData object with landmarks
        frame_width: Frame width
        frame_height: Frame height
        
    Returns:
        np.ndarray: Frame with landmarks drawn
    """
    import cv2
    
    # Convert normalized coordinates to pixel coordinates
    landmark_points = []
    for landmark in hand_data.landmarks:
        x = int(landmark.x * frame_width)
        y = int(landmark.y * frame_height)
        landmark_points.append((x, y))
    
    # Draw landmarks
    for i, point in enumerate(landmark_points):
        cv2.circle(frame, point, 5, (0, 255, 0), -1)
        cv2.putText(frame, str(i), (point[0] + 10, point[1]), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.3, (255, 255, 255), 1)
    
    # Draw connections between landmarks
    connections = [
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
    
    for start_idx, end_idx in connections:
        if start_idx < len(landmark_points) and end_idx < len(landmark_points):
            cv2.line(frame, landmark_points[start_idx], landmark_points[end_idx], (255, 0, 0), 2)
    
    return frame


if __name__ == "__main__":
    # Test the hand detector module
    print("Testing Hand Detector Module...")
    
    try:
        # Initialize detector
        detector = HandDetector()
        
        # Test with a dummy frame
        test_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        
        # This will return empty list since no hands in black frame
        hands = detector.detect_hands(test_frame)
        print(f"Detected {len(hands)} hands in test frame")
        
        # Test landmark names
        print(f"Available landmarks: {len(detector.LANDMARK_NAMES)}")
        print("Sample landmark names:", list(detector.LANDMARK_NAMES.values())[:5])
        
        detector.close()
        print("Hand detector test completed successfully!")
        
    except Exception as e:
        print(f"Hand detector test failed: {e}")