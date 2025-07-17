"""
JSM Queue Module

This module provides functionality for working with Jira Service Management (JSM)
queues, including custom queues, queue metrics, and analytics.
"""

import json
import logging
import os
import re
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta

import requests

from .jsm import JiraServiceManager

logger = logging.getLogger(__name__)

class JSMQueueManager:
    """
    Manages Jira Service Management queues and queue analytics.
    """

    def __init__(
        self, 
        jsm_client: Optional[JiraServiceManager] = None,
        url: Optional[str] = None, 
        username: Optional[str] = None, 
        api_token: Optional[str] = None
    ):
        """
        Initialize the JSM Queue Manager.

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
        
        logger.debug(f"Initialized JSMQueueManager with URL: {self.url}")

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

    # Queue Operations
    def get_queues(
        self, service_desk_id: str, include_counts: bool = False
    ) -> List[Dict]:
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
        start: int = 0, limit: int = 50,
        expand: Optional[str] = None
    ) -> List[Dict]:
        """
        Get issues in a queue.

        Args:
            service_desk_id: The service desk ID
            queue_id: The queue ID
            start: Starting index for pagination
            limit: Maximum number of results to return
            expand: Optional fields to expand

        Returns:
            List of issues
        """
        params = {
            "start": start,
            "limit": limit
        }
        
        if expand:
            params["expand"] = expand
            
        response = self._make_api_request(
            "GET", f"/servicedesk/{service_desk_id}/queue/{queue_id}/issue",
            params=params
        )
        return response.get("values", [])

    def create_custom_queue(
        self, service_desk_id: str, name: str, jql: str, description: Optional[str] = None
    ) -> Dict:
        """
        Create a custom queue for a service desk.

        Args:
            service_desk_id: The service desk ID
            name: Queue name
            jql: JQL query for the queue
            description: Optional queue description

        Returns:
            Created queue
        """
        # Get service desk
        service_desk = self.jsm_client.get_service_desk(service_desk_id)
        project_key = service_desk.get("projectKey")
        
        # Get project
        project = self._make_jira_api_request("GET", f"/project/{project_key}")
        
        # Create queue property
        data = {
            "name": name,
            "jql": jql
        }
        
        if description:
            data["description"] = description
            
        # Get next available custom queue ID
        custom_queues = self._get_custom_queues(project["id"])
        next_id = max([q.get("id", 0) for q in custom_queues] + [100]) + 1
        
        property_key = f"sd.queue.custom.{next_id}"
        property_data = {
            "key": property_key,
            "value": data
        }
        
        response = self._make_jira_api_request(
            "PUT", f"/project/{project['id']}/properties/{property_key}",
            data=property_data
        )
        
        return {
            "id": str(next_id),
            "name": name,
            "jql": jql,
            "description": description
        }

    def update_custom_queue(
        self, service_desk_id: str, queue_id: str,
        name: Optional[str] = None, jql: Optional[str] = None,
        description: Optional[str] = None
    ) -> Dict:
        """
        Update a custom queue.

        Args:
            service_desk_id: The service desk ID
            queue_id: The queue ID
            name: Optional new queue name
            jql: Optional new JQL query
            description: Optional new description

        Returns:
            Updated queue
        """
        # Get service desk
        service_desk = self.jsm_client.get_service_desk(service_desk_id)
        project_key = service_desk.get("projectKey")
        
        # Get project
        project = self._make_jira_api_request("GET", f"/project/{project_key}")
        
        # Get existing queue
        property_key = f"sd.queue.custom.{queue_id}"
        try:
            response = self._make_jira_api_request(
                "GET", f"/project/{project['id']}/properties/{property_key}"
            )
            queue_data = response.get("value", {})
        except ValueError:
            raise ValueError(f"Queue {queue_id} not found")
            
        # Update queue data
        if name:
            queue_data["name"] = name
            
        if jql:
            queue_data["jql"] = jql
            
        if description is not None:
            queue_data["description"] = description
            
        # Update property
        property_data = {
            "key": property_key,
            "value": queue_data
        }
        
        response = self._make_jira_api_request(
            "PUT", f"/project/{project['id']}/properties/{property_key}",
            data=property_data
        )
        
        return {
            "id": queue_id,
            **queue_data
        }

    def delete_custom_queue(
        self, service_desk_id: str, queue_id: str
    ) -> Dict:
        """
        Delete a custom queue.

        Args:
            service_desk_id: The service desk ID
            queue_id: The queue ID

        Returns:
            Status response
        """
        # Get service desk
        service_desk = self.jsm_client.get_service_desk(service_desk_id)
        project_key = service_desk.get("projectKey")
        
        # Get project
        project = self._make_jira_api_request("GET", f"/project/{project_key}")
        
        # Delete queue property
        property_key = f"sd.queue.custom.{queue_id}"
        
        try:
            self._make_jira_api_request(
                "DELETE", f"/project/{project['id']}/properties/{property_key}"
            )
            return {"status": "success", "message": f"Queue {queue_id} deleted"}
        except ValueError as e:
            return {"status": "error", "message": str(e)}

    def _get_custom_queues(self, project_id: str) -> List[Dict]:
        """
        Get custom queues for a project.

        Args:
            project_id: The project ID

        Returns:
            List of custom queues
        """
        # Get all project properties
        response = self._make_jira_api_request(
            "GET", f"/project/{project_id}/properties"
        )
        
        keys = response.get("keys", [])
        custom_queues = []
        
        for key in keys:
            if key["key"].startswith("sd.queue.custom."):
                try:
                    key_id = int(key["key"].split(".")[-1])
                    
                    # Get property value
                    property_response = self._make_jira_api_request(
                        "GET", f"/project/{project_id}/properties/{key['key']}"
                    )
                    
                    value = property_response.get("value", {})
                    custom_queues.append({
                        "id": key_id,
                        **value
                    })
                except (ValueError, IndexError):
                    continue
                    
        return custom_queues

    # Queue Assignment
    def assign_issue_to_queue(
        self, service_desk_id: str, queue_id: str, issue_id: str
    ) -> Dict:
        """
        Assign an issue to a queue by updating fields based on the queue's JQL.

        Args:
            service_desk_id: The service desk ID
            queue_id: The queue ID
            issue_id: The issue ID

        Returns:
            Status response
        """
        # Get service desk
        service_desk = self.jsm_client.get_service_desk(service_desk_id)
        project_key = service_desk.get("projectKey")
        
        # Get project
        project = self._make_jira_api_request("GET", f"/project/{project_key}")
        
        # Get queue JQL
        property_key = f"sd.queue.custom.{queue_id}"
        try:
            response = self._make_jira_api_request(
                "GET", f"/project/{project['id']}/properties/{property_key}"
            )
            queue_data = response.get("value", {})
            jql = queue_data.get("jql", "")
        except ValueError:
            raise ValueError(f"Queue {queue_id} not found")
            
        # Extract field updates from JQL
        field_updates = self._extract_field_updates_from_jql(jql)
        
        if not field_updates:
            return {
                "status": "error",
                "message": "Could not determine field updates from queue JQL"
            }
            
        # Update issue fields
        data = {
            "fields": field_updates
        }
        
        try:
            self._make_jira_api_request("PUT", f"/issue/{issue_id}", data=data)
            return {"status": "success", "message": f"Issue {issue_id} assigned to queue {queue_id}"}
        except ValueError as e:
            return {"status": "error", "message": str(e)}

    def _extract_field_updates_from_jql(self, jql: str) -> Dict:
        """
        Extract field updates from JQL query.

        Args:
            jql: JQL query

        Returns:
            Field updates dict
        """
        field_updates = {}
        
        # Common JQL patterns
        patterns = [
            (r'status\s*=\s*"?([^"]+)"?', "status", "name"),
            (r'priority\s*=\s*"?([^"]+)"?', "priority", "name"),
            (r'assignee\s*=\s*"?([^"]+)"?', "assignee", "name"),
            (r'labels\s*=\s*"?([^"]+)"?', "labels", None)
        ]
        
        for pattern, field, subfield in patterns:
            matches = re.findall(pattern, jql, re.IGNORECASE)
            if matches:
                value = matches[0].strip('"')
                if subfield:
                    field_updates[field] = {subfield: value}
                else:
                    field_updates[field] = value
                    
        return field_updates

    # Queue Metrics and Analytics
    def get_queue_metrics(
        self, service_desk_id: str, queue_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict:
        """
        Get metrics for a queue.

        Args:
            service_desk_id: The service desk ID
            queue_id: The queue ID
            start_date: Optional start date for time-based metrics
            end_date: Optional end date for time-based metrics

        Returns:
            Queue metrics
        """
        # Set default date range if not provided
        if not end_date:
            end_date = datetime.now()
        if not start_date:
            start_date = end_date - timedelta(days=30)
            
        # Get all issues in the queue
        all_issues = []
        start = 0
        limit = 100
        
        while True:
            batch = self.get_queue_issues(
                service_desk_id, queue_id, 
                start=start, limit=limit, 
                expand="changelog,status,priority,assignee,created,updated,resolution"
            )
            
            if not batch:
                break
                
            all_issues.extend(batch)
            
            if len(batch) < limit:
                break
                
            start += limit
            
        # Filter by date range
        time_range_issues = [i for i in all_issues if self._is_issue_in_time_range(i, start_date, end_date)]
        
        # Calculate metrics
        metrics = {
            "total_issues": len(all_issues),
            "issues_in_time_range": len(time_range_issues),
            "avg_resolution_time": self._calculate_avg_resolution_time(time_range_issues),
            "avg_response_time": self._calculate_avg_response_time(time_range_issues),
            "status_breakdown": self._get_status_breakdown(all_issues),
            "priority_breakdown": self._get_priority_breakdown(all_issues),
            "creation_rate": self._calculate_creation_rate(time_range_issues, start_date, end_date),
            "resolution_rate": self._calculate_resolution_rate(time_range_issues, start_date, end_date),
            "time_period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            }
        }
        
        return metrics

    def _is_issue_in_time_range(
        self, issue: Dict, start_date: datetime, end_date: datetime
    ) -> bool:
        """
        Check if an issue is in the specified time range.

        Args:
            issue: Issue data
            start_date: Start date
            end_date: End date

        Returns:
            True if issue is in time range
        """
        created_str = issue.get("fields", {}).get("created")
        if not created_str:
            return False
            
        try:
            created_date = datetime.fromisoformat(created_str.replace("Z", "+00:00"))
            return start_date <= created_date <= end_date
        except (ValueError, TypeError):
            return False

    def _calculate_avg_resolution_time(self, issues: List[Dict]) -> float:
        """
        Calculate average resolution time in hours.

        Args:
            issues: List of issues

        Returns:
            Average resolution time in hours
        """
        resolved_issues = []
        
        for issue in issues:
            created_str = issue.get("fields", {}).get("created")
            resolved_str = issue.get("fields", {}).get("resolutiondate")
            
            if not (created_str and resolved_str):
                continue
                
            try:
                created_date = datetime.fromisoformat(created_str.replace("Z", "+00:00"))
                resolved_date = datetime.fromisoformat(resolved_str.replace("Z", "+00:00"))
                duration = (resolved_date - created_date).total_seconds() / 3600  # Convert to hours
                resolved_issues.append(duration)
            except (ValueError, TypeError):
                continue
                
        if not resolved_issues:
            return 0
            
        return sum(resolved_issues) / len(resolved_issues)

    def _calculate_avg_response_time(self, issues: List[Dict]) -> float:
        """
        Calculate average first response time in hours.

        Args:
            issues: List of issues

        Returns:
            Average first response time in hours
        """
        response_times = []
        
        for issue in issues:
            created_str = issue.get("fields", {}).get("created")
            
            # Look for first comment in changelog
            changelog = issue.get("changelog", {}).get("histories", [])
            first_comment_date = None
            
            for history in changelog:
                for item in history.get("items", []):
                    if item.get("field") == "Comment" and item.get("fieldtype") == "jira":
                        comment_date_str = history.get("created")
                        try:
                            comment_date = datetime.fromisoformat(comment_date_str.replace("Z", "+00:00"))
                            if not first_comment_date or comment_date < first_comment_date:
                                first_comment_date = comment_date
                        except (ValueError, TypeError):
                            continue
            
            if not (created_str and first_comment_date):
                continue
                
            try:
                created_date = datetime.fromisoformat(created_str.replace("Z", "+00:00"))
                duration = (first_comment_date - created_date).total_seconds() / 3600  # Convert to hours
                response_times.append(duration)
            except (ValueError, TypeError):
                continue
                
        if not response_times:
            return 0
            
        return sum(response_times) / len(response_times)

    def _get_status_breakdown(self, issues: List[Dict]) -> Dict[str, int]:
        """
        Get breakdown of issues by status.

        Args:
            issues: List of issues

        Returns:
            Status breakdown
        """
        breakdown = {}
        
        for issue in issues:
            status = issue.get("fields", {}).get("status", {}).get("name", "Unknown")
            breakdown[status] = breakdown.get(status, 0) + 1
            
        return breakdown

    def _get_priority_breakdown(self, issues: List[Dict]) -> Dict[str, int]:
        """
        Get breakdown of issues by priority.

        Args:
            issues: List of issues

        Returns:
            Priority breakdown
        """
        breakdown = {}
        
        for issue in issues:
            priority = issue.get("fields", {}).get("priority", {}).get("name", "Unknown")
            breakdown[priority] = breakdown.get(priority, 0) + 1
            
        return breakdown

    def _calculate_creation_rate(
        self, issues: List[Dict], start_date: datetime, end_date: datetime
    ) -> Dict[str, float]:
        """
        Calculate issue creation rate.

        Args:
            issues: List of issues
            start_date: Start date
            end_date: End date

        Returns:
            Creation rate metrics
        """
        # Group issues by creation date
        days = {}
        weeks = {}
        months = {}
        
        for issue in issues:
            created_str = issue.get("fields", {}).get("created")
            if not created_str:
                continue
                
            try:
                created_date = datetime.fromisoformat(created_str.replace("Z", "+00:00"))
                day_key = created_date.strftime("%Y-%m-%d")
                week_key = created_date.strftime("%Y-%W")
                month_key = created_date.strftime("%Y-%m")
                
                days[day_key] = days.get(day_key, 0) + 1
                weeks[week_key] = weeks.get(week_key, 0) + 1
                months[month_key] = months.get(month_key, 0) + 1
            except (ValueError, TypeError):
                continue
        
        # Calculate time span
        time_span_days = (end_date - start_date).days or 1  # Avoid division by zero
        time_span_weeks = time_span_days / 7
        time_span_months = time_span_days / 30
        
        return {
            "per_day": len(issues) / time_span_days,
            "per_week": len(issues) / time_span_weeks,
            "per_month": len(issues) / time_span_months,
            "days": days,
            "weeks": weeks,
            "months": months
        }

    def _calculate_resolution_rate(
        self, issues: List[Dict], start_date: datetime, end_date: datetime
    ) -> Dict[str, float]:
        """
        Calculate issue resolution rate.

        Args:
            issues: List of issues
            start_date: Start date
            end_date: End date

        Returns:
            Resolution rate metrics
        """
        # Filter to resolved issues
        resolved_issues = [i for i in issues if i.get("fields", {}).get("resolutiondate")]
        
        # Group issues by resolution date
        days = {}
        weeks = {}
        months = {}
        
        for issue in resolved_issues:
            resolved_str = issue.get("fields", {}).get("resolutiondate")
            if not resolved_str:
                continue
                
            try:
                resolved_date = datetime.fromisoformat(resolved_str.replace("Z", "+00:00"))
                day_key = resolved_date.strftime("%Y-%m-%d")
                week_key = resolved_date.strftime("%Y-%W")
                month_key = resolved_date.strftime("%Y-%m")
                
                days[day_key] = days.get(day_key, 0) + 1
                weeks[week_key] = weeks.get(week_key, 0) + 1
                months[month_key] = months.get(month_key, 0) + 1
            except (ValueError, TypeError):
                continue
        
        # Calculate time span
        time_span_days = (end_date - start_date).days or 1  # Avoid division by zero
        time_span_weeks = time_span_days / 7
        time_span_months = time_span_days / 30
        
        return {
            "per_day": len(resolved_issues) / time_span_days,
            "per_week": len(resolved_issues) / time_span_weeks,
            "per_month": len(resolved_issues) / time_span_months,
            "days": days,
            "weeks": weeks,
            "months": months
        }