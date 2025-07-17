"""
Mock test suite for Jira Service Management advanced functionality.

This test validates the advanced JSM functionality using mocks instead of actual API calls,
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
from mcp_atlassian.jsm_knowledge_base import JSMKnowledgeBase
from mcp_atlassian.jsm_queue import JSMQueueManager
from mcp_atlassian.jsm_approvals import JSMApprovalManager
from mcp_atlassian.jsm_forms import JSMFormManager


class TestMockJSMAdvanced(unittest.TestCase):
    """Test advanced JSM functionality with mocks."""

    def setUp(self):
        """
        Set up the test environment with mock environment variables.
        This allows tests to run without actual credentials.
        """
        # Mock environment variables needed by JiraServiceManager
        self.env_patcher = patch.dict('os.environ', {
            'JSM_URL': 'https://YOUR-CREDENTIALS@YOUR-DOMAIN/knowledgebase", params={"start": 0, "limit": 50})
        
        print("✅ get_knowledge_bases works with mock API")
    
    def test_search_articles(self):
        """Test searching knowledge base articles with mocks."""
        # Mock the API response
        self.mock_api_request.return_value = {
            "values": [
                {
                    "id": "2001",
                    "title": "How to Reset Your Password",
                    "status": "published",
                    "lastModified": "2025-04-15T10:30:00Z"
                },
                {
                    "id": "2002",
                    "title": "Password Policy Guidelines",
                    "status": "published",
                    "lastModified": "2025-04-10T14:20:00Z"
                }
            ]
        }
        
        # Call the method
        query = "password"
        kb_id = "1001"
        articles = self.kb_service.search_articles(query=query, knowledge_base_id=kb_id)
        
        # Verify results
        self.assertEqual(len(articles["values"]), 2)
        self.assertEqual(articles["values"][0]["title"], "How to Reset Your Password")
        
        # Verify the API was called correctly
        expected_params = {
            "query": query,
            "knowledgeBaseId": kb_id,
            "start": 0,
            "limit": 50
        }
        self.mock_api_request.assert_called_once_with("GET", "/knowledgebase/article/search", params=expected_params)
        
        print("✅ search_articles works with mock API")
    
    # ===== Queue Management Tests =====
    
    def test_get_queues_with_count(self):
        """Test retrieving queues with issue counts."""
        # Mock the API response for get_queues
        self.mock_api_request.return_value = {
            "values": [
                {
                    "id": "3001",
                    "name": "Unassigned Issues",
                    "jqlQuery": "project = SD AND assignee IS EMPTY"
                },
                {
                    "id": "3002",
                    "name": "High Priority Issues",
                    "jqlQuery": "project = SD AND priority = High"
                }
            ]
        }
        
        # Prepare mock responses for get_queue_count calls
        def side_effect_func(*args, **kwargs):
            if args[0] == "GET" and args[1].endswith("/3001/issue"):
                return {"size": 5}
            elif args[0] == "GET" and args[1].endswith("/3002/issue"):
                return {"size": 3}
            return self.mock_api_request.return_value
            
        self.mock_api_request.side_effect = side_effect_func
        
        # Call the method
        service_desk_id = "4001"
        queues = self.queue_service.get_queues(service_desk_id=service_desk_id, include_count=True)
        
        # Verify results
        self.assertEqual(len(queues["values"]), 2)
        self.assertEqual(queues["values"][0]["name"], "Unassigned Issues")
        self.assertEqual(queues["values"][0]["issueCount"], 5)
        self.assertEqual(queues["values"][1]["issueCount"], 3)
        
        # Verify the API calls - should be 3 calls in total (1 for queues, 2 for counts)
        expected_calls = [
            call("GET", f"/servicedesk/{service_desk_id}/queue", params={"start": 0, "limit": 50}),
            call("GET", f"/servicedesk/{service_desk_id}/queue/3001/issue", params={"limit": 1}),
            call("GET", f"/servicedesk/{service_desk_id}/queue/3002/issue", params={"limit": 1})
        ]
        self.assertEqual(self.mock_api_request.call_count, 3)
        self.mock_api_request.assert_has_calls(expected_calls, any_order=True)
        
        print("✅ get_queues_with_count works with mock API")
    
    # ===== Approvals Tests =====
    
    def test_answer_approval_with_comment(self):
        """Test answering an approval with a comment."""
        # Mock the API response
        self.mock_api_request.return_value = {
            "id": "5001",
            "approvalStatus": "APPROVED",
            "approver": {
                "accountId": "user123",
                "displayName": "Test User"
            },
            "createdDate": "2025-05-01T09:30:00Z",
            "completedDate": "2025-05-01T10:15:00Z",
            "comment": "Approved after reviewing the documentation"
        }
        
        # Call the method
        issue_key = "SD-456"
        approval_id = "5001"
        decision = "approve"
        comment = "Approved after reviewing the documentation"
        
        result = self.approval_service.answer_approval(
            issue_id_or_key=issue_key,
            approval_id=approval_id,
            decision=decision,
            comment=comment
        )
        
        # Verify results
        self.assertEqual(result["approvalStatus"], "APPROVED")
        self.assertEqual(result["comment"], comment)
        
        # Verify the API was called correctly
        expected_data = {
            "decision": decision,
            "comment": comment
        }
        self.mock_api_request.assert_called_once_with(
            "POST", 
            f"/request/{issue_key}/approval/{approval_id}", 
            data=expected_data
        )
        
        print("✅ answer_approval_with_comment works with mock API")
    
    def test_get_approval_metrics(self):
        """Test getting approval metrics for a service desk."""
        # Mock the requests call to return a list of requests
        requests_response = {
            "values": [
                {
                    "issueKey": "SD-123",
                    "createdDate": "2025-04-01T10:00:00Z"
                },
                {
                    "issueKey": "SD-124",
                    "createdDate": "2025-04-02T11:00:00Z"
                }
            ]
        }
        
        # Mock approvals response for first request
        approvals_response1 = {
            "values": [
                {
                    "id": "a1",
                    "approvalStatus": "APPROVED",
                    "createdDate": "2025-04-01T10:30:00Z",
                    "completedDate": "2025-04-01T13:30:00Z",  # 3 hours
                    "approvalType": "LEVEL_1"
                }
            ]
        }
        
        # Mock approvals response for second request
        approvals_response2 = {
            "values": [
                {
                    "id": "a2",
                    "approvalStatus": "DECLINED",
                    "createdDate": "2025-04-02T12:00:00Z",
                    "completedDate": "2025-04-02T13:00:00Z",  # 1 hour
                    "approvalType": "LEVEL_1"
                },
                {
                    "id": "a3",
                    "approvalStatus": "PENDING",
                    "createdDate": "2025-04-03T09:00:00Z",
                    "approvalType": "LEVEL_2"
                }
            ]
        }
        
        # Set up the mock to return different values based on the call
        def side_effect_func(*args, **kwargs):
            if args[0] == "GET" and "/request" in args[1] and not args[1].endswith("/approval"):
                return requests_response
            elif args[0] == "GET" and args[1].endswith("SD-123/approval"):
                return approvals_response1
            elif args[0] == "GET" and args[1].endswith("SD-124/approval"):
                return approvals_response2
            return {}
            
        self.mock_api_request.side_effect = side_effect_func
        
        # Call the method
        service_desk_id = "sd-1001"
        metrics = self.approval_service.get_approval_metrics(service_desk_id=service_desk_id)
        
        # Verify results
        self.assertEqual(metrics["totalApprovals"], 3)
        self.assertEqual(metrics["approved"], 1)
        self.assertEqual(metrics["declined"], 1)
        self.assertEqual(metrics["pending"], 1)
        self.assertEqual(metrics["avgApprovalTimeHours"], 2)  # Average of 3 hours and 1 hour
        self.assertEqual(metrics["approvalsByType"]["LEVEL_1"], 2)
        self.assertEqual(metrics["approvalsByType"]["LEVEL_2"], 1)
        
        print("✅ get_approval_metrics works with mock API")
    
    # ===== Form Management Tests =====
    
    def test_create_custom_field(self):
        """Test creating a custom field for forms."""
        # Mock the API response
        self.mock_api_request.return_value = {
            "id": "customfield_10100",
            "name": "Priority Level",
            "description": "The priority level of the request",
            "type": "com.atlassian.jira.plugin.system.customfieldtypes:select",
            "searcherKey": "com.atlassian.jira.plugin.system.customfieldtypes:selectsearcher"
        }
        
        # Call the method
        name = "Priority Level"
        description = "The priority level of the request"
        field_type = "select"
        
        result = self.form_service.create_custom_field(
            name=name,
            description=description,
            field_type=field_type
        )
        
        # Verify results
        self.assertEqual(result["id"], "customfield_10100")
        self.assertEqual(result["name"], name)
        
        # Verify the API was called correctly
        expected_data = {
            "name": name,
            "description": description,
            "type": "com.atlassian.jira.plugin.system.customfieldtypes:select",
            "searcherKey": "com.atlassian.jira.plugin.system.customfieldtypes:selectsearcher"
        }
        self.mock_api_request.assert_called_once_with("POST", "/field", data=expected_data)
        
        print("✅ create_custom_field works with mock API")
    
    def test_validate_form_data(self):
        """Test validating form data against field requirements."""
        # Mock the API response for get_request_type_fields
        self.mock_api_request.return_value = {
            "requestTypeFields": [
                {
                    "fieldId": "summary",
                    "name": "Summary",
                    "required": True,
                    "jiraSchema": {"type": "string"}
                },
                {
                    "fieldId": "description",
                    "name": "Description",
                    "required": True,
                    "jiraSchema": {"type": "string"}
                },
                {
                    "fieldId": "priority",
                    "name": "Priority",
                    "required": False,
                    "jiraSchema": {"type": "option"},
                    "allowedValues": [
                        {"value": "High"},
                        {"value": "Medium"},
                        {"value": "Low"}
                    ]
                }
            ]
        }
        
        # Call the method with valid data
        service_desk_id = "sd-1001"
        request_type_id = "rt-2001"
        form_data = {
            "summary": "Test Request",
            "description": "This is a test request",
            "priority": "Medium"
        }
        
        result = self.form_service.validate_form_data(
            service_desk_id=service_desk_id,
            request_type_id=request_type_id,
            form_data=form_data
        )
        
        # Verify results
        self.assertTrue(result["isValid"])
        self.assertEqual(len(result["errors"]), 0)
        
        # Call with invalid data - missing required field
        invalid_data = {
            "summary": "Test Request",
            # description is missing
            "priority": "Medium"
        }
        
        result = self.form_service.validate_form_data(
            service_desk_id=service_desk_id,
            request_type_id=request_type_id,
            form_data=invalid_data
        )
        
        # Verify results
        self.assertFalse(result["isValid"])
        self.assertIn("description", result["errors"])
        
        # Call with invalid data - invalid option value
        invalid_data2 = {
            "summary": "Test Request",
            "description": "This is a test request",
            "priority": "Critical"  # Not in allowed values
        }
        
        result = self.form_service.validate_form_data(
            service_desk_id=service_desk_id,
            request_type_id=request_type_id,
            form_data=invalid_data2
        )
        
        # Verify results
        self.assertFalse(result["isValid"])
        self.assertIn("priority", result["errors"])
        
        print("✅ validate_form_data works with mock API")


if __name__ == '__main__':
    unittest.main()