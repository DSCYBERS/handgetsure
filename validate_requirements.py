#!/usr/bin/env python3
"""
Requirements Validator
Comprehensive validation of all system requirements for the hand gesture tool.
"""

import sys
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def main():
    """Main entry point for requirements validation."""
    print("🔍 HAND GESTURE TOOL - REQUIREMENTS VALIDATOR")
    print("=" * 60)
    print("This utility validates all system requirements")
    print("before running the hand gesture recognition tool.")
    print("=" * 60)
    print()
    
    try:
        # Import and use the requirements manager
        from requirements_manager import get_requirements_manager
        
        manager = get_requirements_manager()
        
        # Run full validation
        logger.info("🚀 Starting comprehensive requirements validation...")
        
        try:
            success = manager.full_validation()
        except Exception as validation_error:
            # Handle validation errors gracefully
            logger.error(f"Validation process failed: {validation_error}")
            success = False
            manager.validation_errors.append(f"Validation process error: {validation_error}")
        
        # Print summary
        summary = manager.get_validation_summary()
        
        print("\n📋 VALIDATION SUMMARY")
        print("=" * 40)
        print(f"Python Version: {summary['python_version']}")
        print(f"Platform: {summary['platform']}")
        print(f"Status: {'✅ PASSED' if summary['passed'] else '❌ FAILED'}")
        
        if summary['errors']:
            print(f"\n🚫 ERRORS ({len(summary['errors'])}):")
            for i, error in enumerate(summary['errors'], 1):
                print(f"   {i}. {error}")
        
        if summary['warnings']:
            print(f"\n⚠️  WARNINGS ({len(summary['warnings'])}):")
            for i, warning in enumerate(summary['warnings'], 1):
                print(f"   {i}. {warning}")
        
        if success and not summary['errors']:
            print("\n🎉 ALL REQUIREMENTS SATISFIED!")
            print("✅ The hand gesture tool is ready to use")
            print("💡 Run 'python main.py' to start the application")
        else:
            print("\n🚫 REQUIREMENTS NOT SATISFIED")
            print("💡 Run installer: python install.py")
            print("💡 Check documentation: REQUIREMENTS.md")
        
        print("=" * 60)
        sys.exit(0 if success and not summary['errors'] else 1)
        
    except ImportError as e:
        logger.error(f"❌ Failed to import requirements manager: {e}")
        print("\n🚫 VALIDATOR ERROR")
        print("❌ Cannot import requirements validation modules")
        print("💡 Ensure you're running from the project directory")
        print("💡 Try: python install.py")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\nValidation interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Validation failed: {e}")
        print(f"\n❌ Validation failed with error: {e}")
        print("💡 Check logs for details")
        print("💡 Try: python install.py")
        sys.exit(1)

if __name__ == "__main__":
    main()