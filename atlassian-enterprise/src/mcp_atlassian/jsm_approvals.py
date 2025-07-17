"""
Jira Service Management Approvals Workflow Module.

This module provides enhanced functionality for working with JSM approvals,
including approval process management, approval rules, and advanced workflows.

Author: Claude Code
Date: May 7, 2025
"""

import logging
from typing import Dict, List, Optional, Union, Any
import os
import requests
import time

# Configure logging
logger = logging.getLogger("mcp-jsm-approvals")

class JSMApprovalManager:
    """
    Handles operations related to Jira Service Management approval workflows.
    
    This class provides functionality for advanced approval management,
    including multi-level approvals, conditional approvals, and approval analytics.
    """
    
    def __init__(self, jsm_client=None, url=None, username=None, api_token=None):
        """
        Initialize the JSM Approval Manager.
        
        Args:
            jsm_client: Existing JiraServiceManager instance (optional)
            url: The JSM URL (defaults to environment variable or jsm_client)
            username: The JSM username (defaults to environment variable or jsm_client)
            api_token: The JSM API token (defaults to environment variable or jsm_client)
        """
        if jsm_client:
            self.url = jsm_client.url
            self.auth = jsm_client.auth
            self.headers = jsm_client.headers
            self.api_base = jsm_client.api_base
            self._make_api_request = jsm_client._make_api_request
        else:
            self.url = url or os.getenv("JSM_URL") or os.getenv("JIRA_URL")
            self.username = username or os.getenv("JSM_USERNAME") or os.getenv("JIRA_USERNAME")
            self.api_token = api_token or os.getenv("JSM_API_TOKEN") or os.getenv("JIRA_API_TOKEN")
            
            if not all([self.url, self.username, self.api_token]):
                raise ValueError("Missing required JSM environment variables")
            
            # Ensure URL doesn't end with a slash
            self.url = self.url.rstrip("/")
            
            # Base API URLs
            self.api_base = f"{self.url}/rest/servicedeskapi"
            # For some approval operations, we need to use additional APIs
            self.jira_api_base = f"{self.url}/rest/api/3"
            self.jira_approvals_api = f"{self.url}/rest/zephyr-connect/public/1.0"
            
            # Authentication tuple for requests
            self.auth = (self.username, self.api_token)
            
            # Standard headers for API requests
            self.headers = {
                "Accept": "application/json",
                "Content-Type": "application/json"
            }
            
            logger.info(f"Initialized JSM Approval Manager for {self.url}")
            
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
                    raise ValueError("Approval resource not found")
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
            
    def _make_jira_api_request(self, method: str, endpoint: str, data: Optional[Dict] = None, params: Optional[Dict] = None) -> Dict:
        """
        Make a request to the Jira API.
        
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
            
        url = f"{self.jira_api_base}{endpoint}"
        
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
                error_msg = f"Jira API Error: {response.status_code} - {response.text}"
                logger.error(error_msg)
                raise ValueError(error_msg)
            
            # Return JSON response or empty dict for 204 No Content
            return response.json() if response.content else {}
            
        except requests.RequestException as e:
            logger.error(f"Error making Jira API request to {endpoint}: {str(e)}")
            raise ValueError(f"Jira API request failed: {str(e)}")
            
    # ======= APPROVAL OPERATIONS =======
    
    def get_request_approvals(self, issue_id_or_key: str, expand: Optional[List[str]] = None) -> Dict:
        """
        Get approvals for a request with expanded information.
        
        Args:
            issue_id_or_key: The ID or key of the issue
            expand: List of fields to expand in the response
            
        Returns:
            Dictionary containing approval information
        """
        params = {}
        if expand:
            params["expand"] = ",".join(expand)
            
        return self._make_api_request("GET", f"/request/{issue_id_or_key}/approval", params=params)
    
    def get_approval_details(self, issue_id_or_key: str, approval_id: str) -> Dict:
        """
        Get detailed information about a specific approval.
        
        Args:
            issue_id_or_key: The ID or key of the issue
            approval_id: The ID of the approval
            
        Returns:
            Dictionary containing detailed approval information
        """
        return self._make_api_request("GET", f"/request/{issue_id_or_key}/approval/{approval_id}")
    
    def answer_approval(self, issue_id_or_key: str, approval_id: str, decision: str, 
                       comment: Optional[str] = None) -> Dict:
        """
        Answer an approval for a request with optional comment.
        
        Args:
            issue_id_or_key: The ID or key of the issue
            approval_id: The ID of the approval
            decision: The decision (approve or decline)
            comment: Optional comment explaining the decision
            
        Returns:
            Dictionary containing approval result information
        """
        if decision.lower() not in ["approve", "decline"]:
            raise ValueError("Decision must be either 'approve' or 'decline'")
            
        data = {"decision": decision.lower()}
        
        if comment:
            data["comment"] = comment
            
        return self._make_api_request("POST", f"/request/{issue_id_or_key}/approval/{approval_id}", data=data)
    
    # ======= MULTI-LEVEL APPROVAL OPERATIONS =======
    
    def create_approval_level(self, issue_id_or_key: str, approver_account_ids: List[str], 
                            level_name: str, approval_type: str = "any_approver") -> Dict:
        """
        Create a new approval level for an issue.
        
        Args:
            issue_id_or_key: The ID or key of the issue
            approver_account_ids: List of account IDs for approvers
            level_name: Name for this approval level
            approval_type: Type of approval required ('any_approver' or 'all_approvers')
            
        Returns:
            Dictionary containing created approval level information
        """
        # This is a custom implementation that uses transitions and approvals
        # First, get current issue status
        issue_info = self._make_jira_api_request("GET", f"/issue/{issue_id_or_key}")
        current_status = issue_info.get("fields", {}).get("status", {}).get("name", "")
        
        # Create a custom field for tracking approval level
        approvers_data = {
            "approvers": approver_account_ids,
            "approval_type": approval_type,
            "level_name": level_name,
            "status": "pending"
        }
        
        # Add as a property to the issue (this is simplified; in practice
        # you might use a custom field or another mechanism)
        property_data = {
            "approval_level": approvers_data
        }
        
        return self._make_jira_api_request(
            "PUT", 
            f"/issue/{issue_id_or_key}/properties/approval_levels",
            data=property_data
        )
    
    def get_approval_levels(self, issue_id_or_key: str) -> Dict:
        """
        Get all approval levels for an issue.
        
        Args:
            issue_id_or_key: The ID or key of the issue
            
        Returns:
            Dictionary containing approval levels information
        """
        return self._make_jira_api_request("GET", f"/issue/{issue_id_or_key}/properties/approval_levels")
    
    # ======= APPROVAL WORKFLOW OPERATIONS =======
    
    def create_approval_workflow(self, service_desk_id: str, workflow_name: str, 
                               request_type_id: str, approval_steps: List[Dict]) -> Dict:
        """
        Create a new approval workflow for a service desk request type.
        
        Args:
            service_desk_id: The ID of the service desk
            workflow_name: Name for the workflow
            request_type_id: The ID of the request type
            approval_steps: List of approval step configurations
            
        Returns:
            Dictionary containing created workflow information
        """
        # This is a custom implementation
        # In practice, this might require admin API access or workflow scheme modifications
        
        # Get project key for the service desk
        service_desk_info = self._make_api_request("GET", f"/servicedesk/{service_desk_id}")
        project_key = service_desk_info.get("projectKey", "")
        
        # Format workflow data
        workflow_data = {
            "name": workflow_name,
            "projectKey": project_key,
            "requestTypeId": request_type_id,
            "steps": approval_steps
        }
        
        # Store as a property on the project
        return self._make_jira_api_request(
            "PUT", 
            f"/project/{project_key}/properties/approval_workflow",
            data=workflow_data
        )
    
    def get_approval_workflow(self, project_key: str) -> Dict:
        """
        Get approval workflow configuration for a project.
        
        Args:
            project_key: The project key
            
        Returns:
            Dictionary containing workflow configuration
        """
        return self._make_jira_api_request("GET", f"/project/{project_key}/properties/approval_workflow")
    
    # ======= APPROVAL ANALYTICS OPERATIONS =======
    
    def get_approval_metrics(self, service_desk_id: str, 
                           time_period: str = "1m") -> Dict:
        """
        Get approval metrics for a service desk.
        
        Args:
            service_desk_id: The ID of the service desk
            time_period: Time period for metrics (e.g., "1d", "1w", "1m")
            
        Returns:
            Dictionary containing approval metrics
        """
        # This is a custom implementation that calculates metrics
        # from approval history
        
        # Get all requests for the service desk
        requests = self._get_all_service_desk_requests(service_desk_id)
        
        # Filter by time period
        requests = self._filter_requests_by_time_period(requests, time_period)
        
        # Get approval history for each request
        approvals = []
        for request in requests:
            issue_key = request.get("issueKey")
            if issue_key:
                try:
                    request_approvals = self._make_api_request("GET", f"/request/{issue_key}/approval")
                    if "values" in request_approvals:
                        approvals.extend(request_approvals["values"])
                except Exception as e:
                    logger.error(f"Error getting approvals for {issue_key}: {str(e)}")
        
        # Calculate metrics
        metrics = {
            "totalApprovals": len(approvals),
            "approved": sum(1 for a in approvals if a.get("approvalStatus") == "APPROVED"),
            "declined": sum(1 for a in approvals if a.get("approvalStatus") == "DECLINED"),
            "pending": sum(1 for a in approvals if a.get("approvalStatus") == "PENDING"),
            "avgApprovalTimeHours": self._calculate_avg_approval_time(approvals),
            "approvalsByType": self._group_approvals_by_type(approvals)
        }
        
        return metrics
    
    def _get_all_service_desk_requests(self, service_desk_id: str) -> List[Dict]:
        """Get all requests for a service desk (handles pagination)."""
        all_requests = []
        start = 0
        limit = 100
        
        while True:
            params = {
                "serviceDeskId": service_desk_id,
                "start": start,
                "limit": limit
            }
            
            result = self._make_api_request("GET", "/request", params=params)
            
            if "values" not in result or not result["values"]:
                break
                
            all_requests.extend(result["values"])
            
            if len(result["values"]) < limit:
                break
                
            start += limit
            
        return all_requests
    
    def _filter_requests_by_time_period(self, requests: List[Dict], time_period: str) -> List[Dict]:
        """Filter requests by creation time period."""
        import datetime
        
        # Parse time period to get timedelta
        unit = time_period[-1]
        amount = int(time_period[:-1])
        
        if unit == "d":
            delta = datetime.timedelta(days=amount)
        elif unit == "w":
            delta = datetime.timedelta(weeks=amount)
        elif unit == "m":
            delta = datetime.timedelta(days=amount*30)  # Approximate
        else:
            delta = datetime.timedelta(days=7)  # Default to 1 week
            
        start_date = datetime.datetime.now(datetime.timezone.utc) - delta
        
        filtered_requests = []
        for request in requests:
            created_date = request.get("createdDate")
            if created_date:
                created_dt = datetime.datetime.fromisoformat(created_date.replace("Z", "+00:00"))
                if created_dt > start_date:
                    filtered_requests.append(request)
                    
        return filtered_requests
    
    def _calculate_avg_approval_time(self, approvals: List[Dict]) -> float:
        """Calculate average approval time in hours."""
        import datetime
        
        completed_approvals = [a for a in approvals if a.get("approvalStatus") in ["APPROVED", "DECLINED"]]
        if not completed_approvals:
            return 0
            
        total_hours = 0
        count = 0
        
        for approval in completed_approvals:
            created_date = approval.get("createdDate")
            completed_date = approval.get("completedDate")
            
            if created_date and completed_date:
                created_dt = datetime.datetime.fromisoformat(created_date.replace("Z", "+00:00"))
                completed_dt = datetime.datetime.fromisoformat(completed_date.replace("Z", "+00:00"))
                diff_hours = (completed_dt - created_dt).total_seconds() / 3600
                total_hours += diff_hours
                count += 1
                
        if count == 0:
            return 0
            
        return round(total_hours / count, 2)
    
    def _group_approvals_by_type(self, approvals: List[Dict]) -> Dict:
        """Group approvals by approval type."""
        result = {}
        for approval in approvals:
            approval_type = approval.get("approvalType", "Unknown")
            if approval_type not in result:
                result[approval_type] = 0
            result[approval_type] += 1
        return result