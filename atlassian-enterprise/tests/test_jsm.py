"""
Mock test suite for Jira Service Management integration.

This test validates the JSM functionality using mocks instead of actual API calls,
making it suitable for running in environments without credentials.
"""

import unittest
import sys
import os
from unittest.mock import patch, MagicMock, call
import uuid

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

from mcp_atlassian.jsm import JiraServiceManager


class TestMockJSM(unittest.TestCase):
    """Test JSM functionality with mocks."""

    def setUp(self):
        """
        Set up the test environment with mock environment variables.
        This allows tests to run without actual credentials.
        """
        # Mock environment variables needed by JiraServiceManager
        self.env_patcher = patch.dict('os.environ', {
            'JSM_URL': 'https://YOUR-CREDENTIALS@YOUR-DOMAIN/servicedesk", params={"start": 0, "limit": 50})
        
        print("✅ get_service_desks works with mock API")

    def test_get_request_types(self):
        """Test retrieving request types with mocks."""
        # Mock the API response
        self.mock_api_request.return_value = {
            "values": [
                {
                    "id": "20001",
                    "name": "IT Help",
                    "description": "Get IT help",
                    "helpText": "Request IT support"
                },
                {
                    "id": "20002",
                    "name": "Access Request",
                    "description": "Request access to a system",
                    "helpText": "Request access to applications"
                }
            ]
        }
        
        # Call the method
        service_desk_id = "10001"
        request_types = self.jsm_manager.get_request_types(service_desk_id)
        
        # Verify results
        self.assertEqual(len(request_types["values"]), 2)
        self.assertEqual(request_types["values"][0]["id"], "20001")
        self.assertEqual(request_types["values"][0]["name"], "IT Help")
        
        # Verify the API was called correctly
        self.mock_api_request.assert_called_once_with(
            "GET", 
            f"/servicedesk/{service_desk_id}/requesttype", 
            params={"start": 0, "limit": 50}
        )
        
        print("✅ get_request_types works with mock API")

    def test_create_customer_request(self):
        """Test creating a customer request with mocks."""
        # Mock the API response
        self.mock_api_request.return_value = {
            "issueId": "10099",
            "issueKey": "SDP-123",
            "requestId": "123456",
            "self": "https://YOUR-CREDENTIALS@YOUR-DOMAIN/request/{issue_key}/participant")
        
        print("✅ get_request_participants works with mock API")

    def test_get_request_sla(self):
        """Test retrieving request SLA information with mocks."""
        # Mock the API response
        self.mock_api_request.return_value = {
            "values": [
                {
                    "id": "3",
                    "name": "Time to resolution",
                    "ongoingCycle": {
                        "breachTime": {
                            "epochMillis": 1590019199999,
                            "iso8601": "2020-05-20T23:59:59+0000"
                        },
                        "elapsedTime": {
                            "millis": 86400000,
                            "friendly": "1 day"
                        },
                        "remainingTime": {
                            "millis": 86400000,
                            "friendly": "1 day"
                        }
                    }
                }
            ]
        }
        
        # Call the method
        issue_key = "SDP-123"
        sla = self.jsm_manager.get_request_sla(issue_key)
        
        # Verify results
        self.assertEqual(len(sla["values"]), 1)
        self.assertEqual(sla["values"][0]["name"], "Time to resolution")
        
        # Verify the API was called correctly
        self.mock_api_request.assert_called_once_with("GET", f"/request/{issue_key}/sla")
        
        print("✅ get_request_sla works with mock API")

    def test_get_queues(self):
        """Test retrieving service desk queues with mocks."""
        # Mock the API response
        self.mock_api_request.return_value = {
            "values": [
                {
                    "id": "1",
                    "name": "Unassigned",
                    "jqlQuery": "project = SDP AND resolution = Unresolved AND assignee = null"
                },
                {
                    "id": "2",
                    "name": "Assigned to Me",
                    "jqlQuery": "project = SDP AND resolution = Unresolved AND assignee = currentUser()"
                }
            ]
        }
        
        # Call the method
        service_desk_id = "10001"
        queues = self.jsm_manager.get_queues(service_desk_id)
        
        # Verify results
        self.assertEqual(len(queues["values"]), 2)
        self.assertEqual(queues["values"][0]["name"], "Unassigned")
        
        # Verify the API was called correctly
        self.mock_api_request.assert_called_once_with(
            "GET", 
            f"/servicedesk/{service_desk_id}/queue", 
            params={"start": 0, "limit": 50}
        )
        
        print("✅ get_queues works with mock API")


if __name__ == '__main__':
    unittest.main()