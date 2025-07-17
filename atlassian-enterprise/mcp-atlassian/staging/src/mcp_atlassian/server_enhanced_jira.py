"""
Server integration for Enhanced Jira manager.

This module provides server integration for the Enhanced Jira manager.
It registers tools for the Enhanced Jira functionality and handles tool calls.
"""

import logging
import json
from typing import Any, Dict, List, Optional

from mcp.types import Tool

from .enhanced_jira import EnhancedJiraManager
from .config import get_config
from .feature_flags import is_enabled, ENHANCED_JIRA

logger = logging.getLogger("mcp-atlassian-server-enhanced-jira")

# Global Enhanced Jira manager instance
_enhanced_jira_manager = None

def get_enhanced_jira_manager() -> EnhancedJiraManager:
    """
    Get Enhanced Jira manager singleton instance.
    
    Returns:
        EnhancedJiraManager: Enhanced Jira manager
    """
    global _enhanced_jira_manager
    
    if _enhanced_jira_manager is None:
        config = get_config()
        _enhanced_jira_manager = EnhancedJiraManager(
            url=config.jira.url,
            username=config.jira.username,
            api_token=config.jira.api_token
        )
    
    return _enhanced_jira_manager

def get_enhanced_jira_available() -> bool:
    """
    Check if Enhanced Jira is available.
    
    Returns:
        bool: True if Enhanced Jira is available
    """
    # Check if Enhanced Jira is enabled
    if not is_enabled(ENHANCED_JIRA):
        logger.debug("Enhanced Jira is disabled")
        return False
    
    # Check if Jira config is available
    config = get_config()
    if not config.jira.url or not config.jira.username or not config.jira.api_token:
        logger.warning("Jira configuration is incomplete")
        return False
    
    # Try to get Enhanced Jira manager
    try:
        get_enhanced_jira_manager()
        return True
    except Exception as e:
        logger.error(f"Failed to initialize Enhanced Jira manager: {str(e)}")
        return False

def handle_enhanced_jira_tool_call(name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle Enhanced Jira tool call.
    
    Args:
        name: Tool name
        arguments: Tool arguments
        
    Returns:
        Dict[str, Any]: Tool response
    """
    # Check if Enhanced Jira is available
    if not get_enhanced_jira_available():
        return {
            "error": "Enhanced Jira is not available. Enable it with the ENHANCED_JIRA feature flag."
        }
    
    # Get Enhanced Jira manager
    manager = get_enhanced_jira_manager()
    
    # Handle tool calls
    try:
        if name == "jira_enhanced_create_issue":
            return handle_create_issue(arguments, manager)
        elif name == "jira_enhanced_create_epic":
            return handle_create_epic(arguments, manager)
        elif name == "jira_enhanced_update_issue":
            return handle_update_issue(arguments, manager)
        elif name == "jira_enhanced_search_issues":
            return handle_search_issues(arguments, manager)
        elif name == "jira_enhanced_add_comment":
            return handle_add_comment(arguments, manager)
        elif name == "jira_enhanced_transition_issue":
            return handle_transition_issue(arguments, manager)
        elif name == "jira_enhanced_assign_issue":
            return handle_assign_issue(arguments, manager)
        elif name == "jira_enhanced_get_transitions":
            return handle_get_transitions(arguments, manager)
        elif name == "jira_enhanced_add_issues_to_epic":
            return handle_add_issues_to_epic(arguments, manager)
        elif name == "jira_enhanced_bulk_create_issues":
            return handle_bulk_create_issues(arguments, manager)
        elif name == "jira_enhanced_get_custom_fields":
            return handle_get_custom_fields(arguments, manager)
        elif name == "jira_enhanced_get_custom_field_id":
            return handle_get_custom_field_id(arguments, manager)
        else:
            return {
                "error": f"Unknown Enhanced Jira tool: {name}"
            }
    except Exception as e:
        logger.error(f"Error handling Enhanced Jira tool call: {str(e)}")
        return {
            "error": f"Error handling Enhanced Jira tool call: {str(e)}"
        }

def handle_create_issue(arguments: Dict[str, Any], manager: EnhancedJiraManager) -> Dict[str, Any]:
    """
    Handle create issue tool call.
    
    Args:
        arguments: Tool arguments
        manager: Enhanced Jira manager
        
    Returns:
        Dict[str, Any]: Tool response
    """
    # Get required arguments
    project_key = arguments.get("project_key")
    summary = arguments.get("summary")
    description = arguments.get("description", "")
    issue_type = arguments.get("issue_type", "Task")
    name = arguments.get("name")
    dept = arguments.get("dept")
    
    # Get optional arguments
    custom_fields = arguments.get("custom_fields", {})
    
    # Validate required arguments
    if not project_key:
        return {"error": "project_key is required"}
    if not summary:
        return {"error": "summary is required"}
    
    # Create issue
    issue = manager.create_issue(
        project_key=project_key,
        summary=summary,
        description=description,
        issue_type=issue_type,
        name=name,
        dept=dept,
        custom_fields=custom_fields
    )
    
    # Return response
    return {
        "key": issue.key,
        "id": issue.id,
        "self": issue.self,
        "summary": issue.fields.summary,
    }

def handle_create_epic(arguments: Dict[str, Any], manager: EnhancedJiraManager) -> Dict[str, Any]:
    """
    Handle create epic tool call.
    
    Args:
        arguments: Tool arguments
        manager: Enhanced Jira manager
        
    Returns:
        Dict[str, Any]: Tool response
    """
    # Get required arguments
    project_key = arguments.get("project_key")
    name = arguments.get("name")
    summary = arguments.get("summary")
    description = arguments.get("description", "")
    dept = arguments.get("dept")
    
    # Get optional arguments
    custom_fields = arguments.get("custom_fields", {})
    
    # Validate required arguments
    if not project_key:
        return {"error": "project_key is required"}
    if not name:
        return {"error": "name is required"}
    if not summary:
        return {"error": "summary is required"}
    
    # Create epic
    epic = manager.create_epic(
        project_key=project_key,
        name=name,
        summary=summary,
        description=description,
        dept=dept,
        custom_fields=custom_fields
    )
    
    # Return response
    return {
        "key": epic.key,
        "id": epic.id,
        "self": epic.self,
        "summary": epic.fields.summary,
    }

def handle_update_issue(arguments: Dict[str, Any], manager: EnhancedJiraManager) -> Dict[str, Any]:
    """
    Handle update issue tool call.
    
    Args:
        arguments: Tool arguments
        manager: Enhanced Jira manager
        
    Returns:
        Dict[str, Any]: Tool response
    """
    # Get required arguments
    issue_key = arguments.get("issue_key")
    fields = arguments.get("fields", {})
    
    # Validate required arguments
    if not issue_key:
        return {"error": "issue_key is required"}
    if not fields:
        return {"error": "fields is required"}
    
    # Update issue
    issue = manager.update_issue(issue_key, fields)
    
    # Return response
    return {
        "key": issue.key,
        "id": issue.id,
        "self": issue.self,
        "summary": issue.fields.summary,
    }

def handle_search_issues(arguments: Dict[str, Any], manager: EnhancedJiraManager) -> Dict[str, Any]:
    """
    Handle search issues tool call.
    
    Args:
        arguments: Tool arguments
        manager: Enhanced Jira manager
        
    Returns:
        Dict[str, Any]: Tool response
    """
    # Get required arguments
    jql = arguments.get("jql")
    
    # Get optional arguments
    max_results = arguments.get("max_results", 50)
    fields = arguments.get("fields")
    
    # Validate required arguments
    if not jql:
        return {"error": "jql is required"}
    
    # Search issues
    issues = manager.search_issues(jql, max_results, fields)
    
    # Return response
    result = []
    for issue in issues:
        result.append({
            "key": issue.key,
            "id": issue.id,
            "self": issue.self,
            "summary": issue.fields.summary,
        })
    
    return {
        "issues": result,
        "total": len(result),
    }

def handle_add_comment(arguments: Dict[str, Any], manager: EnhancedJiraManager) -> Dict[str, Any]:
    """
    Handle add comment tool call.
    
    Args:
        arguments: Tool arguments
        manager: Enhanced Jira manager
        
    Returns:
        Dict[str, Any]: Tool response
    """
    # Get required arguments
    issue_key = arguments.get("issue_key")
    comment = arguments.get("comment")
    
    # Validate required arguments
    if not issue_key:
        return {"error": "issue_key is required"}
    if not comment:
        return {"error": "comment is required"}
    
    # Add comment
    result = manager.add_comment(issue_key, comment)
    
    # Return response
    return {
        "id": result.id,
        "body": result.body,
    }

def handle_transition_issue(arguments: Dict[str, Any], manager: EnhancedJiraManager) -> Dict[str, Any]:
    """
    Handle transition issue tool call.
    
    Args:
        arguments: Tool arguments
        manager: Enhanced Jira manager
        
    Returns:
        Dict[str, Any]: Tool response
    """
    # Get required arguments
    issue_key = arguments.get("issue_key")
    transition = arguments.get("transition")
    
    # Validate required arguments
    if not issue_key:
        return {"error": "issue_key is required"}
    if not transition:
        return {"error": "transition is required"}
    
    # Transition issue
    manager.transition_issue(issue_key, transition)
    
    # Return response
    return {
        "success": True,
        "message": f"Transitioned {issue_key} with transition {transition}",
    }

def handle_assign_issue(arguments: Dict[str, Any], manager: EnhancedJiraManager) -> Dict[str, Any]:
    """
    Handle assign issue tool call.
    
    Args:
        arguments: Tool arguments
        manager: Enhanced Jira manager
        
    Returns:
        Dict[str, Any]: Tool response
    """
    # Get required arguments
    issue_key = arguments.get("issue_key")
    assignee = arguments.get("assignee")
    
    # Validate required arguments
    if not issue_key:
        return {"error": "issue_key is required"}
    if assignee is None:  # Allow empty string to unassign
        return {"error": "assignee is required"}
    
    # Assign issue
    manager.assign_issue(issue_key, assignee)
    
    # Return response
    return {
        "success": True,
        "message": f"Assigned {issue_key} to {assignee or 'no one'}",
    }

def handle_get_transitions(arguments: Dict[str, Any], manager: EnhancedJiraManager) -> Dict[str, Any]:
    """
    Handle get transitions tool call.
    
    Args:
        arguments: Tool arguments
        manager: Enhanced Jira manager
        
    Returns:
        Dict[str, Any]: Tool response
    """
    # Get required arguments
    issue_key = arguments.get("issue_key")
    
    # Validate required arguments
    if not issue_key:
        return {"error": "issue_key is required"}
    
    # Get transitions
    transitions = manager.get_transitions(issue_key)
    
    # Return response
    result = []
    for transition in transitions:
        result.append({
            "id": transition.get("id"),
            "name": transition.get("name"),
        })
    
    return {
        "transitions": result,
    }

def handle_add_issues_to_epic(arguments: Dict[str, Any], manager: EnhancedJiraManager) -> Dict[str, Any]:
    """
    Handle add issues to epic tool call.
    
    Args:
        arguments: Tool arguments
        manager: Enhanced Jira manager
        
    Returns:
        Dict[str, Any]: Tool response
    """
    # Get required arguments
    epic_key = arguments.get("epic_key")
    issues = arguments.get("issues", [])
    
    # Validate required arguments
    if not epic_key:
        return {"error": "epic_key is required"}
    if not issues:
        return {"error": "issues is required"}
    
    # Add issues to epic
    manager.add_issues_to_epic(epic_key, issues)
    
    # Return response
    return {
        "success": True,
        "message": f"Added {len(issues)} issues to {epic_key}",
    }

def handle_bulk_create_issues(arguments: Dict[str, Any], manager: EnhancedJiraManager) -> Dict[str, Any]:
    """
    Handle bulk create issues tool call.
    
    Args:
        arguments: Tool arguments
        manager: Enhanced Jira manager
        
    Returns:
        Dict[str, Any]: Tool response
    """
    # Get required arguments
    issues = arguments.get("issues", [])
    
    # Validate required arguments
    if not issues:
        return {"error": "issues is required"}
    
    # Create issues
    created = manager.bulk_create_issues(issues)
    
    # Return response
    result = []
    for issue in created:
        result.append({
            "key": issue.key,
            "id": issue.id,
            "self": issue.self,
            "summary": issue.fields.summary,
        })
    
    return {
        "issues": result,
        "total": len(result),
    }

def handle_get_custom_fields(arguments: Dict[str, Any], manager: EnhancedJiraManager) -> Dict[str, Any]:
    """
    Handle get custom fields tool call.
    
    Args:
        arguments: Tool arguments
        manager: Enhanced Jira manager
        
    Returns:
        Dict[str, Any]: Tool response
    """
    # Get custom fields
    fields = manager.get_custom_fields()
    
    # Return response
    return {
        "fields": fields,
        "total": len(fields),
    }

def handle_get_custom_field_id(arguments: Dict[str, Any], manager: EnhancedJiraManager) -> Dict[str, Any]:
    """
    Handle get custom field ID tool call.
    
    Args:
        arguments: Tool arguments
        manager: Enhanced Jira manager
        
    Returns:
        Dict[str, Any]: Tool response
    """
    # Get required arguments
    field_name = arguments.get("field_name")
    
    # Validate required arguments
    if not field_name:
        return {"error": "field_name is required"}
    
    # Get custom field ID
    field_id = manager.get_custom_field_id(field_name)
    
    # Return response
    return {
        "field_name": field_name,
        "field_id": field_id,
    }

def get_enhanced_jira_tools() -> List[Tool]:
    """
    Get all Enhanced Jira tools.
    
    Returns:
        List[Tool]: List of Enhanced Jira tools
    """
    try:
        # Make sure manager can be initialized before registering tools
        get_enhanced_jira_manager()
        
        tools = [
            Tool(
                name="jira_enhanced_create_issue",
                description="Create a Jira issue with custom fields support",
                input_schema={
                    "type": "object",
                    "properties": {
                        "project_key": {"type": "string", "description": "Project key"},
                        "summary": {"type": "string", "description": "Issue summary"},
                        "description": {"type": "string", "description": "Issue description"},
                        "issue_type": {"type": "string", "description": "Issue type (default: Task)"},
                        "name": {"type": "string", "description": "Name (required)"},
                        "dept": {"type": "string", "description": "Department (required)"},
                        "custom_fields": {"type": "object", "description": "Custom fields as key-value pairs"},
                    },
                    "required": ["project_key", "summary", "name", "dept"],
                },
            ),
            Tool(
                name="jira_enhanced_create_epic",
                description="Create a Jira epic with custom fields support",
                input_schema={
                    "type": "object",
                    "properties": {
                        "project_key": {"type": "string", "description": "Project key"},
                        "name": {"type": "string", "description": "Epic name (required)"},
                        "summary": {"type": "string", "description": "Epic summary"},
                        "description": {"type": "string", "description": "Epic description"},
                        "dept": {"type": "string", "description": "Department (required)"},
                        "custom_fields": {"type": "object", "description": "Custom fields as key-value pairs"},
                    },
                    "required": ["project_key", "name", "summary", "dept"],
                },
            ),
            Tool(
                name="jira_enhanced_update_issue",
                description="Update a Jira issue with advanced fields support",
                input_schema={
                    "type": "object",
                    "properties": {
                        "issue_key": {"type": "string", "description": "Issue key"},
                        "fields": {"type": "object", "description": "Fields to update as key-value pairs"},
                    },
                    "required": ["issue_key", "fields"],
                },
            ),
            Tool(
                name="jira_enhanced_search_issues",
                description="Search Jira issues with advanced JQL support",
                input_schema={
                    "type": "object",
                    "properties": {
                        "jql": {"type": "string", "description": "JQL query"},
                        "max_results": {"type": "integer", "description": "Maximum results to return (default: 50)"},
                        "fields": {"type": "array", "items": {"type": "string"}, "description": "Fields to include"},
                    },
                    "required": ["jql"],
                },
            ),
            Tool(
                name="jira_enhanced_add_comment",
                description="Add a comment to a Jira issue",
                input_schema={
                    "type": "object",
                    "properties": {
                        "issue_key": {"type": "string", "description": "Issue key"},
                        "comment": {"type": "string", "description": "Comment text"},
                    },
                    "required": ["issue_key", "comment"],
                },
            ),
            Tool(
                name="jira_enhanced_transition_issue",
                description="Transition a Jira issue to a new status",
                input_schema={
                    "type": "object",
                    "properties": {
                        "issue_key": {"type": "string", "description": "Issue key"},
                        "transition": {"type": "string", "description": "Transition ID or name"},
                    },
                    "required": ["issue_key", "transition"],
                },
            ),
            Tool(
                name="jira_enhanced_assign_issue",
                description="Assign a Jira issue to a user",
                input_schema={
                    "type": "object",
                    "properties": {
                        "issue_key": {"type": "string", "description": "Issue key"},
                        "assignee": {"type": "string", "description": "Assignee username (empty string to unassign)"},
                    },
                    "required": ["issue_key", "assignee"],
                },
            ),
            Tool(
                name="jira_enhanced_get_transitions",
                description="Get available transitions for a Jira issue",
                input_schema={
                    "type": "object",
                    "properties": {
                        "issue_key": {"type": "string", "description": "Issue key"},
                    },
                    "required": ["issue_key"],
                },
            ),
            Tool(
                name="jira_enhanced_add_issues_to_epic",
                description="Add issues to a Jira epic",
                input_schema={
                    "type": "object",
                    "properties": {
                        "epic_key": {"type": "string", "description": "Epic key"},
                        "issues": {"type": "array", "items": {"type": "string"}, "description": "Issue keys"},
                    },
                    "required": ["epic_key", "issues"],
                },
            ),
            Tool(
                name="jira_enhanced_bulk_create_issues",
                description="Create multiple Jira issues in bulk",
                input_schema={
                    "type": "object",
                    "properties": {
                        "issues": {
                            "type": "array",
                            "items": {"type": "object"},
                            "description": "List of issue field dictionaries",
                        },
                    },
                    "required": ["issues"],
                },
            ),
            Tool(
                name="jira_enhanced_get_custom_fields",
                description="Get all custom fields defined in Jira",
                input_schema={
                    "type": "object",
                    "properties": {},
                },
            ),
            Tool(
                name="jira_enhanced_get_custom_field_id",
                description="Get custom field ID by name",
                input_schema={
                    "type": "object",
                    "properties": {
                        "field_name": {"type": "string", "description": "Field name"},
                    },
                    "required": ["field_name"],
                },
            ),
        ]
        
        return tools
    except Exception as e:
        logger.error(f"Error getting Enhanced Jira tools: {str(e)}")
        return []
EOF < /dev/null
