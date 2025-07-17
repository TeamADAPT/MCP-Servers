"""
Jira Service Management Advanced Queue Management Module.

This module provides advanced queue management capabilities for Jira Service Management,
allowing for queue creation, modification, and advanced filtering of issues.

Author: Claude Code
Date: May 7, 2025
"""

import logging
from typing import Dict, List, Optional, Union, Any
import os
import requests
import json

# Configure logging
logger = logging.getLogger("mcp-jsm-queue")

class JSMQueueManager:
    """
    Handles advanced queue operations for Jira Service Management.
    
    This class provides functionality for working with JSM queues,
    including creating custom queues, applying filters, and managing
    queue assignments.
    """
    
    def __init__(self, jsm_client=None, url=None, username=None, api_token=None):
        """
        Initialize the JSM Queue Manager.
        
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
            self.jira_api_base = f"{self.url}/rest/api/3"  # For Jira API operations
            
            # Authentication tuple for requests
            self.auth = (self.username, self.api_token)
            
            # Standard headers for API requests
            self.headers = {
                "Accept": "application/json",
                "Content-Type": "application/json"
            }
            
            logger.info(f"Initialized JSM Queue Manager for {self.url}")
            
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
                    raise ValueError("Queue resource not found")
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
        Make a request to the Jira API (for operations not available in Service Desk API).
        
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
            
    # ======= QUEUE MANAGEMENT OPERATIONS =======
    
    def get_queues(self, service_desk_id: str, include_count: bool = False, start: int = 0, limit: int = 50) -> Dict:
        """
        Get queues for a service desk with enhanced options.
        
        Args:
            service_desk_id: The ID of the service desk
            include_count: Whether to include issue count for each queue
            start: Starting index for pagination
            limit: Maximum results to return
            
        Returns:
            Dictionary containing queue information with optional counts
        """
        params = {"start": start, "limit": limit}
        result = self._make_api_request("GET", f"/servicedesk/{service_desk_id}/queue", params=params)
        
        if include_count and "values" in result:
            for queue in result["values"]:
                # Get count for each queue
                queue_id = queue["id"]
                count_result = self._get_queue_count(service_desk_id, queue_id)
                queue["issueCount"] = count_result.get("issueCount", 0)
                
        return result
    
    def _get_queue_count(self, service_desk_id: str, queue_id: str) -> Dict:
        """
        Get the count of issues in a queue.
        
        Args:
            service_desk_id: The ID of the service desk
            queue_id: The ID of the queue
            
        Returns:
            Dictionary containing the issue count
        """
        # This is a private helper method to get the count
        params = {"limit": 1}  # We only need the count, not the actual issues
        result = self._make_api_request("GET", f"/servicedesk/{service_desk_id}/queue/{queue_id}/issue", params=params)
        
        return {"issueCount": result.get("size", 0)}
    
    def get_queue_issues(self, service_desk_id: str, queue_id: str, 
                        start: int = 0, limit: int = 50,
                        order_by: Optional[str] = None,
                        expand: Optional[List[str]] = None) -> Dict:
        """
        Get issues in a queue with advanced filtering options.
        
        Args:
            service_desk_id: The ID of the service desk
            queue_id: The ID of the queue
            start: Starting index for pagination
            limit: Maximum results to return
            order_by: Field to order results by (e.g., "created", "-priority")
            expand: List of fields to expand in the response
            
        Returns:
            Dictionary containing issue information
        """
        params = {"start": start, "limit": limit}
        
        if order_by:
            params["orderBy"] = order_by
            
        if expand:
            params["expand"] = ",".join(expand)
            
        return self._make_api_request("GET", f"/servicedesk/{service_desk_id}/queue/{queue_id}/issue", params=params)
    
    def create_custom_queue(self, service_desk_id: str, name: str, jql_filter: str, description: Optional[str] = None) -> Dict:
        """
        Create a custom queue with JQL filter for a service desk.
        
        Args:
            service_desk_id: The ID of the service desk
            name: Queue name
            jql_filter: JQL query to filter issues in the queue
            description: Optional queue description
            
        Returns:
            Dictionary containing created queue information
        """
        # This requires Jira API as it's not available in Service Desk API
        project_key = self._get_project_key_for_service_desk(service_desk_id)
        
        data = {
            "name": name,
            "description": description or "",
            "jql": jql_filter,
            "projectKey": project_key,
            "isShared": False
        }
        
        return self._make_jira_api_request("POST", "/filter", data=data)
    
    def _get_project_key_for_service_desk(self, service_desk_id: str) -> str:
        """
        Get the project key for a service desk ID.
        
        Args:
            service_desk_id: The ID of the service desk
            
        Returns:
            Project key for the service desk
        """
        # Get service desk details which include project key
        service_desk_info = self._make_api_request("GET", f"/servicedesk/{service_desk_id}")
        return service_desk_info.get("projectKey", "")
    
    def update_custom_queue(self, filter_id: str, name: Optional[str] = None, 
                           jql_filter: Optional[str] = None, 
                           description: Optional[str] = None) -> Dict:
        """
        Update a custom queue.
        
        Args:
            filter_id: The ID of the filter/queue to update
            name: Optional new queue name
            jql_filter: Optional new JQL query
            description: Optional new description
            
        Returns:
            Dictionary containing updated queue information
        """
        # Get current filter details
        current_filter = self._make_jira_api_request("GET", f"/filter/{filter_id}")
        
        # Update only provided fields
        data = {
            "name": name or current_filter.get("name", ""),
            "description": description if description is not None else current_filter.get("description", ""),
            "jql": jql_filter or current_filter.get("jql", "")
        }
        
        return self._make_jira_api_request("PUT", f"/filter/{filter_id}", data=data)
    
    def delete_custom_queue(self, filter_id: str) -> Dict:
        """
        Delete a custom queue.
        
        Args:
            filter_id: The ID of the filter/queue to delete
            
        Returns:
            Dictionary containing result information
        """
        return self._make_jira_api_request("DELETE", f"/filter/{filter_id}")
    
    # ======= QUEUE ASSIGNMENT OPERATIONS =======
    
    def assign_issue_to_queue(self, issue_id_or_key: str, queue_id: str) -> Dict:
        """
        Assign an issue to a specific queue (by updating relevant fields).
        
        Args:
            issue_id_or_key: The ID or key of the issue
            queue_id: The ID of the target queue
            
        Returns:
            Dictionary containing result information
        """
        # Get queue details to determine its filter criteria
        queue_filter = self._make_jira_api_request("GET", f"/filter/{queue_id}")
        jql = queue_filter.get("jql", "")
        
        # Extract field updates needed to match the queue's JQL
        field_updates = self._extract_field_updates_from_jql(jql)
        
        # Update the issue with the necessary fields
        data = {
            "fields": field_updates
        }
        
        return self._make_jira_api_request("PUT", f"/issue/{issue_id_or_key}", data=data)
    
    def _extract_field_updates_from_jql(self, jql: str) -> Dict:
        """
        Extract field updates needed to match a JQL query.
        This is a simplified implementation and may need enhancement for complex JQL.
        
        Args:
            jql: JQL query string
            
        Returns:
            Dictionary of field updates needed
        """
        field_updates = {}
        
        # Simple JQL parser - this is basic and would need enhancement for production
        if "status =" in jql:
            # Extract status name
            import re
            status_match = re.search(r"status\s*=\s*['\"]([^'\"]+)['\"]", jql)
            if status_match:
                status_name = status_match.group(1)
                # We would need to get the transition ID for this status
                # This is simplified and assumes direct field setting
                field_updates["status"] = {"name": status_name}
                
        if "priority =" in jql:
            priority_match = re.search(r"priority\s*=\s*['\"]([^'\"]+)['\"]", jql)
            if priority_match:
                priority_name = priority_match.group(1)
                field_updates["priority"] = {"name": priority_name}
                
        # Add more field extractors as needed
        
        return field_updates
    
    # ======= QUEUE METRICS OPERATIONS =======
    
    def get_queue_metrics(self, service_desk_id: str, queue_id: str, 
                         time_period: str = "1w") -> Dict:
        """
        Get performance metrics for a queue.
        
        Args:
            service_desk_id: The ID of the service desk
            queue_id: The ID of the queue
            time_period: Time period for metrics (e.g., "1d", "1w", "1m")
            
        Returns:
            Dictionary containing queue metrics
        """
        # This is a custom implementation as direct metrics API might not exist
        # We'll get issues and calculate metrics ourselves
        all_issues = self._get_all_queue_issues(service_desk_id, queue_id)
        
        # Calculate various metrics
        metrics = {
            "totalIssues": len(all_issues),
            "averageResolutionTime": self._calculate_avg_resolution_time(all_issues),
            "averageResponseTime": self._calculate_avg_response_time(all_issues),
            "issuesByStatus": self._group_issues_by_status(all_issues),
            "issuesByPriority": self._group_issues_by_priority(all_issues),
            "resolvedLastPeriod": self._count_resolved_in_period(all_issues, time_period),
            "createdLastPeriod": self._count_created_in_period(all_issues, time_period)
        }
        
        return metrics
    
    def _get_all_queue_issues(self, service_desk_id: str, queue_id: str) -> List[Dict]:
        """Get all issues in a queue (handles pagination)."""
        all_issues = []
        start = 0
        limit = 100
        
        while True:
            result = self._make_api_request(
                "GET", 
                f"/servicedesk/{service_desk_id}/queue/{queue_id}/issue", 
                params={"start": start, "limit": limit, "expand": "fields"}
            )
            
            if "values" not in result or not result["values"]:
                break
                
            all_issues.extend(result["values"])
            
            if len(result["values"]) < limit:
                break
                
            start += limit
            
        return all_issues
    
    def _calculate_avg_resolution_time(self, issues: List[Dict]) -> Dict:
        """Calculate average resolution time for issues."""
        import datetime
        
        resolved_issues = [issue for issue in issues if issue.get("fields", {}).get("resolutiondate")]
        if not resolved_issues:
            return {"hours": 0, "days": 0}
            
        total_seconds = 0
        for issue in resolved_issues:
            created = issue.get("fields", {}).get("created")
            resolved = issue.get("fields", {}).get("resolutiondate")
            
            if created and resolved:
                # Parse ISO format dates and calculate difference
                created_dt = datetime.datetime.fromisoformat(created.replace("Z", "+00:00"))
                resolved_dt = datetime.datetime.fromisoformat(resolved.replace("Z", "+00:00"))
                diff_seconds = (resolved_dt - created_dt).total_seconds()
                total_seconds += diff_seconds
                
        avg_seconds = total_seconds / len(resolved_issues)
        return {
            "hours": round(avg_seconds / 3600, 2),
            "days": round(avg_seconds / 86400, 2)
        }
    
    def _calculate_avg_response_time(self, issues: List[Dict]) -> Dict:
        """Calculate average first response time for issues."""
        # This is a simplified version and would need actual first response timestamp
        # For a real implementation, you'd need to check the first comment timestamp
        return {"hours": 0, "days": 0}  # Placeholder
    
    def _group_issues_by_status(self, issues: List[Dict]) -> Dict:
        """Group issues by status."""
        result = {}
        for issue in issues:
            status = issue.get("fields", {}).get("status", {}).get("name", "Unknown")
            if status not in result:
                result[status] = 0
            result[status] += 1
        return result
    
    def _group_issues_by_priority(self, issues: List[Dict]) -> Dict:
        """Group issues by priority."""
        result = {}
        for issue in issues:
            priority = issue.get("fields", {}).get("priority", {}).get("name", "Unknown")
            if priority not in result:
                result[priority] = 0
            result[priority] += 1
        return result
    
    def _count_resolved_in_period(self, issues: List[Dict], time_period: str) -> int:
        """Count issues resolved in the given time period."""
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
        
        count = 0
        for issue in issues:
            resolved_date = issue.get("fields", {}).get("resolutiondate")
            if resolved_date:
                resolved_dt = datetime.datetime.fromisoformat(resolved_date.replace("Z", "+00:00"))
                if resolved_dt > start_date:
                    count += 1
                    
        return count
    
    def _count_created_in_period(self, issues: List[Dict], time_period: str) -> int:
        """Count issues created in the given time period."""
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
        
        count = 0
        for issue in issues:
            created_date = issue.get("fields", {}).get("created")
            if created_date:
                created_dt = datetime.datetime.fromisoformat(created_date.replace("Z", "+00:00"))
                if created_dt > start_date:
                    count += 1
                    
        return count