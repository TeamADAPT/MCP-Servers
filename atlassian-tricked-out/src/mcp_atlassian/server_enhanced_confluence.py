"""
Server module for enhanced Confluence features.

This module provides new Confluence tools for space management, templates, and content features.
"""

import logging
from typing import List
from mcp.types import Tool

from .space_management import ConfluenceSpaceManager
from .template_management import ConfluenceTemplateManager
from .content_management import ConfluenceContentManager
from .config import ConfluenceConfig
import os

# Configure logging
logger = logging.getLogger("mcp-atlassian")

def get_enhanced_confluence_available() -> bool:
    """Determine if enhanced Confluence features are available based on environment variables."""
    return all(
        [os.getenv("CONFLUENCE_URL"), os.getenv("CONFLUENCE_USERNAME"), os.getenv("CONFLUENCE_API_TOKEN")]
    )

def initialize_enhanced_confluence_managers():
    """Initialize the enhanced Confluence managers if credentials are available."""
    if not get_enhanced_confluence_available():
        return None, None, None
        
    try:
        # Get Confluence credentials from environment
        url = os.getenv("CONFLUENCE_URL")
        username = os.getenv("CONFLUENCE_USERNAME")
        token = os.getenv("CONFLUENCE_API_TOKEN")
        
        # Create the config
        config = ConfluenceConfig(url=url, username=username, api_token=token)
        
        # Initialize the managers
        space_manager = ConfluenceSpaceManager(config)
        template_manager = ConfluenceTemplateManager(config)
        content_manager = ConfluenceContentManager(config)
        
        return space_manager, template_manager, content_manager
    except Exception as e:
        logger.error(f"Failed to initialize enhanced Confluence managers: {str(e)}")
        return None, None, None


def get_enhanced_confluence_tools() -> List[Tool]:
    """Get the list of enhanced Confluence tools."""
    tools = []
    
    # Space Management Tools
    tools.extend([
        Tool(
            name="confluence_space_get_all",
            description="Get all Confluence spaces with optional filtering",
            inputSchema={
                "type": "object",
                "properties": {
                    "start": {
                        "type": "number",
                        "description": "Starting index for pagination",
                        "default": 0
                    },
                    "limit": {
                        "type": "number",
                        "description": "Maximum number of spaces to return",
                        "default": 25
                    },
                    "space_type": {
                        "type": "string",
                        "description": "Type of space ('global', 'personal', or 'archived')",
                        "default": "global",
                        "enum": ["global", "personal", "archived"]
                    },
                    "status": {
                        "type": "string",
                        "description": "Space status ('current' or 'archived')",
                        "default": "current",
                        "enum": ["current", "archived"]
                    },
                    "expand": {
                        "type": "string",
                        "description": "Additional fields to expand (e.g., 'description,homepage')"
                    }
                }
            }
        ),
        Tool(
            name="confluence_space_get",
            description="Get a specific Confluence space by key",
            inputSchema={
                "type": "object",
                "properties": {
                    "space_key": {
                        "type": "string",
                        "description": "The space key"
                    },
                    "expand": {
                        "type": "string",
                        "description": "Additional fields to expand (e.g., 'description,homepage')"
                    }
                },
                "required": ["space_key"]
            }
        ),
        Tool(
            name="confluence_space_create",
            description="Create a new Confluence space",
            inputSchema={
                "type": "object",
                "properties": {
                    "key": {
                        "type": "string",
                        "description": "The space key (must be unique, uppercase, no spaces)"
                    },
                    "name": {
                        "type": "string",
                        "description": "The space name"
                    },
                    "description": {
                        "type": "string",
                        "description": "Optional space description"
                    },
                    "template_key": {
                        "type": "string",
                        "description": "Optional template key for space creation"
                    }
                },
                "required": ["key", "name"]
            }
        ),
        Tool(
            name="confluence_space_create_from_template",
            description="Create a new Confluence space from a template with parameters",
            inputSchema={
                "type": "object",
                "properties": {
                    "key": {
                        "type": "string",
                        "description": "The space key (must be unique, uppercase, no spaces)"
                    },
                    "name": {
                        "type": "string",
                        "description": "The space name"
                    },
                    "description": {
                        "type": "string",
                        "description": "Optional space description"
                    },
                    "template_key": {
                        "type": "string",
                        "description": "Template key for space creation"
                    },
                    "template_params": {
                        "type": "object",
                        "description": "Optional template parameters for customizing the template"
                    }
                },
                "required": ["key", "name", "template_key"]
            }
        ),
        Tool(
            name="confluence_space_update",
            description="Update a Confluence space",
            inputSchema={
                "type": "object",
                "properties": {
                    "space_key": {
                        "type": "string",
                        "description": "The space key to update"
                    },
                    "name": {
                        "type": "string",
                        "description": "Optional new name for the space"
                    },
                    "description": {
                        "type": "string",
                        "description": "Optional new description for the space"
                    }
                },
                "required": ["space_key"]
            }
        ),
        Tool(
            name="confluence_space_archive",
            description="Archive a Confluence space",
            inputSchema={
                "type": "object",
                "properties": {
                    "space_key": {
                        "type": "string",
                        "description": "The space key to archive"
                    }
                },
                "required": ["space_key"]
            }
        ),
        Tool(
            name="confluence_space_restore",
            description="Restore an archived Confluence space",
            inputSchema={
                "type": "object",
                "properties": {
                    "space_key": {
                        "type": "string",
                        "description": "The space key to restore"
                    }
                },
                "required": ["space_key"]
            }
        ),
        Tool(
            name="confluence_space_permissions_get",
            description="Get permission settings for a space",
            inputSchema={
                "type": "object",
                "properties": {
                    "space_key": {
                        "type": "string",
                        "description": "The space key"
                    }
                },
                "required": ["space_key"]
            }
        ),
        Tool(
            name="confluence_space_permissions_add",
            description="Add a permission to a space",
            inputSchema={
                "type": "object",
                "properties": {
                    "space_key": {
                        "type": "string",
                        "description": "The space key"
                    },
                    "permission": {
                        "type": "string",
                        "description": "The permission to add (e.g., 'read', 'create', 'delete', 'admin')"
                    },
                    "subject_type": {
                        "type": "string",
                        "description": "The type of subject",
                        "enum": ["user", "group"]
                    },
                    "subject_key": {
                        "type": "string",
                        "description": "The key of the user or group"
                    }
                },
                "required": ["space_key", "permission", "subject_type", "subject_key"]
            }
        ),
        Tool(
            name="confluence_space_permissions_remove",
            description="Remove a permission from a space",
            inputSchema={
                "type": "object",
                "properties": {
                    "space_key": {
                        "type": "string",
                        "description": "The space key"
                    },
                    "permission_id": {
                        "type": "string",
                        "description": "The ID of the permission to remove"
                    }
                },
                "required": ["space_key", "permission_id"]
            }
        )
    ])
    
    # Template Management Tools
    tools.extend([
        Tool(
            name="confluence_templates_get_all",
            description="Get available content templates",
            inputSchema={
                "type": "object",
                "properties": {
                    "start": {
                        "type": "number",
                        "description": "Starting index for pagination",
                        "default": 0
                    },
                    "limit": {
                        "type": "number",
                        "description": "Maximum number of templates to return",
                        "default": 50
                    },
                    "expand": {
                        "type": "string",
                        "description": "Additional fields to expand"
                    }
                }
            }
        ),
        Tool(
            name="confluence_templates_get_blueprints",
            description="Get available blueprint templates",
            inputSchema={
                "type": "object",
                "properties": {
                    "start": {
                        "type": "number",
                        "description": "Starting index for pagination",
                        "default": 0
                    },
                    "limit": {
                        "type": "number",
                        "description": "Maximum number of blueprints to return",
                        "default": 50
                    }
                }
            }
        ),
        Tool(
            name="confluence_templates_get_space",
            description="Get templates available in a specific space",
            inputSchema={
                "type": "object",
                "properties": {
                    "space_key": {
                        "type": "string",
                        "description": "The space key"
                    },
                    "start": {
                        "type": "number",
                        "description": "Starting index for pagination",
                        "default": 0
                    },
                    "limit": {
                        "type": "number",
                        "description": "Maximum number of templates to return",
                        "default": 50
                    }
                },
                "required": ["space_key"]
            }
        ),
        Tool(
            name="confluence_templates_get_by_id",
            description="Get a template by ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "template_id": {
                        "type": "string",
                        "description": "The template ID"
                    }
                },
                "required": ["template_id"]
            }
        ),
        Tool(
            name="confluence_templates_create",
            description="Create a new content template",
            inputSchema={
                "type": "object",
                "properties": {
                    "space_key": {
                        "type": "string",
                        "description": "The space key where the template will be created"
                    },
                    "name": {
                        "type": "string",
                        "description": "The name of the template"
                    },
                    "content": {
                        "type": "string",
                        "description": "The template content in storage format"
                    },
                    "template_type": {
                        "type": "string",
                        "description": "The type of template",
                        "default": "page",
                        "enum": ["page", "blogpost"]
                    },
                    "label": {
                        "type": "string",
                        "description": "Optional label for the template"
                    },
                    "description": {
                        "type": "string",
                        "description": "Optional description for the template"
                    }
                },
                "required": ["space_key", "name", "content"]
            }
        ),
        Tool(
            name="confluence_templates_create_page",
            description="Create a new page from a template",
            inputSchema={
                "type": "object",
                "properties": {
                    "space_key": {
                        "type": "string",
                        "description": "The space key where the page will be created"
                    },
                    "title": {
                        "type": "string",
                        "description": "The title of the page"
                    },
                    "template_id": {
                        "type": "string",
                        "description": "The ID of the template to use"
                    },
                    "parent_id": {
                        "type": "string",
                        "description": "Optional parent page ID"
                    },
                    "template_parameters": {
                        "type": "object",
                        "description": "Optional parameters to customize the template"
                    }
                },
                "required": ["space_key", "title", "template_id"]
            }
        ),
        Tool(
            name="confluence_templates_create_page_from_blueprint",
            description="Create a new page from a blueprint",
            inputSchema={
                "type": "object",
                "properties": {
                    "space_key": {
                        "type": "string",
                        "description": "The space key where the page will be created"
                    },
                    "title": {
                        "type": "string",
                        "description": "The title of the page"
                    },
                    "blueprint_id": {
                        "type": "string",
                        "description": "The ID of the blueprint to use"
                    },
                    "parent_id": {
                        "type": "string",
                        "description": "Optional parent page ID"
                    },
                    "blueprint_parameters": {
                        "type": "object",
                        "description": "Optional parameters to customize the blueprint"
                    }
                },
                "required": ["space_key", "title", "blueprint_id"]
            }
        )
    ])
    
    # Advanced Content Management Tools
    tools.extend([
        Tool(
            name="confluence_content_get_properties",
            description="Get all properties for a content",
            inputSchema={
                "type": "object",
                "properties": {
                    "content_id": {
                        "type": "string",
                        "description": "The content ID"
                    }
                },
                "required": ["content_id"]
            }
        ),
        Tool(
            name="confluence_content_get_property",
            description="Get a specific property for a content",
            inputSchema={
                "type": "object",
                "properties": {
                    "content_id": {
                        "type": "string",
                        "description": "The content ID"
                    },
                    "property_key": {
                        "type": "string",
                        "description": "The property key"
                    }
                },
                "required": ["content_id", "property_key"]
            }
        ),
        Tool(
            name="confluence_content_set_property",
            description="Set a property for a content",
            inputSchema={
                "type": "object",
                "properties": {
                    "content_id": {
                        "type": "string",
                        "description": "The content ID"
                    },
                    "property_key": {
                        "type": "string",
                        "description": "The property key"
                    },
                    "property_value": {
                        "type": "object",
                        "description": "The property value (can be any JSON-serializable value)"
                    }
                },
                "required": ["content_id", "property_key", "property_value"]
            }
        ),
        Tool(
            name="confluence_content_get_restrictions",
            description="Get restrictions for a content",
            inputSchema={
                "type": "object",
                "properties": {
                    "content_id": {
                        "type": "string",
                        "description": "The content ID"
                    }
                },
                "required": ["content_id"]
            }
        ),
        Tool(
            name="confluence_content_add_restriction",
            description="Add a restriction to a content",
            inputSchema={
                "type": "object",
                "properties": {
                    "content_id": {
                        "type": "string",
                        "description": "The content ID"
                    },
                    "restriction_type": {
                        "type": "string",
                        "description": "The restriction type",
                        "enum": ["read", "update"]
                    },
                    "subject_type": {
                        "type": "string",
                        "description": "The subject type",
                        "enum": ["user", "group"]
                    },
                    "subject_key": {
                        "type": "string",
                        "description": "The key of the user or group"
                    }
                },
                "required": ["content_id", "restriction_type", "subject_type", "subject_key"]
            }
        ),
        Tool(
            name="confluence_content_get_labels",
            description="Get labels for a content",
            inputSchema={
                "type": "object",
                "properties": {
                    "content_id": {
                        "type": "string",
                        "description": "The content ID"
                    },
                    "prefix": {
                        "type": "string",
                        "description": "Optional prefix to filter labels"
                    }
                },
                "required": ["content_id"]
            }
        ),
        Tool(
            name="confluence_content_add_label",
            description="Add a label to a content",
            inputSchema={
                "type": "object",
                "properties": {
                    "content_id": {
                        "type": "string",
                        "description": "The content ID"
                    },
                    "label": {
                        "type": "string",
                        "description": "The label name"
                    },
                    "prefix": {
                        "type": "string",
                        "description": "Optional label prefix (default: 'global')"
                    }
                },
                "required": ["content_id", "label"]
            }
        ),
        Tool(
            name="confluence_content_add_multiple_labels",
            description="Add multiple labels to a content",
            inputSchema={
                "type": "object",
                "properties": {
                    "content_id": {
                        "type": "string",
                        "description": "The content ID"
                    },
                    "labels": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        },
                        "description": "List of label names"
                    },
                    "prefix": {
                        "type": "string",
                        "description": "Optional label prefix (default: 'global')"
                    }
                },
                "required": ["content_id", "labels"]
            }
        ),
        Tool(
            name="confluence_content_get_by_label",
            description="Find content with a specific label",
            inputSchema={
                "type": "object",
                "properties": {
                    "label": {
                        "type": "string",
                        "description": "The label name to search for"
                    },
                    "space_key": {
                        "type": "string",
                        "description": "Optional space key to limit search"
                    },
                    "content_type": {
                        "type": "string",
                        "description": "Optional content type filter",
                        "enum": ["page", "blogpost"]
                    },
                    "start": {
                        "type": "number",
                        "description": "Starting index for pagination",
                        "default": 0
                    },
                    "limit": {
                        "type": "number",
                        "description": "Maximum number of results to return",
                        "default": 25
                    }
                },
                "required": ["label"]
            }
        ),
        Tool(
            name="confluence_content_get_available_macros",
            description="Get a list of available macros",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="confluence_content_add_macro",
            description="Add a macro to a page or blog post",
            inputSchema={
                "type": "object",
                "properties": {
                    "content_id": {
                        "type": "string",
                        "description": "The content ID"
                    },
                    "macro_key": {
                        "type": "string",
                        "description": "The macro key (e.g., 'info', 'code', 'jira')"
                    },
                    "macro_parameters": {
                        "type": "object",
                        "description": "Parameters for the macro"
                    },
                    "macro_body": {
                        "type": "string",
                        "description": "Optional body for body macros"
                    }
                },
                "required": ["content_id", "macro_key", "macro_parameters"]
            }
        ),
        Tool(
            name="confluence_content_get_versions",
            description="Get versions of a content",
            inputSchema={
                "type": "object",
                "properties": {
                    "content_id": {
                        "type": "string",
                        "description": "The content ID"
                    },
                    "start": {
                        "type": "number",
                        "description": "Starting index for pagination",
                        "default": 0
                    },
                    "limit": {
                        "type": "number",
                        "description": "Maximum number of versions to return",
                        "default": 25
                    }
                },
                "required": ["content_id"]
            }
        ),
        Tool(
            name="confluence_content_compare_versions",
            description="Compare two versions of a content",
            inputSchema={
                "type": "object",
                "properties": {
                    "content_id": {
                        "type": "string",
                        "description": "The content ID"
                    },
                    "source_version": {
                        "type": "number",
                        "description": "The source version number"
                    },
                    "target_version": {
                        "type": "number",
                        "description": "The target version number"
                    }
                },
                "required": ["content_id", "source_version", "target_version"]
            }
        ),
        Tool(
            name="confluence_content_with_attachments",
            description="Create a page with attachments in a single operation",
            inputSchema={
                "type": "object",
                "properties": {
                    "space_key": {
                        "type": "string",
                        "description": "The space key"
                    },
                    "title": {
                        "type": "string",
                        "description": "The page title"
                    },
                    "content": {
                        "type": "string",
                        "description": "The page content"
                    },
                    "parent_id": {
                        "type": "string",
                        "description": "Optional parent page ID"
                    },
                    "attachments": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        },
                        "description": "Optional list of file paths to attach"
                    },
                    "content_type": {
                        "type": "string",
                        "description": "The content type",
                        "default": "markdown",
                        "enum": ["markdown", "storage"]
                    }
                },
                "required": ["space_key", "title", "content"]
            }
        ),
        Tool(
            name="confluence_content_batch_update",
            description="Update multiple pages in batch",
            inputSchema={
                "type": "object",
                "properties": {
                    "updates": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "content_id": {
                                    "type": "string",
                                    "description": "The content ID"
                                },
                                "title": {
                                    "type": "string",
                                    "description": "Optional new title"
                                },
                                "content": {
                                    "type": "string",
                                    "description": "Optional new content"
                                },
                                "content_type": {
                                    "type": "string",
                                    "description": "Optional content type",
                                    "default": "markdown",
                                    "enum": ["markdown", "storage"]
                                },
                                "version_message": {
                                    "type": "string",
                                    "description": "Optional version message"
                                }
                            },
                            "required": ["content_id"]
                        }
                    }
                },
                "required": ["updates"]
            }
        ),
        Tool(
            name="confluence_content_batch_move",
            description="Move multiple pages in batch",
            inputSchema={
                "type": "object",
                "properties": {
                    "moves": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "content_id": {
                                    "type": "string",
                                    "description": "The content ID"
                                },
                                "target_parent_id": {
                                    "type": "string",
                                    "description": "Optional new parent ID"
                                },
                                "target_space_key": {
                                    "type": "string",
                                    "description": "Optional new space key"
                                },
                                "position": {
                                    "type": "number",
                                    "description": "Optional position"
                                }
                            },
                            "required": ["content_id"]
                        }
                    }
                },
                "required": ["moves"]
            }
        ),
        Tool(
            name="confluence_content_add_comment_with_mentions",
            description="Add a comment to content with user mentions",
            inputSchema={
                "type": "object",
                "properties": {
                    "content_id": {
                        "type": "string",
                        "description": "The content ID"
                    },
                    "comment_text": {
                        "type": "string",
                        "description": "The comment text"
                    },
                    "mentions": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        },
                        "description": "Optional list of usernames to mention"
                    }
                },
                "required": ["content_id", "comment_text"]
            }
        )
    ])
    
    return tools

def handle_enhanced_confluence_tool_call(name: str, arguments: dict, space_manager, template_manager, content_manager):
    """Handle calls to enhanced Confluence tools."""
    
    # Space Management Tools
    if name == "confluence_space_get_all":
        start = arguments.get("start", 0)
        limit = arguments.get("limit", 25)
        space_type = arguments.get("space_type", "global")
        status = arguments.get("status", "current")
        expand = arguments.get("expand")
        
        return space_manager.get_all_spaces(
            start=start,
            limit=limit,
            space_type=space_type,
            status=status,
            expand=expand
        )
        
    elif name == "confluence_space_get":
        space_key = arguments["space_key"]
        expand = arguments.get("expand")
        
        return space_manager.get_space(
            space_key=space_key,
            expand=expand
        )
        
    elif name == "confluence_space_create":
        key = arguments["key"]
        name = arguments["name"]
        description = arguments.get("description")
        template_key = arguments.get("template_key")
        
        return space_manager.create_space(
            key=key,
            name=name,
            description=description,
            template_key=template_key
        )
        
    elif name == "confluence_space_create_from_template":
        key = arguments["key"]
        name = arguments["name"]
        description = arguments.get("description")
        template_key = arguments["template_key"]
        template_params = arguments.get("template_params")
        
        return space_manager.create_space_from_template(
            key=key,
            name=name,
            description=description,
            template_key=template_key,
            template_params=template_params
        )
        
    elif name == "confluence_space_update":
        space_key = arguments["space_key"]
        name = arguments.get("name")
        description = arguments.get("description")
        
        return space_manager.update_space(
            space_key=space_key,
            name=name,
            description=description
        )
        
    elif name == "confluence_space_archive":
        space_key = arguments["space_key"]
        
        return space_manager.archive_space(
            space_key=space_key
        )
        
    elif name == "confluence_space_restore":
        space_key = arguments["space_key"]
        
        return space_manager.restore_space(
            space_key=space_key
        )
        
    elif name == "confluence_space_permissions_get":
        space_key = arguments["space_key"]
        
        return space_manager.get_space_permissions(
            space_key=space_key
        )
        
    elif name == "confluence_space_permissions_add":
        space_key = arguments["space_key"]
        permission = arguments["permission"]
        subject_type = arguments["subject_type"]
        subject_key = arguments["subject_key"]
        
        return space_manager.add_space_permission(
            space_key=space_key,
            permission=permission,
            subject_type=subject_type,
            subject_key=subject_key
        )
        
    elif name == "confluence_space_permissions_remove":
        space_key = arguments["space_key"]
        permission_id = arguments["permission_id"]
        
        return space_manager.remove_space_permission(
            space_key=space_key,
            permission_id=permission_id
        )
    
    # Template Management Tools
    elif name == "confluence_templates_get_all":
        start = arguments.get("start", 0)
        limit = arguments.get("limit", 50)
        expand = arguments.get("expand")
        
        return template_manager.get_content_templates(
            start=start,
            limit=limit,
            expand=expand
        )
        
    elif name == "confluence_templates_get_blueprints":
        start = arguments.get("start", 0)
        limit = arguments.get("limit", 50)
        
        return template_manager.get_blueprint_templates(
            start=start,
            limit=limit
        )
        
    elif name == "confluence_templates_get_space":
        space_key = arguments["space_key"]
        start = arguments.get("start", 0)
        limit = arguments.get("limit", 50)
        
        return template_manager.get_space_templates(
            space_key=space_key,
            start=start,
            limit=limit
        )
        
    elif name == "confluence_templates_get_by_id":
        template_id = arguments["template_id"]
        
        return template_manager.get_template_by_id(
            template_id=template_id
        )
        
    elif name == "confluence_templates_create":
        space_key = arguments["space_key"]
        name = arguments["name"]
        content = arguments["content"]
        template_type = arguments.get("template_type", "page")
        label = arguments.get("label")
        description = arguments.get("description")
        
        return template_manager.create_template(
            space_key=space_key,
            name=name,
            content=content,
            template_type=template_type,
            label=label,
            description=description
        )
        
    elif name == "confluence_templates_create_page":
        space_key = arguments["space_key"]
        title = arguments["title"]
        template_id = arguments["template_id"]
        parent_id = arguments.get("parent_id")
        template_parameters = arguments.get("template_parameters")
        
        return template_manager.create_page_from_template(
            space_key=space_key,
            title=title,
            template_id=template_id,
            parent_id=parent_id,
            template_parameters=template_parameters
        )
        
    elif name == "confluence_templates_create_page_from_blueprint":
        space_key = arguments["space_key"]
        title = arguments["title"]
        blueprint_id = arguments["blueprint_id"]
        parent_id = arguments.get("parent_id")
        blueprint_parameters = arguments.get("blueprint_parameters")
        
        return template_manager.create_page_from_blueprint(
            space_key=space_key,
            title=title,
            blueprint_id=blueprint_id,
            parent_id=parent_id,
            blueprint_parameters=blueprint_parameters
        )
    
    # Content Management Tools
    elif name == "confluence_content_get_properties":
        content_id = arguments["content_id"]
        
        return content_manager.get_content_properties(
            content_id=content_id
        )
        
    elif name == "confluence_content_get_property":
        content_id = arguments["content_id"]
        property_key = arguments["property_key"]
        
        return content_manager.get_content_property(
            content_id=content_id,
            property_key=property_key
        )
        
    elif name == "confluence_content_set_property":
        content_id = arguments["content_id"]
        property_key = arguments["property_key"]
        property_value = arguments["property_value"]
        
        return content_manager.set_content_property(
            content_id=content_id,
            property_key=property_key,
            property_value=property_value
        )
        
    elif name == "confluence_content_get_restrictions":
        content_id = arguments["content_id"]
        
        return content_manager.get_content_restrictions(
            content_id=content_id
        )
        
    elif name == "confluence_content_add_restriction":
        content_id = arguments["content_id"]
        restriction_type = arguments["restriction_type"]
        subject_type = arguments["subject_type"]
        subject_key = arguments["subject_key"]
        
        return content_manager.add_content_restriction(
            content_id=content_id,
            restriction_type=restriction_type,
            subject_type=subject_type,
            subject_key=subject_key
        )
        
    elif name == "confluence_content_get_labels":
        content_id = arguments["content_id"]
        prefix = arguments.get("prefix")
        
        return content_manager.get_content_labels(
            content_id=content_id,
            prefix=prefix
        )
        
    elif name == "confluence_content_add_label":
        content_id = arguments["content_id"]
        label = arguments["label"]
        prefix = arguments.get("prefix")
        
        return content_manager.add_label(
            content_id=content_id,
            label=label,
            prefix=prefix
        )
        
    elif name == "confluence_content_add_multiple_labels":
        content_id = arguments["content_id"]
        labels = arguments["labels"]
        prefix = arguments.get("prefix")
        
        return content_manager.add_multiple_labels(
            content_id=content_id,
            labels=labels,
            prefix=prefix
        )
        
    elif name == "confluence_content_get_by_label":
        label = arguments["label"]
        space_key = arguments.get("space_key")
        content_type = arguments.get("content_type")
        start = arguments.get("start", 0)
        limit = arguments.get("limit", 25)
        
        return content_manager.get_content_by_label(
            label=label,
            space_key=space_key,
            content_type=content_type,
            start=start,
            limit=limit
        )
        
    elif name == "confluence_content_get_available_macros":
        return content_manager.get_available_macros()
        
    elif name == "confluence_content_add_macro":
        content_id = arguments["content_id"]
        macro_key = arguments["macro_key"]
        macro_parameters = arguments["macro_parameters"]
        macro_body = arguments.get("macro_body")
        
        return content_manager.add_macro_to_page(
            content_id=content_id,
            macro_key=macro_key,
            macro_parameters=macro_parameters,
            macro_body=macro_body
        )
        
    elif name == "confluence_content_get_versions":
        content_id = arguments["content_id"]
        start = arguments.get("start", 0)
        limit = arguments.get("limit", 25)
        
        return content_manager.get_content_versions(
            content_id=content_id,
            start=start,
            limit=limit
        )
        
    elif name == "confluence_content_compare_versions":
        content_id = arguments["content_id"]
        source_version = arguments["source_version"]
        target_version = arguments["target_version"]
        
        return content_manager.compare_versions(
            content_id=content_id,
            source_version=source_version,
            target_version=target_version
        )
        
    elif name == "confluence_content_with_attachments":
        space_key = arguments["space_key"]
        title = arguments["title"]
        content = arguments["content"]
        parent_id = arguments.get("parent_id")
        attachments = arguments.get("attachments", [])
        content_type = arguments.get("content_type", "markdown")
        
        return content_manager.create_page_with_attachments(
            space_key=space_key,
            title=title,
            content=content,
            parent_id=parent_id,
            attachments=attachments,
            content_type=content_type
        )
        
    elif name == "confluence_content_batch_update":
        updates = arguments["updates"]
        
        return content_manager.batch_update_content(
            updates=updates
        )
        
    elif name == "confluence_content_batch_move":
        moves = arguments["moves"]
        
        return content_manager.batch_move_content(
            moves=moves
        )
        
    elif name == "confluence_content_add_comment_with_mentions":
        content_id = arguments["content_id"]
        comment_text = arguments["comment_text"]
        mentions = arguments.get("mentions")
        
        return content_manager.add_comment_with_mentions(
            content_id=content_id,
            comment_text=comment_text,
            mentions=mentions
        )
        
    raise ValueError(f"Unknown enhanced Confluence tool: {name}")