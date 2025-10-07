# Sample test file - expand with actual tests
import unittest
from src.camera import CameraManager

class TestCamera(unittest.TestCase):
    def test_camera_init(self):
        camera = CameraManager()
        self.assertIsNotNone(camera)

if __name__ == '__main__':
    unittest.main()