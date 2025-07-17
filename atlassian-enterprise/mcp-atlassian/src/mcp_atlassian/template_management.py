"""
Confluence Template Management Module

This module provides enhanced capabilities for managing Confluence templates,
including creation, viewing, and using templates to create pages.
"""

import json
import logging
from typing import Dict, List, Optional, Any, Union

import requests

from .config import ConfluenceConfig

logger = logging.getLogger(__name__)


class ConfluenceTemplateManager:
    """Class for managing Confluence templates with enhanced capabilities."""

    def __init__(self, config: ConfluenceConfig):
        """
        Initialize the Template Manager with Confluence configuration.

        Args:
            config: ConfluenceConfig object with Confluence connection details
        """
        self.base_url = config.url.rstrip("/")
        self.auth = (config.username, config.api_token)
        self.headers = {"Content-Type": "application/json"}
        logger.debug(f"Initialized ConfluenceTemplateManager with base URL: {self.base_url}")

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

    # Template Retrieval
    def get_content_templates(self) -> List[Dict]:
        """
        Get all available content templates.

        Returns:
            List of template dictionaries
        """
        return self._make_api_request("GET", "/template")

    def get_blueprint_templates(self) -> List[Dict]:
        """
        Get all available blueprint templates.

        Returns:
            List of blueprint dictionaries
        """
        return self._make_api_request("GET", "/blueprint/instance")

    def get_space_templates(self, space_key: str) -> List[Dict]:
        """
        Get templates in a specific space.

        Args:
            space_key: The space key

        Returns:
            List of template dictionaries
        """
        params = {"spaceKey": space_key}
        return self._make_api_request("GET", "/template/space", params=params)

    def get_template_by_id(self, template_id: str) -> Dict:
        """
        Get a template by ID.

        Args:
            template_id: The template ID

        Returns:
            Template data
        """
        return self._make_api_request("GET", f"/template/{template_id}")

    # Template Categories
    def get_template_categories(self) -> List[Dict]:
        """
        Get all template categories.

        Returns:
            List of category dictionaries
        """
        return self._make_api_request("GET", "/template/category")

    def create_template_category(self, name: str) -> Dict:
        """
        Create a new template category.

        Args:
            name: Category name

        Returns:
            Created category data
        """
        data = {"name": name}
        return self._make_api_request("POST", "/template/category", data=data)

    def add_template_to_category(self, template_id: str, category_id: str) -> Dict:
        """
        Add a template to a category.

        Args:
            template_id: The template ID
            category_id: The category ID

        Returns:
            Status response
        """
        data = {"categoryId": category_id}
        return self._make_api_request("PUT", f"/template/{template_id}/category", data=data)

    def remove_template_from_category(self, template_id: str, category_id: str) -> Dict:
        """
        Remove a template from a category.

        Args:
            template_id: The template ID
            category_id: The category ID

        Returns:
            Status response
        """
        params = {"categoryId": category_id}
        return self._make_api_request("DELETE", f"/template/{template_id}/category", params=params)

    # Template Operations
    def create_template(
        self, space_key: str, name: str, template_type: str, body: str, labels: Optional[List[str]] = None
    ) -> Dict:
        """
        Create a new content template.

        Args:
            space_key: The space key
            name: Template name
            template_type: Template type (page or blogpost)
            body: Template body in storage format
            labels: Optional list of labels

        Returns:
            Created template data
        """
        data = {
            "name": name,
            "templateType": template_type,
            "space": {"key": space_key},
            "body": {"storage": {"value": body, "representation": "storage"}},
        }

        if labels:
            data["labels"] = [{"name": label} for label in labels]

        return self._make_api_request("POST", "/template", data=data)

    def update_template(
        self, template_id: str, name: Optional[str] = None, body: Optional[str] = None, labels: Optional[List[str]] = None
    ) -> Dict:
        """
        Update an existing template.

        Args:
            template_id: The template ID
            name: Optional new template name
            body: Optional new template body
            labels: Optional new labels

        Returns:
            Updated template data
        """
        # Get current template
        current = self.get_template_by_id(template_id)
        
        data = {
            "name": name or current.get("name", ""),
            "templateType": current.get("templateType", "page"),
            "space": current.get("space", {}),
        }
        
        if body:
            data["body"] = {"storage": {"value": body, "representation": "storage"}}
        
        if labels is not None:
            data["labels"] = [{"name": label} for label in labels]

        return self._make_api_request("PUT", f"/template/{template_id}", data=data)

    def delete_template(self, template_id: str) -> Dict:
        """
        Delete a template.

        Args:
            template_id: The template ID

        Returns:
            Status response
        """
        return self._make_api_request("DELETE", f"/template/{template_id}")

    def clone_template(self, template_id: str, target_space_key: str) -> Dict:
        """
        Clone a template to another space.

        Args:
            template_id: The template ID
            target_space_key: Target space key

        Returns:
            Cloned template data
        """
        # Get current template
        template = self.get_template_by_id(template_id)
        
        # Create new template in target space
        return self.create_template(
            space_key=target_space_key,
            name=template.get("name", "Cloned Template"),
            template_type=template.get("templateType", "page"),
            body=template.get("body", {}).get("storage", {}).get("value", ""),
            labels=[label.get("name") for label in template.get("labels", [])]
        )

    # Using Templates
    def create_page_from_template(
        self, space_key: str, title: str, template_id: str, ancestor_id: Optional[str] = None, parameters: Optional[Dict] = None
    ) -> Dict:
        """
        Create a page using a template.

        Args:
            space_key: The space key
            title: Page title
            template_id: Template ID
            ancestor_id: Optional parent page ID
            parameters: Optional template parameters

        Returns:
            Created page data
        """
        endpoint = "/content"
        data = {
            "type": "page",
            "title": title,
            "space": {"key": space_key},
            "metadata": {
                "properties": {
                    "template-id": {"key": "template-id", "value": template_id}
                }
            }
        }
        
        if ancestor_id:
            data["ancestors"] = [{"id": ancestor_id}]
            
        if parameters:
            for key, value in parameters.items():
                data["metadata"]["properties"][key] = {"key": key, "value": value}

        return self._make_api_request("POST", endpoint, data=data)

    def create_page_from_blueprint(
        self, space_key: str, title: str, blueprint_id: str, ancestor_id: Optional[str] = None, parameters: Optional[Dict] = None
    ) -> Dict:
        """
        Create a page using a blueprint.

        Args:
            space_key: The space key
            title: Page title
            blueprint_id: Blueprint ID
            ancestor_id: Optional parent page ID
            parameters: Optional blueprint parameters

        Returns:
            Created page data
        """
        endpoint = "/content"
        data = {
            "type": "page",
            "title": title,
            "space": {"key": space_key},
            "metadata": {
                "properties": {
                    "blueprint-id": {"key": "blueprint-id", "value": blueprint_id}
                }
            }
        }
        
        if ancestor_id:
            data["ancestors"] = [{"id": ancestor_id}]
            
        if parameters:
            for key, value in parameters.items():
                data["metadata"]["properties"][key] = {"key": key, "value": value}

        return self._make_api_request("POST", endpoint, data=data)

    def create_custom_template(
        self, space_key: str, name: str, html_content: str, labels: Optional[List[str]] = None
    ) -> Dict:
        """
        Create a custom template with HTML content.

        Args:
            space_key: The space key
            name: Template name
            html_content: HTML content for template
            labels: Optional list of labels

        Returns:
            Created template data
        """
        # First convert HTML to storage format
        convert_data = {
            "value": html_content,
            "representation": "editor"
        }
        convert_url = f"{self.base_url}/rest/api/contentbody/convert/storage"
        
        try:
            response = requests.post(
                url=convert_url,
                json=convert_data,
                headers=self.headers,
                auth=self.auth
            )
            
            if response.status_code >= 400:
                error_msg = f"API request failed: {response.status_code} - {response.text}"
                logger.error(error_msg)
                raise ValueError(error_msg)
                
            storage_body = response.json().get("value", "")
            
            # Now create the template with storage format
            return self.create_template(
                space_key=space_key,
                name=name,
                template_type="page",
                body=storage_body,
                labels=labels
            )
            
        except requests.RequestException as e:
            error_msg = f"Request error for {convert_url}: {str(e)}"
            logger.error(error_msg)
            raise ValueError(error_msg)