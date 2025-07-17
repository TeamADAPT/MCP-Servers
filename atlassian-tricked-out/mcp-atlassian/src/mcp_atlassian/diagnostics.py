"""Diagnostics Module for MCP Atlassian Integration.

This module provides diagnostic tools for troubleshooting and validating
the MCP Atlassian integration setup.
"""

import os
import sys
import json
import logging
import platform
import traceback
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import pkg_resources

from .feature_flags import get_all_flags, get_feature_groups
from .constants import (
    TOOL_CATEGORY_CONFLUENCE,
    TOOL_CATEGORY_JIRA,
    TOOL_CATEGORY_JSM,
    TOOL_CATEGORY_BITBUCKET,
    TOOL_CATEGORY_ENTERPRISE,
)

# Configure logging
logger = logging.getLogger("mcp-atlassian")


def check_required_env_vars() -> Dict[str, bool]:
    """Check if required environment variables are set.
    
    Returns:
        Dict[str, bool]: Dictionary with environment variable status
    """
    required_vars = {
        # Core Jira vars
        "JIRA_URL": False,
        "JIRA_USERNAME": False,
        "JIRA_API_TOKEN": False,
        
        # Core Confluence vars
        "CONFLUENCE_URL": False,
        "CONFLUENCE_USERNAME": False,
        "CONFLUENCE_API_TOKEN": False,
    }
    
    # Optional environment variables grouped by feature
    optional_vars = {
        "ENABLE_ENHANCED_JIRA": False,
        "ENABLE_ENHANCED_CONFLUENCE": False,
        "ENABLE_JSM": False,
        "ENABLE_BITBUCKET": False,
        "ENABLE_ENTERPRISE": False,
        "FEATURE_FLAGS_CONFIG": False,
        "MCP_ATLASSIAN_LOG_LEVEL": False,
    }
    
    # Check required vars
    for var_name in required_vars:
        value = os.getenv(var_name)
        required_vars[var_name] = value is not None and value != ""
    
    # Check optional vars
    for var_name in optional_vars:
        value = os.getenv(var_name)
        optional_vars[var_name] = value is not None and value != ""
    
    return {
        "required": required_vars,
        "optional": optional_vars,
        "all_required_vars_set": all(required_vars.values())
    }


def check_dependencies() -> Dict[str, Any]:
    """Check if required dependencies are installed.
    
    Returns:
        Dict[str, Any]: Dictionary with dependency status
    """
    required_packages = [
        "mcp",
        "atlassian-python-api",
        "pydantic",
        "python-dotenv",
    ]
    
    package_status = {}
    for package in required_packages:
        try:
            version = pkg_resources.get_distribution(package).version
            package_status[package] = {
                "installed": True,
                "version": version
            }
        except pkg_resources.DistributionNotFound:
            package_status[package] = {
                "installed": False,
                "version": None
            }
        except Exception as e:
            package_status[package] = {
                "installed": False,
                "version": None,
                "error": str(e)
            }
    
    return {
        "package_status": package_status,
        "all_required_packages_installed": all(info["installed"] for info in package_status.values())
    }


def check_atlassian_api_connection() -> Dict[str, Any]:
    """Check connection to Atlassian APIs.
    
    Returns:
        Dict[str, Any]: Dictionary with connection status
    """
    results = {
        "jira": {
            "connected": False,
            "error": None
        },
        "confluence": {
            "connected": False,
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
                results["jira"]["connected"] = True
                results["jira"]["server_info"] = {
                    "version": server_info.get("version", "Unknown"),
                    "build_number": server_info.get("buildNumber", "Unknown"),
                    "server_title": server_info.get("serverTitle", "Unknown")
                }
        except Exception as e:
            results["jira"]["error"] = str(e)
            logger.error(f"Error checking Jira connection: {e}")
    else:
        results["jira"]["error"] = "Missing required environment variables"
    
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
                results["confluence"]["connected"] = True
                results["confluence"]["spaces_count"] = spaces.get("size", 0)
        except Exception as e:
            results["confluence"]["error"] = str(e)
            logger.error(f"Error checking Confluence connection: {e}")
    else:
        results["confluence"]["error"] = "Missing required environment variables"
    
    return results


def check_feature_flags() -> Dict[str, Any]:
    """Check feature flag status.
    
    Returns:
        Dict[str, Any]: Dictionary with feature flag status
    """
    all_flags = get_all_flags()
    feature_groups = get_feature_groups()
    
    # Organize flags by group
    grouped_flags = {}
    for group_name, flags in feature_groups.items():
        grouped_flags[group_name] = {
            flag: all_flags.get(flag, False) for flag in flags if flag in all_flags
        }
    
    # Find enabled features
    enabled_flags = [name for name, enabled in all_flags.items() if enabled]
    
    return {
        "all_flags": all_flags,
        "grouped_flags": grouped_flags,
        "enabled_flags": enabled_flags,
        "has_enabled_flags": len(enabled_flags) > 0
    }


def check_modules_loaded() -> Dict[str, Any]:
    """Check which enhanced modules are loaded.
    
    Returns:
        Dict[str, Any]: Dictionary with module load status
    """
    module_status = {
        "enhanced_jira": False,
        "enhanced_confluence": False,
        "jsm": False,
        "bitbucket": False,
        "enterprise": False
    }
    
    # Check for enhanced Jira module
    try:
        from . import enhanced_jira
        module_status["enhanced_jira"] = True
    except ImportError:
        pass
    
    # We only check for module files existence, not actually importing them
    # to avoid potential import errors if they have missing dependencies
    module_path = os.path.dirname(os.path.abspath(__file__))
    
    # Check for server module files
    server_modules = {
        "server_enhanced_jira.py": "enhanced_jira",
        "server_enhanced_confluence.py": "enhanced_confluence",
        "server_jira_service_management.py": "jsm",
        "server_bitbucket.py": "bitbucket",
        "server_enterprise.py": "enterprise"
    }
    
    for filename, feature in server_modules.items():
        file_path = os.path.join(module_path, filename)
        if os.path.exists(file_path):
            module_status[feature] = True
    
    return module_status


def get_system_info() -> Dict[str, Any]:
    """Get system information.
    
    Returns:
        Dict[str, Any]: Dictionary with system information
    """
    return {
        "platform": platform.platform(),
        "python_version": platform.python_version(),
        "python_implementation": platform.python_implementation(),
        "python_path": sys.executable,
        "date": datetime.now().isoformat(),
    }


def run_diagnostics() -> Dict[str, Any]:
    """Run all diagnostics and return results.
    
    Returns:
        Dict[str, Any]: Dictionary with all diagnostic results
    """
    return {
        "system_info": get_system_info(),
        "env_vars": check_required_env_vars(),
        "dependencies": check_dependencies(),
        "feature_flags": check_feature_flags(),
        "modules_loaded": check_modules_loaded(),
        "api_connection": check_atlassian_api_connection(),
    }


def format_diagnostics_report(diagnostics: Dict[str, Any]) -> str:
    """Format diagnostics results as a readable report.
    
    Args:
        diagnostics: Dictionary with diagnostics results
        
    Returns:
        str: Formatted report
    """
    def _format_status(status: bool) -> str:
        return "[✓]" if status else "[✗]"
    
    lines = []
    
    # System info
    system_info = diagnostics["system_info"]
    lines.append("=== System Information ===")
    lines.append(f"Platform: {system_info['platform']}")
    lines.append(f"Python: {system_info['python_version']} ({system_info['python_implementation']})")
    lines.append(f"Python Path: {system_info['python_path']}")
    lines.append(f"Date: {system_info['date']}")
    lines.append("")
    
    # Environment variables
    env_vars = diagnostics["env_vars"]
    required_vars = env_vars["required"]
    optional_vars = env_vars["optional"]
    
    lines.append("=== Environment Variables ===")
    lines.append("Required:")
    for var_name, is_set in required_vars.items():
        lines.append(f"  {_format_status(is_set)} {var_name}")
    
    lines.append("\nOptional:")
    for var_name, is_set in optional_vars.items():
        lines.append(f"  {_format_status(is_set)} {var_name}")
    lines.append("")
    
    # Dependencies
    dependencies = diagnostics["dependencies"]
    package_status = dependencies["package_status"]
    
    lines.append("=== Dependencies ===")
    for package, info in package_status.items():
        version_str = f"v{info['version']}" if info["version"] else "Not Installed"
        lines.append(f"  {_format_status(info['installed'])} {package}: {version_str}")
    lines.append("")
    
    # Feature flags
    feature_flags = diagnostics["feature_flags"]
    grouped_flags = feature_flags["grouped_flags"]
    
    lines.append("=== Feature Flags ===")
    for group_name, flags in grouped_flags.items():
        lines.append(f"{group_name.capitalize()}:")
        for flag_name, enabled in flags.items():
            lines.append(f"  {_format_status(enabled)} {flag_name}")
        lines.append("")
    
    # Modules loaded
    modules_loaded = diagnostics["modules_loaded"]
    
    lines.append("=== Module Status ===")
    for module_name, loaded in modules_loaded.items():
        lines.append(f"  {_format_status(loaded)} {module_name}")
    lines.append("")
    
    # API Connection
    api_connection = diagnostics["api_connection"]
    
    lines.append("=== API Connection ===")
    
    # Jira connection
    jira_status = api_connection["jira"]
    lines.append(f"Jira: {_format_status(jira_status['connected'])}")
    if jira_status["connected"]:
        server_info = jira_status["server_info"]
        lines.append(f"  Version: {server_info['version']}")
        lines.append(f"  Build: {server_info['build_number']}")
        lines.append(f"  Title: {server_info['server_title']}")
    elif jira_status["error"]:
        lines.append(f"  Error: {jira_status['error']}")
    
    # Confluence connection
    confluence_status = api_connection["confluence"]
    lines.append(f"Confluence: {_format_status(confluence_status['connected'])}")
    if confluence_status["connected"]:
        lines.append(f"  Spaces Count: {confluence_status['spaces_count']}")
    elif confluence_status["error"]:
        lines.append(f"  Error: {confluence_status['error']}")
    
    return "\n".join(lines)


def save_diagnostics_report(report: str, file_path: Optional[str] = None) -> str:
    """Save diagnostics report to a file.
    
    Args:
        report: Diagnostics report string
        file_path: Path to save the report (optional)
        
    Returns:
        str: Path to the saved report
    """
    if not file_path:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = f"mcp_atlassian_diagnostics_{timestamp}.txt"
    
    with open(file_path, "w") as f:
        f.write(report)
    
    return file_path


def main():
    """Run diagnostics and print report."""
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    print("Running MCP Atlassian diagnostics...")
    diagnostics = run_diagnostics()
    report = format_diagnostics_report(diagnostics)
    
    print("\nDiagnostics Report:")
    print(report)
    
    # Save report
    file_path = save_diagnostics_report(report)
    print(f"\nReport saved to: {file_path}")


if __name__ == "__main__":
    main()