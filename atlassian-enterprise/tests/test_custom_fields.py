"""
Test suite for custom fields functionality in Atlassian MCP integration.

This test suite verifies:
1. Custom fields can be retrieved
2. Global contexts can be created
3. Fields can be assigned to projects
4. Error handling works when fields are unavailable
5. The caching mechanism properly tracks field availability

All tests use the MCP project with specific test values:
- name: "trigger"
- dept: "DevOps-MCP"
"""

import unittest
import sys
import os
from unittest.mock import patch, MagicMock
import json
import uuid

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

from mcp_atlassian.jira import JiraFetcher

# Constants for tests
TEST_NAME = "trigger"
TEST_DEPT = "DevOps-MCP"
TEST_PROJECT_KEY = "MCP"  # Use existing MCP project
TEST_NEW_PROJECT_KEY = f"TST{uuid.uuid4().hex[:4].upper()}"  # Generate random project key


class TestCustomFields(unittest.TestCase):
    """Test custom fields functionality."""

    def setUp(self):
        """Set up the test environment."""
        # Initialize JiraFetcher with real credentials from .env
        self.jira_fetcher = JiraFetcher()
        
        # Clear the custom fields cache before each test
        self.jira_fetcher._custom_fields_cache = {}

    def test_get_custom_fields(self):
        """Test retrieving custom fields."""
        custom_fields = self.jira_fetcher.get_custom_fields()
        
        # Verify we got a list of custom fields
        self.assertIsInstance(custom_fields, list)
        
        # Find our specific custom fields
        name_field = next((f for f in custom_fields if f.get('id') == self.jira_fetcher.NAME_FIELD_ID), None)
        dept_field = next((f for f in custom_fields if f.get('id') == self.jira_fetcher.DEPT_FIELD_ID), None)
        
        # Verify they exist
        self.assertIsNotNone(name_field, f"Name field {self.jira_fetcher.NAME_FIELD_ID} not found")
        self.assertIsNotNone(dept_field, f"Dept field {self.jira_fetcher.DEPT_FIELD_ID} not found")
        
        # Verify fields have expected attributes
        self.assertIn('name', name_field)
        self.assertIn('name', dept_field)
        
        print(f"✅ Found custom fields: {name_field.get('name')} and {dept_field.get('name')}")

    def test_get_field_contexts(self):
        """Test retrieving field contexts."""
        # Get contexts for name field
        name_contexts = self.jira_fetcher.get_field_contexts(self.jira_fetcher.NAME_FIELD_ID)
        
        # Verify we got a list of contexts (might be empty if none exist yet)
        self.assertIsInstance(name_contexts, list)
        
        print(f"✅ Retrieved {len(name_contexts)} contexts for name field")
        
        # Get contexts for dept field
        dept_contexts = self.jira_fetcher.get_field_contexts(self.jira_fetcher.DEPT_FIELD_ID)
        
        # Verify we got a list of contexts
        self.assertIsInstance(dept_contexts, list)
        
        print(f"✅ Retrieved {len(dept_contexts)} contexts for dept field")

    def test_set_custom_fields_global(self):
        """Test setting custom fields as global."""
        result = self.jira_fetcher.set_custom_fields_as_global()
        
        # Verify the operation succeeded
        self.assertIsInstance(result, dict)
        self.assertIn('name_field', result)
        self.assertIn('dept_field', result)
        
        # Verify both fields were processed
        self.assertTrue(result['name_field']['success'])
        self.assertTrue(result['dept_field']['success'])
        
        print("✅ Successfully set custom fields as global")

    def test_create_issue_with_custom_fields(self):
        """Test creating an issue with custom fields."""
        # Create a unique summary for this test
        summary = f"Test Custom Fields {uuid.uuid4().hex[:8]}"
        
        # Create an issue in the MCP project
        result = self.jira_fetcher.create_issue(
            project_key=TEST_PROJECT_KEY,
            summary=summary,
            description="Testing custom fields functionality",
            issue_type="Task",
            name=TEST_NAME,
            dept=TEST_DEPT,
        )
        
        # Verify the issue was created successfully
        self.assertIsInstance(result, dict)
        self.assertIn('key', result)
        self.assertTrue(result['key'].startswith(f"{TEST_PROJECT_KEY}-"))
        
        # Verify custom fields were used
        self.assertIn('custom_fields_used', result)
        self.assertTrue(result['custom_fields_used']['name'])
        self.assertTrue(result['custom_fields_used']['dept'])
        
        print(f"✅ Created issue {result['key']} with custom fields")
        
        # Clean up - get the created issue key
        created_issue_key = result['key']
        
        return created_issue_key  # Return for use in other tests

    def test_create_epic_with_custom_fields(self):
        """Test creating an epic with custom fields."""
        # Create a unique summary for this test
        summary = f"Epic Test {uuid.uuid4().hex[:8]}"
        
        # Create an epic in the MCP project
        result = self.jira_fetcher.create_epic(
            project_key=TEST_PROJECT_KEY,
            summary=summary,
            description="Testing epic custom fields functionality",
            epic_name="Test Epic",
            name=TEST_NAME,
            dept=TEST_DEPT,
        )
        
        # Verify the epic was created successfully
        self.assertIsInstance(result, dict)
        self.assertIn('key', result)
        self.assertTrue(result['key'].startswith(f"{TEST_PROJECT_KEY}-"))
        
        # Verify custom fields were used
        self.assertIn('custom_fields_used', result)
        self.assertTrue(result['custom_fields_used']['name'])
        self.assertTrue(result['custom_fields_used']['dept'])
        
        print(f"✅ Created epic {result['key']} with custom fields")
        
        # Clean up - get the created epic key
        created_epic_key = result['key']
        
        return created_epic_key  # Return for use in other tests

    def test_create_linked_issues(self):
        """Test creating linked issues (epic, stories, subtasks) with custom fields."""
        # Create an epic
        epic_key = self.test_create_epic_with_custom_fields()
        
        # Create a story linked to the epic
        story_result = self.jira_fetcher.create_issue(
            project_key=TEST_PROJECT_KEY,
            summary=f"Story Test {uuid.uuid4().hex[:8]}",
            description="Testing story with custom fields",
            issue_type="Story",
            epic_link=epic_key,
            name=TEST_NAME,
            dept=TEST_DEPT,
        )
        
        # Verify the story was created and linked
        self.assertIsInstance(story_result, dict)
        self.assertIn('key', story_result)
        story_key = story_result['key']
        
        # Create a subtask for the story
        subtask_result = self.jira_fetcher.create_issue(
            project_key=TEST_PROJECT_KEY,
            summary=f"Subtask Test {uuid.uuid4().hex[:8]}",
            description="Testing subtask with custom fields",
            issue_type="Subtask",
            parent_key=story_key,
            name=TEST_NAME,
            dept=TEST_DEPT,
        )
        
        # Verify the subtask was created
        self.assertIsInstance(subtask_result, dict)
        self.assertIn('key', subtask_result)
        
        print(f"✅ Created linked issues: Epic {epic_key} → Story {story_key} → Subtask {subtask_result['key']}")
        
        # Verify the epic contains the story
        epic_issues = self.jira_fetcher.get_epic_issues(epic_key)
        self.assertIsInstance(epic_issues, dict)
        self.assertIn('issues', epic_issues)
        
        # Find the story in the epic's issues
        story_found = any(issue['key'] == story_key for issue in epic_issues['issues'])
        self.assertTrue(story_found, f"Story {story_key} should be linked to Epic {epic_key}")
        
        print(f"✅ Verified Epic {epic_key} contains Story {story_key}")

    def test_cache_mechanism(self):
        """Test the caching mechanism for custom fields availability."""
        # Create a test issue to ensure fields are available
        self.test_create_issue_with_custom_fields()
        
        # Verify cache is populated for the test project
        self.assertIn(TEST_PROJECT_KEY, self.jira_fetcher._custom_fields_cache)
        has_name, has_dept = self.jira_fetcher._custom_fields_cache[TEST_PROJECT_KEY]
        
        # Both fields should be available in the MCP project
        self.assertTrue(has_name)
        self.assertTrue(has_dept)
        
        print(f"✅ Cache correctly shows both fields available for {TEST_PROJECT_KEY}")
        
        # Test the has_custom_fields_for_project method
        has_name, has_dept = self.jira_fetcher._has_custom_fields_for_project(TEST_PROJECT_KEY)
        self.assertTrue(has_name)
        self.assertTrue(has_dept)
        
        print(f"✅ _has_custom_fields_for_project correctly returns true for both fields")

    def test_error_handling_mock(self):
        """Test error handling for unavailable custom fields using mocks."""
        # Mock API response for a field that can't be set
        with patch.object(self.jira_fetcher, '_make_api_request') as mock_api:
            # First call raises an error about the custom field
            mock_api.side_effect = [
                ValueError("API request failed: 400 - Field 'customfield_10057' cannot be set. It is not on the appropriate screen, or unknown."),
                {'key': 'TST-123'}  # Second call succeeds
            ]
            
            # Create an issue that would normally use custom fields
            result = self.jira_fetcher.create_issue(
                project_key="TST",
                summary="Test error handling",
                name=TEST_NAME,
                dept=TEST_DEPT,
            )
            
            # Verify the issue was still created
            self.assertIsInstance(result, dict)
            self.assertIn('key', result)
            
            # Verify the cache was updated to mark the field as unavailable
            self.assertIn("TST", self.jira_fetcher._custom_fields_cache)
            has_name, has_dept = self.jira_fetcher._custom_fields_cache["TST"]
            self.assertFalse(has_name)  # Name field should be marked as unavailable
            
            print("✅ Error handling correctly managed unavailable custom field")

    @unittest.skip("Only run when needed - creates a new project")
    def test_create_new_project(self):
        """Test creating a new project and setting custom fields on it."""
        # Create a new project
        project_result = self.jira_fetcher.create_project(
            key=TEST_NEW_PROJECT_KEY,
            name=f"Test Project {TEST_NEW_PROJECT_KEY}",
        )
        
        # Verify project was created
        self.assertIsInstance(project_result, dict)
        self.assertTrue(project_result['success'])
        
        print(f"✅ Created new project {TEST_NEW_PROJECT_KEY}")
        
        # Set custom fields as global to ensure they're available
        self.jira_fetcher.set_custom_fields_as_global()
        
        # Create an issue in the new project
        issue_result = self.jira_fetcher.create_issue(
            project_key=TEST_NEW_PROJECT_KEY,
            summary=f"Issue in new project {uuid.uuid4().hex[:8]}",
            name=TEST_NAME,
            dept=TEST_DEPT,
        )
        
        # Verify issue was created
        self.assertIsInstance(issue_result, dict)
        self.assertIn('key', issue_result)
        self.assertTrue(issue_result['key'].startswith(f"{TEST_NEW_PROJECT_KEY}-"))
        
        print(f"✅ Created issue {issue_result['key']} in new project")
        
        # Check if custom fields were used
        self.assertIn('custom_fields_used', issue_result)
        print(f"Custom fields used: {issue_result['custom_fields_used']}")


if __name__ == '__main__':
    unittest.main()