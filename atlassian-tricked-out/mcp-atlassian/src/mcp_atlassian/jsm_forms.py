"""
JSM Forms Module

This module provides functionality for working with Jira Service Management (JSM)
forms, including custom fields and form validation.
"""

import json
import logging
import os
from typing import Dict, List, Optional, Any, Union, Tuple

import requests

from .jsm import JiraServiceManager

logger = logging.getLogger(__name__)

class JSMFormManager:
    """
    Manages Jira Service Management forms and custom fields.
    """

    # Field type mapping for create operations
    FIELD_TYPE_MAPPING = {
        "text": {"fieldType": "string", "searcherKey": "stringTextSearcher"},
        "number": {"fieldType": "number", "searcherKey": "numberRangeSearcher"},
        "date": {"fieldType": "date", "searcherKey": "dateRangeSearcher"},
        "datetime": {"fieldType": "datetime", "searcherKey": "datetimeRangeSearcher"},
        "checkbox": {"fieldType": "checkbox", "searcherKey": "checkboxSearcher"},
        "select": {"fieldType": "option", "searcherKey": "optionSearcher"},
        "multiselect": {"fieldType": "multiOption", "searcherKey": "multiOptionSearcher"},
        "radio": {"fieldType": "radioButtons", "searcherKey": "radioButtonsSearcher"},
        "textarea": {"fieldType": "textarea", "searcherKey": "textAreaSearcher"},
        "url": {"fieldType": "url", "searcherKey": "urlSearcher"},
        "user": {"fieldType": "user", "searcherKey": "userSearcher"},
        "group": {"fieldType": "group", "searcherKey": "groupSearcher"}
    }

    def __init__(
        self, 
        jsm_client: Optional[JiraServiceManager] = None,
        url: Optional[str] = None, 
        username: Optional[str] = None, 
        api_token: Optional[str] = None
    ):
        """
        Initialize the JSM Form Manager.

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
        
        logger.debug(f"Initialized JSMFormManager with URL: {self.url}")

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

    # Custom Fields
    def get_custom_fields(self) -> List[Dict]:
        """
        Get all custom fields.

        Returns:
            List of custom fields
        """
        response = self._make_jira_api_request("GET", "/field")
        # Filter to custom fields only
        return [field for field in response if field.get("custom", False)]

    def create_custom_field(
        self, name: str, description: str, type_key: str, 
        context_project_ids: Optional[List[str]] = None,
        context_issue_type_ids: Optional[List[str]] = None
    ) -> Dict:
        """
        Create a custom field.

        Args:
            name: Field name
            description: Field description
            type_key: Field type key (text, number, select, etc.)
            context_project_ids: Optional list of project IDs for field context
            context_issue_type_ids: Optional list of issue type IDs for field context

        Returns:
            Created field
        """
        if type_key not in self.FIELD_TYPE_MAPPING:
            raise ValueError(f"Unsupported field type: {type_key}. " + 
                            f"Supported types: {', '.join(self.FIELD_TYPE_MAPPING.keys())}")
        
        field_type = self.FIELD_TYPE_MAPPING[type_key]
        
        data = {
            "name": name,
            "description": description,
            "type": field_type["fieldType"],
            "searcherKey": field_type["searcherKey"]
        }
        
        # Create field
        field = self._make_jira_api_request("POST", "/field", data=data)
        
        # Set context if provided
        if context_project_ids or context_issue_type_ids:
            context_data = {
                "fieldId": field["id"],
                "isGlobalContext": not bool(context_project_ids),
                "contextId": None
            }
            
            if context_project_ids:
                context_data["projectIds"] = context_project_ids
                
            if context_issue_type_ids:
                context_data["issueTypeIds"] = context_issue_type_ids
                
            self._make_jira_api_request("POST", "/field/context", data=context_data)
            
        return field

    def configure_field_options(
        self, field_id: str, options: List[Dict]
    ) -> Dict:
        """
        Configure options for a select/multiselect field.

        Args:
            field_id: The field ID
            options: List of option dictionaries with "value" and optionally "disabled" keys

        Returns:
            Status response
        """
        data = {
            "options": [{"value": opt["value"], "disabled": opt.get("disabled", False)} for opt in options]
        }
        
        return self._make_jira_api_request(
            "PUT", f"/field/{field_id}/option", data=data
        )

    # Form Configuration
    def get_form_configuration(
        self, service_desk_id: str, request_type_id: str
    ) -> Dict:
        """
        Get form configuration for a request type.

        Args:
            service_desk_id: The service desk ID
            request_type_id: The request type ID

        Returns:
            Form configuration
        """
        return self._make_api_request(
            "GET", f"/servicedesk/{service_desk_id}/requesttype/{request_type_id}/field"
        )

    def update_form_field_order(
        self, service_desk_id: str, request_type_id: str, field_order: List[str]
    ) -> Dict:
        """
        Update the order of fields in a form.

        Args:
            service_desk_id: The service desk ID
            request_type_id: The request type ID
            field_order: List of field IDs in desired order

        Returns:
            Status response
        """
        # Get current form configuration
        config = self.get_form_configuration(service_desk_id, request_type_id)
        
        # Get project key
        service_desk = self.jsm_client.get_service_desk(service_desk_id)
        project_key = service_desk.get("projectKey")
        
        # Get project
        project = self._make_jira_api_request("GET", f"/project/{project_key}")
        
        # Update property
        property_key = f"sd.form.order.{request_type_id}"
        data = {
            "key": property_key,
            "value": field_order
        }
        
        return self._make_jira_api_request(
            "PUT", f"/project/{project['id']}/properties/{property_key}", data=data
        )

    def configure_field_requirements(
        self, service_desk_id: str, request_type_id: str, 
        required_fields: List[str], optional_fields: List[str]
    ) -> Dict:
        """
        Configure which fields are required or optional.

        Args:
            service_desk_id: The service desk ID
            request_type_id: The request type ID
            required_fields: List of required field IDs
            optional_fields: List of optional field IDs

        Returns:
            Status response
        """
        # Get service desk
        service_desk = self.jsm_client.get_service_desk(service_desk_id)
        project_key = service_desk.get("projectKey")
        
        # Get project
        project = self._make_jira_api_request("GET", f"/project/{project_key}")
        
        # Update property
        property_key = f"sd.form.requirements.{request_type_id}"
        data = {
            "key": property_key,
            "value": {
                "required": required_fields,
                "optional": optional_fields
            }
        }
        
        return self._make_jira_api_request(
            "PUT", f"/project/{project['id']}/properties/{property_key}", data=data
        )

    def create_field_group(
        self, service_desk_id: str, request_type_id: str, 
        group_name: str, field_ids: List[str]
    ) -> Dict:
        """
        Create a field group in a form.

        Args:
            service_desk_id: The service desk ID
            request_type_id: The request type ID
            group_name: Name of the group
            field_ids: List of field IDs to include in the group

        Returns:
            Status response
        """
        # This is a placeholder as JSM doesn't natively support field groups
        # Custom implementation would be needed with UI extensions
        
        return {
            "status": "error",
            "message": "Field groups are not natively supported in JSM API"
        }

    # Form Validation
    def validate_form_data(
        self, service_desk_id: str, request_type_id: str, form_data: Dict
    ) -> Dict:
        """
        Validate form data against field requirements.

        Args:
            service_desk_id: The service desk ID
            request_type_id: The request type ID
            form_data: Form data as field_id: value dict

        Returns:
            Validation result
        """
        # Get form configuration
        config = self.get_form_configuration(service_desk_id, request_type_id)
        fields = config.get("requestTypeFields", [])
        
        # Get field requirements
        service_desk = self.jsm_client.get_service_desk(service_desk_id)
        project_key = service_desk.get("projectKey")
        project = self._make_jira_api_request("GET", f"/project/{project_key}")
        
        property_key = f"sd.form.requirements.{request_type_id}"
        try:
            req_response = self._make_jira_api_request(
                "GET", f"/project/{project['id']}/properties/{property_key}"
            )
            requirements = req_response.get("value", {})
        except ValueError:
            # Default to all fields from the form config
            requirements = {
                "required": [f["fieldId"] for f in fields if f.get("required", False)],
                "optional": [f["fieldId"] for f in fields if not f.get("required", False)]
            }
        
        # Validate required fields
        errors = {}
        required_fields = requirements.get("required", [])
        
        for field_id in required_fields:
            if field_id not in form_data or form_data[field_id] is None or form_data[field_id] == "":
                errors[field_id] = "This field is required"
                
        # Validate field types
        field_map = {f["fieldId"]: f for f in fields}
        
        for field_id, value in form_data.items():
            if field_id not in field_map:
                continue
                
            field = field_map[field_id]
            field_type = field.get("jiraSchema", {}).get("type")
            
            # Skip empty optional fields
            if not value and field_id not in required_fields:
                continue
                
            # Validate by field type
            if field_type == "number" and value is not None:
                try:
                    float(value)
                except (ValueError, TypeError):
                    errors[field_id] = "Must be a number"
                    
            elif field_type == "option" and value is not None:
                options = [o.get("value") for o in field.get("validValues", [])]
                if options and value not in options:
                    errors[field_id] = "Invalid option selected"
                    
            elif field_type == "array" and value is not None:
                if not isinstance(value, list):
                    errors[field_id] = "Must be a list"
                else:
                    options = [o.get("value") for o in field.get("validValues", [])]
                    if options and any(v not in options for v in value):
                        errors[field_id] = "Invalid option(s) selected"
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }