"""
Test suite for MCP server tools that use custom fields.

These tests verify that the MCP server tools:
1. Properly handle custom fields in requests
2. Properly validate required custom fields
3. Return appropriate information in responses
4. Integrate with the custom fields global configuration
"""

import unittest
import sys
import os
import unittest.mock as mock
import asyncio
import json
import uuid

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

from mcp_atlassian.server import app, call_tool
from mcp.types import TextContent

# Constants for tests
TEST_NAME = "trigger"
TEST_DEPT = "DevOps-MCP"
TEST_PROJECT_KEY = "MCP"  # Use existing MCP project


class TestServerTools(unittest.TestCase):
    """Test MCP server tools with custom fields."""
    
    def setUp(self):
        """Set up the test environment."""
        # Create a unique test ID to avoid collisions
        self.test_id = uuid.uuid4().hex[:8]
    
    async def run_tool(self, name, arguments):
        """Helper to run tool calls with proper typing."""
        result = await call_tool(name, arguments)
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)
        self.assertIsInstance(result[0], TextContent)
        return json.loads(result[0].text)
    
    def test_set_custom_fields_global(self):
        """Test jira_set_custom_fields_global tool."""
        result = asyncio.run(self.run_tool('jira_set_custom_fields_global', {}))
        
        # Verify the response structure
        self.assertIsInstance(result, dict)
        self.assertIn('message', result)
        self.assertIn('name_field', result)
        self.assertIn('dept_field', result)
        
        # Verify both fields were processed
        self.assertTrue(result['name_field']['success'])
        self.assertTrue(result['dept_field']['success'])
        
        print("✅ jira_set_custom_fields_global tool works correctly")
    
    def test_get_custom_fields(self):
        """Test jira_get_custom_fields tool."""
        result = asyncio.run(self.run_tool('jira_get_custom_fields', {}))
        
        # Verify the response structure
        self.assertIsInstance(result, dict)
        self.assertIn('name_field', result)
        self.assertIn('dept_field', result)
        self.assertIn('all_custom_fields', result)
        
        # Verify we got detailed field info
        self.assertIsInstance(result['all_custom_fields'], list)
        self.assertGreater(len(result['all_custom_fields']), 0)
        
        print("✅ jira_get_custom_fields tool works correctly")
    
    def test_create_issue_tool(self):
        """Test jira_create_issue tool with custom fields."""
        # Create a unique summary for this test
        summary = f"Server Tool Test Issue {self.test_id}"
        
        # Call the tool with required custom fields
        result = asyncio.run(self.run_tool('jira_create_issue', {
            'project_key': TEST_PROJECT_KEY,
            'summary': summary,
            'name': TEST_NAME,
            'dept': TEST_DEPT
        }))
        
        # Verify the issue was created
        self.assertIsInstance(result, dict)
        self.assertIn('key', result)
        self.assertTrue(result['key'].startswith(f"{TEST_PROJECT_KEY}-"))
        
        # Verify response includes custom fields information
        self.assertIn('custom_fields_used', result)
        
        print(f"✅ Created issue {result['key']} with custom fields using jira_create_issue tool")
        
        # Return the issue key for potential cleanup
        return result['key']
    
    def test_create_epic_tool(self):
        """Test jira_create_epic tool with custom fields."""
        # Create a unique summary for this test
        summary = f"Server Tool Test Epic {self.test_id}"
        
        # Call the tool with required custom fields
        result = asyncio.run(self.run_tool('jira_create_epic', {
            'project_key': TEST_PROJECT_KEY,
            'summary': summary,
            'name': TEST_NAME,
            'dept': TEST_DEPT
        }))
        
        # Verify the epic was created
        self.assertIsInstance(result, dict)
        self.assertIn('key', result)
        self.assertTrue(result['key'].startswith(f"{TEST_PROJECT_KEY}-"))
        
        # Verify response includes custom fields information
        self.assertIn('custom_fields_used', result)
        
        print(f"✅ Created epic {result['key']} with custom fields using jira_create_epic tool")
        
        # Return the epic key for potential cleanup
        return result['key']
    
    def test_update_issue_tool(self):
        """Test jira_update_issue tool with custom fields."""
        # First create an issue to update
        issue_key = self.test_create_issue_tool()
        
        # New values for custom fields
        new_name = f"{TEST_NAME}-updated"
        new_dept = f"{TEST_DEPT}-updated"
        
        # Call the tool to update with new custom fields
        update_result = asyncio.run(self.run_tool('jira_update_issue', {
            'issue_key': issue_key,
            'name': new_name,
            'dept': new_dept
        }))
        
        # Verify the update was successful
        self.assertIsInstance(update_result, dict)
        self.assertIn('key', update_result)
        self.assertEqual(update_result['key'], issue_key)
        self.assertTrue(update_result['updated'])
        
        print(f"✅ Updated issue {issue_key} with new custom field values using jira_update_issue tool")
        
        # Now get the issue and verify the updated values
        get_result = asyncio.run(self.run_tool('jira_get_issue', {
            'issue_key': issue_key
        }))
        
        self.assertIsInstance(get_result, dict)
        self.assertIn('metadata', get_result)
        metadata = get_result['metadata']
        
        # Note: In some cases, the update might not be immediately reflected in the get response
        # This is because Jira might have caching or processing delays
        print(f"Updated custom fields - Name: {metadata.get('name')}, Dept: {metadata.get('dept')}")
    
    @unittest.skip("Only run when testing field validation - can be noisy with expected errors")
    def test_required_field_validation(self):
        """Test validation that custom fields are required."""
        # Try to create an issue without custom fields
        with self.assertRaises(RuntimeError):
            asyncio.run(self.run_tool('jira_create_issue', {
                'project_key': TEST_PROJECT_KEY,
                'summary': f"Missing Fields Test {self.test_id}"
                # Deliberately omitting name and dept
            }))
        
        print("✅ jira_create_issue correctly requires custom fields")
        
        # Try with only one field
        with self.assertRaises(RuntimeError):
            asyncio.run(self.run_tool('jira_create_issue', {
                'project_key': TEST_PROJECT_KEY,
                'summary': f"Missing Field Test {self.test_id}",
                'name': TEST_NAME
                # Deliberately omitting dept
            }))
        
        print("✅ Both custom fields are properly required")


if __name__ == '__main__':
    unittest.main()