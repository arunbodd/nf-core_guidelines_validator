"""
Setup script for nfcore_validator
"""
from setuptools import setup, find_packages

setup(
    name="nfcore_validator",
    version="0.1.0",
    description="An AI agent for validating nf-core pipeline compliance",
    author="nf-core community",
    packages=find_packages(),
    install_requires=[
        "langchain>=0.0.267",
        "openai>=0.27.0",
        "faiss-cpu>=1.7.4",
        "beautifulsoup4>=4.12.0",
        "requests>=2.28.0",
    ],
    entry_points={
        "console_scripts": [
            "nfcore-validator=nfcore_validator.cli.main:main",
        ],
    },
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
)
