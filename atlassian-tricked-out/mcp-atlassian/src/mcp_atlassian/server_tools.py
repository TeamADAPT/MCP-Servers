"""Server tools for MCP Atlassian integration.

This module provides utility functions for working with the MCP server.
It includes tools for checking module availability, verifying credentials,
and registering tools with the MCP server.
"""

import os
import logging
import importlib.util
import sys
from typing import List, Dict, Any, Optional, Callable, Tuple

from mcp.types import Tool

from .feature_flags import is_enabled, get_all_flags
from .constants import (
    TOOL_CATEGORY_CONFLUENCE,
    TOOL_CATEGORY_JIRA,
    TOOL_CATEGORY_JSM,
    TOOL_CATEGORY_BITBUCKET,
    TOOL_CATEGORY_ENTERPRISE,
    STATUS_SUCCESS,
    STATUS_ERROR,
    ERROR_MISSING_CREDENTIALS,
    ERROR_SERVICE_UNAVAILABLE,
)

# Configure logging
logger = logging.getLogger("mcp-atlassian")


def verify_module_imports() -> Dict[str, bool]:
    """Verify that all required modules can be imported.
    
    Returns:
        Dict[str, bool]: Dictionary with module import status
    """
    modules = {
        "enhanced_jira": False,
        "server_enhanced_jira": False,
        "server_enhanced_confluence": False,
        "server_jira_service_management": False,
        "server_bitbucket": False,
        "server_enterprise": False,
    }
    
    for module_name in modules:
        try:
            full_module_name = f"src.mcp_atlassian.{module_name}"
            spec = importlib.util.find_spec(full_module_name)
            if spec is not None:
                modules[module_name] = True
        except (ImportError, AttributeError) as e:
            logger.warning(f"Module {module_name} not available: {e}")
    
    return modules


def verify_credentials() -> Dict[str, bool]:
    """Verify that required credentials are available.
    
    Returns:
        Dict[str, bool]: Dictionary with credential availability status
    """
    credentials = {
        "jira": all([
            os.getenv("JIRA_URL"),
            os.getenv("JIRA_USERNAME"),
            os.getenv("JIRA_API_TOKEN")
        ]),
        "confluence": all([
            os.getenv("CONFLUENCE_URL"),
            os.getenv("CONFLUENCE_USERNAME"),
            os.getenv("CONFLUENCE_API_TOKEN")
        ]),
    }
    
    return credentials


def verify_feature_availability() -> Dict[str, Dict[str, Any]]:
    """Verify feature availability based on credentials and feature flags.
    
    Returns:
        Dict[str, Dict[str, Any]]: Dictionary with feature availability status
    """
    credentials = verify_credentials()
    modules = verify_module_imports()
    flags = get_all_flags()
    
    availability = {
        "base_jira": {
            "available": credentials["jira"],
            "reason": None if credentials["jira"] else ERROR_MISSING_CREDENTIALS
        },
        "base_confluence": {
            "available": credentials["confluence"],
            "reason": None if credentials["confluence"] else ERROR_MISSING_CREDENTIALS
        },
        "enhanced_jira": {
            "available": (
                credentials["jira"] and 
                modules["enhanced_jira"] and 
                modules["server_enhanced_jira"] and
                flags.get("enhanced_jira", False)
            ),
            "reason": _get_unavailability_reason(
                credentials["jira"], 
                modules["enhanced_jira"] and modules["server_enhanced_jira"],
                flags.get("enhanced_jira", False)
            )
        },
        "enhanced_confluence": {
            "available": (
                credentials["confluence"] and 
                modules["server_enhanced_confluence"] and
                flags.get("enhanced_confluence", False)
            ),
            "reason": _get_unavailability_reason(
                credentials["confluence"], 
                modules["server_enhanced_confluence"],
                flags.get("enhanced_confluence", False)
            )
        },
        "jsm": {
            "available": (
                credentials["jira"] and 
                modules["server_jira_service_management"] and
                flags.get("jsm", False)
            ),
            "reason": _get_unavailability_reason(
                credentials["jira"], 
                modules["server_jira_service_management"],
                flags.get("jsm", False)
            )
        },
        "bitbucket": {
            "available": (
                modules["server_bitbucket"] and
                flags.get("bitbucket", False)
            ),
            "reason": _get_unavailability_reason(
                True,  # No credentials required yet
                modules["server_bitbucket"],
                flags.get("bitbucket", False)
            )
        },
        "enterprise": {
            "available": (
                credentials["jira"] and 
                credentials["confluence"] and 
                modules["server_enterprise"] and
                flags.get("enterprise", False)
            ),
            "reason": _get_unavailability_reason(
                credentials["jira"] and credentials["confluence"], 
                modules["server_enterprise"],
                flags.get("enterprise", False)
            )
        }
    }
    
    return availability


def _get_unavailability_reason(has_credentials: bool, has_module: bool, is_flag_enabled: bool) -> Optional[str]:
    """Get the reason why a feature is unavailable.
    
    Args:
        has_credentials: Whether the required credentials are available
        has_module: Whether the required module is available
        is_flag_enabled: Whether the feature flag is enabled
        
    Returns:
        Optional[str]: Reason why the feature is unavailable, or None if available
    """
    if not has_credentials:
        return ERROR_MISSING_CREDENTIALS
    if not has_module:
        return "Module not available"
    if not is_flag_enabled:
        return "Feature not enabled"
    return None


def get_module_function(module_name: str, function_name: str) -> Optional[Callable]:
    """Get a function from a module dynamically.
    
    Args:
        module_name: Name of the module
        function_name: Name of the function
        
    Returns:
        Optional[Callable]: Function if found, None otherwise
    """
    try:
        module = importlib.import_module(f"src.mcp_atlassian.{module_name}")
        function = getattr(module, function_name, None)
        return function
    except (ImportError, AttributeError) as e:
        logger.warning(f"Could not get function {function_name} from module {module_name}: {e}")
        return None


def safe_import_module_tools(module_name: str, get_tools_function: str, feature_name: str) -> List[Tool]:
    """Safely import tools from a module, handling any exceptions.
    
    Args:
        module_name: Name of the module
        get_tools_function: Name of the function that returns tools
        feature_name: Name of the feature for logging
        
    Returns:
        List[Tool]: List of tools from the module, or empty list if module not available
    """
    if not is_enabled(feature_name):
        logger.debug(f"Feature {feature_name} is not enabled, skipping tool import")
        return []
    
    try:
        function = get_module_function(module_name, get_tools_function)
        if function:
            tools = function()
            logger.info(f"Loaded {len(tools)} tools from {module_name}")
            return tools
        else:
            logger.warning(f"Function {get_tools_function} not found in module {module_name}")
            return []
    except Exception as e:
        logger.error(f"Error importing tools from {module_name}: {e}")
        return []


def runtime_check_api_availability() -> Dict[str, Dict[str, Any]]:
    """Perform a runtime check of API availability.
    
    Returns:
        Dict[str, Dict[str, Any]]: Dictionary with API availability status
    """
    results = {
        "jira": {
            "available": False,
            "error": None
        },
        "confluence": {
            "available": False,
            "error": None
        }
    }
    
    # Check Jira connection
    if all([os.getenv("JIRA_URL"), os.getenv("JIRA_USERNAME"), os.getenv("JIRA_API_TOKEN")]):
        try:
            from atlassian import Jira
            jira = Jira(
                url=os.getenv("JIRA_URL"),
                username=os.getenv("JIRA_USERNAME"),
                password=os.getenv("JIRA_API_TOKEN"),
                cloud=True
            )
            
            # Try to get server info
            server_info = jira.get_server_info()
            if server_info:
                results["jira"]["available"] = True
        except Exception as e:
            results["jira"]["error"] = str(e)
            logger.error(f"Error checking Jira availability: {e}")
    else:
        results["jira"]["error"] = ERROR_MISSING_CREDENTIALS
    
    # Check Confluence connection
    if all([os.getenv("CONFLUENCE_URL"), os.getenv("CONFLUENCE_USERNAME"), os.getenv("CONFLUENCE_API_TOKEN")]):
        try:
            from atlassian import Confluence
            confluence = Confluence(
                url=os.getenv("CONFLUENCE_URL"),
                username=os.getenv("CONFLUENCE_USERNAME"),
                password=os.getenv("CONFLUENCE_API_TOKEN"),
                cloud=True
            )
            
            # Try to get Confluence spaces
            spaces = confluence.get_all_spaces(limit=1)
            if spaces and "results" in spaces:
                results["confluence"]["available"] = True
        except Exception as e:
            results["confluence"]["error"] = str(e)
            logger.error(f"Error checking Confluence availability: {e}")
    else:
        results["confluence"]["error"] = ERROR_MISSING_CREDENTIALS
    
    return results


def create_availability_check_report() -> str:
    """Create a report of feature and API availability.
    
    Returns:
        str: Report of availability status
    """
    feature_availability = verify_feature_availability()
    api_availability = runtime_check_api_availability()
    
    lines = []
    lines.append("MCP Atlassian Availability Report")
    lines.append("===============================")
    
    # API Availability
    lines.append("\nAPI Availability:")
    for api_name, status in api_availability.items():
        status_str = "✓ Available" if status["available"] else f"✗ Unavailable: {status['error']}"
        lines.append(f"  {api_name}: {status_str}")
    
    # Feature Availability
    lines.append("\nFeature Availability:")
    for feature_name, status in feature_availability.items():
        status_str = "✓ Available" if status["available"] else f"✗ Unavailable: {status['reason']}"
        lines.append(f"  {feature_name}: {status_str}")
    
    return "\n".join(lines)


def handle_tool_exception(name: str, error: Exception) -> Dict[str, Any]:
    """Handle an exception from a tool call.
    
    Args:
        name: Name of the tool
        error: The exception that occurred
        
    Returns:
        Dict[str, Any]: Error response
    """
    logger.error(f"Error executing tool {name}: {error}")
    
    return {
        "status": STATUS_ERROR,
        "message": f"Tool execution failed: {str(error)}",
        "error": str(error),
        "tool": name
    }