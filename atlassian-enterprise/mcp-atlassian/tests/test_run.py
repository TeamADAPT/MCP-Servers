#!/usr/bin/env python3
"""
Test script for Enhanced Confluence integration
"""

import os
import sys
import unittest
from unittest import mock

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.mcp_atlassian.server_enhanced_confluence import (
    get_enhanced_confluence_available,
    get_enhanced_confluence_tools,
    handle_enhanced_confluence_tool_call
)

# Mock the is_enabled function
@mock.patch('src.mcp_atlassian.server_enhanced_confluence.is_enabled')
def test_get_tools_count_with_all_features_enabled(mock_is_enabled):
    """Test that we get tools when features are enabled."""
    mock_is_enabled.return_value = True
    tools = get_enhanced_confluence_tools()
    print(f"Number of tools returned: {len(tools)}")
    print(f"Tool names: {[t.name for t in tools]}")
    assert len(tools) > 0, "No tools returned"

# Mock the availability function
@mock.patch.dict(os.environ, {
    "CONFLUENCE_URL": "https://YOUR-CREDENTIALS@YOUR-DOMAIN