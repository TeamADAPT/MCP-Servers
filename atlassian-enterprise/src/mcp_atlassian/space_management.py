"""
Confluence Space Management Module.

This module provides space management functionality for Confluence.
"""

import logging
import json
import requests
from typing import Dict, List, Optional, Any, Union

from .config import ConfluenceConfig

# Configure logging
logger = logging.getLogger("mcp-atlassian")


class ConfluenceSpaceManager:
    """Manages Confluence spaces, including creation, archiving, and permissions."""

    def __init__(self, config: ConfluenceConfig):
        """
        Initialize the ConfluenceSpaceManager.

        Args:
            config: ConfluenceConfig object with Confluence credentials
        """
        self.config = config
        self.base_url = config.url
        self.auth = (config.username, config.api_token)
        self.headers = {"Content-Type": "application/json"}
        
    def _make_api_request(self, method: str, endpoint: str, data: Optional[Dict] = None,
                         params: Optional[Dict] = None, files: Optional[Dict] = None) -> Dict:
        """
        Make an API request to Confluence.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint (without base URL)
            data: Request data
            params: Query parameters
            files: Files for multipart/form-data requests
            
        Returns:
            Response data as dictionary
        
        Raises:
            ValueError: For API errors with appropriate message
        """
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = requests.request(
                method=method,
                url=url,
                json=data,
                params=params,
                files=files,
                auth=self.auth,
                headers=self.headers
            )
            
            # Check for errors
            if response.status_code >= 400:
                error_msg = f"API request failed: {response.status_code} - {response.text}"
                logger.error(error_msg)
                raise ValueError(error_msg)
                
            if response.status_code == 204:  # No content
                return {}
                
            return response.json()
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Request error: {str(e)}"
            logger.error(error_msg)
            raise ValueError(error_msg)
    
    def get_all_spaces(self, start: int = 0, limit: int = 25, 
                      space_type: str = "global", status: str = "current",
                      expand: Optional[str] = None) -> Dict:
        """
        Get all spaces with optional filtering.
        
        Args:
            start: Starting index for pagination
            limit: Maximum number of spaces to return
            space_type: Type of space ("global", "personal", or "archived")
            status: Space status ("current" or "archived")
            expand: Additional fields to expand 
                   (e.g., "description,homepage,metadata,icon,description.plain")
            
        Returns:
            Dictionary containing spaces information
        """
        params = {
            "start": start,
            "limit": limit,
            "type": space_type,
            "status": status
        }
        
        if expand:
            params["expand"] = expand
            
        return self._make_api_request("GET", "/rest/api/space", params=params)
    
    def get_space(self, space_key: str, expand: Optional[str] = None) -> Dict:
        """
        Get a specific space by key.
        
        Args:
            space_key: The space key
            expand: Additional fields to expand
                   (e.g., "description,homepage,metadata,icon,description.plain")
            
        Returns:
            Dictionary containing space information
        """
        params = {}
        if expand:
            params["expand"] = expand
            
        return self._make_api_request(
            "GET", 
            f"/rest/api/space/{space_key}", 
            params=params
        )
    
    def create_space(self, key: str, name: str, description: Optional[str] = None, 
                    template_key: Optional[str] = None) -> Dict:
        """
        Create a new Confluence space.
        
        Args:
            key: The space key (must be unique, uppercase, no spaces)
            name: The space name
            description: Optional space description
            template_key: Optional template key for space creation
            
        Returns:
            Dictionary containing created space information
        """
        # Validate the space key
        if not key.isupper() or ' ' in key:
            raise ValueError("Space key must be uppercase with no spaces")
            
        # Prepare the space data
        space_data = {
            "key": key,
            "name": name,
            "description": {
                "plain": {
                    "value": description or "",
                    "representation": "plain"
                }
            }
        }
        
        # If using a template, add the template key
        if template_key:
            space_data["template"] = template_key
            
        return self._make_api_request("POST", "/rest/api/space", data=space_data)
    
    def create_space_from_template(self, key: str, name: str, template_key: str, 
                                  description: Optional[str] = None, template_params: Optional[Dict] = None) -> Dict:
        """
        Create a new Confluence space from a template with parameters.
        
        Args:
            key: The space key (must be unique, uppercase, no spaces)
            name: The space name
            description: Optional space description
            template_key: Template key for space creation
            template_params: Optional template parameters for customizing the template
            
        Returns:
            Dictionary containing created space information
        """
        # Validate the space key
        if not key.isupper() or ' ' in key:
            raise ValueError("Space key must be uppercase with no spaces")
            
        # Prepare the space data
        space_data = {
            "key": key,
            "name": name,
            "description": {
                "plain": {
                    "value": description or "",
                    "representation": "plain"
                }
            },
            "template": template_key
        }
        
        # Add template parameters if provided
        if template_params:
            space_data["templateParams"] = template_params
            
        return self._make_api_request("POST", "/rest/api/space", data=space_data)
    
    def update_space(self, space_key: str, name: Optional[str] = None, 
                    description: Optional[str] = None) -> Dict:
        """
        Update a Confluence space.
        
        Args:
            space_key: The space key to update
            name: Optional new name for the space
            description: Optional new description for the space
            
        Returns:
            Dictionary containing updated space information
        """
        # Get the current space information
        current_space = self.get_space(space_key, expand="description")
        
        # Prepare the update data
        update_data = {
            "name": name or current_space["name"],
            "description": current_space.get("description", {})
        }
        
        # Update description if provided
        if description:
            update_data["description"] = {
                "plain": {
                    "value": description,
                    "representation": "plain"
                }
            }
            
        return self._make_api_request(
            "PUT", 
            f"/rest/api/space/{space_key}", 
            data=update_data
        )
    
    def archive_space(self, space_key: str) -> Dict:
        """
        Archive a Confluence space.
        
        Args:
            space_key: The space key to archive
            
        Returns:
            Dictionary containing operation status
        """
        return self._make_api_request(
            "PUT", 
            f"/rest/api/space/{space_key}/archive"
        )
    
    def restore_space(self, space_key: str) -> Dict:
        """
        Restore an archived Confluence space.
        
        Args:
            space_key: The space key to restore
            
        Returns:
            Dictionary containing operation status
        """
        return self._make_api_request(
            "PUT", 
            f"/rest/api/space/{space_key}/unarchive"
        )
    
    def delete_space(self, space_key: str) -> Dict:
        """
        Delete a Confluence space.
        
        Warning: This permanently deletes the space and all its content.
        
        Args:
            space_key: The space key to delete
            
        Returns:
            Empty dictionary on success
        """
        return self._make_api_request(
            "DELETE", 
            f"/rest/api/space/{space_key}"
        )
    
    def get_space_permissions(self, space_key: str) -> Dict:
        """
        Get permission settings for a space.
        
        Args:
            space_key: The space key
            
        Returns:
            Dictionary containing space permissions
        """
        return self._make_api_request(
            "GET", 
            f"/rest/api/space/{space_key}/permission"
        )
    
    def add_space_permission(self, space_key: str, permission: str, 
                            subject_type: str, subject_key: str) -> Dict:
        """
        Add a permission to a space.
        
        Args:
            space_key: The space key
            permission: The permission to add (e.g., "read", "create", "delete", "admin")
            subject_type: The type of subject ("user" or "group")
            subject_key: The key of the user or group
            
        Returns:
            Dictionary containing the added permission details
        """
        permission_data = {
            "subject": {
                "type": subject_type,
                "identifier": subject_key
            },
            "operation": {
                "key": permission,
                "target": "space"
            }
        }
        
        return self._make_api_request(
            "POST", 
            f"/rest/api/space/{space_key}/permission", 
            data=permission_data
        )
    
    def remove_space_permission(self, space_key: str, permission_id: str) -> Dict:
        """
        Remove a permission from a space.
        
        Args:
            space_key: The space key
            permission_id: The ID of the permission to remove
            
        Returns:
            Empty dictionary on success
        """
        return self._make_api_request(
            "DELETE", 
            f"/rest/api/space/{space_key}/permission/{permission_id}"
        )
    
    def get_space_templates(self, space_key: str) -> List[Dict]:
        """
        Get templates available in a space.
        
        Args:
            space_key: The space key
            
        Returns:
            List of templates in the space
        """
        response = self._make_api_request(
            "GET", 
            f"/rest/api/space/{space_key}/template"
        )
        return response.get("results", [])
    
    def get_available_space_templates(self) -> List[Dict]:
        """
        Get all available space templates.
        
        Returns:
            List of available space templates
        """
        response = self._make_api_request(
            "GET", 
            "/rest/api/spacetemplate"
        )
        return response.get("results", [])
    
    def get_space_content(self, space_key: str, content_type: str = "page", 
                         start: int = 0, limit: int = 25, 
                         expand: Optional[str] = None,
                         status: str = "current") -> Dict:
        """
        Get content within a space.
        
        Args:
            space_key: The space key
            content_type: The type of content ("page", "blogpost", "comment", etc.)
            start: Starting index for pagination
            limit: Maximum number of items to return
            expand: Additional fields to expand
            status: Content status ("current", "draft", "trashed", etc.)
            
        Returns:
            Dictionary containing content
        """
        params = {
            "spaceKey": space_key,
            "type": content_type,
            "start": start,
            "limit": limit,
            "status": status
        }
        
        if expand:
            params["expand"] = expand
            
        return self._make_api_request("GET", "/rest/api/content", params=params)
    
    def copy_space(self, source_key: str, target_key: str, target_name: str,
                  description: Optional[str] = None, include_attachments: bool = True,
                  include_comments: bool = True) -> Dict:
        """
        Copy a space to a new key (uses the long-running task API).
        
        Args:
            source_key: The source space key
            target_key: The target space key (must be unique)
            target_name: The name for the new space
            description: Optional description for the new space
            include_attachments: Whether to include attachments in the copy
            include_comments: Whether to include comments in the copy
            
        Returns:
            Dictionary containing the task status
        """
        copy_data = {
            "sourceBlueprintId": source_key,
            "targetBlueprintId": target_key,
            "name": target_name,
            "description": {
                "plain": {
                    "value": description or f"Copy of {source_key}",
                    "representation": "plain"
                }
            },
            "copyOptions": {
                "copyAttachments": include_attachments,
                "copyComments": include_comments
            }
        }
        
        # Start the copy task
        task_response = self._make_api_request(
            "POST", 
            "/rest/api/space/_copy", 
            data=copy_data
        )
        
        # Return the task ID and status
        return {
            "task_id": task_response.get("id"),
            "status": task_response.get("status"),
            "message": "Space copy started. Check task status using get_task_status."
        }
    
    def get_task_status(self, task_id: str) -> Dict:
        """
        Get the status of a long-running task.
        
        Args:
            task_id: The ID of the task
            
        Returns:
            Dictionary containing task status
        """
        return self._make_api_request(
            "GET", 
            f"/rest/api/longtask/{task_id}"
        )
    
    def export_space(self, space_key: str, export_type: str = "html") -> Dict:
        """
        Export a space to a file.
        
        Args:
            space_key: The space key to export
            export_type: The type of export ("html", "pdf", "xml")
            
        Returns:
            Dictionary containing the task status
        """
        export_data = {
            "spaceKey": space_key,
            "exportType": export_type
        }
        
        # Start the export task
        task_response = self._make_api_request(
            "POST", 
            "/rest/api/space/export", 
            data=export_data
        )
        
        # Return the task ID and status
        return {
            "task_id": task_response.get("id"),
            "status": task_response.get("status"),
            "message": "Space export started. Check task status using get_task_status."
        }
    
    def get_space_property(self, space_key: str, property_key: str) -> Dict:
        """
        Get a property for a space.
        
        Args:
            space_key: The space key
            property_key: The key of the property to get
            
        Returns:
            Dictionary containing the property value
        """
        return self._make_api_request(
            "GET", 
            f"/rest/api/space/{space_key}/property/{property_key}"
        )
    
    def set_space_property(self, space_key: str, property_key: str, property_value: Any) -> Dict:
        """
        Set a property for a space.
        
        Args:
            space_key: The space key
            property_key: The key of the property to set
            property_value: The value of the property
            
        Returns:
            Dictionary containing the property details
        """
        property_data = {
            "key": property_key,
            "value": property_value
        }
        
        return self._make_api_request(
            "PUT", 
            f"/rest/api/space/{space_key}/property/{property_key}", 
            data=property_data
        )
    
    def delete_space_property(self, space_key: str, property_key: str) -> Dict:
        """
        Delete a property from a space.
        
        Args:
            space_key: The space key
            property_key: The key of the property to delete
            
        Returns:
            Empty dictionary on success
        """
        return self._make_api_request(
            "DELETE", 
            f"/rest/api/space/{space_key}/property/{property_key}"
        )