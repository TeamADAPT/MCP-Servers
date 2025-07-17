"""
Marketplace App Integration for MCP Atlassian.

This module provides enterprise-grade integration with Atlassian Marketplace apps,
including connectors for popular apps like Tempo, automation capabilities,
and an extensible framework for future integrations.
"""

import os
import json
import logging
import importlib
import inspect
from typing import Dict, List, Optional, Any, Callable, Union, Tuple, Type
from abc import ABC, abstractmethod

from .auth import with_auth_client, AuthenticatedClient

# Configure logging
logger = logging.getLogger("mcp-atlassian.marketplace_integration")


class AppConnector(ABC):
    """
    Abstract base class for marketplace app connectors.
    
    All app connectors should inherit from this class and implement
    the required methods.
    """
    
    @property
    @abstractmethod
    def app_key(self) -> str:
        """Return the unique key for this app connector."""
        pass
        
    @property
    @abstractmethod
    def app_name(self) -> str:
        """Return the human-readable name for this app."""
        pass
        
    @property
    @abstractmethod
    def app_description(self) -> str:
        """Return a description of the app's functionality."""
        pass
        
    @property
    def app_version(self) -> str:
        """Return the app version that this connector supports."""
        return "latest"
        
    @property
    def supported_products(self) -> List[str]:
        """Return the Atlassian products this app supports."""
        return ["jira", "confluence"]
        
    @property
    def required_scopes(self) -> List[str]:
        """Return the OAuth scopes required by this app."""
        return []
        
    @property
    def configuration_params(self) -> Dict[str, Dict]:
        """
        Return configuration parameters required by this connector.
        
        Each parameter should have a key and a dict with:
        - description: Human-readable description
        - required: Whether the param is required
        - type: Data type (string, integer, boolean, etc.)
        - default: Default value (optional)
        """
        return {}
        
    @abstractmethod
    def validate_configuration(self, config: Dict) -> Tuple[bool, Optional[str]]:
        """
        Validate the connector configuration.
        
        Args:
            config: Configuration parameters
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        pass
        
    @abstractmethod
    def get_capabilities(self) -> List[Dict]:
        """
        Return a list of capabilities provided by this connector.
        
        Each capability should be a dict with:
        - id: Unique identifier
        - name: Human-readable name
        - description: Human-readable description
        - method_name: Name of the method implementing this capability
        - parameters: Dict of parameter definitions similar to configuration_params
        
        Returns:
            List of capability dictionaries
        """
        pass


class TempoConnector(AppConnector):
    """
    Connector for Tempo Timesheets, a time tracking app for Jira.
    
    Provides integration with Tempo API for time tracking, reporting,
    and worklog management.
    """
    
    @property
    def app_key(self) -> str:
        return "com.tempoplugin.tempo-timesheets"
        
    @property
    def app_name(self) -> str:
        return "Tempo Timesheets"
        
    @property
    def app_description(self) -> str:
        return "Time tracking, planning, and visualization tool for Jira."
        
    @property
    def app_version(self) -> str:
        return "4.x"
        
    @property
    def supported_products(self) -> List[str]:
        return ["jira"]
        
    @property
    def required_scopes(self) -> List[str]:
        return ["tempo-timesheets:read", "tempo-timesheets:write"]
        
    @property
    def configuration_params(self) -> Dict[str, Dict]:
        return {
            "tempo_api_token": {
                "description": "Tempo API token for authentication",
                "required": True,
                "type": "string",
                "secret": True
            },
            "tempo_base_url": {
                "description": "Base URL for Tempo API",
                "required": False,
                "type": "string",
                "default": "https://YOUR-CREDENTIALS@YOUR-DOMAIN/worklogs", 
                params=request_params
            )
            
            if response.get("error"):
                return response
                
            return {
                "worklogs": response.get("results", []),
                "metadata": {
                    "total": response.get("metadata", {}).get("count", 0),
                    "from_date": params["from_date"],
                    "to_date": params["to_date"]
                }
            }
        except Exception as e:
            logger.error(f"Error getting Tempo worklogs: {str(e)}")
            return {"error": f"Failed to retrieve worklogs: {str(e)}"}
            
    @with_auth_client("jira")
    def create_worklog(self, client: AuthenticatedClient, config: Dict, params: Dict) -> Dict:
        """
        Create a worklog in Tempo.
        
        Args:
            client: Authenticated client
            config: Connector configuration
            params: Function parameters
            
        Returns:
            Dict containing created worklog data
        """
        # Validate required parameters
        required_params = ["issue_key", "time_spent_seconds", "start_date", "start_time"]
        missing = [p for p in required_params if p not in params]
        if missing:
            return {"error": f"Missing required parameters: {', '.join(missing)}"}
            
        # Get account ID for the currently authenticated user
        try:
            user_response = client.request(
                "GET",
                f"{os.environ.get('JIRA_URL')}/rest/api/2/myself"
            )
            
            if user_response.status_code != 200:
                return {"error": f"Failed to retrieve user data: {user_response.text}"}
                
            account_id = user_response.json().get("accountId")
            if not account_id:
                return {"error": "Failed to determine user account ID"}
                
            # Prepare worklog data
            start_datetime = f"{params['start_date']}T{params['start_time']}"
            
            worklog_data = {
                "issueKey": params["issue_key"],
                "timeSpentSeconds": params["time_spent_seconds"],
                "startDate": params["start_date"],
                "startTime": params["start_time"],
                "authorAccountId": account_id,
                "description": params.get("description", "")
            }
            
            # Make API request to Tempo
            response = self._tempo_request(
                client,
                config,
                "POST",
                "/worklogs",
                json=worklog_data
            )
            
            if response.get("error"):
                return response
                
            return {
                "worklog": response,
                "message": f"Worklog created successfully for {params['issue_key']}"
            }
        except Exception as e:
            logger.error(f"Error creating Tempo worklog: {str(e)}")
            return {"error": f"Failed to create worklog: {str(e)}"}
            
    @with_auth_client("jira")
    def get_user_schedule(self, client: AuthenticatedClient, config: Dict, params: Dict) -> Dict:
        """
        Get a user's work schedule from Tempo.
        
        Args:
            client: Authenticated client
            config: Connector configuration
            params: Function parameters
            
        Returns:
            Dict containing user schedule data
        """
        # Validate required parameters
        if "user_id" not in params or "from_date" not in params or "to_date" not in params:
            return {"error": "Missing required parameters: user_id, from_date, and to_date"}
            
        # Prepare request parameters
        request_params = {
            "from": params["from_date"],
            "to": params["to_date"],
            "userId": params["user_id"]
        }
        
        # Make API request to Tempo
        try:
            response = self._tempo_request(
                client,
                config,
                "GET",
                "/user-schedule",
                params=request_params
            )
            
            if response.get("error"):
                return response
                
            return {
                "user_id": params["user_id"],
                "schedule": response.get("results", []),
                "metadata": {
                    "total_days": len(response.get("results", [])),
                    "from_date": params["from_date"],
                    "to_date": params["to_date"]
                }
            }
        except Exception as e:
            logger.error(f"Error getting Tempo user schedule: {str(e)}")
            return {"error": f"Failed to retrieve user schedule: {str(e)}"}
            
    @with_auth_client("jira")
    def get_timesheet_approvals(self, client: AuthenticatedClient, config: Dict, params: Dict) -> Dict:
        """
        Get timesheet approval status from Tempo.
        
        Args:
            client: Authenticated client
            config: Connector configuration
            params: Function parameters
            
        Returns:
            Dict containing timesheet approval data
        """
        # Validate required parameters
        if "from_date" not in params or "to_date" not in params:
            return {"error": "Missing required parameters: from_date and to_date"}
            
        # At least one of user_id or team_id is required
        if "user_id" not in params and "team_id" not in params:
            return {"error": "At least one of user_id or team_id is required"}
            
        # Prepare request parameters
        request_params = {
            "from": params["from_date"],
            "to": params["to_date"],
            "limit": 1000
        }
        
        if "user_id" in params:
            request_params["userId"] = params["user_id"]
        if "team_id" in params:
            request_params["teamId"] = params["team_id"]
            
        # Make API request to Tempo
        try:
            response = self._tempo_request(
                client,
                config,
                "GET",
                "/timesheet-approvals",
                params=request_params
            )
            
            if response.get("error"):
                return response
                
            return {
                "approvals": response.get("results", []),
                "metadata": {
                    "total": response.get("metadata", {}).get("count", 0),
                    "from_date": params["from_date"],
                    "to_date": params["to_date"]
                }
            }
        except Exception as e:
            logger.error(f"Error getting Tempo timesheet approvals: {str(e)}")
            return {"error": f"Failed to retrieve timesheet approvals: {str(e)}"}
            
    def _tempo_request(self, client: AuthenticatedClient, config: Dict, method: str, 
                      endpoint: str, params: Optional[Dict] = None, json: Optional[Dict] = None) -> Dict:
        """
        Make a request to the Tempo API.
        
        Args:
            client: Authenticated client (used only for logging)
            config: Connector configuration
            method: HTTP method
            endpoint: API endpoint
            params: Query parameters
            json: JSON body data
            
        Returns:
            Dict containing response data
        """
        import requests
        
        base_url = config.get("tempo_base_url", "https://YOUR-CREDENTIALS@YOUR-DOMAIN/rest/atm/1.0"
            response = self._zephyr_request(
                client,
                config,
                "GET",
                f"{base_url}/testcase/search",
                params=request_params
            )
            
            if response.get("error"):
                return response
                
            return {
                "test_cases": response.get("values", []),
                "metadata": {
                    "total": response.get("total", 0),
                    "project_key": params["project_key"]
                }
            }
        except Exception as e:
            logger.error(f"Error getting Zephyr test cases: {str(e)}")
            return {"error": f"Failed to retrieve test cases: {str(e)}"}
            
    @with_auth_client("jira")
    def create_test_case(self, client: AuthenticatedClient, config: Dict, params: Dict) -> Dict:
        """
        Create a test case in Zephyr.
        
        Args:
            client: Authenticated client
            config: Connector configuration
            params: Function parameters
            
        Returns:
            Dict containing created test case data
        """
        # Validate required parameters
        required_params = ["project_key", "name", "objective"]
        missing = [p for p in required_params if p not in params]
        if missing:
            return {"error": f"Missing required parameters: {', '.join(missing)}"}
            
        # Prepare test case data
        test_case_data = {
            "projectKey": params["project_key"],
            "name": params["name"],
            "objective": params["objective"]
        }
        
        # Add optional fields
        if "precondition" in params:
            test_case_data["precondition"] = params["precondition"]
        if "folder_id" in params:
            test_case_data["folderId"] = params["folder_id"]
            
        # Add test steps if provided
        if "steps" in params and params["steps"]:
            test_case_data["testScript"] = {
                "steps": params["steps"]
            }
            
        # Make API request to Zephyr
        try:
            base_url = f"{os.environ.get('JIRA_URL')}/rest/atm/1.0"
            response = self._zephyr_request(
                client,
                config,
                "POST",
                f"{base_url}/testcase",
                json=test_case_data
            )
            
            if response.get("error"):
                return response
                
            return {
                "test_case": response,
                "message": f"Test case {response.get('key')} created successfully"
            }
        except Exception as e:
            logger.error(f"Error creating Zephyr test case: {str(e)}")
            return {"error": f"Failed to create test case: {str(e)}"}
            
    @with_auth_client("jira")
    def create_test_execution(self, client: AuthenticatedClient, config: Dict, params: Dict) -> Dict:
        """
        Create a test execution in Zephyr.
        
        Args:
            client: Authenticated client
            config: Connector configuration
            params: Function parameters
            
        Returns:
            Dict containing created test execution data
        """
        # Validate required parameters
        required_params = ["project_key", "test_case_key", "status"]
        missing = [p for p in required_params if p not in params]
        if missing:
            return {"error": f"Missing required parameters: {', '.join(missing)}"}
            
        # Validate status
        valid_statuses = ["PASS", "FAIL", "BLOCKED", "UNEXECUTED"]
        if params["status"] not in valid_statuses:
            return {"error": f"Invalid status. Must be one of: {', '.join(valid_statuses)}"}
            
        # Prepare execution data
        execution_data = {
            "projectKey": params["project_key"],
            "testCaseKey": params["test_case_key"],
            "status": params["status"]
        }
        
        # Add optional fields
        if "environment" in params:
            execution_data["environment"] = params["environment"]
        if "comment" in params:
            execution_data["comment"] = params["comment"]
        if "issue_key" in params:
            execution_data["issueKey"] = params["issue_key"]
            
        # Make API request to Zephyr
        try:
            base_url = f"{os.environ.get('JIRA_URL')}/rest/atm/1.0"
            response = self._zephyr_request(
                client,
                config,
                "POST",
                f"{base_url}/testrun",
                json=execution_data
            )
            
            if response.get("error"):
                return response
                
            return {
                "execution": response,
                "message": f"Test execution created successfully for {params['test_case_key']}"
            }
        except Exception as e:
            logger.error(f"Error creating Zephyr test execution: {str(e)}")
            return {"error": f"Failed to create test execution: {str(e)}"}
            
    @with_auth_client("jira")
    def get_test_cycles(self, client: AuthenticatedClient, config: Dict, params: Dict) -> Dict:
        """
        Get test cycles from Zephyr.
        
        Args:
            client: Authenticated client
            config: Connector configuration
            params: Function parameters
            
        Returns:
            Dict containing test cycle data
        """
        # Validate required parameters
        if "project_key" not in params:
            return {"error": "Missing required parameter: project_key"}
            
        # Prepare request parameters
        request_params = {
            "projectKey": params["project_key"],
            "maxResults": params.get("max_results", 50)
        }
        
        # Make API request to Zephyr
        try:
            base_url = f"{os.environ.get('JIRA_URL')}/rest/atm/1.0"
            response = self._zephyr_request(
                client,
                config,
                "GET",
                f"{base_url}/testrun/search",
                params=request_params
            )
            
            if response.get("error"):
                return response
                
            return {
                "test_cycles": response.get("values", []),
                "metadata": {
                    "total": response.get("total", 0),
                    "project_key": params["project_key"]
                }
            }
        except Exception as e:
            logger.error(f"Error getting Zephyr test cycles: {str(e)}")
            return {"error": f"Failed to retrieve test cycles: {str(e)}"}
            
    def _zephyr_request(self, client: AuthenticatedClient, config: Dict, method: str, 
                       url: str, params: Optional[Dict] = None, json: Optional[Dict] = None) -> Dict:
        """
        Make a request to the Zephyr API.
        
        Args:
            client: Authenticated client
            config: Connector configuration
            method: HTTP method
            url: API URL
            params: Query parameters
            json: JSON body data
            
        Returns:
            Dict containing response data
        """
        api_key = config.get("zephyr_api_key")
        
        if not api_key:
            return {"error": "Missing Zephyr API key in configuration"}
            
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            # Use the authenticated client to make the request
            response = client.request(
                method,
                url,
                headers=headers,
                params=params,
                json=json
            )
            
            if response.status_code >= 400:
                logger.error(f"Zephyr API error: {response.status_code} - {response.text}")
                return {
                    "error": f"Zephyr API error: {response.status_code}",
                    "details": response.text
                }
                
            return response.json()
        except Exception as e:
            logger.error(f"Error making Zephyr API request: {str(e)}")
            return {"error": f"Failed to communicate with Zephyr API: {str(e)}"}


class AppIntegrationManager:
    """
    Manages the integration with Atlassian Marketplace apps.
    
    Provides a centralized interface for interacting with various apps,
    managing their configuration, and executing their capabilities.
    """
    
    def __init__(self):
        """Initialize the AppIntegrationManager."""
        self.connectors = {}
        self.configs = {}
        
        # Load available app connectors
        self._load_connectors()
        
    def _load_connectors(self):
        """Load all available app connectors."""
        # Register built-in connectors
        self.register_connector(TempoConnector())
        self.register_connector(ZephyrConnector())
        
        # TODO: Discover and load external connectors from plugins directory
        
    def register_connector(self, connector: AppConnector) -> bool:
        """
        Register an app connector.
        
        Args:
            connector: AppConnector instance to register
            
        Returns:
            bool indicating success
        """
        if not isinstance(connector, AppConnector):
            logger.error(f"Attempted to register invalid connector: {connector}")
            return False
            
        app_key = connector.app_key
        if app_key in self.connectors:
            logger.warning(f"Connector for {app_key} already registered, overwriting")
            
        self.connectors[app_key] = connector
        logger.info(f"Registered connector for {connector.app_name} ({app_key})")
        return True
        
    def get_available_apps(self) -> List[Dict]:
        """
        Get a list of all available app integrations.
        
        Returns:
            List of app dictionaries with metadata
        """
        return [
            {
                "app_key": connector.app_key,
                "name": connector.app_name,
                "description": connector.app_description,
                "version": connector.app_version,
                "products": connector.supported_products,
                "configured": connector.app_key in self.configs,
                "capabilities_count": len(connector.get_capabilities())
            }
            for connector in self.connectors.values()
        ]
        
    def configure_app(self, app_key: str, config: Dict) -> Dict:
        """
        Configure an app integration.
        
        Args:
            app_key: Unique key for the app
            config: Configuration parameters
            
        Returns:
            Dict containing configuration result
        """
        if app_key not in self.connectors:
            return {"error": f"Unknown app: {app_key}"}
            
        connector = self.connectors[app_key]
        
        # Validate configuration
        is_valid, error = connector.validate_configuration(config)
        if not is_valid:
            return {"error": f"Invalid configuration: {error}"}
            
        # Store configuration
        self.configs[app_key] = config
        
        return {
            "success": True,
            "message": f"{connector.app_name} configured successfully",
            "app_key": app_key
        }
        
    def get_app_capabilities(self, app_key: str) -> Dict:
        """
        Get capabilities for a specific app.
        
        Args:
            app_key: Unique key for the app
            
        Returns:
            Dict containing app capabilities
        """
        if app_key not in self.connectors:
            return {"error": f"Unknown app: {app_key}"}
            
        connector = self.connectors[app_key]
        capabilities = connector.get_capabilities()
        
        return {
            "app_key": app_key,
            "app_name": connector.app_name,
            "configured": app_key in self.configs,
            "capabilities": capabilities
        }
        
    def execute_capability(self, app_key: str, capability_id: str, params: Dict) -> Dict:
        """
        Execute an app capability.
        
        Args:
            app_key: Unique key for the app
            capability_id: ID of the capability to execute
            params: Parameters for the capability
            
        Returns:
            Dict containing execution result
        """
        if app_key not in self.connectors:
            return {"error": f"Unknown app: {app_key}"}
            
        if app_key not in self.configs:
            return {"error": f"App {app_key} is not configured"}
            
        connector = self.connectors[app_key]
        config = self.configs[app_key]
        
        # Find the capability
        capabilities = connector.get_capabilities()
        capability = next((c for c in capabilities if c["id"] == capability_id), None)
        
        if not capability:
            return {"error": f"Unknown capability: {capability_id}"}
            
        # Get the method implementing the capability
        method_name = capability["method_name"]
        if not hasattr(connector, method_name):
            return {"error": f"Capability implementation not found: {method_name}"}
            
        method = getattr(connector, method_name)
        
        # Execute the capability
        try:
            # Pass the configuration to the method
            result = method(config=config, params=params)
            return result
        except Exception as e:
            logger.error(f"Error executing capability {capability_id}: {str(e)}")
            return {"error": f"Failed to execute capability: {str(e)}"}
            
    def get_app_status(self, app_key: str) -> Dict:
        """
        Get status information for an app.
        
        Args:
            app_key: Unique key for the app
            
        Returns:
            Dict containing app status
        """
        if app_key not in self.connectors:
            return {"error": f"Unknown app: {app_key}"}
            
        connector = self.connectors[app_key]
        configured = app_key in self.configs
        
        # Get additional status information if the app is configured
        status_info = {
            "app_key": app_key,
            "app_name": connector.app_name,
            "configured": configured,
            "version": connector.app_version,
            "products": connector.supported_products
        }
        
        if configured:
            # Add configuration status (without exposing sensitive values)
            config = self.configs[app_key]
            config_params = connector.configuration_params
            
            sanitized_config = {}
            for param, value in config.items():
                if param in config_params:
                    if config_params[param].get("secret", False):
                        sanitized_config[param] = "********"
                    else:
                        sanitized_config[param] = value
                else:
                    sanitized_config[param] = value
                    
            status_info["configuration"] = sanitized_config
            
        return status_info
        
    def remove_app_configuration(self, app_key: str) -> Dict:
        """
        Remove configuration for an app.
        
        Args:
            app_key: Unique key for the app
            
        Returns:
            Dict containing result
        """
        if app_key not in self.connectors:
            return {"error": f"Unknown app: {app_key}"}
            
        if app_key not in self.configs:
            return {"message": f"App {app_key} is not configured"}
            
        # Remove the configuration
        del self.configs[app_key]
        
        return {
            "success": True,
            "message": f"Configuration removed for {self.connectors[app_key].app_name}"
        }


# Create a global instance
app_integration_manager = AppIntegrationManager()