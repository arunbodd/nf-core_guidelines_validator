"""
Main entry point for nfcore_validator
"""
import sys
from .cli.main import main

if __name__ == "__main__":
    sys.exit(main())
