#!/usr/bin/env python3
"""
Validates enhanced Confluence modules individually
"""

import os
import sys
import logging
import importlib.util
from types import ModuleType

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("module_validator")

def validate_module(module_path, module_name):
    """Validate a Python module by importing it directly."""
    try:
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        if spec is None:
            logger.error(f"Failed to find module: {module_path}")
            return None
            
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        logger.info(f"Successfully imported {module_name}")
        return module
    except Exception as e:
        logger.error(f"Error importing {module_name}: {e}")
        return None

if __name__ == "__main__":
    # Path to src directory
    src_path = os.path.join(os.path.dirname(__file__), "src/mcp_atlassian")
    
    # Validate space_management.py
    space_mgmt_path = os.path.join(src_path, "space_management.py")
    space_mgmt = validate_module(space_mgmt_path, "space_management")
    
    # Validate template_management.py
    template_mgmt_path = os.path.join(src_path, "template_management.py")
    template_mgmt = validate_module(template_mgmt_path, "template_management")
    
    # Validate content_management.py
    content_mgmt_path = os.path.join(src_path, "content_management.py")
    content_mgmt = validate_module(content_mgmt_path, "content_management")
    
    # Test class initialization with mock config
    if all([space_mgmt, template_mgmt, content_mgmt]):
        class MockConfig:
            def __init__(self):
                self.url = "https://YOUR-CREDENTIALS@YOUR-DOMAIN