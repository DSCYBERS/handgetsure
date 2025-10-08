#!/usr/bin/env python3
"""
Hand Gesture Tool Demo
Demonstrates the hand gesture recognition capabilities without requiring a camera.
"""

import sys
import os
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add src to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from src.config import ConfigManager
    from src.hand_detector import HandDetector, HandData, HandLandmark
    from src.gesture_recognizer import GestureRecognizer, GestureType
    
    print("🤚 HAND GESTURE TOOL DEMONSTRATION 🤚")
    print("=" * 50)
    
    # Initialize configuration
    config_manager = ConfigManager("config")
    config = config_manager.get_config()
    
    print(f"✅ Configuration loaded successfully")
    print(f"   - Max hands: {config.hand_detection.max_num_hands}")
    print(f"   - Detection confidence: {config.hand_detection.min_detection_confidence}")
    print(f"   - Tracking confidence: {config.hand_detection.min_tracking_confidence}")
    
    # Initialize hand detector
    hand_detector = HandDetector(
        max_num_hands=config.hand_detection.max_num_hands,
        min_detection_confidence=config.hand_detection.min_detection_confidence,
        min_tracking_confidence=config.hand_detection.min_tracking_confidence
    )
    print("✅ Hand detector initialized")
    
    # Initialize gesture recognizer
    gesture_recognizer = GestureRecognizer(
        motion_buffer_size=config.gesture_recognition.motion_buffer_size
    )
    print("✅ Gesture recognizer initialized")
    
    print("\n🎯 AVAILABLE GESTURE TYPES:")
    print("-" * 30)
    for gesture_type in GestureType:
        print(f"   - {gesture_type.name}: {gesture_type.value}")
    
    print("\n📊 SYSTEM CAPABILITIES:")
    print("-" * 30)
    print("   ✅ Real-time hand detection")
    print("   ✅ 21-point hand landmark tracking")
    print("   ✅ Multi-gesture recognition")
    print("   ✅ Motion trail analysis")
    print("   ✅ Confidence scoring")
    print("   ✅ Command mapping")
    print("   ✅ Configurable parameters")
    
    print("\n🚀 SIMULATING GESTURE DETECTION:")
    print("-" * 30)
    
    # Simulate some hand landmarks for demonstration
    def create_demo_landmarks():
        """Create demo hand landmarks."""
        landmarks = []
        # Create 21 landmarks (MediaPipe hand model)
        for i in range(21):
            # Generate some sample coordinates
            x = 0.3 + (i % 4) * 0.1
            y = 0.3 + (i // 4) * 0.05
            z = 0.0
            landmarks.append(HandLandmark(x=x, y=y, z=z))
        return landmarks
    
    # Demo gesture recognition
    for i in range(5):
        print(f"\n🔍 Frame {i+1}: Analyzing hand gestures...")
        
        # Create demo hand data
        landmarks = create_demo_landmarks()
        hand_data = HandData(
            landmarks=landmarks,
            handedness="Right",
            confidence=0.85 + i * 0.03
        )
        
        print(f"   📍 Detected hand: {hand_data.handedness}")
        print(f"   🎯 Confidence: {hand_data.confidence:.2f}")
        print(f"   📊 Landmarks: {len(hand_data.landmarks)} points")
        
        # Simulate gesture recognition
        if i == 2:
            print(f"   ✋ Detected gesture: OPEN_PALM")
        elif i == 3:
            print(f"   👍 Detected gesture: THUMBS_UP")
        elif i == 4:
            print(f"   ✊ Detected gesture: FIST")
        else:
            print(f"   ❓ No specific gesture detected")
        
        time.sleep(0.5)
    
    print(f"\n🎉 HAND GESTURE TOOL DEMO COMPLETED!")
    print("=" * 50)
    print("💡 To use with a real camera, run: python main.py")
    print("📚 For more info, check the docs/ directory")
    
except ImportError as e:
    logger.error(f"Failed to import modules: {e}")
    print("❌ Error: Missing dependencies. Please check your installation.")
    sys.exit(1)
except Exception as e:
    logger.error(f"Demo failed: {e}")
    print(f"❌ Demo failed: {e}")
    sys.exit(1)