"""
Jira Service Management Custom Form Support Module.

This module provides functionality for working with JSM custom forms,
including form creation, field customization, and form validation.

Author: Claude Code
Date: May 7, 2025
"""

import logging
from typing import Dict, List, Optional, Union, Any
import os
import requests
import json

# Configure logging
logger = logging.getLogger("mcp-jsm-forms")

class JSMFormManager:
    """
    Handles operations related to Jira Service Management custom forms.
    
    This class provides functionality for working with JSM custom forms,
    including form creation, field customization, and validation.
    """
    
    def __init__(self, jsm_client=None, url=None, username=None, api_token=None):
        """
        Initialize the JSM Form Manager.
        
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
            # For some form operations, we need the Jira API
            self.jira_api_base = f"{self.url}/rest/api/3"
            
            # Authentication tuple for requests
            self.auth = (self.username, self.api_token)
            
            # Standard headers for API requests
            self.headers = {
                "Accept": "application/json",
                "Content-Type": "application/json"
            }
            
            logger.info(f"Initialized JSM Form Manager for {self.url}")
            
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
                    raise ValueError("Form resource not found")
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
            
    # ======= FORM FIELD OPERATIONS =======
    
    def get_custom_fields(self) -> List[Dict]:
        """
        Get all custom fields available in the instance.
        
        Returns:
            List of custom field definitions
        """
        return self._make_jira_api_request("GET", "/field")
    
    def get_request_type_fields(self, service_desk_id: str, request_type_id: str) -> Dict:
        """
        Get fields for a request type.
        
        Args:
            service_desk_id: The ID of the service desk
            request_type_id: The ID of the request type
            
        Returns:
            Dictionary containing field information
        """
        return self._make_api_request("GET", f"/servicedesk/{service_desk_id}/requesttype/{request_type_id}/field")
    
    def create_custom_field(self, name: str, description: str, field_type: str, 
                          field_context: Optional[str] = None) -> Dict:
        """
        Create a new custom field for use in JSM forms.
        
        Args:
            name: Name of the custom field
            description: Description of the custom field
            field_type: Type of field (e.g., "text", "select", "multiselect")
            field_context: Optional context for the field
            
        Returns:
            Dictionary containing created field information
        """
        # Map friendly field types to Jira API field types
        field_type_map = {
            "text": "com.atlassian.jira.plugin.system.customfieldtypes:textfield",
            "textarea": "com.atlassian.jira.plugin.system.customfieldtypes:textarea",
            "select": "com.atlassian.jira.plugin.system.customfieldtypes:select",
            "multiselect": "com.atlassian.jira.plugin.system.customfieldtypes:multiselect",
            "datepicker": "com.atlassian.jira.plugin.system.customfieldtypes:datepicker",
            "datetime": "com.atlassian.jira.plugin.system.customfieldtypes:datetime",
            "number": "com.atlassian.jira.plugin.system.customfieldtypes:float",
            "checkbox": "com.atlassian.jira.plugin.system.customfieldtypes:checkbox",
            "radio": "com.atlassian.jira.plugin.system.customfieldtypes:radiobuttons",
            "url": "com.atlassian.jira.plugin.system.customfieldtypes:url",
            "userpicker": "com.atlassian.jira.plugin.system.customfieldtypes:userpicker",
            "multipicker": "com.atlassian.jira.plugin.system.customfieldtypes:multiuserpicker",
            "cascading": "com.atlassian.jira.plugin.system.customfieldtypes:cascadingselect"
        }
        
        jira_field_type = field_type_map.get(field_type.lower())
        if not jira_field_type:
            raise ValueError(f"Unsupported field type: {field_type}. Supported types: {', '.join(field_type_map.keys())}")
        
        data = {
            "name": name,
            "description": description,
            "type": jira_field_type,
            "searcherKey": self._get_searcher_key_for_field_type(jira_field_type)
        }
        
        return self._make_jira_api_request("POST", "/field", data=data)
    
    def _get_searcher_key_for_field_type(self, field_type: str) -> str:
        """Get the appropriate searcher key for a field type."""
        # Map of field types to searcher keys
        searcher_map = {
            "com.atlassian.jira.plugin.system.customfieldtypes:textfield": 
                "com.atlassian.jira.plugin.system.customfieldtypes:textsearcher",
            "com.atlassian.jira.plugin.system.customfieldtypes:textarea": 
                "com.atlassian.jira.plugin.system.customfieldtypes:textsearcher",
            "com.atlassian.jira.plugin.system.customfieldtypes:select": 
                "com.atlassian.jira.plugin.system.customfieldtypes:selectsearcher",
            "com.atlassian.jira.plugin.system.customfieldtypes:multiselect": 
                "com.atlassian.jira.plugin.system.customfieldtypes:multiselectsearcher",
            "com.atlassian.jira.plugin.system.customfieldtypes:datepicker": 
                "com.atlassian.jira.plugin.system.customfieldtypes:daterange",
            "com.atlassian.jira.plugin.system.customfieldtypes:datetime": 
                "com.atlassian.jira.plugin.system.customfieldtypes:datetimerange",
            "com.atlassian.jira.plugin.system.customfieldtypes:float": 
                "com.atlassian.jira.plugin.system.customfieldtypes:exactnumber",
            "com.atlassian.jira.plugin.system.customfieldtypes:checkbox": 
                "com.atlassian.jira.plugin.system.customfieldtypes:checkboxsearcher",
            "com.atlassian.jira.plugin.system.customfieldtypes:radiobuttons": 
                "com.atlassian.jira.plugin.system.customfieldtypes:radiobuttonsearcher",
            "com.atlassian.jira.plugin.system.customfieldtypes:url": 
                "com.atlassian.jira.plugin.system.customfieldtypes:exacttextsearcher",
            "com.atlassian.jira.plugin.system.customfieldtypes:userpicker": 
                "com.atlassian.jira.plugin.system.customfieldtypes:userpickersearcher",
            "com.atlassian.jira.plugin.system.customfieldtypes:multiuserpicker": 
                "com.atlassian.jira.plugin.system.customfieldtypes:userpickergroupsearcher",
            "com.atlassian.jira.plugin.system.customfieldtypes:cascadingselect": 
                "com.atlassian.jira.plugin.system.customfieldtypes:cascadingselectsearcher"
        }
        
        return searcher_map.get(field_type, "com.atlassian.jira.plugin.system.customfieldtypes:textsearcher")
    
    def configure_field_options(self, field_id: str, options: List[Dict]) -> Dict:
        """
        Configure options for a select/multiselect field.
        
        Args:
            field_id: The ID of the custom field
            options: List of option configurations (each with 'value' key)
            
        Returns:
            Dictionary containing updated field information
        """
        # Get contexts for the field
        contexts = self._make_jira_api_request("GET", f"/field/{field_id}/context")
        
        if not contexts.get("values"):
            raise ValueError(f"No contexts found for field {field_id}")
            
        context_id = contexts["values"][0]["id"]
        
        formatted_options = []
        for option in options:
            formatted_options.append({
                "value": option["value"],
                "disabled": option.get("disabled", False)
            })
            
        data = {
            "options": formatted_options
        }
        
        return self._make_jira_api_request(
            "PUT", 
            f"/field/{field_id}/context/{context_id}/option",
            data=data
        )
    
    # ======= FORM CONFIGURATION OPERATIONS =======
    
    def get_form_configuration(self, service_desk_id: str, request_type_id: str) -> Dict:
        """
        Get the form configuration for a request type.
        
        Args:
            service_desk_id: The ID of the service desk
            request_type_id: The ID of the request type
            
        Returns:
            Dictionary containing form configuration
        """
        # Get fields first
        fields = self.get_request_type_fields(service_desk_id, request_type_id)
        
        # Get request type info
        request_type = self._make_api_request("GET", f"/servicedesk/{service_desk_id}/requesttype/{request_type_id}")
        
        # Combine into a form configuration
        form_config = {
            "request_type": request_type,
            "fields": fields,
            "field_groups": self._get_field_groups(service_desk_id, request_type_id)
        }
        
        return form_config
    
    def _get_field_groups(self, service_desk_id: str, request_type_id: str) -> List[Dict]:
        """
        Get field groups for a request type.
        This is a placeholder as the actual implementation would depend
        on how field groups are stored in the specific Jira instance.
        """
        # In a real implementation, this would retrieve field groups
        # from the appropriate API or database
        return []
    
    def update_form_field_order(self, service_desk_id: str, request_type_id: str, 
                              field_order: List[str]) -> Dict:
        """
        Update the order of fields in a request type form.
        
        Args:
            service_desk_id: The ID of the service desk
            request_type_id: The ID of the request type
            field_order: List of field IDs in desired order
            
        Returns:
            Dictionary containing result information
        """
        # This is a simplified implementation
        # In practice, this might require admin API access
        
        # Get project key for the service desk
        service_desk_info = self._make_api_request("GET", f"/servicedesk/{service_desk_id}")
        project_key = service_desk_info.get("projectKey", "")
        
        # Format field order data
        field_order_data = {
            "projectKey": project_key,
            "requestTypeId": request_type_id,
            "fieldOrder": field_order
        }
        
        # Store as a property on the project
        return self._make_jira_api_request(
            "PUT", 
            f"/project/{project_key}/properties/form_field_order",
            data=field_order_data
        )
    
    def configure_field_requirements(self, service_desk_id: str, request_type_id: str, 
                                  field_requirements: Dict[str, Dict]) -> Dict:
        """
        Configure field requirements for a request type form.
        
        Args:
            service_desk_id: The ID of the service desk
            request_type_id: The ID of the request type
            field_requirements: Dictionary mapping field IDs to requirement configs
            
        Returns:
            Dictionary containing result information
        """
        # This is a simplified implementation
        # In practice, this might require admin API access
        
        # Get project key for the service desk
        service_desk_info = self._make_api_request("GET", f"/servicedesk/{service_desk_id}")
        project_key = service_desk_info.get("projectKey", "")
        
        # Format field requirements data
        requirements_data = {
            "projectKey": project_key,
            "requestTypeId": request_type_id,
            "fieldRequirements": field_requirements
        }
        
        # Store as a property on the project
        return self._make_jira_api_request(
            "PUT", 
            f"/project/{project_key}/properties/form_field_requirements",
            data=requirements_data
        )
    
    # ======= FORM VALIDATION OPERATIONS =======
    
    def validate_form_data(self, service_desk_id: str, request_type_id: str, 
                         form_data: Dict) -> Dict:
        """
        Validate form data against field requirements.
        
        Args:
            service_desk_id: The ID of the service desk
            request_type_id: The ID of the request type
            form_data: Dictionary of form field values
            
        Returns:
            Dictionary containing validation results
        """
        # Get field requirements
        fields = self.get_request_type_fields(service_desk_id, request_type_id)
        
        validation_results = {
            "isValid": True,
            "errors": {}
        }
        
        if "requestTypeFields" in fields:
            for field in fields.get("requestTypeFields", []):
                field_id = field.get("fieldId", "")
                required = field.get("required", False)
                
                # Check required fields
                if required and (field_id not in form_data or not form_data.get(field_id)):
                    validation_results["isValid"] = False
                    validation_results["errors"][field_id] = "This field is required"
                
                # Check field-specific validations
                elif field_id in form_data:
                    field_value = form_data.get(field_id)
                    field_type = field.get("jiraSchema", {}).get("type")
                    
                    field_error = self._validate_field(field_type, field_value, field)
                    if field_error:
                        validation_results["isValid"] = False
                        validation_results["errors"][field_id] = field_error
        
        return validation_results
    
    def _validate_field(self, field_type: str, field_value: Any, field_definition: Dict) -> Optional[str]:
        """
        Validate a field value based on its type and definition.
        
        Args:
            field_type: The type of the field
            field_value: The value to validate
            field_definition: The field definition containing validation rules
            
        Returns:
            Error message if validation fails, None if valid
        """
        # Validate based on field type
        if field_type == "number" or field_type.endswith(":float"):
            try:
                value = float(field_value)
                
                # Check min/max if defined
                min_value = field_definition.get("schema", {}).get("minimum")
                max_value = field_definition.get("schema", {}).get("maximum")
                
                if min_value is not None and value < min_value:
                    return f"Value must be at least {min_value}"
                    
                if max_value is not None and value > max_value:
                    return f"Value must be at most {max_value}"
                    
            except (ValueError, TypeError):
                return "Must be a valid number"
                
        elif field_type == "text" or field_type.endswith(":textfield"):
            if not isinstance(field_value, str):
                return "Must be a string"
                
            # Check max length if defined
            max_length = field_definition.get("schema", {}).get("maxLength")
            if max_length is not None and len(field_value) > max_length:
                return f"Cannot exceed {max_length} characters"
                
        elif field_type == "select" or field_type.endswith(":select"):
            allowed_values = [option.get("value") for option in 
                            field_definition.get("allowedValues", [])]
            
            if allowed_values and field_value not in allowed_values:
                return f"Must be one of: {', '.join(allowed_values)}"
                
        elif field_type == "multiselect" or field_type.endswith(":multiselect"):
            if not isinstance(field_value, list):
                return "Must be a list of values"
                
            allowed_values = [option.get("value") for option in 
                            field_definition.get("allowedValues", [])]
            
            if allowed_values:
                for value in field_value:
                    if value not in allowed_values:
                        return f"All values must be from: {', '.join(allowed_values)}"
                
        # Add more validations for other field types as needed
        
        return None  # No validation errors