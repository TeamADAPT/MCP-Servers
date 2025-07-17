"""
Confluence Space Management Module

This module provides enhanced capabilities for managing Confluence spaces,
including creation, updates, permissions, and space templates.
"""

import json
import logging
from typing import Dict, List, Optional, Any, Union

import requests

from .config import ConfluenceConfig

logger = logging.getLogger(__name__)


class ConfluenceSpaceManager:
    """Class for managing Confluence spaces with enhanced capabilities."""

    def __init__(self, config: ConfluenceConfig):
        """
        Initialize the Space Manager with Confluence configuration.

        Args:
            config: ConfluenceConfig object with Confluence connection details
        """
        self.base_url = config.url.rstrip("/")
        self.auth = (config.username, config.api_token)
        self.headers = {"Content-Type": "application/json"}
        logger.debug(f"Initialized ConfluenceSpaceManager with base URL: {self.base_url}")

    def _make_api_request(
        self, method: str, endpoint: str, params: Optional[Dict] = None, data: Optional[Dict] = None
    ) -> Dict:
        """
        Make an API request to Confluence.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint to call
            params: Optional query parameters
            data: Optional data to send in request body

        Returns:
            Response data as dictionary
        """
        url = f"{self.base_url}/rest/api{endpoint}"
        json_data = json.dumps(data) if data else None

        try:
            response = requests.request(
                method=method,
                url=url,
                params=params,
                data=json_data,
                headers=self.headers,
                auth=self.auth,
            )

            if response.status_code == 204:  # No Content
                return {"status": "success"}

            if response.status_code >= 400:
                error_msg = f"API request failed: {response.status_code} - {response.text}"
                logger.error(error_msg)
                raise ValueError(error_msg)

            return response.json() if response.text else {}

        except requests.RequestException as e:
            error_msg = f"Request error for {url}: {str(e)}"
            logger.error(error_msg)
            raise ValueError(error_msg)

    # Space Operations
    def get_all_spaces(
        self, space_type: Optional[str] = None, status: Optional[str] = None, label: Optional[str] = None
    ) -> List[Dict]:
        """
        Get all spaces with optional filtering.

        Args:
            space_type: Filter by space type (personal or global)
            status: Filter by status (current or archived)
            label: Filter by label

        Returns:
            List of space dictionaries
        """
        params = {"limit": 100}
        if space_type:
            params["type"] = space_type
        if status:
            params["status"] = status
        if label:
            params["label"] = label

        spaces = []
        start = 0

        while True:
            params["start"] = start
            response = self._make_api_request("GET", "/space", params=params)
            
            if "results" in response and response["results"]:
                spaces.extend(response["results"])
                if response.get("_links", {}).get("next"):
                    start += len(response["results"])
                else:
                    break
            else:
                break

        return spaces

    def get_space(self, space_key: str, expand: Optional[str] = None) -> Dict:
        """
        Get a specific space by key.

        Args:
            space_key: The space key
            expand: Optional comma-separated list of properties to expand

        Returns:
            Space data
        """
        params = {}
        if expand:
            params["expand"] = expand

        return self._make_api_request("GET", f"/space/{space_key}", params=params)

    def create_space(
        self, key: str, name: str, description: Optional[str] = None, is_private: bool = False
    ) -> Dict:
        """
        Create a new space.

        Args:
            key: Space key (must be unique)
            name: Space name
            description: Optional space description
            is_private: Whether the space should be private

        Returns:
            Created space data
        """
        # Validate space key format
        if not key or not key.isalnum():
            raise ValueError("Space key must be alphanumeric")

        data = {
            "key": key,
            "name": name,
            "description": {
                "plain": {"value": description or "", "representation": "plain"}
            },
            "type": "global"
        }

        space = self._make_api_request("POST", "/space", data=data)
        
        # Set permissions if private
        if is_private:
            self.add_space_permission(
                key, "user", "unlicensed_users", "read", "false"
            )
            self.add_space_permission(
                key, "user", "anonymous", "read", "false"
            )
            
        return space

    def update_space(
        self, space_key: str, name: Optional[str] = None, description: Optional[str] = None
    ) -> Dict:
        """
        Update a space's basic information.

        Args:
            space_key: The space key
            name: New space name
            description: New space description

        Returns:
            Updated space data
        """
        # Get current space data
        current = self.get_space(space_key)
        
        data = {
            "name": name or current.get("name", ""),
            "description": {
                "plain": {
                    "value": description or current.get("description", {}).get("plain", {}).get("value", ""),
                    "representation": "plain"
                }
            },
            "type": current.get("type", "global")
        }

        return self._make_api_request("PUT", f"/space/{space_key}", data=data)

    def delete_space(self, space_key: str) -> Dict:
        """
        Delete a space.

        Args:
            space_key: The space key

        Returns:
            Status response
        """
        return self._make_api_request("DELETE", f"/space/{space_key}")

    def archive_space(self, space_key: str) -> Dict:
        """
        Archive a space.

        Args:
            space_key: The space key

        Returns:
            Status response
        """
        return self._make_api_request("PUT", f"/space/{space_key}/archive")

    def restore_space(self, space_key: str) -> Dict:
        """
        Restore an archived space.

        Args:
            space_key: The space key

        Returns:
            Status response
        """
        return self._make_api_request("DELETE", f"/space/{space_key}/archive")

    # Space Content
    def get_space_content(
        self, space_key: str, content_type: Optional[str] = None, expand: Optional[str] = None
    ) -> List[Dict]:
        """
        Get content in a space.

        Args:
            space_key: The space key
            content_type: Optional content type filter (page, blogpost, etc.)
            expand: Optional properties to expand

        Returns:
            List of content items
        """
        params = {"limit": 100}
        if content_type:
            params["type"] = content_type
        if expand:
            params["expand"] = expand

        results = []
        start = 0

        while True:
            params["start"] = start
            response = self._make_api_request(
                "GET", f"/space/{space_key}/content", params=params
            )
            
            if "results" in response and response["results"]:
                results.extend(response["results"])
                if "next" in response.get("_links", {}):
                    start += len(response["results"])
                else:
                    break
            else:
                break

        return results

    # Space Templates
    def create_space_from_template(self, key: str, name: str, template_key: str) -> Dict:
        """
        Create a space based on an existing space as template.

        Args:
            key: New space key
            name: New space name
            template_key: Key of space to use as template

        Returns:
            Created space data and task ID for tracking
        """
        data = {
            "spaceKey": key,
            "name": name,
            "copyPermissions": True,
            "copyContentPermissions": True
        }
        
        response = self._make_api_request(
            "POST", f"/space/{template_key}/copy", data=data
        )
        
        return {
            "status": "in_progress",
            "task_id": response.get("id", ""),
            "new_space_key": key,
            "template_key": template_key
        }

    def get_task_status(self, task_id: str) -> Dict:
        """
        Get the status of a long-running task.

        Args:
            task_id: The task ID

        Returns:
            Task status information
        """
        return self._make_api_request("GET", f"/longtask/{task_id}")

    # Space Permissions
    def get_space_permissions(self, space_key: str) -> Dict:
        """
        Get permissions for a space.

        Args:
            space_key: The space key

        Returns:
            Space permissions data
        """
        return self._make_api_request("GET", f"/space/{space_key}/permission")

    def add_space_permission(
        self, space_key: str, type_: str, subject: str, operation: str, value: str
    ) -> Dict:
        """
        Add a permission to a space.

        Args:
            space_key: The space key
            type_: Permission type (user, group)
            subject: User or group name
            operation: Permission operation (read, create, etc.)
            value: Permission value (true, false)

        Returns:
            Status response
        """
        data = {
            "subject": {
                "type": type_,
                "identifier": subject
            },
            "operation": {
                "key": operation,
                "target": "space"
            },
            "allow": value.lower() == "true"
        }
        
        return self._make_api_request(
            "POST", f"/space/{space_key}/permission", data=data
        )

    def remove_space_permission(self, space_key: str, permission_id: str) -> Dict:
        """
        Remove a permission from a space.

        Args:
            space_key: The space key
            permission_id: The permission ID to remove

        Returns:
            Status response
        """
        return self._make_api_request(
            "DELETE", f"/space/{space_key}/permission/{permission_id}"
        )

    # Space Properties
    def get_space_property(self, space_key: str, property_key: str) -> Dict:
        """
        Get a space property.

        Args:
            space_key: The space key
            property_key: The property key

        Returns:
            Property data
        """
        return self._make_api_request(
            "GET", f"/space/{space_key}/property/{property_key}"
        )

    def set_space_property(self, space_key: str, property_key: str, value: Any) -> Dict:
        """
        Set a space property.

        Args:
            space_key: The space key
            property_key: The property key
            value: The property value

        Returns:
            Updated property data
        """
        data = {
            "key": property_key,
            "value": value
        }
        
        return self._make_api_request(
            "PUT", f"/space/{space_key}/property/{property_key}", data=data
        )

    def delete_space_property(self, space_key: str, property_key: str) -> Dict:
        """
        Delete a space property.

        Args:
            space_key: The space key
            property_key: The property key

        Returns:
            Status response
        """
        return self._make_api_request(
            "DELETE", f"/space/{space_key}/property/{property_key}"
        )