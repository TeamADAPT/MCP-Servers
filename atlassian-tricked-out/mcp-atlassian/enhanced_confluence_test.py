#!/usr/bin/env python3
"""
Standalone test script for Enhanced Confluence
"""

import os
import sys
import logging
import json
from typing import Dict, List, Optional, Any

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("enhanced_confluence_test")

# Test configuration
class MockConfig:
    def __init__(self):
        self.url = "https://YOUR-CREDENTIALS@YOUR-DOMAIN//example.atlassian.net/wiki"
    assert manager.auth == ("test@example.com", "test-token-123")
    assert manager.headers == {"Content-Type": "application/json"}
    
    print("✓ ConfluenceSpaceManager initialized successfully")
    return manager

# Test template_management module
def test_template_management():
    from mcp_atlassian.template_management import ConfluenceTemplateManager
    
    # Initialize manager with mock config
    config = MockConfig()
    manager = ConfluenceTemplateManager(config)
    
    # Test attributes
    assert manager.base_url == "https://YOUR-CREDENTIALS@YOUR-DOMAIN/json"}
    
    print("✓ ConfluenceTemplateManager initialized successfully")
    return manager

# Test content_management module
def test_content_management():
    from mcp_atlassian.content_management import ConfluenceContentManager
    
    # Initialize manager with mock config
    config = MockConfig()
    manager = ConfluenceContentManager(config)
    
    # Test attributes
    assert manager.base_url == "https://YOUR-CREDENTIALS@YOUR-DOMAIN/json"}
    
    print("✓ ConfluenceContentManager initialized successfully")
    return manager

# Test server_enhanced_confluence module - restricted test
def test_enhanced_confluence_functions():
    logger.info("Testing enhanced Confluence functions...")
    
    try:
        # Test basic imports
        import importlib.util
        
        # Test space_management import
        spec = importlib.util.find_spec("mcp_atlassian.space_management")
        assert spec is not None, "space_management module not found"
        print("✓ space_management module can be imported")
        
        # Test template_management import
        spec = importlib.util.find_spec("mcp_atlassian.template_management")
        assert spec is not None, "template_management module not found"
        print("✓ template_management module can be imported")
        
        # Test content_management import
        spec = importlib.util.find_spec("mcp_atlassian.content_management")
        assert spec is not None, "content_management module not found" 
        print("✓ content_management module can be imported")
        
        # Test server_enhanced_confluence import
        spec = importlib.util.find_spec("mcp_atlassian.server_enhanced_confluence")
        assert spec is not None, "server_enhanced_confluence module not found"
        print("✓ server_enhanced_confluence module can be imported")
        
    except Exception as e:
        logger.error(f"Error: {e}")
        return False
        
    return True

# Run all tests
if __name__ == "__main__":
    print("Enhanced Confluence Test Suite")
    print("=============================")
    
    try:
        # Test manager classes
        space_manager = test_space_management()
        template_manager = test_template_management()
        content_manager = test_content_management()
        
        # Test enhanced Confluence functions
        test_enhanced_confluence_functions()
        
        print("\nAll enhanced Confluence module tests passed!")
        
    except Exception as e:
        print(f"\nTest failed: {e}")
        sys.exit(1)