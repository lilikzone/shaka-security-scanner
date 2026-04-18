#!/usr/bin/env python
"""Setup script for Web Penetration Testing Framework."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="shaka-security-scanner",
    version="0.1.0",
    author="Shaka Security Scanner Team",
    author_email="team@example.com",
    description="A comprehensive security testing tool for web applications with AWS Bedrock AI integration",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/shaka-security-scanner",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Information Technology",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Security",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development :: Testing",
    ],
    python_requires=">=3.9",
    install_requires=[
        "httpx>=0.25.0",
        "beautifulsoup4>=4.12.0",
        "cryptography>=41.0.0",
        "click>=8.1.0",
        "rich>=13.0.0",
        "jinja2>=3.1.0",
        "reportlab>=4.0.0",
        "pytest>=7.0.0",
        "hypothesis>=6.0.0",
        "pytest-asyncio>=0.21.0",
        "boto3>=1.28.0",
        "pyyaml>=6.0",
        "python-multipart>=0.0.6",
        "aiofiles>=23.0.0",
        "pydantic>=2.0.0",
    ],
    extras_require={
        "dev": [
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "mypy>=1.0.0",
            "ruff>=0.0.280",
        ],
        "docs": [
            "sphinx>=7.0.0",
            "sphinx-rtd-theme>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "shaka-scan=shaka_security_scanner.cli:main",
        ],
    },
)