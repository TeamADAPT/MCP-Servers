"""
Jira Service Management (JSM) Module

This module provides integration with Jira Service Management (JSM),
including service desks, request types, customer requests, and more.
"""

import json
import logging
import os
from typing import Dict, List, Optional, Any, Union

import requests

logger = logging.getLogger(__name__)

class JiraServiceManager:
    """
    Manages Jira Service Management operations and API interactions.
    """

    def __init__(
        self, 
        url: Optional[str] = None, 
        username: Optional[str] = None, 
        api_token: Optional[str] = None
    ):
        """
        Initialize the Jira Service Management manager.

        Args:
            url: JSM URL (defaults to JSM_URL or JIRA_URL environment variable)
            username: JSM username (defaults to JSM_USERNAME or JIRA_USERNAME environment variable)
            api_token: JSM API token (defaults to JSM_API_TOKEN or JIRA_API_TOKEN environment variable)
        """
        # Use provided values or fall back to environment variables
        self.url = url or os.environ.get("JSM_URL") or os.environ.get("JIRA_URL")
        self.username = username or os.environ.get("JSM_USERNAME") or os.environ.get("JIRA_USERNAME")
        self.api_token = api_token or os.environ.get("JSM_API_TOKEN") or os.environ.get("JIRA_API_TOKEN")
        
        if not all([self.url, self.username, self.api_token]):
            missing = []
            if not self.url:
                missing.append("JSM_URL or JIRA_URL")
            if not self.username:
                missing.append("JSM_USERNAME or JIRA_USERNAME")
            if not self.api_token:
                missing.append("JSM_API_TOKEN or JIRA_API_TOKEN")
            raise ValueError(f"Missing required JSM credentials: {', '.join(missing)}")
        
        # Normalize URL
        self.url = self.url.rstrip("/")
        self.auth = (self.username, self.api_token)
        self.headers = {"Content-Type": "application/json"}
        
        logger.debug(f"Initialized JiraServiceManager with URL: {self.url}")

    def _make_api_request(
        self, method: str, endpoint: str, params: Optional[Dict] = None, data: Optional[Dict] = None
    ) -> Dict:
        """
        Make an API request to the JSM API.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint (without base URL)
            params: Optional query parameters
            data: Optional data for POST/PUT requests

        Returns:
            Response as dictionary
        """
        url = f"{self.url}/rest/servicedeskapi{endpoint}"
        json_data = json.dumps(data) if data else None
        
        try:
            response = requests.request(
                method=method,
                url=url,
                params=params,
                data=json_data,
                headers=self.headers,
                auth=self.auth
            )
            
            if response.status_code == 204:  # No Content
                return {"status": "success"}
                
            if response.status_code >= 400:
                error_msg = f"JSM API request failed: {response.status_code}"
                if response.status_code == 404:
                    error_msg = f"Resource not found: {url}"
                elif response.status_code == 403:
                    error_msg = f"Permission denied for: {url}"
                elif response.status_code == 400:
                    error_msg = f"Bad request: {response.text}"
                else:
                    error_msg = f"API request failed ({response.status_code}): {response.text}"
                
                logger.error(error_msg)
                raise ValueError(error_msg)
                
            return response.json()
            
        except requests.RequestException as e:
            error_msg = f"Request error for {url}: {str(e)}"
            logger.error(error_msg)
            raise ValueError(error_msg)

    # Service Desk Operations
    def get_service_desks(self, start: int = 0, limit: int = 50) -> List[Dict]:
        """
        Get all service desks.

        Args:
            start: Starting index for pagination
            limit: Maximum number of results to return

        Returns:
            List of service desks
        """
        params = {
            "start": start,
            "limit": limit
        }
        
        response = self._make_api_request("GET", "/servicedesk", params=params)
        return response.get("values", [])

    def get_service_desk(self, service_desk_id: str) -> Dict:
        """
        Get a specific service desk.

        Args:
            service_desk_id: The service desk ID

        Returns:
            Service desk details
        """
        return self._make_api_request("GET", f"/servicedesk/{service_desk_id}")

    # Request Type Operations
    def get_request_types(self, service_desk_id: str, start: int = 0, limit: int = 50) -> List[Dict]:
        """
        Get request types for a service desk.

        Args:
            service_desk_id: The service desk ID
            start: Starting index for pagination
            limit: Maximum number of results to return

        Returns:
            List of request types
        """
        params = {
            "start": start,
            "limit": limit
        }
        
        response = self._make_api_request(
            "GET", f"/servicedesk/{service_desk_id}/requesttype", params=params
        )
        return response.get("values", [])

    def get_request_type_fields(self, service_desk_id: str, request_type_id: str) -> List[Dict]:
        """
        Get fields for a request type.

        Args:
            service_desk_id: The service desk ID
            request_type_id: The request type ID

        Returns:
            List of fields
        """
        response = self._make_api_request(
            "GET", f"/servicedesk/{service_desk_id}/requesttype/{request_type_id}/field"
        )
        return response.get("requestTypeFields", [])

    # Customer Request Operations
    def create_customer_request(
        self, service_desk_id: str, request_type_id: str, 
        summary: str, description: Optional[str] = None,
        custom_fields: Optional[Dict] = None
    ) -> Dict:
        """
        Create a customer request (service desk ticket).

        Args:
            service_desk_id: The service desk ID
            request_type_id: The request type ID
            summary: Request summary
            description: Request description
            custom_fields: Optional custom fields as {field_id: field_value}

        Returns:
            Created request details
        """
        data = {
            "serviceDeskId": service_desk_id,
            "requestTypeId": request_type_id,
            "requestFieldValues": {
                "summary": summary
            }
        }
        
        if description:
            data["requestFieldValues"]["description"] = description
            
        if custom_fields:
            for field_id, field_value in custom_fields.items():
                data["requestFieldValues"][field_id] = field_value
        
        return self._make_api_request("POST", "/request", data=data)

    def get_customer_requests(
        self, service_desk_id: Optional[str] = None,
        request_status: Optional[str] = None,
        search_term: Optional[str] = None,
        start: int = 0, limit: int = 50
    ) -> List[Dict]:
        """
        Get customer requests.

        Args:
            service_desk_id: Optional service desk ID to filter by
            request_status: Optional status to filter by (OPEN, CLOSED)
            search_term: Optional search term
            start: Starting index for pagination
            limit: Maximum number of results to return

        Returns:
            List of customer requests
        """
        params = {
            "start": start,
            "limit": limit
        }
        
        if service_desk_id:
            params["serviceDeskId"] = service_desk_id
            
        if request_status:
            params["requestStatus"] = request_status
            
        if search_term:
            params["searchTerm"] = search_term
        
        response = self._make_api_request("GET", "/request", params=params)
        return response.get("values", [])

    def get_customer_request(self, request_id: str) -> Dict:
        """
        Get a specific customer request.

        Args:
            request_id: The request ID

        Returns:
            Request details
        """
        return self._make_api_request("GET", f"/request/{request_id}")

    # Request Participants Operations
    def get_request_participants(self, request_id: str) -> List[Dict]:
        """
        Get participants for a request.

        Args:
            request_id: The request ID

        Returns:
            List of participants
        """
        response = self._make_api_request("GET", f"/request/{request_id}/participant")
        return response.get("values", [])

    def add_request_participant(self, request_id: str, account_id: str) -> Dict:
        """
        Add a participant to a request.

        Args:
            request_id: The request ID
            account_id: User account ID

        Returns:
            Status response
        """
        data = {
            "accountId": account_id
        }
        
        return self._make_api_request("POST", f"/request/{request_id}/participant", data=data)

    def remove_request_participant(self, request_id: str, account_id: str) -> Dict:
        """
        Remove a participant from a request.

        Args:
            request_id: The request ID
            account_id: User account ID

        Returns:
            Status response
        """
        return self._make_api_request(
            "DELETE", f"/request/{request_id}/participant/{account_id}"
        )

    # SLA Operations
    def get_request_sla(self, request_id: str) -> List[Dict]:
        """
        Get SLA information for a request.

        Args:
            request_id: The request ID

        Returns:
            SLA information
        """
        response = self._make_api_request("GET", f"/request/{request_id}/sla")
        return response.get("values", [])

    # Queues Operations
    def get_queues(self, service_desk_id: str, include_counts: bool = False) -> List[Dict]:
        """
        Get queues for a service desk.

        Args:
            service_desk_id: The service desk ID
            include_counts: Whether to include issue counts

        Returns:
            List of queues
        """
        params = {}
        if include_counts:
            params["includeCount"] = "true"
            
        response = self._make_api_request(
            "GET", f"/servicedesk/{service_desk_id}/queue", params=params
        )
        return response.get("values", [])

    def get_queue_issues(
        self, service_desk_id: str, queue_id: str,
        start: int = 0, limit: int = 50
    ) -> List[Dict]:
        """
        Get issues in a queue.

        Args:
            service_desk_id: The service desk ID
            queue_id: The queue ID
            start: Starting index for pagination
            limit: Maximum number of results to return

        Returns:
            List of issues
        """
        params = {
            "start": start,
            "limit": limit
        }
        
        response = self._make_api_request(
            "GET", f"/servicedesk/{service_desk_id}/queue/{queue_id}/issue", params=params
        )
        return response.get("values", [])

    # Organizations Operations
    def get_organizations(self, service_desk_id: Optional[str] = None) -> List[Dict]:
        """
        Get organizations for the user.

        Args:
            service_desk_id: Optional service desk ID to filter by

        Returns:
            List of organizations
        """
        endpoint = "/organization"
        if service_desk_id:
            endpoint = f"/servicedesk/{service_desk_id}/organization"
            
        response = self._make_api_request("GET", endpoint)
        return response.get("values", [])

    def add_organization(self, service_desk_id: str, organization_id: str) -> Dict:
        """
        Add an organization to a service desk.

        Args:
            service_desk_id: The service desk ID
            organization_id: The organization ID

        Returns:
            Status response
        """
        data = {
            "organizationId": organization_id
        }
        
        return self._make_api_request(
            "POST", f"/servicedesk/{service_desk_id}/organization", data=data
        )

    def remove_organization(self, service_desk_id: str, organization_id: str) -> Dict:
        """
        Remove an organization from a service desk.

        Args:
            service_desk_id: The service desk ID
            organization_id: The organization ID

        Returns:
            Status response
        """
        return self._make_api_request(
            "DELETE", f"/servicedesk/{service_desk_id}/organization/{organization_id}"
        )

    # Approvals Operations
    def get_request_approvals(self, request_id: str) -> List[Dict]:
        """
        Get approvals for a request.

        Args:
            request_id: The request ID

        Returns:
            List of approvals
        """
        response = self._make_api_request("GET", f"/request/{request_id}/approval")
        return response.get("values", [])

    def answer_approval(
        self, request_id: str, approval_id: str, decision: str, comment: Optional[str] = None
    ) -> Dict:
        """
        Answer an approval.

        Args:
            request_id: The request ID
            approval_id: The approval ID
            decision: The decision ("approve" or "decline")
            comment: Optional comment

        Returns:
            Status response
        """
        if decision not in ["approve", "decline"]:
            raise ValueError("Decision must be 'approve' or 'decline'")
            
        data = {
            "decision": decision
        }
        
        if comment:
            data["comment"] = comment
            
        return self._make_api_request(
            "POST", f"/request/{request_id}/approval/{approval_id}/{decision}", data=data
        )