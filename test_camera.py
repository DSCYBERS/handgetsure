#!/usr/bin/env python3
"""
Camera Test Utility
Tests camera availability and functionality before running the hand gesture tool.
"""

import cv2
import sys
import os

def test_camera():
    """Test camera availability and functionality."""
    print("🔍 CAMERA AVAILABILITY TEST")
    print("=" * 40)
    
    cameras_found = []
    
    # Test multiple camera indices
    for camera_index in range(5):  # Test cameras 0-4
        print(f"\n📹 Testing camera index {camera_index}...")
        
        try:
            cap = cv2.VideoCapture(camera_index)
            
            if cap.isOpened():
                # Try to read a frame
                ret, frame = cap.read()
                
                if ret and frame is not None:
                    height, width = frame.shape[:2]
                    print(f"   ✅ Camera {camera_index}: Working - Resolution: {width}x{height}")
                    cameras_found.append(camera_index)
                else:
                    print(f"   ⚠️  Camera {camera_index}: Opens but cannot read frames")
            else:
                print(f"   ❌ Camera {camera_index}: Cannot open")
                
            cap.release()
            
        except Exception as e:
            print(f"   ❌ Camera {camera_index}: Error - {e}")
    
    print("\n" + "=" * 40)
    
    if cameras_found:
        print(f"✅ SUCCESS: Found {len(cameras_found)} working camera(s)")
        print(f"📋 Working camera indices: {cameras_found}")
        print("\n🎉 Your system is ready for the hand gesture tool!")
        print("💡 Run 'python main.py' to start the application")
        return True
    else:
        print("❌ FAILURE: No working cameras found")
        print("\n🔧 TROUBLESHOOTING:")
        print("   • Ensure camera is connected")
        print("   • Check camera drivers are installed")
        print("   • Close other applications using the camera")
        print("   • Try reconnecting your camera")
        print("   • On Linux, check camera permissions")
        print("\n💡 Camera test commands:")
        print("   • Linux: v4l2-ctl --list-devices")
        print("   • Windows: Open Camera app")
        print("   • macOS: Open Photo Booth")
        return False

def main():
    """Main entry point."""
    print("🤚 HAND GESTURE TOOL - CAMERA TEST")
    print("=" * 50)
    print("This utility tests if your camera is working properly")
    print("before running the hand gesture recognition tool.")
    print("=" * 50)
    
    try:
        success = test_camera()
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()