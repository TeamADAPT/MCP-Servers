#!/usr/bin/env python3
"""
Focused test script for Enhanced Confluence tools
"""

import os
import sys
import json
from unittest import mock

# Add src directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

# Mock the feature flags module
sys.modules['mcp_atlassian.feature_flags'] = mock.MagicMock()
sys.modules['mcp_atlassian.feature_flags'].is_enabled.return_value = True

# Import the modules now that mocks are in place
from mcp_atlassian.space_management import ConfluenceSpaceManager
from mcp_atlassian.template_management import ConfluenceTemplateManager
from mcp_atlassian.content_management import ConfluenceContentManager

# Test the manager classes
def test_managers():
    """Test manager class init methods."""
    config = mock.MagicMock()
    config.url = "https://YOUR-CREDENTIALS@YOUR-DOMAIN