"""
Mock test suite that doesn't require actual Jira/Confluence credentials.

This test validates the custom fields functionality using mocks instead
of actual API calls, making it suitable for running in environments
without credentials.
"""

import unittest
import sys
import os
from unittest.mock import patch, MagicMock, call
import uuid

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

from mcp_atlassian.jira import JiraFetcher


class TestMockCustomFields(unittest.TestCase):
    """Test custom fields functionality with mocks."""

    def setUp(self):
        """
        Set up the test environment with mock environment variables.
        This allows tests to run without actual credentials.
        """
        # Mock environment variables needed by JiraFetcher
        self.env_patcher = patch.dict('os.environ', {
            'JIRA_URL': 'https://YOUR-CREDENTIALS@YOUR-DOMAIN/field")
        
        print("✅ get_custom_fields works with mock API")

    def test_get_field_contexts(self):
        """Test getting field contexts with mocks."""
        # Mock the API response - fix the format to match the code
        self.mock_api_request.return_value = {
            "values": [
                {
                    "id": "10000",
                    "name": "Global Context",
                    "type": "CustomFieldContext"
                }
            ]
        }
        
        # Call the method
        contexts = self.jira_fetcher.get_field_contexts("customfield_10057")
        
        # Verify results
        self.assertEqual(len(contexts), 1)
        self.assertEqual(contexts[0]['id'], "10000")
        self.assertEqual(contexts[0]['name'], "Global Context")
        
        # Verify the API was called correctly
        self.mock_api_request.assert_called_once_with("GET", "/field/customfield_10057/context")
        
        print("✅ get_field_contexts works with mock API")
        
    def test_create_global_field_context(self):
        """Test creating a global context for a custom field."""
        # Mock the API response
        self.mock_api_request.return_value = {
            "id": "10001",
            "name": "Test Global Context",
            "description": "Test Description",
            "isGlobalContext": True,
            "isAnyIssueType": True
        }
        
        # Call the method
        result = self.jira_fetcher.create_global_field_context(
            field_id="customfield_10057",
            name="Test Global Context",
            description="Test Description"
        )
        
        # Verify results
        self.assertEqual(result["id"], "10001")
        self.assertEqual(result["name"], "Test Global Context")
        
        # Verify the API was called correctly
        self.mock_api_request.assert_called_once_with(
            "POST", 
            "/field/customfield_10057/context", 
            {
                "name": "Test Global Context",
                "description": "Test Description",
                "projectIds": [],
                "issueTypeIds": []
            }
        )
        
        print("✅ create_global_field_context works with mock API")
        
    def test_assign_field_to_projects(self):
        """Test assigning a field to projects."""
        # Mock the API response
        self.mock_api_request.return_value = {
            "success": True
        }
        
        # Call the method with no project IDs (global assignment)
        result = self.jira_fetcher.assign_field_to_projects(
            field_id="customfield_10057",
            context_id="10001"
        )
        
        # Verify results
        self.assertEqual(result["success"], True)
        
        # Verify the API was called correctly
        self.mock_api_request.assert_called_once_with(
            "PUT", 
            "/field/customfield_10057/context/10001/project", 
            {
                "projectIds": []
            }
        )
        
        print("✅ assign_field_to_projects works with mock API (global)")
        
        # Reset the mock
        self.mock_api_request.reset_mock()
        
        # Call the method with specific project IDs
        project_ids = ["10100", "10101"]
        result = self.jira_fetcher.assign_field_to_projects(
            field_id="customfield_10057",
            context_id="10001",
            project_ids=project_ids
        )
        
        # Verify the API was called correctly with project IDs
        self.mock_api_request.assert_called_once_with(
            "PUT", 
            "/field/customfield_10057/context/10001/project", 
            {
                "projectIds": project_ids
            }
        )
        
        print("✅ assign_field_to_projects works with mock API (specific projects)")
        
    def test_set_custom_fields_as_global(self):
        """Test setting custom fields as global."""
        # Set up mock responses for each API call in the method
        def mock_api_side_effect(*args, **kwargs):
            method, endpoint = args[0], args[1]
            
            if method == "GET" and "/field/customfield_10057/context" in endpoint:
                return {"values": []} # No existing contexts for name field
            elif method == "GET" and "/field/customfield_10058/context" in endpoint:
                return {"values": [{"id": "20000", "name": "Existing Dept Context"}]} # Existing context for dept field
            elif method == "POST" and "/field/customfield_10057/context" in endpoint:
                return {"id": "10001", "name": "Global Name Field Context"}
            elif method == "PUT" and "/field/customfield_10057/context/10001/project" in endpoint:
                return {"success": True}
            elif method == "PUT" and "/field/customfield_10058/context/20000/project" in endpoint:
                return {"success": True}
            
            # Fallback for unexpected calls
            return {"success": False, "error": f"Unexpected call: {method} {endpoint}"}
        
        # Configure the mock to use our side effect function
        self.mock_api_request.side_effect = mock_api_side_effect
        
        # Call the method
        result = self.jira_fetcher.set_custom_fields_as_global()
        
        # Verify results
        self.assertTrue(result["name_field"]["success"])
        self.assertEqual(result["name_field"]["field_id"], "customfield_10057")
        self.assertEqual(result["name_field"]["context_id"], "10001")
        
        self.assertTrue(result["dept_field"]["success"])
        self.assertEqual(result["dept_field"]["field_id"], "customfield_10058")
        self.assertEqual(result["dept_field"]["context_id"], "20000")
        
        # Verify the expected API calls were made
        expected_calls = [
            call("GET", "/field/customfield_10057/context"),
            call("POST", "/field/customfield_10057/context", {
                "name": "Global Name Field Context",
                "description": "Context for Name field that applies to all projects and issue types",
                "projectIds": [],
                "issueTypeIds": []
            }),
            call("PUT", "/field/customfield_10057/context/10001/project", {"projectIds": []}),
            call("GET", "/field/customfield_10058/context"),
            call("PUT", "/field/customfield_10058/context/20000/project", {"projectIds": []})
        ]
        
        self.mock_api_request.assert_has_calls(expected_calls, any_order=False)
        
        # Verify the cache was cleared
        self.assertEqual(self.jira_fetcher._custom_fields_cache, {})
        
        print("✅ set_custom_fields_as_global works with mock API")

    def test_create_issue_with_unavailable_fields(self):
        """Test issue creation with unavailable custom fields."""
        # Set up internal cache to indicate fields are not available
        self.jira_fetcher._custom_fields_cache = {
            "TEST": (False, False)  # Neither name nor dept field available
        }
        
        # Mock the _make_api_request method to return a successful issue creation
        self.mock_api_request.return_value = {
            "key": "TEST-123"
        }
        
        # Mock jira.issue for get_issue
        issue_mock = {
            "key": "TEST-123",
            "fields": {
                "summary": f"Test Issue {self.test_id}",
                "issuetype": {"name": "Task"},
                "status": {"name": "To Do"},
                "created": "2023-04-19T12:00:00.000+0000",
                "priority": {"name": "Medium"}
            }
        }
        
        self.jira_mock.issue.return_value = issue_mock
        
        # Call create_issue with custom fields that should be ignored due to cache
        result = self.jira_fetcher.create_issue(
            project_key="TEST",
            summary=f"Test Issue {self.test_id}",
            name="trigger",
            dept="DevOps-MCP"
        )
        
        # Verify results
        self.assertEqual(result["key"], "TEST-123")
        
        # Verify the API was called correctly
        api_call_args = self.mock_api_request.call_args[0]
        self.assertEqual(api_call_args[0], "POST")
        self.assertEqual(api_call_args[1], "/issue")
        
        # Verify custom_fields_used reflects unavailable fields
        self.assertIn("custom_fields_used", result)
        self.assertFalse(result["custom_fields_used"]["name"])
        self.assertFalse(result["custom_fields_used"]["dept"])
        
        print("✅ create_issue correctly handles unavailable custom fields")
        
        return result
    
    def test_create_issue_field_error_retry(self):
        """Test issue creation with field error that requires retry."""
        # Reset cache to default state
        self.jira_fetcher._custom_fields_cache = {}
        
        # Configure mock to fail on first call then succeed on retry
        def mock_api_side_effect(*args, **kwargs):
            method, endpoint = args[0], args[1]
            
            if method == "POST" and endpoint == "/issue":
                # Get the data for validation
                data = args[2] if len(args) > 2 else kwargs.get('data', {})
                fields = data.get('fields', {})
                
                # First call will have custom fields and should raise error
                if self.jira_fetcher.NAME_FIELD_ID in fields:
                    error_msg = "API request failed: 400 - Field 'customfield_10057' cannot be set. It is not on the appropriate screen, or unknown."
                    raise ValueError(error_msg)
                
                # Retry without custom fields will succeed
                return {"key": "TEST-123"}
                
        # Configure the mock
        self.mock_api_request.side_effect = mock_api_side_effect
        
        # Mock jira.issue for get_issue
        issue_mock = {
            "key": "TEST-123",
            "fields": {
                "summary": "Test Issue with Retry",
                "issuetype": {"name": "Task"},
                "status": {"name": "To Do"},
                "created": "2023-04-19T12:00:00.000+0000",
                "priority": {"name": "Medium"}
            }
        }
        
        self.jira_mock.issue.return_value = issue_mock
        
        # Call create_issue - first attempt will fail, but it should retry and succeed
        result = self.jira_fetcher.create_issue(
            project_key="TEST",
            summary="Test Issue with Retry",
            name="trigger",
            dept="DevOps-MCP"
        )
        
        # Verify the result
        self.assertEqual(result["key"], "TEST-123")
        
        # Verify cache was updated to mark fields as unavailable
        self.assertIn("TEST", self.jira_fetcher._custom_fields_cache)
        has_name, has_dept = self.jira_fetcher._custom_fields_cache["TEST"]
        self.assertFalse(has_name)  # Should be marked as unavailable
        
        print("✅ create_issue correctly retries after field error")
    
    def test_validate_required_fields(self):
        """Test validation of required name and dept fields."""
        # Test missing name field
        with self.assertRaises(ValueError) as context:
            self.jira_fetcher.create_issue(
                project_key="TEST",
                summary="Test without name",
                dept="DevOps-MCP"
                # name is deliberately omitted
            )
        
        self.assertIn("'name' is a required parameter", str(context.exception))
        
        # Test missing dept field
        with self.assertRaises(ValueError) as context:
            self.jira_fetcher.create_issue(
                project_key="TEST",
                summary="Test without dept",
                name="trigger"
                # dept is deliberately omitted
            )
        
        self.assertIn("'dept' is a required parameter", str(context.exception))
        
        # Similar tests for create_epic
        with self.assertRaises(ValueError) as context:
            self.jira_fetcher.create_epic(
                project_key="TEST",
                summary="Epic without name",
                dept="DevOps-MCP"
                # name is deliberately omitted
            )
        
        self.assertIn("'name' is a required parameter", str(context.exception))
        
        print("✅ create_issue and create_epic correctly validate required fields")
    
    def test_has_custom_fields_for_project(self):
        """Test the cache mechanism for tracking field availability."""
        # Initially cache should be empty
        self.jira_fetcher._custom_fields_cache = {}
        
        # First call should assume fields are available
        has_name, has_dept = self.jira_fetcher._has_custom_fields_for_project("TEST")
        self.assertTrue(has_name)
        self.assertTrue(has_dept)
        
        # Cache should be updated
        self.assertIn("TEST", self.jira_fetcher._custom_fields_cache)
        self.assertEqual(self.jira_fetcher._custom_fields_cache["TEST"], (True, True))
        
        # Update cache to mark name field as unavailable
        self.jira_fetcher._update_custom_fields_cache("TEST", self.jira_fetcher.NAME_FIELD_ID, False)
        
        # Now check again
        has_name, has_dept = self.jira_fetcher._has_custom_fields_for_project("TEST")
        self.assertFalse(has_name)  # Should now be False
        self.assertTrue(has_dept)   # Should still be True
        
        print("✅ _has_custom_fields_for_project correctly tracks field availability")
    
    def test_create_epic_with_unavailable_fields(self):
        """Test epic creation with unavailable custom fields."""
        # Set up internal cache to indicate fields are not available
        self.jira_fetcher._custom_fields_cache = {
            "TEST": (False, False)  # Neither name nor dept field available
        }
        
        # Mock the _make_api_request method to return a successful epic creation
        self.mock_api_request.return_value = {
            "key": "TEST-456"
        }
        
        # Mock jira.issue for get_issue
        epic_mock = {
            "key": "TEST-456",
            "fields": {
                "summary": "Test Epic",
                "issuetype": {"name": "Epic"},
                "status": {"name": "To Do"},
                "created": "2023-04-19T12:00:00.000+0000",
                "priority": {"name": "Medium"},
                "customfield_10011": "Test Epic Name"  # Epic Name field
            }
        }
        
        self.jira_mock.issue.return_value = epic_mock
        
        # Call create_epic with custom fields that should be ignored due to cache
        result = self.jira_fetcher.create_epic(
            project_key="TEST",
            summary="Test Epic",
            epic_name="Test Epic Name",
            name="trigger",
            dept="DevOps-MCP"
        )
        
        # Verify results
        self.assertEqual(result["key"], "TEST-456")
        
        # Verify the API was called correctly
        api_call_args = self.mock_api_request.call_args[0]
        self.assertEqual(api_call_args[0], "POST")
        self.assertEqual(api_call_args[1], "/issue")
        
        # Verify custom_fields_used reflects unavailable fields
        self.assertIn("custom_fields_used", result)
        self.assertFalse(result["custom_fields_used"]["name"])
        self.assertFalse(result["custom_fields_used"]["dept"])
        
        print("✅ create_epic correctly handles unavailable custom fields")


if __name__ == '__main__':
    unittest.main()