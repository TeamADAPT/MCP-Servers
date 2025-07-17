"""
Tests for the Confluence Content Management module.
"""

import unittest
from unittest.mock import patch, MagicMock

from mcp_atlassian.content_management import ConfluenceContentManager
from mcp_atlassian.config import ConfluenceConfig


class TestConfluenceContentManager(unittest.TestCase):
    """Test cases for the ConfluenceContentManager class."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_config = ConfluenceConfig(
            url="https://YOUR-CREDENTIALS@YOUR-DOMAIN//example.atlassian.net/rest/api/content/content123/property",
            json=None,
            params=None,
            files=None,
            auth=("test_user", "test_token"),
            headers={"Content-Type": "application/json"}
        )
        
        # Check the result
        self.assertEqual(result["results"][0]["key"], "test-property")
        self.assertEqual(result["results"][0]["value"]["data"], "test-value")
        
    @patch('requests.request')
    def test_set_content_property(self, mock_request):
        """Test setting a content property."""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": "prop456",
            "key": "new-property",
            "value": {"data": "new-value"}
        }
        mock_request.return_value = mock_response
        
        # Setup get_content_property to fail (property doesn't exist)
        self.content_manager.get_content_property = MagicMock(side_effect=ValueError("Property not found"))
        
        # Call the method
        result = self.content_manager.set_content_property(
            content_id="content123",
            property_key="new-property",
            property_value={"data": "new-value"}
        )
        
        # Verify the request was made correctly
        mock_request.assert_called_once_with(
            method="POST",
            url="https://YOUR-CREDENTIALS@YOUR-DOMAIN//example.atlassian.net/rest/api/content/content123/label",
            json=None,
            params={},
            files=None,
            auth=("test_user", "test_token"),
            headers={"Content-Type": "application/json"}
        )
        
        # Check the result
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["name"], "test-label")
        self.assertEqual(result[0]["prefix"], "global")
        
    @patch('requests.request')
    def test_add_label(self, mock_request):
        """Test adding a label to content."""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "results": [
                {
                    "id": "label456",
                    "name": "new-label",
                    "prefix": "global"
                }
            ]
        }
        mock_request.return_value = mock_response
        
        # Call the method
        result = self.content_manager.add_label(
            content_id="content123",
            label="new-label"
        )
        
        # Verify the request was made correctly
        mock_request.assert_called_once_with(
            method="POST",
            url="https://YOUR-CREDENTIALS@YOUR-DOMAIN//example.atlassian.net/rest/api/content",
            json=None,
            params={
                "start": 0,
                "limit": 25,
                "label": "search-label",
                "spaceKey": "TEST"
            },
            files=None,
            auth=("test_user", "test_token"),
            headers={"Content-Type": "application/json"}
        )
        
        # Check the result
        self.assertEqual(result["results"][0]["title"], "Content with Label")
        self.assertEqual(result["results"][0]["space"]["key"], "TEST")
        
    @patch('requests.request')
    def test_get_content_restrictions(self, mock_request):
        """Test getting content restrictions."""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "read": {
                "restrictions": {
                    "user": {
                        "results": [
                            {"name": "user123"}
                        ]
                    }
                }
            },
            "update": {
                "restrictions": {
                    "group": {
                        "results": [
                            {"name": "group456"}
                        ]
                    }
                }
            }
        }
        mock_request.return_value = mock_response
        
        # Call the method
        result = self.content_manager.get_content_restrictions("content123")
        
        # Verify the request was made correctly
        mock_request.assert_called_once_with(
            method="GET",
            url="https://YOUR-CREDENTIALS@YOUR-DOMAIN/p>"}}
        }
        
        mock_put_response = MagicMock()
        mock_put_response.status_code = 200
        mock_put_response.json.return_value = {
            "id": "content123",
            "title": "Test Page",
            "type": "page",
            "version": {"number": 2},
            "body": {"storage": {"value": "<p>Existing content</p><ac:structured-macro ac:name=\"info\"><ac:parameter ac:name=\"title\">Info Title</ac:parameter><ac:plain-text-body><![CDATA[Info Body]]></ac:plain-text-body></ac:structured-macro>"}}
        }
        
        # Configure the mock to return different responses in sequence
        mock_request.side_effect = [mock_get_response, mock_put_response]
        
        # Call the method
        result = self.content_manager.add_macro_to_page(
            content_id="content123",
            macro_key="info",
            macro_parameters={"title": "Info Title"},
            macro_body="Info Body"
        )
        
        # Verify that both requests were made correctly
        self.assertEqual(mock_request.call_count, 2)
        
        # First call: GET the content
        first_call_args = mock_request.call_args_list[0][1]
        self.assertEqual(first_call_args["method"], "GET")
        self.assertEqual(first_call_args["url"], "https://example.atlassian.net/rest/api/content/content123")
        self.assertEqual(first_call_args["params"], {"expand": "body.storage,version"})
        
        # Second call: PUT the updated content
        second_call_args = mock_request.call_args_list[1][1]
        self.assertEqual(second_call_args["method"], "PUT")
        self.assertEqual(second_call_args["url"], "https://example.atlassian.net/rest/api/content/content123")
        
        # Check that the JSON payload contains the expected data
        json_data = second_call_args["json"]
        self.assertEqual(json_data["version"]["number"], 2)  # Incremented version
        self.assertEqual(json_data["title"], "Test Page")
        self.assertTrue("<ac:structured-macro ac:name=\"info\">" in json_data["body"]["storage"]["value"])
        self.assertTrue("<ac:parameter ac:name=\"title\">Info Title</ac:parameter>" in json_data["body"]["storage"]["value"])
        
        # Check the result
        self.assertEqual(result["id"], "content123")
        self.assertEqual(result["version"]["number"], 2)


if __name__ == '__main__':
    unittest.main()