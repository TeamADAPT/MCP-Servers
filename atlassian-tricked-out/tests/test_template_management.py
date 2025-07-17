"""
Tests for the Confluence Template Management module.
"""

import unittest
from unittest.mock import patch, MagicMock

from mcp_atlassian.template_management import ConfluenceTemplateManager
from mcp_atlassian.config import ConfluenceConfig


class TestConfluenceTemplateManager(unittest.TestCase):
    """Test cases for the ConfluenceTemplateManager class."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_config = ConfluenceConfig(
            url="https://YOUR-CREDENTIALS@YOUR-DOMAIN//example.atlassian.net/rest/api/template",
            json=None,
            params={"start": 0, "limit": 50},
            files=None,
            auth=("test_user", "test_token"),
            headers={"Content-Type": "application/json"}
        )
        
        # Check the result
        self.assertEqual(result["results"][0]["name"], "Meeting Notes")
        self.assertEqual(result["results"][0]["templateType"], "page")
        
    @patch('requests.request')
    def test_get_blueprint_templates(self, mock_request):
        """Test getting blueprint templates."""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "results": [
                {
                    "id": "blueprint123",
                    "name": "Project Plan",
                    "templateType": "blueprint"
                }
            ]
        }
        mock_request.return_value = mock_response
        
        # Call the method
        result = self.template_manager.get_blueprint_templates()
        
        # Verify the request was made correctly
        mock_request.assert_called_once_with(
            method="GET",
            url="https://YOUR-CREDENTIALS@YOUR-DOMAIN/p>"}}
        }
        mock_request.return_value = mock_response
        
        # Call the method
        result = self.template_manager.create_template(
            space_key="TEST",
            name="New Template",
            content="<p>Template content</p>",
            template_type="page",
            description="Template description"
        )
        
        # Verify the request was made correctly
        mock_request.assert_called_once_with(
            method="POST",
            url="https://YOUR-CREDENTIALS@YOUR-DOMAIN//example.atlassian.net/rest/api/content",
            json={
                "type": "page",
                "title": "New Page",
                "space": {"key": "TEST"},
                "templateId": "template123",
                "ancestors": [{"id": "parent456"}]
            },
            params=None,
            files=None,
            auth=("test_user", "test_token"),
            headers={"Content-Type": "application/json"}
        )
        
        # Check the result
        self.assertEqual(result["title"], "New Page")
        self.assertEqual(result["space"]["key"], "TEST")
        
    @patch('requests.request')
    def test_create_page_from_blueprint(self, mock_request):
        """Test creating a page from blueprint."""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": "page789",
            "title": "Blueprint Page",
            "type": "page",
            "space": {"key": "TEST"}
        }
        mock_request.return_value = mock_response
        
        # Call the method
        result = self.template_manager.create_page_from_blueprint(
            space_key="TEST",
            title="Blueprint Page",
            blueprint_id="blueprint123",
            blueprint_parameters={"param1": "value1"}
        )
        
        # Verify the request was made correctly
        mock_request.assert_called_once_with(
            method="POST",
            url="https://example.atlassian.net/rest/api/content",
            json={
                "type": "page",
                "title": "Blueprint Page",
                "space": {"key": "TEST"},
                "metadata": {
                    "blueprint": {
                        "id": "blueprint123",
                        "parameters": {"param1": "value1"}
                    }
                }
            },
            params=None,
            files=None,
            auth=("test_user", "test_token"),
            headers={"Content-Type": "application/json"}
        )
        
        # Check the result
        self.assertEqual(result["title"], "Blueprint Page")
        self.assertEqual(result["type"], "page")


if __name__ == '__main__':
    unittest.main()