"""
Gesture Recognition Module
Implements rule-based gesture classification using hand landmark data.
"""

import numpy as np
from typing import Dict, List, Optional, NamedTuple
from enum import Enum
import logging
from .hand_detector import HandData

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GestureType(Enum):
    """Enumeration of recognized gesture types."""
    UNKNOWN = "unknown"
    OPEN_PALM = "open_palm"
    FIST = "fist"
    THUMBS_UP = "thumbs_up"
    THUMBS_DOWN = "thumbs_down"
    INDEX_POINT = "index_point"
    PEACE_SIGN = "peace_sign"
    OK_SIGN = "ok_sign"
    STOP_SIGN = "stop_sign"
    ROCK_SIGN = "rock_sign"
    SWIPE_LEFT = "swipe_left"
    SWIPE_RIGHT = "swipe_right"
    SWIPE_UP = "swipe_up"
    SWIPE_DOWN = "swipe_down"
    PINCH = "pinch"
    GRAB = "grab"


class GestureResult(NamedTuple):
    """Result of gesture recognition."""
    gesture: GestureType
    confidence: float
    hand_center: tuple
    additional_data: Dict


class GestureRecognizer:
    """Rule-based gesture recognition using hand landmarks."""
    
    def __init__(self, motion_buffer_size: int = 10):
        """
        Initialize gesture recognizer.
        
        Args:
            motion_buffer_size: Size of buffer for motion-based gestures
        """
        self.motion_buffer_size = motion_buffer_size
        self.motion_history = []  # Store recent hand positions for motion detection
        self.previous_gesture = GestureType.UNKNOWN
        self.gesture_stability_count = 0
        self.min_stability_frames = 3  # Minimum frames to confirm gesture
        
        logger.info("Gesture recognizer initialized")
    
    def recognize_gesture(self, hand_data: HandData) -> GestureResult:
        """
        Recognize gesture from hand landmark data.
        
        Args:
            hand_data: HandData object with landmarks
            
        Returns:
            GestureResult: Recognition result with gesture type and confidence
        """
        try:
            # Get finger states
            finger_states = self._get_finger_states(hand_data)
            
            # Calculate geometric features
            distances = self._calculate_distances(hand_data)
            angles = self._calculate_angles(hand_data)
            
            # Get hand center for motion tracking
            hand_center = self._get_hand_center(hand_data)
            
            # Update motion history
            self._update_motion_history(hand_center)
            
            # Recognize static gestures
            static_gesture = self._recognize_static_gesture(finger_states, distances, angles, hand_data)
            
            # Recognize motion gestures
            motion_gesture = self._recognize_motion_gesture()
            
            # Prioritize motion gestures over static ones
            if motion_gesture != GestureType.UNKNOWN:
                final_gesture = motion_gesture
                confidence = 0.8
            else:
                final_gesture = static_gesture
                confidence = self._calculate_confidence(static_gesture, finger_states, distances)
            
            # Apply gesture stability filtering
            final_gesture = self._apply_stability_filter(final_gesture)
            
            return GestureResult(
                gesture=final_gesture,
                confidence=confidence,
                hand_center=hand_center,
                additional_data={
                    'finger_states': finger_states,
                    'distances': distances,
                    'angles': angles,
                    'handedness': hand_data.handedness
                }
            )
            
        except Exception as e:
            logger.error(f"Error in gesture recognition: {e}")
            return GestureResult(
                gesture=GestureType.UNKNOWN,
                confidence=0.0,
                hand_center=(0, 0),
                additional_data={}
            )
    
    def _get_finger_states(self, hand_data: HandData) -> Dict[str, bool]:
        """Get finger extension states."""
        landmarks = hand_data.landmarks
        finger_states = {}
        
        # Thumb (different logic based on handedness)
        if hand_data.handedness == "Right":
            thumb_extended = landmarks[4].x > landmarks[3].x
        else:  # Left hand
            thumb_extended = landmarks[4].x < landmarks[3].x
        
        finger_states["thumb"] = thumb_extended
        
        # Other fingers (tip above base = extended)
        finger_indices = {
            "index": (8, 6),
            "middle": (12, 10),
            "ring": (16, 14),
            "pinky": (20, 18)
        }
        
        for finger_name, (tip_idx, base_idx) in finger_indices.items():
            finger_extended = landmarks[tip_idx].y < landmarks[base_idx].y
            finger_states[finger_name] = finger_extended
        
        return finger_states
    
    def _calculate_distances(self, hand_data: HandData) -> Dict[str, float]:
        """Calculate key distances between landmarks."""
        landmarks = hand_data.landmarks
        distances = {}
        
        # Thumb-index distance (for pinch detection)
        thumb_tip = landmarks[4]
        index_tip = landmarks[8]
        distances["thumb_index"] = np.sqrt(
            (thumb_tip.x - index_tip.x)**2 + (thumb_tip.y - index_tip.y)**2
        )
        
        # Index-middle distance
        middle_tip = landmarks[12]
        distances["index_middle"] = np.sqrt(
            (index_tip.x - middle_tip.x)**2 + (index_tip.y - middle_tip.y)**2
        )
        
        # Wrist-middle distance (hand size reference)
        wrist = landmarks[0]
        distances["wrist_middle"] = np.sqrt(
            (wrist.x - middle_tip.x)**2 + (wrist.y - middle_tip.y)**2
        )
        
        return distances
    
    def _calculate_angles(self, hand_data: HandData) -> Dict[str, float]:
        """Calculate key angles for gesture recognition."""
        landmarks = hand_data.landmarks
        angles = {}
        
        # Thumb angle relative to palm
        wrist = landmarks[0]
        thumb_base = landmarks[2]
        thumb_tip = landmarks[4]
        
        # Vector from wrist to thumb base
        v1 = np.array([thumb_base.x - wrist.x, thumb_base.y - wrist.y])
        # Vector from thumb base to tip
        v2 = np.array([thumb_tip.x - thumb_base.x, thumb_tip.y - thumb_base.y])
        
        # Calculate angle between vectors
        if np.linalg.norm(v1) > 0 and np.linalg.norm(v2) > 0:
            cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
            angles["thumb_angle"] = np.arccos(np.clip(cos_angle, -1, 1))
        else:
            angles["thumb_angle"] = 0
        
        return angles
    
    def _get_hand_center(self, hand_data: HandData) -> tuple:
        """Calculate hand center point."""
        landmarks = hand_data.landmarks
        center_x = sum(landmark.x for landmark in landmarks) / len(landmarks)
        center_y = sum(landmark.y for landmark in landmarks) / len(landmarks)
        return (center_x, center_y)
    
    def _update_motion_history(self, hand_center: tuple):
        """Update motion history for swipe detection."""
        self.motion_history.append(hand_center)
        
        # Keep only recent positions
        if len(self.motion_history) > self.motion_buffer_size:
            self.motion_history.pop(0)
    
    def _recognize_static_gesture(self, finger_states: Dict[str, bool], 
                                 distances: Dict[str, float], 
                                 angles: Dict[str, float],
                                 hand_data: HandData) -> GestureType:
        """Recognize static hand gestures."""
        
        # Count extended fingers
        extended_fingers = sum(finger_states.values())
        
        # Open palm - all fingers extended
        if extended_fingers == 5:
            return GestureType.OPEN_PALM
        
        # Fist - no fingers extended
        if extended_fingers == 0:
            return GestureType.FIST
        
        # Thumbs up - only thumb extended
        if finger_states["thumb"] and extended_fingers == 1:
            return GestureType.THUMBS_UP
        
        # Index pointing - only index extended
        if finger_states["index"] and extended_fingers == 1:
            return GestureType.INDEX_POINT
        
        # Peace sign - index and middle extended
        if (finger_states["index"] and finger_states["middle"] and 
            extended_fingers == 2):
            return GestureType.PEACE_SIGN
        
        # Rock sign - index and pinky extended
        if (finger_states["index"] and finger_states["pinky"] and 
            extended_fingers == 2):
            return GestureType.ROCK_SIGN
        
        # OK sign - thumb and index close, others extended
        if (distances["thumb_index"] < 0.05 and 
            finger_states["middle"] and finger_states["ring"] and finger_states["pinky"]):
            return GestureType.OK_SIGN
        
        # Pinch - thumb and index very close
        if distances["thumb_index"] < 0.03:
            return GestureType.PINCH
        
        # Stop sign - all fingers except thumb extended
        if (finger_states["index"] and finger_states["middle"] and 
            finger_states["ring"] and finger_states["pinky"] and 
            not finger_states["thumb"]):
            return GestureType.STOP_SIGN
        
        return GestureType.UNKNOWN
    
    def _recognize_motion_gesture(self) -> GestureType:
        """Recognize motion-based gestures (swipes)."""
        if len(self.motion_history) < 5:
            return GestureType.UNKNOWN
        
        # Get first and last positions
        start_pos = self.motion_history[0]
        end_pos = self.motion_history[-1]
        
        # Calculate movement
        dx = end_pos[0] - start_pos[0]
        dy = end_pos[1] - start_pos[1]
        distance = np.sqrt(dx**2 + dy**2)
        
        # Minimum movement threshold
        if distance < 0.1:
            return GestureType.UNKNOWN
        
        # Determine swipe direction
        if abs(dx) > abs(dy):
            # Horizontal swipe
            if dx > 0:
                return GestureType.SWIPE_RIGHT
            else:
                return GestureType.SWIPE_LEFT
        else:
            # Vertical swipe
            if dy > 0:
                return GestureType.SWIPE_DOWN
            else:
                return GestureType.SWIPE_UP
    
    def _calculate_confidence(self, gesture: GestureType, 
                            finger_states: Dict[str, bool], 
                            distances: Dict[str, float]) -> float:
        """Calculate confidence score for recognized gesture."""
        if gesture == GestureType.UNKNOWN:
            return 0.0
        
        # Base confidence
        confidence = 0.7
        
        # Adjust based on gesture clarity
        if gesture in [GestureType.OPEN_PALM, GestureType.FIST]:
            # Clear all-or-nothing gestures
            confidence = 0.9
        elif gesture == GestureType.PINCH:
            # Confidence based on thumb-index distance
            distance = distances.get("thumb_index", 1.0)
            confidence = max(0.5, 1.0 - distance * 10)
        
        return confidence
    
    def _apply_stability_filter(self, current_gesture: GestureType) -> GestureType:
        """Apply temporal filtering to stabilize gesture recognition."""
        if current_gesture == self.previous_gesture:
            self.gesture_stability_count += 1
        else:
            self.gesture_stability_count = 1
            self.previous_gesture = current_gesture
        
        # Only return gesture if it's been stable for minimum frames
        if self.gesture_stability_count >= self.min_stability_frames:
            return current_gesture
        else:
            return GestureType.UNKNOWN
    
    def reset_motion_history(self):
        """Reset motion history (useful when hand disappears)."""
        self.motion_history.clear()
    
    def get_gesture_description(self, gesture: GestureType) -> str:
        """Get human-readable description of gesture."""
        descriptions = {
            GestureType.UNKNOWN: "Unknown gesture",
            GestureType.OPEN_PALM: "Open palm",
            GestureType.FIST: "Closed fist",
            GestureType.THUMBS_UP: "Thumbs up",
            GestureType.THUMBS_DOWN: "Thumbs down",
            GestureType.INDEX_POINT: "Pointing finger",
            GestureType.PEACE_SIGN: "Peace sign",
            GestureType.OK_SIGN: "OK sign",
            GestureType.STOP_SIGN: "Stop sign",
            GestureType.ROCK_SIGN: "Rock and roll",
            GestureType.SWIPE_LEFT: "Swipe left",
            GestureType.SWIPE_RIGHT: "Swipe right",
            GestureType.SWIPE_UP: "Swipe up",
            GestureType.SWIPE_DOWN: "Swipe down",
            GestureType.PINCH: "Pinch gesture",
            GestureType.GRAB: "Grab gesture"
        }
        return descriptions.get(gesture, "Unknown gesture")


if __name__ == "__main__":
    # Test the gesture recognizer
    print("Testing Gesture Recognizer...")
    
    recognizer = GestureRecognizer()
    
    # Test gesture descriptions
    for gesture in GestureType:
        description = recognizer.get_gesture_description(gesture)
        print(f"{gesture.value}: {description}")
    
    print("Gesture recognizer test completed!")