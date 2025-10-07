#!/usr/bin/env python3
"""
Setup script for Hand Gesture Control System
"""

from setuptools import setup, find_packages
import os

# Read README for long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="handgetsure",
    version="1.0.0",
    author="DSCYBERS",
    author_email="contact@dscybers.com",
    description="Dynamic Gesture-Based Live System Control Using Google MediaPipe Hand Recognition",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/DSCYBERS/handgetsure",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Multimedia :: Graphics :: Capture :: Digital Camera",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Human Machine Interfaces",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Hardware :: Hardware Drivers",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.4.2",
            "black>=23.9.1",
            "flake8>=6.1.0",
            "mypy>=1.5.0",
            "coverage>=7.3.0",
        ],
        "ml": [
            "scikit-learn>=1.3.1",
            "tensorflow>=2.13.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "handgetsure=main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.json", "*.md", "*.txt"],
        "config": ["*.json"],
        "docs": ["*.md"],
    },
    keywords="gesture recognition, computer vision, mediapipe, hand tracking, automation, accessibility",
    project_urls={
        "Bug Reports": "https://github.com/DSCYBERS/handgetsure/issues",
        "Source": "https://github.com/DSCYBERS/handgetsure",
        "Documentation": "https://github.com/DSCYBERS/handgetsure/wiki",
        "Funding": "https://github.com/sponsors/DSCYBERS",
    },
)