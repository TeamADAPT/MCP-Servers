#!/usr/bin/env python
"""Run tests for the MCP Atlassian Integration."""

import os
import sys
import pytest
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp-test")

def main():
    """Run pytest with command line arguments."""
    logger.info("Running MCP Atlassian tests...")
    
    # Add the project root to Python path
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, project_root)
    
    # Run pytest with any provided arguments
    args = sys.argv[1:] if len(sys.argv) > 1 else ["-v"]
    exit_code = pytest.main(args)
    
    if exit_code == 0:
        logger.info("All tests passed!")
    else:
        logger.error(f"Tests failed with exit code {exit_code}")
    
    return exit_code

if __name__ == "__main__":
    sys.exit(main())