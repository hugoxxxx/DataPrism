"""
Setup configuration for DataPrism
DataPrism 的设置配置
"""

from setuptools import setup, find_packages

setup(
    name="DataPrism",
    version="0.1.0",
    description="A lightweight, high-aesthetic, high-performance ExifTool GUI station",
    author="Your Name",
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=[
        "PySide6>=6.10.0",
        "piexif>=1.1.3",
        "Pillow>=11.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=8.0.0",
            "pytest-cov>=4.1.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "dataprism=main:main",
        ]
    }
)
