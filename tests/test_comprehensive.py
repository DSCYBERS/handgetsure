#!/usr/bin/env python3
"""
Comprehensive test suite for the hand gesture control system.
"""

import unittest
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.hand_detector import HandLandmark, HandData
from src.gesture_recognizer import GestureType, GestureResult
from utils.helpers import normalize_coordinates, denormalize_coordinates, calculate_distance


class TestHandDetector(unittest.TestCase):
    """Test cases for hand detection functionality."""
    
    def test_hand_landmark_creation(self):
        """Test HandLandmark creation."""
        landmark = HandLandmark(x=0.5, y=0.3, z=0.1)
        self.assertEqual(landmark.x, 0.5)
        self.assertEqual(landmark.y, 0.3)
        self.assertEqual(landmark.z, 0.1)
    
    def test_hand_data_creation(self):
        """Test HandData creation."""
        landmarks = [HandLandmark(0.1, 0.2, 0.3) for _ in range(21)]
        hand_data = HandData(landmarks=landmarks, handedness="Right", confidence=0.9)
        self.assertEqual(len(hand_data.landmarks), 21)
        self.assertEqual(hand_data.handedness, "Right")
        self.assertEqual(hand_data.confidence, 0.9)


class TestGestureRecognizer(unittest.TestCase):
    """Test cases for gesture recognition."""
    
    def test_gesture_types(self):
        """Test gesture type enumeration."""
        self.assertEqual(GestureType.OPEN_PALM.value, "open_palm")
        self.assertEqual(GestureType.FIST.value, "fist")
        self.assertEqual(GestureType.THUMBS_UP.value, "thumbs_up")
    
    def test_gesture_result_creation(self):
        """Test GestureResult creation."""
        result = GestureResult(
            gesture_type=GestureType.OPEN_PALM,
            confidence=0.85,
            timestamp=1234567890
        )
        self.assertEqual(result.gesture_type, GestureType.OPEN_PALM)
        self.assertEqual(result.confidence, 0.85)


class TestUtilityFunctions(unittest.TestCase):
    """Test cases for utility functions."""
    
    def test_coordinate_normalization(self):
        """Test coordinate normalization."""
        norm_x, norm_y = normalize_coordinates(320, 240, 640, 480)
        self.assertEqual(norm_x, 0.5)
        self.assertEqual(norm_y, 0.5)
        
        norm_x, norm_y = normalize_coordinates(0, 0, 640, 480)
        self.assertEqual(norm_x, 0.0)
        self.assertEqual(norm_y, 0.0)
    
    def test_coordinate_denormalization(self):
        """Test coordinate denormalization."""
        x, y = denormalize_coordinates(0.5, 0.5, 640, 480)
        self.assertEqual(x, 320)
        self.assertEqual(y, 240)
        
        x, y = denormalize_coordinates(1.0, 1.0, 100, 100)
        self.assertEqual(x, 100)
        self.assertEqual(y, 100)
    
    def test_distance_calculation(self):
        """Test distance calculation."""
        # Test with simple 3-4-5 triangle
        dist = calculate_distance((0, 0), (3, 4))
        self.assertAlmostEqual(dist, 5.0, places=6)
        
        # Test with same point
        dist = calculate_distance((5, 5), (5, 5))
        self.assertEqual(dist, 0.0)
        
        # Test with negative coordinates
        dist = calculate_distance((-1, -1), (2, 3))
        expected = (3**2 + 4**2)**0.5
        self.assertAlmostEqual(dist, expected, places=6)


class TestProjectStructure(unittest.TestCase):
    """Test cases for project structure and configuration."""
    
    def test_required_files_exist(self):
        """Test that all required files exist."""
        required_files = [
            'main.py',
            'requirements.txt',
            'README.md',
            'setup.py',
            'LICENSE',
            '.gitignore',
            'src/__init__.py',
            'config/default_config.json'
        ]
        
        for file_path in required_files:
            self.assertTrue(os.path.exists(file_path), f"Required file missing: {file_path}")
    
    def test_src_modules_exist(self):
        """Test that all source modules exist."""
        src_modules = [
            'src/camera.py',
            'src/hand_detector.py',
            'src/gesture_recognizer.py',
            'src/command_mapper.py',
            'src/visualizer.py',
            'src/config.py'
        ]
        
        for module in src_modules:
            self.assertTrue(os.path.exists(module), f"Source module missing: {module}")


if __name__ == '__main__':
    # Create a test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTests(loader.loadTestsFromTestCase(TestHandDetector))
    suite.addTests(loader.loadTestsFromTestCase(TestGestureRecognizer))
    suite.addTests(loader.loadTestsFromTestCase(TestUtilityFunctions))
    suite.addTests(loader.loadTestsFromTestCase(TestProjectStructure))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Exit with proper code
    sys.exit(0 if result.wasSuccessful() else 1)