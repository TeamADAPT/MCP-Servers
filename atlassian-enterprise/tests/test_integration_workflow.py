"""
Integration test suite for Atlassian MCP that tests the full workflow
of creating and linking issues across Jira and Confluence.

This test verifies:
1. Custom fields work across both services
2. Epic > Story > Subtask hierarchy can be created
3. Confluence pages can be linked to Jira issues
4. Name and Dept custom fields are properly handled throughout
"""

import unittest
import sys
import os
import uuid
import json
import time

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

from mcp_atlassian.jira import JiraFetcher
from mcp_atlassian.confluence import ConfluenceFetcher

# Constants for tests
TEST_NAME = "trigger"
TEST_DEPT = "DevOps-MCP"
TEST_PROJECT_KEY = "MCP"  # Use existing MCP project
TEST_CONFLUENCE_SPACE = "DS"  # DevOps Space


class TestIntegrationWorkflow(unittest.TestCase):
    """End-to-end tests for Jira and Confluence integration with custom fields."""

    def setUp(self):
        """Set up test environment with fresh Jira and Confluence connections."""
        self.jira_fetcher = JiraFetcher()
        self.confluence_fetcher = ConfluenceFetcher()
        
        # Generate a unique test ID to avoid collisions
        self.test_id = uuid.uuid4().hex[:8]
        
        # Clear the custom fields cache
        self.jira_fetcher._custom_fields_cache = {}

    def test_full_workflow(self):
        """
        Test the complete workflow:
        1. Create an Epic in Jira
        2. Create a Story linked to the Epic
        3. Create a Subtask for the Story
        4. Create a Confluence page
        5. Add a comment to the Jira issue with the Confluence page link
        """
        # Step 1: Create an Epic
        epic_summary = f"Integration Test Epic {self.test_id}"
        epic_result = self.jira_fetcher.create_epic(
            project_key=TEST_PROJECT_KEY,
            summary=epic_summary,
            description="Testing full integration workflow with custom fields",
            epic_name=f"Test Epic {self.test_id}",
            name=TEST_NAME,
            dept=TEST_DEPT
        )
        
        # Verify the Epic was created
        self.assertIsInstance(epic_result, dict)
        self.assertIn('key', epic_result)
        epic_key = epic_result['key']
        print(f"✅ Created Epic {epic_key}: {epic_summary}")
        
        # Verify custom fields were used
        self.assertIn('custom_fields_used', epic_result)
        self.assertTrue(epic_result['custom_fields_used']['name'])
        self.assertTrue(epic_result['custom_fields_used']['dept'])
        
        # Step 2: Create a Story linked to the Epic
        story_summary = f"Integration Test Story {self.test_id}"
        story_result = self.jira_fetcher.create_issue(
            project_key=TEST_PROJECT_KEY,
            summary=story_summary,
            description="Story for testing integration workflow",
            issue_type="Story",
            epic_link=epic_key,
            name=TEST_NAME,
            dept=TEST_DEPT
        )
        
        # Verify the Story was created
        self.assertIsInstance(story_result, dict)
        self.assertIn('key', story_result)
        story_key = story_result['key']
        print(f"✅ Created Story {story_key} linked to Epic {epic_key}")
        
        # Step 3: Create a Subtask for the Story
        subtask_summary = f"Integration Test Subtask {self.test_id}"
        subtask_result = self.jira_fetcher.create_issue(
            project_key=TEST_PROJECT_KEY,
            summary=subtask_summary,
            description="Subtask for testing integration workflow",
            issue_type="Subtask",
            parent_key=story_key,
            name=TEST_NAME,
            dept=TEST_DEPT
        )
        
        # Verify the Subtask was created
        self.assertIsInstance(subtask_result, dict)
        self.assertIn('key', subtask_result)
        subtask_key = subtask_result['key']
        print(f"✅ Created Subtask {subtask_key} for Story {story_key}")
        
        # Step 4: Create a Confluence page
        page_title = f"Integration Test Page {self.test_id}"
        page_content = f"""
# Integration Test Page

This page is linked to:
- Epic: [{epic_key}]
- Story: [{story_key}]
- Subtask: [{subtask_key}]

## Custom Fields
- Name: {TEST_NAME}
- Dept: {TEST_DEPT}

## Test Details
- Test ID: {self.test_id}
- Created: {time.strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        page_result = self.confluence_fetcher.create_page(
            space_key=TEST_CONFLUENCE_SPACE,
            title=page_title,
            content=page_content
        )
        
        # Verify the page was created
        self.assertIsInstance(page_result, dict)
        self.assertIn('id', page_result)
        page_id = page_result['id']
        page_url = page_result.get('_links', {}).get('base') + page_result.get('_links', {}).get('webui', '')
        print(f"✅ Created Confluence page {page_id}: {page_title}")
        
        # Step 5: Add a comment to the Jira Story with the Confluence page link
        comment = f"Documentation created: [Integration Test Page|{page_url}]"
        comment_result = self.jira_fetcher.add_comment(
            issue_key=story_key,
            comment=comment
        )
        
        # Verify the comment was added
        self.assertIsInstance(comment_result, dict)
        self.assertIn('id', comment_result)
        print(f"✅ Added comment to Story {story_key} with Confluence page link")
        
        # Step 6: Verify Epic contains the Story
        epic_issues = self.jira_fetcher.get_epic_issues(epic_key)
        self.assertIsInstance(epic_issues, dict)
        self.assertIn('issues', epic_issues)
        
        # Find the story in the epic's issues
        story_found = any(issue['key'] == story_key for issue in epic_issues['issues'])
        self.assertTrue(story_found, f"Story {story_key} should be linked to Epic {epic_key}")
        print(f"✅ Verified Epic {epic_key} contains Story {story_key}")
        
        # Step 7: Get the Jira issue and check custom fields
        issue = self.jira_fetcher.get_issue(story_key)
        self.assertEqual(issue.metadata['name'], TEST_NAME)
        self.assertEqual(issue.metadata['dept'], TEST_DEPT)
        print(f"✅ Verified custom fields in Story {story_key}: name={TEST_NAME}, dept={TEST_DEPT}")
        
        # Final verification of full structure
        print(f"""
✅ Successfully completed integration test with custom fields:
- Epic: {epic_key} - {epic_summary}
  - Story: {story_key} - {story_summary}
    - Subtask: {subtask_key} - {subtask_summary}
- Confluence: {page_id} - {page_title}
- Custom Fields: name="{TEST_NAME}", dept="{TEST_DEPT}"
""")
        
        # Return the created entities for potential use in other tests
        return {
            'epic_key': epic_key,
            'story_key': story_key,
            'subtask_key': subtask_key,
            'page_id': page_id
        }


if __name__ == '__main__':
    unittest.main()