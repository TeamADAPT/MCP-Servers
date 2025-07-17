"""Enhanced Jira integration with support for custom fields and improved API handling.

This module extends the base Jira integration with support for:
- Global custom field management
- Improved error handling and retries
- Standardized API request handling
- Field availability caching
"""

import json
import logging
import os
import time
from typing import Dict, List, Optional, Tuple, Union, Any

from atlassian import Jira
from dotenv import load_dotenv

from .config import JiraConfig
from .constants import (
    API_PATH_JIRA,
    HTTP_GET,
    HTTP_POST,
    HTTP_PUT,
    HTTP_DELETE,
    STATUS_SUCCESS,
    STATUS_ERROR,
    STATUS_WARNING,
)

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger("mcp-enhanced-jira")


class EnhancedJiraManager:
    """Enhanced Jira manager with support for custom fields and improved API handling."""

    # Custom field constants
    CUSTOM_FIELD_NAME = "customfield_10000"
    CUSTOM_FIELD_DEPARTMENT = "customfield_10001"
    CUSTOM_FIELD_EPIC_LINK = "customfield_10002"

    def __init__(self):
        """Initialize the Enhanced Jira manager with Jira client."""
        url = os.getenv("JIRA_URL")
        username = os.getenv("JIRA_USERNAME")
        token = os.getenv("JIRA_API_TOKEN")

        if not all([url, username, token]):
            raise ValueError("Missing required Jira environment variables")

        self.config = JiraConfig(url=url, username=username, api_token=token)
        self.jira = Jira(
            url=self.config.url,
            username=self.config.username,
            password=self.config.api_token,
            cloud=True,
        )
        
        # Cache for custom field availability
        self.field_cache = {}
        self.field_availability_cache = {}

    def _make_api_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        max_retries: int = 3,
        retry_delay: int = 1,
    ) -> Dict[str, Any]:
        """Make a standardized API request to Jira.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint path (without base URL)
            data: Request body data (for POST/PUT)
            params: Query parameters
            headers: Custom headers
            max_retries: Maximum number of retries
            retry_delay: Delay between retries in seconds
            
        Returns:
            Response data as dictionary
        """
        full_url = f"{self.config.url}{API_PATH_JIRA}{endpoint}"
        
        default_headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        
        if headers:
            default_headers.update(headers)
            
        retries = 0
        while retries < max_retries:
            try:
                if method == HTTP_GET:
                    response = self.jira._session.get(
                        full_url, params=params, headers=default_headers
                    )
                elif method == HTTP_POST:
                    response = self.jira._session.post(
                        full_url, params=params, data=json.dumps(data) if data else None, headers=default_headers
                    )
                elif method == HTTP_PUT:
                    response = self.jira._session.put(
                        full_url, params=params, data=json.dumps(data) if data else None, headers=default_headers
                    )
                elif method == HTTP_DELETE:
                    response = self.jira._session.delete(
                        full_url, params=params, headers=default_headers
                    )
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")
                
                if response.status_code in (200, 201, 204):
                    if response.status_code == 204 or not response.text:
                        return {"status": STATUS_SUCCESS}
                    return response.json()
                
                # Handle common errors
                if response.status_code == 401:
                    logger.error(f"Authentication failed: {response.text}")
                    return {"status": STATUS_ERROR, "message": "Authentication failed"}
                
                if response.status_code == 403:
                    logger.error(f"Permission denied: {response.text}")
                    return {"status": STATUS_ERROR, "message": "Permission denied"}
                
                if response.status_code == 404:
                    logger.error(f"Resource not found: {response.text}")
                    return {"status": STATUS_ERROR, "message": "Resource not found"}
                
                # Retry on 429 (rate limit) and 5xx errors
                if response.status_code == 429 or (500 <= response.status_code < 600):
                    retries += 1
                    logger.warning(f"Request failed with status {response.status_code}, retrying ({retries}/{max_retries})")
                    time.sleep(retry_delay)
                    continue
                
                # Other errors
                logger.error(f"API request failed with status {response.status_code}: {response.text}")
                return {"status": STATUS_ERROR, "message": f"API request failed: {response.text}"}
            
            except Exception as e:
                retries += 1
                logger.error(f"Request error: {str(e)}, retrying ({retries}/{max_retries})")
                time.sleep(retry_delay)
        
        return {"status": STATUS_ERROR, "message": "Max retries exceeded"}

    def is_field_available_in_project(self, project_key: str, field_id: str) -> bool:
        """Check if a custom field is available in a specific project.
        
        Args:
            project_key: The project key to check
            field_id: The field ID to check for
            
        Returns:
            True if the field is available, False otherwise
        """
        cache_key = f"{project_key}:{field_id}"
        if cache_key in self.field_availability_cache:
            return self.field_availability_cache[cache_key]
        
        try:
            # First, check if we have the field contexts cached
            if not self.field_cache.get(field_id):
                field_contexts = self.get_field_contexts(field_id)
                if field_contexts.get("status") == STATUS_ERROR:
                    self.field_availability_cache[cache_key] = False
                    return False
                
                self.field_cache[field_id] = field_contexts
            
            # Check if any context applies to this project
            contexts = self.field_cache[field_id].get("contexts", [])
            for context in contexts:
                if "global" in context.get("contextScope", {}).get("projects", []):
                    self.field_availability_cache[cache_key] = True
                    return True
                
                projects = context.get("contextScope", {}).get("projects", [])
                if project_key in projects:
                    self.field_availability_cache[cache_key] = True
                    return True
            
            # If we get here, the field isn't available in this project
            self.field_availability_cache[cache_key] = False
            return False
            
        except Exception as e:
            logger.error(f"Error checking field availability: {e}")
            self.field_availability_cache[cache_key] = False
            return False

    def get_custom_fields(self) -> Dict[str, Any]:
        """Get all custom fields defined in the Jira instance.
        
        Returns:
            Dictionary with custom fields information
        """
        try:
            response = self._make_api_request(
                method=HTTP_GET,
                endpoint="/field",
            )
            
            if response.get("status") == STATUS_ERROR:
                return response
            
            # Filter to include only custom fields
            custom_fields = [field for field in response if field.get("custom", False)]
            
            return {
                "status": STATUS_SUCCESS,
                "custom_fields": custom_fields,
                "count": len(custom_fields)
            }
        except Exception as e:
            logger.error(f"Error getting custom fields: {e}")
            return {"status": STATUS_ERROR, "message": str(e)}

    def get_field_contexts(self, field_id: str) -> Dict[str, Any]:
        """Get contexts for a specific field.
        
        Args:
            field_id: The field ID to get contexts for
            
        Returns:
            Dictionary with field contexts information
        """
        try:
            response = self._make_api_request(
                method=HTTP_GET,
                endpoint=f"/field/{field_id}/context",
            )
            
            if response.get("status") == STATUS_ERROR:
                return response
            
            return {
                "status": STATUS_SUCCESS,
                "field_id": field_id,
                "contexts": response.get("values", []),
                "count": len(response.get("values", []))
            }
        except Exception as e:
            logger.error(f"Error getting field contexts: {e}")
            return {"status": STATUS_ERROR, "message": str(e)}

    def create_global_field_context(self, field_id: str, name: str) -> Dict[str, Any]:
        """Create a global context for a field.
        
        Args:
            field_id: The field ID to create a global context for
            name: The name for the new context
            
        Returns:
            Dictionary with the created context information
        """
        try:
            data = {
                "name": name,
                "description": f"Global context for {name}",
                "isGlobalContext": True,
                "contextScope": {
                    "global": {},
                }
            }
            
            response = self._make_api_request(
                method=HTTP_POST,
                endpoint=f"/field/{field_id}/context",
                data=data,
            )
            
            return response
        except Exception as e:
            logger.error(f"Error creating global field context: {e}")
            return {"status": STATUS_ERROR, "message": str(e)}

    def assign_field_to_projects(
        self, field_id: str, context_id: str, project_keys: List[str]
    ) -> Dict[str, Any]:
        """Assign a field context to specific projects.
        
        Args:
            field_id: The field ID
            context_id: The context ID to assign
            project_keys: List of project keys to assign the field to
            
        Returns:
            Dictionary with the assignment result
        """
        try:
            data = {
                "projectIds": project_keys
            }
            
            response = self._make_api_request(
                method=HTTP_PUT,
                endpoint=f"/field/{field_id}/context/{context_id}/project",
                data=data,
            )
            
            if response.get("status") == STATUS_SUCCESS:
                # Update cache for each project
                for project_key in project_keys:
                    cache_key = f"{project_key}:{field_id}"
                    self.field_availability_cache[cache_key] = True
                
                return {
                    "status": STATUS_SUCCESS,
                    "field_id": field_id,
                    "context_id": context_id,
                    "projects": project_keys
                }
            
            return response
        except Exception as e:
            logger.error(f"Error assigning field to projects: {e}")
            return {"status": STATUS_ERROR, "message": str(e)}

    def set_custom_fields_as_global(self) -> Dict[str, Any]:
        """Set all custom fields to be available globally.
        
        Returns:
            Dictionary with the operation result
        """
        try:
            # Get all custom fields
            custom_fields_result = self.get_custom_fields()
            if custom_fields_result.get("status") == STATUS_ERROR:
                return custom_fields_result
            
            custom_fields = custom_fields_result.get("custom_fields", [])
            
            results = {
                "status": STATUS_SUCCESS,
                "successes": [],
                "failures": [],
                "total": len(custom_fields),
                "success_count": 0,
                "failure_count": 0
            }
            
            # Process each custom field
            for field in custom_fields:
                field_id = field.get("id")
                field_name = field.get("name")
                
                if not field_id:
                    continue
                
                # Get existing contexts
                contexts_result = self.get_field_contexts(field_id)
                if contexts_result.get("status") == STATUS_ERROR:
                    results["failures"].append({
                        "field_id": field_id,
                        "field_name": field_name,
                        "error": "Failed to get contexts"
                    })
                    results["failure_count"] += 1
                    continue
                
                # Check if already has a global context
                contexts = contexts_result.get("contexts", [])
                has_global = any(
                    context.get("isGlobalContext", False) for context in contexts
                )
                
                if has_global:
                    results["successes"].append({
                        "field_id": field_id,
                        "field_name": field_name,
                        "message": "Already has global context"
                    })
                    results["success_count"] += 1
                    continue
                
                # Create global context
                global_context_result = self.create_global_field_context(
                    field_id, f"Global {field_name}"
                )
                
                if global_context_result.get("status") == STATUS_ERROR:
                    results["failures"].append({
                        "field_id": field_id,
                        "field_name": field_name,
                        "error": "Failed to create global context"
                    })
                    results["failure_count"] += 1
                    continue
                
                results["successes"].append({
                    "field_id": field_id,
                    "field_name": field_name,
                    "message": "Created global context"
                })
                results["success_count"] += 1
            
            return results
        except Exception as e:
            logger.error(f"Error setting custom fields as global: {e}")
            return {"status": STATUS_ERROR, "message": str(e)}

    def create_issue_with_custom_fields(
        self,
        project_key: str,
        summary: str,
        issue_type: str = "Task",
        description: str = "",
        labels: Optional[List[str]] = None,
        priority: str = "Medium",
        custom_fields: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Create a Jira issue with custom fields.
        
        This method will attempt to create an issue with the specified custom fields.
        If a custom field is not available in the project, it will be omitted.
        
        Args:
            project_key: The project key
            summary: Issue summary/title
            issue_type: The issue type (Task, Bug, etc.)
            description: Issue description
            labels: List of labels
            priority: Issue priority
            custom_fields: Dictionary of custom field values
            
        Returns:
            Dictionary with the created issue
        """
        try:
            data = {
                "fields": {
                    "project": {"key": project_key},
                    "summary": summary,
                    "issuetype": {"name": issue_type},
                    "description": {
                        "type": "doc",
                        "version": 1,
                        "content": [
                            {
                                "type": "paragraph",
                                "content": [{"text": description, "type": "text"}],
                            }
                        ],
                    },
                    "priority": {"name": priority},
                }
            }
            
            if labels:
                data["fields"]["labels"] = labels
            
            # Add custom fields if they are available in the project
            if custom_fields:
                for field_id, value in custom_fields.items():
                    # Check if field is available in this project
                    if self.is_field_available_in_project(project_key, field_id):
                        data["fields"][field_id] = value
            
            response = self._make_api_request(
                method=HTTP_POST,
                endpoint="/issue",
                data=data,
            )
            
            if response.get("status") == STATUS_ERROR:
                return response
            
            # Get the created issue
            issue = self.jira.issue(response.get("key"))
            
            # Format the response
            return {
                "status": STATUS_SUCCESS,
                "key": issue.get("key"),
                "id": issue.get("id"),
                "summary": issue.get("fields", {}).get("summary"),
                "type": issue.get("fields", {}).get("issuetype", {}).get("name"),
                "status": issue.get("fields", {}).get("status", {}).get("name"),
                "url": f"{self.config.url}/browse/{issue.get('key')}",
                "project": project_key,
                "custom_fields_applied": [
                    field_id for field_id in custom_fields.keys()
                    if self.is_field_available_in_project(project_key, field_id)
                ] if custom_fields else []
            }
        except Exception as e:
            logger.error(f"Error creating issue: {e}")
            return {"status": STATUS_ERROR, "message": str(e)}


# Initialize the manager
enhanced_jira_manager = None

def get_enhanced_jira_manager() -> EnhancedJiraManager:
    """Get or create the enhanced Jira manager instance.
    
    Returns:
        EnhancedJiraManager instance
    """
    global enhanced_jira_manager
    
    if enhanced_jira_manager is None:
        try:
            enhanced_jira_manager = EnhancedJiraManager()
        except Exception as e:
            logger.error(f"Error initializing enhanced Jira manager: {e}")
            raise
    
    return enhanced_jira_manager