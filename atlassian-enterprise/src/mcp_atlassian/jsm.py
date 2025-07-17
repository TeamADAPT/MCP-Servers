"""
Jira Service Management (JSM) Integration for MCP-Atlassian Server.

This module provides integration with Jira Service Management (formerly Service Desk),
enabling operations related to service desks, customer requests, and related features.

Author: Claude Code
Date: May 7, 2025
"""

import logging
import os
import requests
from typing import Dict, List, Optional, Union, Any, Tuple

# Configure logging
logger = logging.getLogger("mcp-jsm")

class JiraServiceManager:
    """
    Handles operations related to Jira Service Management.
    
    This class provides a comprehensive interface to JSM functionality
    including service desk operations, request management, participants,
    SLA tracking, queues, and organizations.
    """

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
        
        logger.info(f"Initialized JSM client for {self.url}")

    def _make_api_request(self, method: str, endpoint: str, data: Optional[Dict] = None, params: Optional[Dict] = None) -> Dict:
        """
        Make a request to the JSM API.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint path (without base URL)
            data: Optional payload for POST/PUT requests
            params: Optional query parameters
            
        Returns:
            Dictionary containing the API response
        """
        # Ensure endpoint starts with /
        if not endpoint.startswith("/"):
            endpoint = f"/{endpoint}"
            
        url = f"{self.api_base}{endpoint}"
        
        try:
            if method.upper() == "GET":
                response = requests.get(url, auth=self.auth, headers=self.headers, params=params)
            elif method.upper() == "POST":
                response = requests.post(url, json=data, auth=self.auth, headers=self.headers, params=params)
            elif method.upper() == "PUT":
                response = requests.put(url, json=data, auth=self.auth, headers=self.headers, params=params)
            elif method.upper() == "DELETE":
                response = requests.delete(url, json=data, auth=self.auth, headers=self.headers, params=params)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
                
            # Handle response and raise appropriate exceptions
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
            
            # Return JSON response or empty dict for 204 No Content
            return response.json() if response.content else {}
            
        except requests.RequestException as e:
            logger.error(f"Error making JSM API request to {endpoint}: {str(e)}")
            raise ValueError(f"JSM API request failed: {str(e)}")

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
        params = {"start": start, "limit": limit}
        return self._make_api_request("GET", "/servicedesk", params=params)
    
    def get_service_desk(self, service_desk_id: str) -> Dict:
        """
        Get details about a specific service desk.
        
        Args:
            service_desk_id: The ID of the service desk
            
        Returns:
            Dictionary containing service desk details
        """
        return self._make_api_request("GET", f"/servicedesk/{service_desk_id}")
    
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
        params = {"start": start, "limit": limit}
        return self._make_api_request("GET", f"/servicedesk/{service_desk_id}/requesttype", params=params)
    
    def get_request_type_fields(self, service_desk_id: str, request_type_id: str) -> Dict:
        """
        Get fields for a request type.
        
        Args:
            service_desk_id: The ID of the service desk
            request_type_id: The ID of the request type
            
        Returns:
            Dictionary containing field information
        """
        return self._make_api_request("GET", f"/servicedesk/{service_desk_id}/requesttype/{request_type_id}/field")
    
    # ======= CUSTOMER REQUEST OPERATIONS =======
    
    def create_customer_request(self, 
                               service_desk_id: str, 
                               request_type_id: str, 
                               summary: str, 
                               description: str, 
                               request_field_values: Optional[Dict] = None,
                               attachments: Optional[List[str]] = None,
                               name: Optional[str] = None,
                               dept: Optional[str] = None) -> Dict:
        """
        Create a customer request (service desk ticket).
        
        Args:
            service_desk_id: The ID of the service desk
            request_type_id: The ID of the request type
            summary: The summary of the request
            description: The description of the request
            request_field_values: Dictionary of field values for the request
            attachments: List of attachment IDs to attach to the request
            name: Name value for custom field (required if available for the request type)
            dept: Department value for custom field (required if available for the request type)
            
        Returns:
            Dictionary containing the created request
        """
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
            
        # Add custom fields if provided
        if name:
            if "customfield_10057" not in data["requestFieldValues"]:
                data["requestFieldValues"]["customfield_10057"] = [name]
                
        if dept:
            if "customfield_10058" not in data["requestFieldValues"]:
                data["requestFieldValues"]["customfield_10058"] = [dept]
        
        # Add attachments if provided
        if attachments:
            data["attachments"] = attachments
        
        return self._make_api_request("POST", "/request", data=data)
    
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
        
        return self._make_api_request("GET", "/request", params=params)
    
    def get_customer_request(self, issue_id_or_key: str, expand: Optional[str] = None) -> Dict:
        """
        Get details about a specific customer request.
        
        Args:
            issue_id_or_key: The ID or key of the issue
            expand: Fields to expand in the response
            
        Returns:
            Dictionary containing request details
        """
        params = {}
        if expand:
            params["expand"] = expand
        
        return self._make_api_request("GET", f"/request/{issue_id_or_key}", params=params)
    
    # ======= REQUEST PARTICIPANTS OPERATIONS =======
    
    def get_request_participants(self, issue_id_or_key: str) -> Dict:
        """
        Get participants for a customer request.
        
        Args:
            issue_id_or_key: The ID or key of the issue
            
        Returns:
            Dictionary containing participant information
        """
        return self._make_api_request("GET", f"/request/{issue_id_or_key}/participant")
    
    def add_request_participant(self, issue_id_or_key: str, account_id: str) -> Dict:
        """
        Add a participant to a customer request.
        
        Args:
            issue_id_or_key: The ID or key of the issue
            account_id: The account ID of the user to add
            
        Returns:
            Dictionary containing participant information
        """
        data = {"accountId": account_id}
        return self._make_api_request("POST", f"/request/{issue_id_or_key}/participant", data=data)
    
    def remove_request_participant(self, issue_id_or_key: str, account_id: str) -> Dict:
        """
        Remove a participant from a customer request.
        
        Args:
            issue_id_or_key: The ID or key of the issue
            account_id: The account ID of the user to remove
            
        Returns:
            Dictionary containing result information
        """
        data = {"accountId": account_id}
        return self._make_api_request("DELETE", f"/request/{issue_id_or_key}/participant", data=data)
    
    # ======= SLA OPERATIONS =======
    
    def get_request_sla(self, issue_id_or_key: str) -> Dict:
        """
        Get SLA information for a request.
        
        Args:
            issue_id_or_key: The ID or key of the issue
            
        Returns:
            Dictionary containing SLA information
        """
        return self._make_api_request("GET", f"/request/{issue_id_or_key}/sla")
    
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
        params = {"start": start, "limit": limit}
        return self._make_api_request("GET", f"/servicedesk/{service_desk_id}/queue", params=params)
    
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
        params = {"start": start, "limit": limit}
        return self._make_api_request("GET", f"/servicedesk/{service_desk_id}/queue/{queue_id}/issue", params=params)
    
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
        params = {"start": start, "limit": limit}
        
        if service_desk_id:
            return self._make_api_request("GET", f"/servicedesk/{service_desk_id}/organization", params=params)
        else:
            return self._make_api_request("GET", "/organization", params=params)
    
    def add_organization(self, service_desk_id: str, organization_id: str) -> Dict:
        """
        Add an organization to a service desk.
        
        Args:
            service_desk_id: The ID of the service desk
            organization_id: The ID of the organization to add
            
        Returns:
            Dictionary containing result information
        """
        data = {"organizationId": organization_id}
        return self._make_api_request("POST", f"/servicedesk/{service_desk_id}/organization", data=data)

    def remove_organization(self, service_desk_id: str, organization_id: str) -> Dict:
        """
        Remove an organization from a service desk.
        
        Args:
            service_desk_id: The ID of the service desk
            organization_id: The ID of the organization to remove
            
        Returns:
            Dictionary containing result information
        """
        data = {"organizationId": organization_id}
        return self._make_api_request("DELETE", f"/servicedesk/{service_desk_id}/organization", data=data)
        
    # ======= APPROVALS OPERATIONS =======
    
    def get_request_approvals(self, issue_id_or_key: str) -> Dict:
        """
        Get approvals for a request.
        
        Args:
            issue_id_or_key: The ID or key of the issue
            
        Returns:
            Dictionary containing approval information
        """
        return self._make_api_request("GET", f"/request/{issue_id_or_key}/approval")
    
    def answer_approval(self, issue_id_or_key: str, approval_id: str, decision: str) -> Dict:
        """
        Answer an approval for a request.
        
        Args:
            issue_id_or_key: The ID or key of the issue
            approval_id: The ID of the approval
            decision: The decision (approve or decline)
            
        Returns:
            Dictionary containing approval result information
        """
        if decision.lower() not in ["approve", "decline"]:
            raise ValueError("Decision must be either 'approve' or 'decline'")
            
        data = {"decision": decision.lower()}
        return self._make_api_request("POST", f"/request/{issue_id_or_key}/approval/{approval_id}", data=data)