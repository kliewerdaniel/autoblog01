#!/usr/bin/env python3
"""
Simple wrapper script to run the Agentic Blog Post Generation System.
This resolves import issues by properly setting up the Python path.
"""

import sys
import os
from pathlib import Path

# Add the current directory to Python path to enable imports
current_dir = Path(__file__).parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

# Now import and run the CLI
from agent.cli import cli

if __name__ == '__main__':
    cli()
