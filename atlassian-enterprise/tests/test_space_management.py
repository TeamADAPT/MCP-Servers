"""
Tests for the Confluence Space Management module.
"""

import unittest
from unittest.mock import patch, MagicMock

from mcp_atlassian.space_management import ConfluenceSpaceManager
from mcp_atlassian.config import ConfluenceConfig


class TestConfluenceSpaceManager(unittest.TestCase):
    """Test cases for the ConfluenceSpaceManager class."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_config = ConfluenceConfig(
            url="https://YOUR-CREDENTIALS@YOUR-DOMAIN//example.atlassian.net/rest/api/space",
            json=None,
            params={"start": 0, "limit": 25, "type": "global", "status": "current"},
            files=None,
            auth=("test_user", "test_token"),
            headers={"Content-Type": "application/json"}
        )
        
        # Check the result
        self.assertEqual(result["results"][0]["key"], "TEST")
        self.assertEqual(result["results"][0]["name"], "Test Space")
        
    @patch('requests.request')
    def test_create_space(self, mock_request):
        """Test creating a space."""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": 456,
            "key": "NEW",
            "name": "New Space",
            "description": {"plain": {"value": "This is a new space"}}
        }
        mock_request.return_value = mock_response
        
        # Call the method
        result = self.space_manager.create_space(
            key="NEW",
            name="New Space",
            description="This is a new space"
        )
        
        # Verify the request was made correctly
        mock_request.assert_called_once_with(
            method="POST",
            url="https://YOUR-CREDENTIALS@YOUR-DOMAIN//example.atlassian.net/rest/api/space/TEST/archive",
            json=None,
            params=None,
            files=None,
            auth=("test_user", "test_token"),
            headers={"Content-Type": "application/json"}
        )
        
        # Check the result
        self.assertEqual(result["key"], "TEST")
        self.assertEqual(result["status"], "archived")
        
    @patch('requests.request')
    def test_add_space_permission(self, mock_request):
        """Test adding a space permission."""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": "123",
            "subject": {
                "type": "user",
                "identifier": "user123"
            },
            "operation": {
                "key": "read",
                "target": "space"
            }
        }
        mock_request.return_value = mock_response
        
        # Call the method
        result = self.space_manager.add_space_permission(
            space_key="TEST",
            permission="read",
            subject_type="user",
            subject_key="user123"
        )
        
        # Verify the request was made correctly
        mock_request.assert_called_once_with(
            method="POST",
            url="https://YOUR-CREDENTIALS@YOUR-DOMAIN//example.atlassian.net/rest/api/space/TEST/template",
            json=None,
            params=None,
            files=None,
            auth=("test_user", "test_token"),
            headers={"Content-Type": "application/json"}
        )
        
        # Check the result
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["name"], "Meeting Notes")
        self.assertEqual(result[0]["templateType"], "page")


if __name__ == '__main__':
    unittest.main()