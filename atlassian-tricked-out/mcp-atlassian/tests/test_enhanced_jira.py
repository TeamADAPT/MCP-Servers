"""Tests for enhanced Jira functionality.

These tests verify that the enhanced Jira functionality works correctly,
including custom field management, bulk operations, and improved API handling.
"""

import json
import unittest
from unittest.mock import patch, MagicMock

from src.mcp_atlassian.enhanced_jira import EnhancedJiraManager
from src.mcp_atlassian.config import JiraConfig
from src.mcp_atlassian.feature_flags import enable_feature, disable_feature, is_enabled
from src.mcp_atlassian.constants import STATUS_SUCCESS, STATUS_ERROR


class TestEnhancedJiraManager(unittest.TestCase):
    """Test the EnhancedJiraManager class functionality."""
    
    def setUp(self):
        """Set up the test environment."""
        # Mock JiraConfig
        self.config = JiraConfig(
            url="https://example.atlassian.net",
            username="test-user",
            api_token="test-token"
        )
        
        # Enable the feature flag
        enable_feature("enhanced_jira")
        
        # Patch the session
        self.session_patch = patch('atlassian.Jira._session')
        self.mock_session = self.session_patch.start()
        
        # Create mock response
        self.mock_response = MagicMock()
        self.mock_response.status_code = 200
        self.mock_response.text = '{}'
        self.mock_response.json.return_value = {}
        
        # Set up methods on the mock session
        self.mock_session.get.return_value = self.mock_response
        self.mock_session.post.return_value = self.mock_response
        self.mock_session.put.return_value = self.mock_response
        self.mock_session.delete.return_value = self.mock_response
        
        # Create manager with mocked session
        self.manager = EnhancedJiraManager()
        self.manager.jira._session = self.mock_session
    
    def tearDown(self):
        """Clean up after tests."""
        # Stop the session patch
        self.session_patch.stop()
        
        # Disable the feature flag
        disable_feature("enhanced_jira")
    
    def test_is_field_available_in_project(self):
        """Test checking if a field is available in a project."""
        # Mock the get_field_contexts method
        self.manager.get_field_contexts = MagicMock()
        self.manager.get_field_contexts.return_value = {
            "status": STATUS_SUCCESS,
            "contexts": [{
                "contextScope": {
                    "projects": ["TEST"]
                }
            }]
        }
        
        # Test field availability
        self.assertTrue(self.manager.is_field_available_in_project("TEST", "customfield_10000"))
        self.manager.get_field_contexts.assert_called_once()
    
    def test_get_custom_fields(self):
        """Test retrieving custom fields."""
        # Set up mock response
        custom_fields_response = [
            {"id": "customfield_10000", "name": "Name", "custom": True},
            {"id": "customfield_10001", "name": "Department", "custom": True}
        ]
        self.mock_response.json.return_value = custom_fields_response
        
        # Call the method
        result = self.manager.get_custom_fields()
        
        # Verify the result
        self.assertEqual(result["status"], STATUS_SUCCESS)
        self.assertEqual(len(result["custom_fields"]), 2)
        self.assertEqual(result["count"], 2)
        self.mock_session.get.assert_called_once()
    
    def test_create_global_field_context(self):
        """Test creating a global field context."""
        # Set up mock response
        context_response = {"id": "context1", "name": "Global Test"}
        self.mock_response.json.return_value = context_response
        
        # Call the method
        result = self.manager.create_global_field_context("customfield_10000", "Global Test")
        
        # Verify the result
        self.assertEqual(result, context_response)
        self.mock_session.post.assert_called_once()
    
    def test_assign_field_to_projects(self):
        """Test assigning a field to projects."""
        # Call the method
        result = self.manager.assign_field_to_projects(
            "customfield_10000", "context1", ["TEST1", "TEST2"]
        )
        
        # Verify the result
        self.assertEqual(result["status"], STATUS_SUCCESS)
        self.assertEqual(result["field_id"], "customfield_10000")
        self.assertEqual(result["context_id"], "context1")
        self.assertEqual(result["projects"], ["TEST1", "TEST2"])
        self.mock_session.put.assert_called_once()
    
    def test_set_custom_fields_as_global(self):
        """Test setting all custom fields as global."""
        # Set up mock responses
        custom_fields_response = [
            {"id": "customfield_10000", "name": "Name", "custom": True},
            {"id": "customfield_10001", "name": "Department", "custom": True}
        ]
        contexts_response = {"values": []}
        context_creation_response = {"id": "context1", "name": "Global Name"}
        
        # Sequence of responses
        self.mock_session.get.side_effect = [
            MagicMock(json=lambda: custom_fields_response, status_code=200),
            MagicMock(json=lambda: contexts_response, status_code=200),
            MagicMock(json=lambda: contexts_response, status_code=200)
        ]
        self.mock_session.post.return_value = MagicMock(
            json=lambda: context_creation_response, status_code=200
        )
        
        # Call the method
        result = self.manager.set_custom_fields_as_global()
        
        # Verify the result
        self.assertEqual(result["status"], STATUS_SUCCESS)
        self.assertEqual(result["total"], 2)
        self.assertEqual(result["success_count"], 2)
        self.assertEqual(len(result["successes"]), 2)
        self.assertEqual(len(result["failures"]), 0)
    
    def test_create_issue_with_custom_fields(self):
        """Test creating an issue with custom fields."""
        # Set up mock response
        issue_response = {
            "key": "TEST-123",
            "id": "10000",
            "fields": {
                "summary": "Test Issue",
                "issuetype": {"name": "Task"},
                "status": {"name": "To Do"}
            }
        }
        self.mock_response.json.return_value = issue_response
        
        # Mock field availability check
        self.manager.is_field_available_in_project = MagicMock(return_value=True)
        
        # Call the method
        result = self.manager.create_issue_with_custom_fields(
            project_key="TEST",
            summary="Test Issue",
            custom_fields={
                "customfield_10000": "Test Name",
                "customfield_10001": "Test Department"
            }
        )
        
        # Verify the result
        self.assertEqual(result["status"], STATUS_SUCCESS)
        self.assertEqual(result["key"], "TEST-123")
        self.assertEqual(result["summary"], "Test Issue")
        self.assertEqual(result["type"], "Task")
        self.assertEqual(result["status"], "To Do")
        self.mock_session.post.assert_called_once()


# Add test for server_enhanced_jira.py functions
class TestServerEnhancedJira(unittest.TestCase):
    """Test the server_enhanced_jira.py module functionality."""
    
    def setUp(self):
        """Set up the test environment."""
        # Enable the feature flag
        enable_feature("enhanced_jira")
        
        # Patch functions
        self.get_enhanced_jira_manager_patch = patch('src.mcp_atlassian.server_enhanced_jira.get_enhanced_jira_manager')
        self.mock_get_manager = self.get_enhanced_jira_manager_patch.start()
        
        # Create mock manager
        self.mock_manager = MagicMock()
        self.mock_get_manager.return_value = self.mock_manager
    
    def tearDown(self):
        """Clean up after tests."""
        # Stop patches
        self.get_enhanced_jira_manager_patch.stop()
        
        # Disable the feature flag
        disable_feature("enhanced_jira")
    
    def test_get_enhanced_jira_available(self):
        """Test checking if enhanced Jira is available."""
        from src.mcp_atlassian.server_enhanced_jira import get_enhanced_jira_available
        
        # Test when enabled
        result = get_enhanced_jira_available()
        self.assertTrue(result)
        
        # Test when disabled
        disable_feature("enhanced_jira")
        result = get_enhanced_jira_available()
        self.assertFalse(result)
        
        # Re-enable for other tests
        enable_feature("enhanced_jira")
    
    def test_get_enhanced_jira_tools(self):
        """Test getting enhanced Jira tools."""
        from src.mcp_atlassian.server_enhanced_jira import get_enhanced_jira_tools
        
        # Test when enabled
        tools = get_enhanced_jira_tools()
        self.assertGreater(len(tools), 0)
        
        # Test when disabled
        disable_feature("enhanced_jira")
        tools = get_enhanced_jira_tools()
        self.assertEqual(len(tools), 0)
        
        # Re-enable for other tests
        enable_feature("enhanced_jira")
    
    def test_handle_enhanced_jira_tool_call(self):
        """Test handling enhanced Jira tool calls."""
        from src.mcp_atlassian.server_enhanced_jira import handle_enhanced_jira_tool_call
        
        # Mock manager methods
        self.mock_manager.get_custom_fields.return_value = {
            "status": STATUS_SUCCESS,
            "custom_fields": [
                {"id": "customfield_10000", "name": "Name"}
            ],
            "count": 1
        }
        
        # Test successful tool call
        result = handle_enhanced_jira_tool_call("jira_get_custom_fields", {})
        self.assertEqual(result["status"], STATUS_SUCCESS)
        self.assertEqual(len(result["custom_fields"]), 1)
        self.assertEqual(result["count"], 1)
        
        # Test unknown tool
        result = handle_enhanced_jira_tool_call("jira_unknown_tool", {})
        self.assertEqual(result["status"], STATUS_ERROR)
        
        # Test when disabled
        disable_feature("enhanced_jira")
        result = handle_enhanced_jira_tool_call("jira_get_custom_fields", {})
        self.assertEqual(result["status"], STATUS_ERROR)
        
        # Re-enable for other tests
        enable_feature("enhanced_jira")


if __name__ == '__main__':
    unittest.main()