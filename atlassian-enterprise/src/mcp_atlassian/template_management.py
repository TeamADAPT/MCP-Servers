"""
Confluence Template Management Module.

This module provides template and blueprint management functionality for Confluence.
"""

import logging
import json
import requests
from typing import Dict, List, Optional, Any, Union

from .config import ConfluenceConfig

# Configure logging
logger = logging.getLogger("mcp-atlassian")


class ConfluenceTemplateManager:
    """Manages Confluence templates, blueprints, and content creation from templates."""

    def __init__(self, config: ConfluenceConfig):
        """
        Initialize the ConfluenceTemplateManager.

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
    
    def get_content_templates(self, start: int = 0, limit: int = 50, expand: Optional[str] = None) -> Dict:
        """
        Get available content templates.
        
        Args:
            start: Starting index for pagination
            limit: Maximum number of templates to return
            expand: Additional fields to expand
            
        Returns:
            Dictionary containing content templates
        """
        params = {
            "start": start,
            "limit": limit
        }
        
        if expand:
            params["expand"] = expand
            
        return self._make_api_request("GET", "/rest/api/template", params=params)
    
    def get_blueprint_templates(self, start: int = 0, limit: int = 50) -> Dict:
        """
        Get available blueprint templates.
        
        Args:
            start: Starting index for pagination
            limit: Maximum number of blueprints to return
            
        Returns:
            Dictionary containing blueprint templates
        """
        params = {
            "start": start,
            "limit": limit
        }
            
        return self._make_api_request("GET", "/rest/api/blueprint/template", params=params)
    
    def get_space_templates(self, space_key: str, start: int = 0, limit: int = 50) -> Dict:
        """
        Get templates available in a specific space.
        
        Args:
            space_key: The space key
            start: Starting index for pagination
            limit: Maximum number of templates to return
            
        Returns:
            Dictionary containing space templates
        """
        params = {
            "start": start,
            "limit": limit
        }
            
        return self._make_api_request("GET", f"/rest/api/space/{space_key}/template", params=params)
    
    def get_template_by_id(self, template_id: str) -> Dict:
        """
        Get a template by ID.
        
        Args:
            template_id: The template ID
            
        Returns:
            Dictionary containing template details
        """
        return self._make_api_request("GET", f"/rest/api/template/{template_id}")
    
    def create_template(self, space_key: str, name: str, content: str, 
                       template_type: str = "page", 
                       label: Optional[str] = None,
                       description: Optional[str] = None) -> Dict:
        """
        Create a new content template.
        
        Args:
            space_key: The space key where the template will be created
            name: The name of the template
            content: The template content in storage format
            template_type: The type of template ("page" or "blogpost")
            label: Optional label for the template
            description: Optional description for the template
            
        Returns:
            Dictionary containing created template details
        """
        template_data = {
            "name": name,
            "templateType": template_type,
            "body": {
                "storage": {
                    "value": content,
                    "representation": "storage"
                }
            },
            "space": {
                "key": space_key
            }
        }
        
        if label:
            template_data["labels"] = [{"name": label}]
            
        if description:
            template_data["description"] = description
            
        return self._make_api_request("POST", "/rest/api/template", data=template_data)
    
    def update_template(self, template_id: str, name: Optional[str] = None, 
                       content: Optional[str] = None, 
                       label: Optional[str] = None,
                       description: Optional[str] = None) -> Dict:
        """
        Update an existing template.
        
        Args:
            template_id: The ID of the template to update
            name: Optional new name for the template
            content: Optional new content for the template
            label: Optional new label for the template
            description: Optional new description for the template
            
        Returns:
            Dictionary containing updated template details
        """
        # Get the current template
        current_template = self.get_template_by_id(template_id)
        
        # Prepare the update data
        template_data = {}
        
        if name:
            template_data["name"] = name
            
        if content:
            template_data["body"] = {
                "storage": {
                    "value": content,
                    "representation": "storage"
                }
            }
            
        if label:
            template_data["labels"] = [{"name": label}]
            
        if description:
            template_data["description"] = description
            
        # Skip update if no changes
        if not template_data:
            return current_template
            
        return self._make_api_request("PUT", f"/rest/api/template/{template_id}", data=template_data)
    
    def delete_template(self, template_id: str) -> Dict:
        """
        Delete a template.
        
        Args:
            template_id: The ID of the template to delete
            
        Returns:
            Empty dictionary on success
        """
        return self._make_api_request("DELETE", f"/rest/api/template/{template_id}")
    
    def create_page_from_template(self, space_key: str, title: str, template_id: str,
                                 parent_id: Optional[str] = None,
                                 template_parameters: Optional[Dict] = None) -> Dict:
        """
        Create a new page from a template.
        
        Args:
            space_key: The space key where the page will be created
            title: The title of the page
            template_id: The ID of the template to use
            parent_id: Optional parent page ID
            template_parameters: Optional parameters to customize the template
            
        Returns:
            Dictionary containing created page details
        """
        page_data = {
            "type": "page",
            "title": title,
            "space": {
                "key": space_key
            },
            "templateId": template_id
        }
        
        # Add parent reference if provided
        if parent_id:
            page_data["ancestors"] = [{"id": parent_id}]
            
        # Add template parameters if provided
        if template_parameters:
            page_data["templateParameters"] = template_parameters
            
        return self._make_api_request("POST", "/rest/api/content", data=page_data)
    
    def create_page_from_blueprint(self, space_key: str, title: str, blueprint_id: str,
                                  parent_id: Optional[str] = None,
                                  blueprint_parameters: Optional[Dict] = None) -> Dict:
        """
        Create a new page from a blueprint.
        
        Args:
            space_key: The space key where the page will be created
            title: The title of the page
            blueprint_id: The ID of the blueprint to use
            parent_id: Optional parent page ID
            blueprint_parameters: Optional parameters to customize the blueprint
            
        Returns:
            Dictionary containing created page details
        """
        page_data = {
            "type": "page",
            "title": title,
            "space": {
                "key": space_key
            },
            "metadata": {
                "blueprint": {
                    "id": blueprint_id
                }
            }
        }
        
        # Add parent reference if provided
        if parent_id:
            page_data["ancestors"] = [{"id": parent_id}]
            
        # Add blueprint parameters if provided
        if blueprint_parameters:
            page_data["metadata"]["blueprint"]["parameters"] = blueprint_parameters
            
        return self._make_api_request("POST", "/rest/api/content", data=page_data)
    
    def create_custom_template(self, space_key: str, name: str, html_content: str, 
                              description: Optional[str] = None,
                              categories: Optional[List[str]] = None) -> Dict:
        """
        Create a custom template that can be used in the editor.
        
        Args:
            space_key: The space key where the template will be created
            name: The name of the template
            html_content: The HTML content of the template
            description: Optional description for the template
            categories: Optional list of category names for the template
            
        Returns:
            Dictionary containing created template details
        """
        template_data = {
            "name": name,
            "templateType": "page",
            "body": {
                "storage": {
                    "value": html_content,
                    "representation": "storage"
                }
            },
            "space": {
                "key": space_key
            }
        }
        
        if description:
            template_data["description"] = description
            
        if categories:
            template_data["categories"] = categories
            
        return self._make_api_request("POST", "/rest/api/template/custom", data=template_data)
    
    def clone_template(self, template_id: str, space_key: str, new_name: Optional[str] = None) -> Dict:
        """
        Clone an existing template to another space or with a new name.
        
        Args:
            template_id: The ID of the template to clone
            space_key: The target space key
            new_name: Optional new name for the cloned template
            
        Returns:
            Dictionary containing cloned template details
        """
        # Get the original template
        original = self.get_template_by_id(template_id)
        
        # Prepare the clone data
        template_data = {
            "name": new_name or f"Copy of {original.get('name', 'Template')}",
            "templateType": original.get("templateType", "page"),
            "body": original.get("body", {}),
            "space": {
                "key": space_key
            }
        }
        
        # Copy description if available
        if "description" in original:
            template_data["description"] = original["description"]
            
        # Copy labels if available
        if "labels" in original:
            template_data["labels"] = original["labels"]
            
        return self._make_api_request("POST", "/rest/api/template", data=template_data)
    
    def get_template_categories(self, space_key: Optional[str] = None) -> List[Dict]:
        """
        Get available template categories.
        
        Args:
            space_key: Optional space key to filter categories
            
        Returns:
            List of template categories
        """
        params = {}
        if space_key:
            params["spaceKey"] = space_key
            
        response = self._make_api_request("GET", "/rest/api/template/category", params=params)
        return response.get("results", [])
    
    def create_template_category(self, name: str, description: Optional[str] = None) -> Dict:
        """
        Create a new template category.
        
        Args:
            name: The name of the category
            description: Optional description for the category
            
        Returns:
            Dictionary containing created category details
        """
        category_data = {
            "name": name
        }
        
        if description:
            category_data["description"] = description
            
        return self._make_api_request("POST", "/rest/api/template/category", data=category_data)
    
    def add_template_to_category(self, template_id: str, category_id: str) -> Dict:
        """
        Add a template to a category.
        
        Args:
            template_id: The ID of the template
            category_id: The ID of the category
            
        Returns:
            Dictionary containing the result
        """
        data = {
            "templateId": template_id,
            "categoryId": category_id
        }
        
        return self._make_api_request(
            "PUT", 
            f"/rest/api/template/{template_id}/category/{category_id}", 
            data=data
        )
    
    def remove_template_from_category(self, template_id: str, category_id: str) -> Dict:
        """
        Remove a template from a category.
        
        Args:
            template_id: The ID of the template
            category_id: The ID of the category
            
        Returns:
            Empty dictionary on success
        """
        return self._make_api_request(
            "DELETE", 
            f"/rest/api/template/{template_id}/category/{category_id}"
        )