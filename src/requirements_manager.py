#!/usr/bin/env python3
"""
Requirements Manager
Centralized requirements validation and management for the hand gesture tool.
"""

import sys
import os
import importlib
import logging
from typing import Dict, List, Tuple, Optional
import platform

logger = logging.getLogger(__name__)

class RequirementsManager:
    """Centralized requirements management for the hand gesture tool."""
    
    MINIMUM_PYTHON_VERSION = (3, 8)
    
    # Critical packages - tool cannot run without these
    CRITICAL_PACKAGES = {
        'cv2': {
            'pip_name': 'opencv-python>=4.8.0',
            'description': 'Computer vision library for camera and image processing'
        },
        'mediapipe': {
            'pip_name': 'mediapipe>=0.10.0',
            'description': 'Google MediaPipe for hand detection and tracking'
        },
        'numpy': {
            'pip_name': 'numpy>=1.21.0',
            'description': 'Numerical computing library'
        }
    }
    
    # Optional packages - enhance functionality but not required
    OPTIONAL_PACKAGES = {
        'pyautogui': {
            'pip_name': 'pyautogui>=0.9.50',
            'description': 'GUI automation for system control'
        },
        'PIL': {
            'pip_name': 'pillow>=10.0.0',
            'description': 'Image processing library'
        },
        'matplotlib': {
            'pip_name': 'matplotlib>=3.7.0',
            'description': 'Plotting library for visualizations'
        },
        'pynput': {
            'pip_name': 'pynput>=1.7.6',
            'description': 'Input control library'
        },
        'psutil': {
            'pip_name': 'psutil>=5.9.0',
            'description': 'System monitoring library'
        }
    }
    
    def __init__(self):
        """Initialize requirements manager."""
        self.validation_errors = []
        self.validation_warnings = []
        self.validation_passed = False
    
    def check_python_version(self) -> bool:
        """Check if Python version meets requirements."""
        current_version = sys.version_info[:2]
        
        if current_version >= self.MINIMUM_PYTHON_VERSION:
            logger.debug(f"Python version {current_version[0]}.{current_version[1]} OK")
            return True
        else:
            error = f"Python {current_version[0]}.{current_version[1]} found, but >={self.MINIMUM_PYTHON_VERSION[0]}.{self.MINIMUM_PYTHON_VERSION[1]} required"
            self.validation_errors.append(error)
            logger.error(error)
            return False
    
    def check_critical_packages(self) -> bool:
        """Check if all critical packages are available."""
        all_available = True
        
        for module_name, package_info in self.CRITICAL_PACKAGES.items():
            try:
                module = importlib.import_module(module_name)
                version = getattr(module, '__version__', 'unknown')
                logger.debug(f"Critical package {module_name} ({version}) OK")
            except ImportError:
                error = f"Critical package '{module_name}' not found - install with: pip install {package_info['pip_name']}"
                self.validation_errors.append(error)
                logger.error(error)
                all_available = False
            except Exception as e:
                error = f"Critical package '{module_name}' error: {e}"
                self.validation_errors.append(error)
                logger.error(error)
                all_available = False
        
        return all_available
    
    def check_optional_packages(self) -> List[str]:
        """Check optional packages and return list of missing ones."""
        missing_packages = []
        
        for module_name, package_info in self.OPTIONAL_PACKAGES.items():
            try:
                module = importlib.import_module(module_name)
                version = getattr(module, '__version__', 'unknown')
                logger.debug(f"Optional package {module_name} ({version}) OK")
            except ImportError:
                missing_packages.append(package_info['pip_name'])
                warning = f"Optional package '{module_name}' not found - some features may be limited"
                self.validation_warnings.append(warning)
                logger.warning(warning)
        
        return missing_packages
    
    def validate_camera_access(self) -> bool:
        """Validate camera access without initializing the full camera system."""
        try:
            import cv2
            
            # Quick test of camera availability
            for camera_index in range(3):
                cap = cv2.VideoCapture(camera_index)
                if cap.isOpened():
                    ret, frame = cap.read()
                    cap.release()
                    if ret and frame is not None:
                        logger.debug(f"Camera {camera_index} is available")
                        return True
                cap.release()
            
            error = "No working camera found - camera is required for this tool"
            self.validation_errors.append(error)
            logger.error(error)
            return False
            
        except Exception as e:
            error = f"Camera validation failed: {e}"
            self.validation_errors.append(error)
            logger.error(error)
            return False
    
    def validate_system_permissions(self) -> bool:
        """Validate system permissions for automation."""
        try:
            # Only test system permissions if we have a display environment
            if 'DISPLAY' not in os.environ and platform.system() != 'Windows':
                logger.warning("Skipping system permissions test in headless environment")
                return True
            
            import pyautogui
            
            # Test basic screen access
            screen_size = pyautogui.size()
            logger.debug(f"Screen access OK: {screen_size}")
            return True
            
        except Exception as e:
            # In headless environments, don't fail for display-related issues
            if 'DISPLAY' in str(e) and 'DISPLAY' not in os.environ:
                logger.warning(f"System permissions limited in headless mode: {e}")
                return True
            else:
                error = f"System permissions validation failed: {e}"
                self.validation_errors.append(error)
                logger.error(error)
                return False
    
    def quick_validation(self) -> bool:
        """Quick validation of critical requirements only."""
        logger.debug("Running quick requirements validation...")
        
        checks = [
            self.check_python_version(),
            self.check_critical_packages(),
        ]
        
        self.validation_passed = all(checks)
        return self.validation_passed
    
    def full_validation(self) -> bool:
        """Full validation of all requirements."""
        logger.debug("Running full requirements validation...")
        
        # Clear previous validation results
        self.validation_errors = []
        self.validation_warnings = []
        
        # Run all checks
        checks = [
            self.check_python_version(),
            self.check_critical_packages(),
            self.validate_camera_access(),
            self.validate_system_permissions(),
        ]
        
        # Check optional packages (doesn't affect validation result)
        self.check_optional_packages()
        
        self.validation_passed = all(checks)
        return self.validation_passed
    
    def get_validation_summary(self) -> Dict:
        """Get validation summary."""
        return {
            'passed': self.validation_passed,
            'errors': self.validation_errors,
            'warnings': self.validation_warnings,
            'python_version': f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            'platform': platform.system(),
        }
    
    def print_validation_errors(self):
        """Print validation errors in a user-friendly format."""
        if not self.validation_errors:
            return
        
        print("\n🚫 REQUIREMENTS NOT SATISFIED")
        print("=" * 50)
        print("❌ The following issues must be fixed:")
        
        for i, error in enumerate(self.validation_errors, 1):
            print(f"   {i}. {error}")
        
        print("\n🔧 QUICK FIX:")
        print("   pip install -r requirements.txt")
        print("\n💡 For detailed help:")
        print("   python validate_requirements.py")
        print("   python install.py")
    
    def print_missing_packages_help(self):
        """Print help for installing missing packages."""
        critical_missing = []
        optional_missing = []
        
        # Check which packages are missing
        for module_name, package_info in self.CRITICAL_PACKAGES.items():
            try:
                importlib.import_module(module_name)
            except ImportError:
                critical_missing.append(package_info['pip_name'])
        
        for module_name, package_info in self.OPTIONAL_PACKAGES.items():
            try:
                importlib.import_module(module_name)
            except ImportError:
                optional_missing.append(package_info['pip_name'])
        
        if critical_missing:
            print("\n📦 MISSING CRITICAL PACKAGES:")
            for package in critical_missing:
                print(f"   • {package}")
            print("\n🔧 Install command:")
            print(f"   pip install {' '.join(critical_missing)}")
        
        if optional_missing:
            print("\n📦 MISSING OPTIONAL PACKAGES:")
            for package in optional_missing:
                print(f"   • {package}")
            print("\n🔧 Install command (optional):")
            print(f"   pip install {' '.join(optional_missing)}")

# Global requirements manager instance
requirements_manager = RequirementsManager()

def validate_critical_requirements_only() -> bool:
    """Quick validation of only critical requirements."""
    return requirements_manager.quick_validation()

def validate_all_requirements() -> bool:
    """Full validation of all requirements."""
    return requirements_manager.full_validation()

def get_requirements_manager() -> RequirementsManager:
    """Get the global requirements manager instance."""
    return requirements_manager