#!/usr/bin/env python3
"""
Setup script for Groq Speech SDK
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="groq-speech",
    version="1.0.0",
    author="Groq Speech SDK Contributors",
    author_email="support@groq.com",
    description="A Python SDK for Groq's speech services, providing real-time speech-to-text capabilities",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/groq/groq-speech-sdk",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Multimedia :: Sound/Audio :: Speech",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=[
        "groq>=0.4.2",
        "numpy>=1.24.3",
        "soundfile>=0.12.1",
        "websockets>=12.0",
        "asyncio-mqtt>=0.16.1",
        "python-dotenv>=1.0.0",
        # Note: pyaudio is installed separately due to system dependencies
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.800",
        ],
        "examples": [
            "matplotlib>=3.3",
            "jupyter>=1.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "groq-speech-demo=examples.basic_recognition:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords="speech recognition groq audio transcription whisper",
    project_urls={
        "Bug Reports": "https://github.com/groq/groq-speech-sdk/issues",
        "Source": "https://github.com/groq/groq-speech-sdk",
        "Documentation": "https://github.com/groq/groq-speech-sdk#readme",
    },
) 