"""
JSM Approvals Module

This module provides enhanced functionality for working with Jira Service Management (JSM)
approvals, including multi-level approvals and approval workflows.
"""

import json
import logging
import os
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta

import requests

from .jsm import JiraServiceManager

logger = logging.getLogger(__name__)

class JSMApprovalManager:
    """
    Manages advanced Jira Service Management approval workflows.
    """

    def __init__(
        self, 
        jsm_client: Optional[JiraServiceManager] = None,
        url: Optional[str] = None, 
        username: Optional[str] = None, 
        api_token: Optional[str] = None
    ):
        """
        Initialize the JSM Approval Manager.

        Args:
            jsm_client: Optional existing JSM client
            url: JSM URL (if not using existing client)
            username: JSM username (if not using existing client)
            api_token: JSM API token (if not using existing client)
        """
        if jsm_client:
            self.jsm_client = jsm_client
            self.url = jsm_client.url
            self.auth = jsm_client.auth
            self.headers = jsm_client.headers
        else:
            # Create new client
            self.jsm_client = JiraServiceManager(url, username, api_token)
            self.url = self.jsm_client.url
            self.auth = self.jsm_client.auth
            self.headers = self.jsm_client.headers
        
        logger.debug(f"Initialized JSMApprovalManager with URL: {self.url}")

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

    def _make_jira_api_request(
        self, method: str, endpoint: str, params: Optional[Dict] = None, data: Optional[Dict] = None
    ) -> Dict:
        """
        Make an API request to the Jira API.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint (without base URL)
            params: Optional query parameters
            data: Optional data for POST/PUT requests

        Returns:
            Response as dictionary
        """
        url = f"{self.url}/rest/api/3{endpoint}"
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
                error_msg = f"Jira API request failed: {response.status_code}"
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

    # Basic Approval Operations
    def get_request_approvals(self, request_id: str, expand: Optional[str] = None) -> List[Dict]:
        """
        Get approvals for a request.

        Args:
            request_id: The request ID
            expand: Optional fields to expand

        Returns:
            List of approvals
        """
        params = {}
        if expand:
            params["expand"] = expand
            
        response = self._make_api_request(
            "GET", f"/request/{request_id}/approval", params=params
        )
        return response.get("values", [])

    def get_approval_details(self, request_id: str, approval_id: str) -> Dict:
        """
        Get details for a specific approval.

        Args:
            request_id: The request ID
            approval_id: The approval ID

        Returns:
            Approval details
        """
        return self._make_api_request(
            "GET", f"/request/{request_id}/approval/{approval_id}"
        )

    def answer_approval(
        self, request_id: str, approval_id: str, decision: str, comment: Optional[str] = None
    ) -> Dict:
        """
        Answer an approval request.

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
            
        data = {}
        if comment:
            data["comment"] = comment
            
        return self._make_api_request(
            "POST", f"/request/{request_id}/approval/{approval_id}/{decision}", data=data
        )

    # Multi-Level Approval Operations
    def create_approval_level(
        self, issue_id: str, approvers: List[str], level_name: str, 
        approval_type: str = "ANY_APPROVER"
    ) -> Dict:
        """
        Create an approval level for an issue.

        Args:
            issue_id: The issue ID
            approvers: List of approver account IDs
            level_name: Name for the approval level
            approval_type: Approval type (ANY_APPROVER, ALL_APPROVERS)

        Returns:
            Created approval level
        """
        if approval_type not in ["ANY_APPROVER", "ALL_APPROVERS"]:
            raise ValueError("approval_type must be 'ANY_APPROVER' or 'ALL_APPROVERS'")
            
        data = {
            "name": level_name,
            "approvers": [{"accountId": approver} for approver in approvers],
            "approvalType": approval_type
        }
        
        return self._make_jira_api_request(
            "POST", f"/issue/{issue_id}/approvals/level", data=data
        )

    def get_approval_levels(self, issue_id: str) -> List[Dict]:
        """
        Get all approval levels for an issue.

        Args:
            issue_id: The issue ID

        Returns:
            List of approval levels
        """
        response = self._make_jira_api_request("GET", f"/issue/{issue_id}/approvals/level")
        return response.get("values", [])

    # Approval Workflow Operations
    def create_approval_workflow(
        self, project_key: str, request_type_id: str, 
        approval_config: Dict[str, Any]
    ) -> Dict:
        """
        Create an approval workflow for a service desk request type.

        Args:
            project_key: The project key
            request_type_id: The request type ID
            approval_config: Approval workflow configuration

        Returns:
            Status response
        """
        # Get project
        project = self._make_jira_api_request("GET", f"/project/{project_key}")
        
        # Set approval configuration as project property
        property_key = f"sd.approval.config.{request_type_id}"
        data = {
            "key": property_key,
            "value": approval_config
        }
        
        return self._make_jira_api_request(
            "PUT", f"/project/{project['id']}/properties/{property_key}", data=data
        )

    def get_approval_workflow(self, project_key: str, request_type_id: str) -> Dict:
        """
        Get approval workflow configuration for a project.

        Args:
            project_key: The project key
            request_type_id: The request type ID

        Returns:
            Approval workflow configuration
        """
        # Get project
        project = self._make_jira_api_request("GET", f"/project/{project_key}")
        
        # Get approval configuration from project property
        property_key = f"sd.approval.config.{request_type_id}"
        
        try:
            response = self._make_jira_api_request(
                "GET", f"/project/{project['id']}/properties/{property_key}"
            )
            return response.get("value", {})
        except ValueError:
            # Property doesn't exist
            return {}

    # Approval Analytics
    def get_approval_metrics(
        self, service_desk_id: str, 
        start_date: Optional[datetime] = None, 
        end_date: Optional[datetime] = None
    ) -> Dict:
        """
        Get approval metrics for a service desk.

        Args:
            service_desk_id: The service desk ID
            start_date: Optional start date for filtering
            end_date: Optional end date for filtering

        Returns:
            Approval metrics
        """
        # Set default date range if not provided
        if not end_date:
            end_date = datetime.now()
        if not start_date:
            start_date = end_date - timedelta(days=30)
            
        # Get all service desk requests
        all_requests = self._get_all_service_desk_requests(service_desk_id)
        
        # Filter by time period
        filtered_requests = self._filter_requests_by_time_period(
            all_requests, start_date, end_date
        )
        
        # Get all approvals for filtered requests
        approvals = []
        for request in filtered_requests:
            request_approvals = self.get_request_approvals(
                request["issueId"], expand="approvalStatus,requestType"
            )
            approvals.extend([{**a, "request": request} for a in request_approvals])
            
        # Calculate approval metrics
        grouped_approvals = self._group_approvals_by_type(approvals)
        
        approved_count = sum(1 for a in approvals if a.get("approvalStatus", {}).get("name") == "APPROVED")
        declined_count = sum(1 for a in approvals if a.get("approvalStatus", {}).get("name") == "DECLINED")
        pending_count = sum(1 for a in approvals if a.get("approvalStatus", {}).get("name") == "PENDING")
        
        avg_approval_time = self._calculate_avg_approval_time(approvals)
        
        return {
            "total_approvals": len(approvals),
            "approved_count": approved_count,
            "declined_count": declined_count,
            "pending_count": pending_count,
            "approval_rate": (approved_count / len(approvals)) if approvals else 0,
            "avg_approval_time_hours": avg_approval_time,
            "approvals_by_type": grouped_approvals,
            "time_period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            }
        }

    def _get_all_service_desk_requests(self, service_desk_id: str) -> List[Dict]:
        """
        Get all requests for a service desk (handles pagination).

        Args:
            service_desk_id: The service desk ID

        Returns:
            List of all requests
        """
        all_requests = []
        start = 0
        limit = 50
        
        while True:
            batch = self.jsm_client.get_customer_requests(
                service_desk_id=service_desk_id, start=start, limit=limit
            )
            all_requests.extend(batch)
            
            if len(batch) < limit:
                break
                
            start += limit
            
        return all_requests

    def _filter_requests_by_time_period(
        self, requests: List[Dict], start_date: datetime, end_date: datetime
    ) -> List[Dict]:
        """
        Filter requests by creation date.

        Args:
            requests: List of requests
            start_date: Start date
            end_date: End date

        Returns:
            Filtered list of requests
        """
        filtered = []
        for request in requests:
            created_str = request.get("createdDate", {}).get("iso8601", "")
            if not created_str:
                continue
                
            try:
                created_date = datetime.fromisoformat(created_str.replace("Z", "+00:00"))
                if start_date <= created_date <= end_date:
                    filtered.append(request)
            except (ValueError, TypeError):
                continue
                
        return filtered

    def _calculate_avg_approval_time(self, approvals: List[Dict]) -> float:
        """
        Calculate average approval time in hours.

        Args:
            approvals: List of approvals

        Returns:
            Average approval time in hours
        """
        # Only consider approved approvals with completed date
        completed_approvals = []
        
        for approval in approvals:
            status = approval.get("approvalStatus", {}).get("name")
            if status != "APPROVED":
                continue
                
            created_str = approval.get("createdDate", {}).get("iso8601", "")
            completed_str = approval.get("completedDate", {}).get("iso8601", "")
            
            if not (created_str and completed_str):
                continue
                
            try:
                created_date = datetime.fromisoformat(created_str.replace("Z", "+00:00"))
                completed_date = datetime.fromisoformat(completed_str.replace("Z", "+00:00"))
                duration = (completed_date - created_date).total_seconds() / 3600  # Convert to hours
                completed_approvals.append(duration)
            except (ValueError, TypeError):
                continue
                
        if not completed_approvals:
            return 0
            
        return sum(completed_approvals) / len(completed_approvals)

    def _group_approvals_by_type(self, approvals: List[Dict]) -> Dict[str, int]:
        """
        Group approvals by request type.

        Args:
            approvals: List of approvals

        Returns:
            Grouped approvals
        """
        grouped = {}
        
        for approval in approvals:
            request_type = approval.get("requestType", {}).get("name", "Unknown")
            grouped[request_type] = grouped.get(request_type, 0) + 1
            
        return grouped