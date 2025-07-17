"""
Tests for Enhanced Confluence functionality
"""

import pytest
import os
from unittest.mock import Mock, patch

from mcp_atlassian.space_management import ConfluenceSpaceManager
from mcp_atlassian.template_management import ConfluenceTemplateManager
from mcp_atlassian.content_management import ConfluenceContentManager
from mcp_atlassian.server_enhanced_confluence import (
    get_enhanced_confluence_available,
    get_enhanced_confluence_tools,
    handle_enhanced_confluence_tool_call
)


class TestEnhancedConfluenceAvailability:
    """Test enhanced Confluence availability checks."""

    def test_availability_with_missing_vars(self):
        """Test availability check with missing env vars."""
        with patch.dict(os.environ, {}, clear=True):
            assert not get_enhanced_confluence_available()

    def test_availability_with_vars(self):
        """Test availability check with env vars set."""
        with patch.dict(os.environ, {
            "CONFLUENCE_URL": "https://YOUR-CREDENTIALS@YOUR-DOMAIN