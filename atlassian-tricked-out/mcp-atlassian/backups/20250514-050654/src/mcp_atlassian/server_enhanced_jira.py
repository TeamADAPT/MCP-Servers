"""Enhanced Jira Tool Registration for MCP-Atlassian Server.

This module contains enhanced Jira tools registration for the MCP-Atlassian server.
It defines tools for advanced Jira functionality, including custom field management.

Usage:
    Import this module in server.py to add enhanced Jira tools to the MCP-Atlassian server.
"""

import logging
import os
from typing import Dict, List, Any, Optional

from mcp.types import Tool

from .constants import (
    STATUS_SUCCESS,
    STATUS_ERROR,
    TOOL_CATEGORY_JIRA,
)
from .enhanced_jira import get_enhanced_jira_manager

# Configure logging
logger = logging.getLogger("mcp-enhanced-jira")

def get_enhanced_jira_available() -> bool:
    """Determine if enhanced Jira is available based on environment variables."""
    return all([
        os.getenv("JIRA_URL"),
        os.getenv("JIRA_USERNAME"),
        os.getenv("JIRA_API_TOKEN")
    ])

def get_enhanced_jira_tools() -> List[Tool]:
    """Get all enhanced Jira tools.
    
    Returns:
        List of Jira tools for the MCP server
    """
    try:
        # Make sure manager can be initialized before registering tools
        get_enhanced_jira_manager()
        
        tools = [
            Tool(
                name="jira_enhanced_create_issue",
                description="Create a Jira issue with custom fields support",
                category=TOOL_CATEGORY_JIRA,
                inputSchema={
                    "type": "object",
                    "properties": {
                        "project_key": {
                            "type": "string",
                            "description": "The project key (e.g., 'PROJ')"
                        },
                        "summary": {
                            "type": "string",
                            "description": "The issue summary/title"
                        },
                        "issue_type": {
                            "type": "string",
                            "description": "The issue type",
                            "default": "Task"
                        },
                        "description": {
                            "type": "string",
                            "description": "The issue description",
                            "default": ""
                        },
                        "labels": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of labels to apply to the issue"
                        },
                        "priority": {
                            "type": "string",
                            "description": "The issue priority",
                            "default": "Medium"
                        },
                        "name": {
                            "type": "string",
                            "description": "Name for custom field"
                        },
                        "dept": {
                            "type": "string", 
                            "description": "Department for custom field"
                        },
                        "epic_link": {
                            "type": "string",
                            "description": "Epic to link this issue to"
                        }
                    },
                    "required": ["project_key", "summary"]
                }
            ),
            Tool(
                name="jira_get_custom_fields",
                description="Get all custom fields defined in Jira",
                category=TOOL_CATEGORY_JIRA,
                inputSchema={
                    "type": "object",
                    "properties": {}
                }
            ),
            Tool(
                name="jira_get_field_contexts",
                description="Get contexts for a specific field",
                category=TOOL_CATEGORY_JIRA,
                inputSchema={
                    "type": "object",
                    "properties": {
                        "field_id": {
                            "type": "string",
                            "description": "The field ID to get contexts for"
                        }
                    },
                    "required": ["field_id"]
                }
            ),
            Tool(
                name="jira_set_fields_global",
                description="Set all custom fields to be available globally",
                category=TOOL_CATEGORY_JIRA,
                inputSchema={
                    "type": "object",
                    "properties": {}
                }
            ),
            Tool(
                name="jira_create_global_field_context",
                description="Create a global context for a field",
                category=TOOL_CATEGORY_JIRA,
                inputSchema={
                    "type": "object",
                    "properties": {
                        "field_id": {
                            "type": "string",
                            "description": "The field ID to create a global context for"
                        },
                        "name": {
                            "type": "string",
                            "description": "The name for the new context"
                        }
                    },
                    "required": ["field_id", "name"]
                }
            ),
            Tool(
                name="jira_assign_field_to_projects",
                description="Assign a field context to specific projects",
                category=TOOL_CATEGORY_JIRA,
                inputSchema={
                    "type": "object",
                    "properties": {
                        "field_id": {
                            "type": "string",
                            "description": "The field ID"
                        },
                        "context_id": {
                            "type": "string",
                            "description": "The context ID to assign"
                        },
                        "project_keys": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of project keys to assign the field to"
                        }
                    },
                    "required": ["field_id", "context_id", "project_keys"]
                }
            )
        ]
        
        return tools
    except Exception as e:
        logger.error(f"Error getting enhanced Jira tools: {e}")
        return []

def handle_enhanced_jira_tool_call(name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Handle calls to enhanced Jira tools.
    
    Args:
        name: The tool name
        arguments: Tool arguments
        
    Returns:
        Tool execution result
    """
    try:
        jira_manager = get_enhanced_jira_manager()
        
        # Enhanced issue creation
        if name == "jira_enhanced_create_issue":
            # Extract standard fields
            project_key = arguments.get("project_key")
            summary = arguments.get("summary")
            issue_type = arguments.get("issue_type", "Task")
            description = arguments.get("description", "")
            labels = arguments.get("labels", [])
            priority = arguments.get("priority", "Medium")
            
            # Extract custom fields if provided
            custom_fields = {}
            
            if "name" in arguments:
                custom_fields[jira_manager.CUSTOM_FIELD_NAME] = arguments.get("name")
                
            if "dept" in arguments:
                custom_fields[jira_manager.CUSTOM_FIELD_DEPARTMENT] = arguments.get("dept")
                
            if "epic_link" in arguments:
                custom_fields[jira_manager.CUSTOM_FIELD_EPIC_LINK] = arguments.get("epic_link")
            
            return jira_manager.create_issue_with_custom_fields(
                project_key=project_key,
                summary=summary,
                issue_type=issue_type,
                description=description,
                labels=labels,
                priority=priority,
                custom_fields=custom_fields
            )
        
        # Get custom fields
        elif name == "jira_get_custom_fields":
            return jira_manager.get_custom_fields()
        
        # Get field contexts
        elif name == "jira_get_field_contexts":
            field_id = arguments.get("field_id")
            return jira_manager.get_field_contexts(field_id)
        
        # Set all fields as global
        elif name == "jira_set_fields_global":
            return jira_manager.set_custom_fields_as_global()
        
        # Create global field context
        elif name == "jira_create_global_field_context":
            field_id = arguments.get("field_id")
            name = arguments.get("name")
            return jira_manager.create_global_field_context(field_id, name)
        
        # Assign field to projects
        elif name == "jira_assign_field_to_projects":
            field_id = arguments.get("field_id")
            context_id = arguments.get("context_id")
            project_keys = arguments.get("project_keys")
            return jira_manager.assign_field_to_projects(field_id, context_id, project_keys)
        
        else:
            return {
                "status": STATUS_ERROR,
                "message": f"Unknown tool: {name}"
            }
    
    except Exception as e:
        logger.error(f"Error handling enhanced Jira tool call {name}: {e}")
        return {"status": STATUS_ERROR, "message": str(e)}