"""
Jira Service Management (JSM) Integration Prototype for MCP-Atlassian Server.

This prototype demonstrates the implementation of JSM functionality in the MCP-Atlassian
server, focusing on service desk operations, request management, and related features.

Author: Cline
Date: April 19, 2025
"""

import logging
import os
import requests
from typing import Dict, List, Optional, Union, Any

# Configure logging
logger = logging.getLogger("mcp-jsm")

class JiraServiceManager:
    """Handles operations related to Jira Service Management (Service Desk)."""

    def __init__(self, url=None, username=None, api_token=None):
        """
        Initialize the JSM client.
        
        Args:
            url: The JSM URL (defaults to environment variable)
            username: The JSM username (defaults to environment variable)
            api_token: The JSM API token (defaults to environment variable)
        """
        self.url = url or os.getenv("JSM_URL") or os.getenv("JIRA_URL")
        self.username = username or os.getenv("JSM_USERNAME") or os.getenv("JIRA_USERNAME")
        self.api_token = api_token or os.getenv("JSM_API_TOKEN") or os.getenv("JIRA_API_TOKEN")
        
        if not all([self.url, self.username, self.api_token]):
            raise ValueError("Missing required JSM environment variables")
        
        # Ensure URL doesn't end with a slash
        self.url = self.url.rstrip("/")
        
        # Base API URL for JSM
        self.api_base = f"{self.url}/rest/servicedeskapi"
        
        # Authentication tuple for requests
        self.auth = (self.username, self.api_token)
        
        # Standard headers for API requests
        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

    def _handle_response(self, response):
        """Handle API responses and raise appropriate exceptions."""
        if response.status_code >= 400:
            error_msg = f"JSM API Error: {response.status_code} - {response.text}"
            logger.error(error_msg)
            
            # Handle specific error codes
            if response.status_code == 404:
                raise ValueError("Service desk resource not found")
            elif response.status_code == 403:
                raise ValueError("Permission denied - check JSM scopes")
            elif response.status_code == 400:
                raise ValueError(f"Bad request: {response.text}")
            else:
                raise ValueError(error_msg)
        
        return response.json()

    # ======= SERVICE DESK OPERATIONS =======
    
    def get_service_desks(self, start: int = 0, limit: int = 50) -> Dict:
        """
        Get all service desks available to the user.
        
        Args:
            start: Starting index for pagination
            limit: Maximum results to return
            
        Returns:
            Dictionary containing service desk information
        """
        url = f"{self.api_base}/servicedesk"
        params = {"start": start, "limit": limit}
        
        response = requests.get(url, auth=self.auth, headers=self.headers, params=params)
        return self._handle_response(response)
    
    def get_service_desk(self, service_desk_id: str) -> Dict:
        """
        Get details about a specific service desk.
        
        Args:
            service_desk_id: The ID of the service desk
            
        Returns:
            Dictionary containing service desk details
        """
        url = f"{self.api_base}/servicedesk/{service_desk_id}"
        
        response = requests.get(url, auth=self.auth, headers=self.headers)
        return self._handle_response(response)
    
    # ======= REQUEST TYPE OPERATIONS =======
    
    def get_request_types(self, service_desk_id: str, start: int = 0, limit: int = 50) -> Dict:
        """
        Get available request types for a service desk.
        
        Args:
            service_desk_id: The ID of the service desk
            start: Starting index for pagination
            limit: Maximum results to return
            
        Returns:
            Dictionary containing request types
        """
        url = f"{self.api_base}/servicedesk/{service_desk_id}/requesttype"
        params = {"start": start, "limit": limit}
        
        response = requests.get(url, auth=self.auth, headers=self.headers, params=params)
        return self._handle_response(response)
    
    def get_request_type_fields(self, service_desk_id: str, request_type_id: str) -> Dict:
        """
        Get fields for a request type.
        
        Args:
            service_desk_id: The ID of the service desk
            request_type_id: The ID of the request type
            
        Returns:
            Dictionary containing field information
        """
        url = f"{self.api_base}/servicedesk/{service_desk_id}/requesttype/{request_type_id}/field"
        
        response = requests.get(url, auth=self.auth, headers=self.headers)
        return self._handle_response(response)
    
    # ======= CUSTOMER REQUEST OPERATIONS =======
    
    def create_customer_request(self, 
                               service_desk_id: str, 
                               request_type_id: str, 
                               summary: str, 
                               description: str, 
                               request_field_values: Optional[Dict] = None,
                               attachments: Optional[List[str]] = None) -> Dict:
        """
        Create a customer request (service desk ticket).
        
        Args:
            service_desk_id: The ID of the service desk
            request_type_id: The ID of the request type
            summary: The summary of the request
            description: The description of the request
            request_field_values: Dictionary of field values for the request
            attachments: List of attachment IDs to attach to the request
            
        Returns:
            Dictionary containing the created request
        """
        url = f"{self.api_base}/request"
        
        # Prepare request data
        data = {
            "serviceDeskId": service_desk_id,
            "requestTypeId": request_type_id,
            "requestFieldValues": {
                "summary": summary,
                "description": description
            }
        }
        
        # Add custom field values if provided
        if request_field_values:
            data["requestFieldValues"].update(request_field_values)
        
        # Add attachments if provided
        if attachments:
            data["attachments"] = attachments
        
        response = requests.post(url, auth=self.auth, headers=self.headers, json=data)
        return self._handle_response(response)
    
    def get_customer_requests(self, 
                            service_desk_id: Optional[str] = None, 
                            request_type_id: Optional[str] = None, 
                            status: Optional[str] = None, 
                            start: int = 0, 
                            limit: int = 50,
                            expand: Optional[str] = None) -> Dict:
        """
        Get customer requests with optional filtering.
        
        Args:
            service_desk_id: Filter by service desk ID
            request_type_id: Filter by request type ID
            status: Filter by request status
            start: Starting index for pagination
            limit: Maximum results to return
            expand: Fields to expand in the response
            
        Returns:
            Dictionary containing customer requests
        """
        url = f"{self.api_base}/request"
        
        # Prepare parameters
        params = {"start": start, "limit": limit}
        
        if service_desk_id:
            params["serviceDeskId"] = service_desk_id
        
        if request_type_id:
            params["requestTypeId"] = request_type_id
        
        if status:
            params["status"] = status
        
        if expand:
            params["expand"] = expand
        
        response = requests.get(url, auth=self.auth, headers=self.headers, params=params)
        return self._handle_response(response)
    
    def get_customer_request(self, issue_id_or_key: str, expand: Optional[str] = None) -> Dict:
        """
        Get details about a specific customer request.
        
        Args:
            issue_id_or_key: The ID or key of the issue
            expand: Fields to expand in the response
            
        Returns:
            Dictionary containing request details
        """
        url = f"{self.api_base}/request/{issue_id_or_key}"
        
        params = {}
        if expand:
            params["expand"] = expand
        
        response = requests.get(url, auth=self.auth, headers=self.headers, params=params)
        return self._handle_response(response)
    
    # ======= REQUEST PARTICIPANTS OPERATIONS =======
    
    def get_request_participants(self, issue_id_or_key: str) -> Dict:
        """
        Get participants for a customer request.
        
        Args:
            issue_id_or_key: The ID or key of the issue
            
        Returns:
            Dictionary containing participant information
        """
        url = f"{self.api_base}/request/{issue_id_or_key}/participant"
        
        response = requests.get(url, auth=self.auth, headers=self.headers)
        return self._handle_response(response)
    
    def add_request_participant(self, issue_id_or_key: str, account_id: str) -> Dict:
        """
        Add a participant to a customer request.
        
        Args:
            issue_id_or_key: The ID or key of the issue
            account_id: The account ID of the user to add
            
        Returns:
            Dictionary containing participant information
        """
        url = f"{self.api_base}/request/{issue_id_or_key}/participant"
        
        data = {
            "accountId": account_id
        }
        
        response = requests.post(url, auth=self.auth, headers=self.headers, json=data)
        return self._handle_response(response)
    
    def remove_request_participant(self, issue_id_or_key: str, account_id: str) -> Dict:
        """
        Remove a participant from a customer request.
        
        Args:
            issue_id_or_key: The ID or key of the issue
            account_id: The account ID of the user to remove
            
        Returns:
            Dictionary containing result information
        """
        url = f"{self.api_base}/request/{issue_id_or_key}/participant"
        
        data = {
            "accountId": account_id
        }
        
        response = requests.delete(url, auth=self.auth, headers=self.headers, json=data)
        return self._handle_response(response)
    
    # ======= SLA OPERATIONS =======
    
    def get_request_sla(self, issue_id_or_key: str) -> Dict:
        """
        Get SLA information for a request.
        
        Args:
            issue_id_or_key: The ID or key of the issue
            
        Returns:
            Dictionary containing SLA information
        """
        url = f"{self.api_base}/request/{issue_id_or_key}/sla"
        
        response = requests.get(url, auth=self.auth, headers=self.headers)
        return self._handle_response(response)
    
    # ======= QUEUES OPERATIONS =======
    
    def get_queues(self, service_desk_id: str, start: int = 0, limit: int = 50) -> Dict:
        """
        Get queues for a service desk.
        
        Args:
            service_desk_id: The ID of the service desk
            start: Starting index for pagination
            limit: Maximum results to return
            
        Returns:
            Dictionary containing queue information
        """
        url = f"{self.api_base}/servicedesk/{service_desk_id}/queue"
        params = {"start": start, "limit": limit}
        
        response = requests.get(url, auth=self.auth, headers=self.headers, params=params)
        return self._handle_response(response)
    
    def get_queue_issues(self, service_desk_id: str, queue_id: str, start: int = 0, limit: int = 50) -> Dict:
        """
        Get issues in a queue.
        
        Args:
            service_desk_id: The ID of the service desk
            queue_id: The ID of the queue
            start: Starting index for pagination
            limit: Maximum results to return
            
        Returns:
            Dictionary containing issue information
        """
        url = f"{self.api_base}/servicedesk/{service_desk_id}/queue/{queue_id}/issue"
        params = {"start": start, "limit": limit}
        
        response = requests.get(url, auth=self.auth, headers=self.headers, params=params)
        return self._handle_response(response)
    
    # ======= ORGANIZATIONS OPERATIONS =======
    
    def get_organizations(self, service_desk_id: Optional[str] = None, start: int = 0, limit: int = 50) -> Dict:
        """
        Get organizations.
        
        Args:
            service_desk_id: Filter by service desk ID
            start: Starting index for pagination
            limit: Maximum results to return
            
        Returns:
            Dictionary containing organization information
        """
        if service_desk_id:
            url = f"{self.api_base}/servicedesk/{service_desk_id}/organization"
        else:
            url = f"{self.api_base}/organization"
        
        params = {"start": start, "limit": limit}
        
        response = requests.get(url, auth=self.auth, headers=self.headers, params=params)
        return self._handle_response(response)
    
    def add_organization(self, service_desk_id: str, organization_id: str) -> Dict:
        """
        Add an organization to a service desk.
        
        Args:
            service_desk_id: The ID of the service desk
            organization_id: The ID of the organization to add
            
        Returns:
            Dictionary containing result information
        """
        url = f"{self.api_base}/servicedesk/{service_desk_id}/organization"
        
        data = {
            "organizationId": organization_id
        }
        
        response = requests.post(url, auth=self.auth, headers=self.headers, json=data)
        return self._handle_response(response)


# Example MCP Tool Implementation
def jsm_create_customer_request(server_name: str, arguments: Dict) -> Dict:
    """
    MCP tool to create a customer request (service desk ticket).
    
    Args:
        server_name: The name of the MCP server
        arguments: Dictionary of arguments for the tool
        
    Returns:
        Dictionary containing the created request
    """
    # Extract arguments
    service_desk_id = arguments.get("service_desk_id")
    request_type_id = arguments.get("request_type_id")
    summary = arguments.get("summary")
    description = arguments.get("description")
    request_field_values = arguments.get("request_field_values")
    attachments = arguments.get("attachments")
    
    # Validate required arguments
    if not all([service_desk_id, request_type_id, summary, description]):
        raise ValueError("Missing required arguments: service_desk_id, request_type_id, summary, description")
    
    # Initialize JSM client
    jsm_client = JiraServiceManager()
    
    # Create customer request
    result = jsm_client.create_customer_request(
        service_desk_id=service_desk_id,
        request_type_id=request_type_id,
        summary=summary,
        description=description,
        request_field_values=request_field_values,
        attachments=attachments
    )
    
    return {
        "request_id": result.get("issueId"),
        "key": result.get("issueKey"),
        "self": result.get("self"),
        "service_desk_id": service_desk_id,
        "request_type_id": request_type_id,
        "summary": summary,
        "created": True
    }


# Example usage (not executed)
def example_usage():
    """Example usage of the JSM client."""
    # Initialize JSM client
    jsm_client = JiraServiceManager()
    
    # Get all service desks
    service_desks = jsm_client.get_service_desks()
    print(f"Found {len(service_desks.get('values', []))} service desks")
    
    # Get request types for the first service desk
    if service_desks.get("values"):
        service_desk_id = service_desks["values"][0]["id"]
        request_types = jsm_client.get_request_types(service_desk_id)
        print(f"Found {len(request_types.get('values', []))} request types")
        
        # Create a customer request using the first request type
        if request_types.get("values"):
            request_type_id = request_types["values"][0]["id"]
            request = jsm_client.create_customer_request(
                service_desk_id=service_desk_id,
                request_type_id=request_type_id,
                summary="Test request from JSM client",
                description="This is a test request created from the JSM client"
            )
            print(f"Created request with ID: {request.get('issueId')} and Key: {request.get('issueKey')}")
