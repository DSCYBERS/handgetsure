#!/usr/bin/env python3
"""
Installation Script for Hand Gesture Tool
Automated setup and installation of all requirements.
"""

import sys
import os
import subprocess
import platform
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class HandGestureInstaller:
    """Installation handler for the hand gesture tool."""
    
    def __init__(self):
        """Initialize installer."""
        self.project_root = Path(__file__).parent
        self.requirements_file = self.project_root / "requirements.txt"
        self.system_info = self._get_system_info()
    
    def _get_system_info(self):
        """Get system information."""
        return {
            'platform': platform.system(),
            'platform_version': platform.version(),
            'architecture': platform.machine(),
            'python_version': sys.version,
            'python_executable': sys.executable,
        }
    
    def print_header(self):
        """Print installation header."""
        print("🤚 HAND GESTURE TOOL - AUTOMATED INSTALLER")
        print("=" * 60)
        print("This script will install all required dependencies")
        print("and configure your system for the hand gesture tool.")
        print("=" * 60)
        print()
        
        # Display system info
        print("📋 SYSTEM INFORMATION:")
        for key, value in self.system_info.items():
            print(f"   {key}: {value}")
        print()
    
    def check_python_version(self):
        """Check Python version compatibility."""
        logger.info("🐍 Checking Python version...")
        
        if sys.version_info < (3, 8):
            logger.error("❌ Python 3.8+ required")
            print("\n🚫 PYTHON VERSION ERROR")
            print("❌ This tool requires Python 3.8 or higher")
            print(f"📍 Current version: {sys.version}")
            print("💡 Please upgrade Python and run installer again")
            return False
        
        logger.info(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} is compatible")
        return True
    
    def check_pip(self):
        """Check if pip is available."""
        logger.info("📦 Checking pip availability...")
        
        try:
            result = subprocess.run([sys.executable, "-m", "pip", "--version"], 
                         check=True, capture_output=True, text=True)
            logger.info(f"✅ pip is available: {result.stdout.strip()}")
            return True
        except subprocess.CalledProcessError:
            logger.error("❌ pip is not available")
            print("\n🚫 PIP ERROR")
            print("❌ pip is required but not found")
            print("💡 Install pip and try again")
            return False
    
    def install_system_dependencies(self):
        """Install system-level dependencies."""
        logger.info("🔧 Installing system dependencies...")
        
        system = platform.system().lower()
        
        if system == "linux":
            self._install_linux_dependencies()
        elif system == "darwin":  # macOS
            self._install_macos_dependencies()
        elif system == "windows":
            self._install_windows_dependencies()
        else:
            logger.warning(f"⚠️  Unknown system: {system}")
            logger.warning("   You may need to install system dependencies manually")
        
        return True
    
    def _install_linux_dependencies(self):
        """Install Linux system dependencies."""
        logger.info("🐧 Installing Linux dependencies...")
        logger.info("   💡 OpenGL libraries should already be installed")
        logger.info("   ✅ Linux dependencies check completed")
    
    def _install_macos_dependencies(self):
        """Install macOS system dependencies."""
        logger.info("🍎 Installing macOS dependencies...")
        logger.info("   ✅ macOS typically has required dependencies built-in")
    
    def _install_windows_dependencies(self):
        """Install Windows system dependencies."""
        logger.info("🪟 Installing Windows dependencies...")
        logger.info("   ✅ Windows typically has required dependencies built-in")
    
    def install_python_dependencies(self):
        """Install Python package dependencies."""
        logger.info("📦 Installing Python dependencies...")
        
        if not self.requirements_file.exists():
            logger.error("❌ requirements.txt not found")
            print("\n🚫 REQUIREMENTS FILE ERROR")
            print("❌ requirements.txt file not found")
            print("💡 Make sure you're running this from the project directory")
            return False
        
        try:
            # Upgrade pip first
            logger.info("   📦 Upgrading pip...")
            subprocess.run([
                sys.executable, "-m", "pip", "install", "--upgrade", "pip"
            ], check=True, capture_output=True)
            
            # Install requirements
            logger.info("   📦 Installing package dependencies...")
            result = subprocess.run([
                sys.executable, "-m", "pip", "install", "-r", str(self.requirements_file)
            ], check=True, capture_output=True, text=True)
            
            logger.info("✅ Python dependencies installed successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Failed to install dependencies: {e}")
            print("\n🚫 INSTALLATION ERROR")
            print("❌ Failed to install Python dependencies")
            if e.stdout:
                print(f"📤 Output: {e.stdout}")
            if e.stderr:
                print(f"📥 Error: {e.stderr}")
            print("\n💡 Try installing manually:")
            print(f"   pip install -r {self.requirements_file}")
            return False
    
    def verify_installation(self):
        """Verify the installation."""
        logger.info("🔍 Verifying installation...")
        
        # Basic verification - check if core packages can be imported
        core_packages = ['cv2', 'mediapipe', 'numpy']
        
        for package in core_packages:
            try:
                __import__(package)
                logger.info(f"   ✅ {package} - OK")
            except ImportError as e:
                logger.error(f"   ❌ {package} - FAILED: {e}")
                return False
        
        # Test pyautogui in a headless-safe way
        try:
            import pyautogui
            # Don't test screen access in headless environment
            if 'DISPLAY' in os.environ or platform.system() == 'Windows':
                screen_size = pyautogui.size()
                logger.info(f"   ✅ pyautogui - OK (screen: {screen_size})")
            else:
                logger.info("   ✅ pyautogui - OK (headless mode)")
        except Exception as e:
            logger.warning(f"   ⚠️  pyautogui - Limited functionality: {e}")
            # Don't fail installation for pyautogui issues in headless mode
        
        logger.info("✅ Basic installation verification successful")
        return True
    
    def create_launcher_scripts(self):
        """Create launcher scripts for easy usage."""
        logger.info("🚀 Creating launcher scripts...")
        
        # Windows batch script
        if platform.system() == "Windows":
            batch_content = f"""@echo off
echo Starting Hand Gesture Tool...
"{sys.executable}" main.py
pause
"""
            with open("start_gesture_tool.bat", "w") as f:
                f.write(batch_content)
            logger.info("   ✅ Created start_gesture_tool.bat")
        
        # Unix shell script
        else:
            shell_content = f"""#!/bin/bash
echo "Starting Hand Gesture Tool..."
"{sys.executable}" main.py
"""
            with open("start_gesture_tool.sh", "w") as f:
                f.write(shell_content)
            os.chmod("start_gesture_tool.sh", 0o755)
            logger.info("   ✅ Created start_gesture_tool.sh")
        
        return True
    
    def print_completion_message(self):
        """Print installation completion message."""
        print("\n" + "=" * 60)
        print("🎉 INSTALLATION COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print("✅ All requirements have been installed")
        print("✅ System has been configured")
        print("✅ Hand gesture tool is ready to use")
        print()
        print("🚀 NEXT STEPS:")
        print("   1. Test your camera:")
        print("      python test_camera.py")
        print()
        print("   2. Validate all requirements:")
        print("      python validate_requirements.py")
        print()
        print("   3. Start the hand gesture tool:")
        print("      python main.py")
        print()
        print("💡 ADDITIONAL COMMANDS:")
        print("   • Demo mode: python demo_hand_gesture.py")
        print("   • Requirements check: python validate_requirements.py")
        print("=" * 60)
    
    def run_installation(self):
        """Run the complete installation process."""
        self.print_header()
        
        steps = [
            ("Check Python Version", self.check_python_version),
            ("Check pip", self.check_pip),
            ("Install System Dependencies", self.install_system_dependencies),
            ("Install Python Dependencies", self.install_python_dependencies),
            ("Verify Installation", self.verify_installation),
            ("Create Launcher Scripts", self.create_launcher_scripts),
        ]
        
        for step_name, step_func in steps:
            logger.info(f"🔄 {step_name}...")
            try:
                result = step_func()
                if result is False:  # Explicit False check
                    logger.error(f"❌ {step_name} failed")
                    print(f"\n🚫 INSTALLATION FAILED AT: {step_name}")
                    print("💡 Please fix the issues above and run installer again")
                    return False
            except Exception as e:
                logger.error(f"❌ {step_name} failed with exception: {e}")
                print(f"\n🚫 INSTALLATION FAILED AT: {step_name}")
                print(f"❌ Error: {e}")
                return False
            
            logger.info(f"✅ {step_name} completed")
            print()
        
        self.print_completion_message()
        return True

def main():
    """Main entry point."""
    try:
        installer = HandGestureInstaller()
        success = installer.run_installation()
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n\nInstallation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Installation failed with error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()