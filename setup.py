#!/usr/bin/env python3
"""
Setup script for Google Cloud Text-to-Speech CLI application
"""

from setuptools import setup, find_packages
import os

# Read README file
def read_readme():
    try:
        with open("README.md", "r", encoding="utf-8") as fh:
            return fh.read()
    except FileNotFoundError:
        return "Google Cloud Text-to-Speech CLI Application"

# Read requirements
def read_requirements():
    try:
        with open("requirements.txt", "r", encoding="utf-8") as fh:
            return [line.strip() for line in fh if line.strip() and not line.startswith("#")]
    except FileNotFoundError:
        return []

setup(
    name="gcp-tts-cli",
    version="1.0.0",
    author="TTS API Team",
    author_email="tts-api@company.com",
    description="Google Cloud Text-to-Speech CLI Tool",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/your-org/gcp-tts-cli",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
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
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "isort>=5.12.0",
            "mypy>=1.0.0",
        ],
        "audio": [
            "pydub>=0.25.1",
            "mutagen>=1.47.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "gcp-tts=src.cli.main:cli",
            "tts-cli=src.cli.main:cli",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.yaml", "*.json", "*.md", "*.txt"],
    },
    project_urls={
        "Bug Reports": "https://github.com/your-org/gcp-tts-cli/issues",
        "Source": "https://github.com/your-org/gcp-tts-cli",
        "Documentation": "https://github.com/your-org/gcp-tts-cli/wiki",
    },
    keywords="google-cloud text-to-speech tts speech-synthesis cli ai voice audio",
)