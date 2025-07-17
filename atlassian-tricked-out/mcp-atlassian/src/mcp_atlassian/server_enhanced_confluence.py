"""
Enhanced Confluence Server Module

This module provides enhanced Confluence tools for the MCP Atlassian server,
integrating space management, template management, and content management capabilities.
"""

import logging
import os
from typing import Dict, List, Optional, Any, Tuple

from mcp.types import Tool

from .config import ConfluenceConfig
from .space_management import ConfluenceSpaceManager
from .template_management import ConfluenceTemplateManager
from .content_management import ConfluenceContentManager
from .feature_flags import is_enabled

logger = logging.getLogger(__name__)

# Check if required environment variables exist
def get_enhanced_confluence_available() -> bool:
    """Check if necessary environment variables exist for Confluence connection."""
    required_vars = ["CONFLUENCE_URL", "CONFLUENCE_USERNAME", "CONFLUENCE_API_TOKEN"]
    return all(os.environ.get(var) for var in required_vars)

# Initialize managers if credentials are available
def initialize_enhanced_confluence_managers() -> Tuple[Optional[ConfluenceSpaceManager],
                                                     Optional[ConfluenceTemplateManager],
                                                     Optional[ConfluenceContentManager]]:
    """Initialize the enhanced Confluence managers if credentials are available."""
    try:
        if get_enhanced_confluence_available():
            config = ConfluenceConfig(
                os.environ.get("CONFLUENCE_URL", ""),
                os.environ.get("CONFLUENCE_USERNAME", ""),
                os.environ.get("CONFLUENCE_API_TOKEN", "")
            )
            space_manager = ConfluenceSpaceManager(config)
            template_manager = ConfluenceTemplateManager(config)
            content_manager = ConfluenceContentManager(config)
            return space_manager, template_manager, content_manager
    except Exception as e:
        logger.error(f"Failed to initialize enhanced Confluence managers: {str(e)}")
    
    return None, None, None

def get_enhanced_confluence_tools() -> List[Tool]:
    """Get all enhanced Confluence tools."""
    tools = []
    
    # Space Management Tools
    if is_enabled("space_management"):
        tools.extend([
            Tool(
                name="confluence_space_get_all",
                description="Get all Confluence spaces with optional filtering",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "space_type": {
                            "type": "string",
                            "enum": ["global", "personal"],
                            "description": "Filter by space type"
                        },
                        "status": {
                            "type": "string",
                            "enum": ["current", "archived"],
                            "description": "Filter by space status"
                        },
                        "label": {
                            "type": "string",
                            "description": "Filter by label"
                        }
                    }
                }
            ),
            Tool(
                name="confluence_space_get",
                description="Get a specific Confluence space by key",
                inputSchema={
                    "type": "object",
                    "required": ["space_key"],
                    "properties": {
                        "space_key": {
                            "type": "string",
                            "description": "Space key"
                        },
                        "expand": {
                            "type": "string",
                            "description": "Comma-separated list of properties to expand"
                        }
                    }
                }
            ),
            Tool(
                name="confluence_space_create",
                description="Create a new Confluence space",
                inputSchema={
                    "type": "object",
                    "required": ["key", "name"],
                    "properties": {
                        "key": {
                            "type": "string",
                            "description": "Space key (must be unique)"
                        },
                        "name": {
                            "type": "string",
                            "description": "Space name"
                        },
                        "description": {
                            "type": "string",
                            "description": "Space description"
                        },
                        "is_private": {
                            "type": "boolean",
                            "description": "Whether the space should be private"
                        }
                    }
                }
            ),
            Tool(
                name="confluence_space_create_from_template",
                description="Create a new Confluence space from a template",
                inputSchema={
                    "type": "object",
                    "required": ["key", "name", "template_key"],
                    "properties": {
                        "key": {
                            "type": "string",
                            "description": "New space key"
                        },
                        "name": {
                            "type": "string",
                            "description": "New space name"
                        },
                        "template_key": {
                            "type": "string",
                            "description": "Key of space to use as template"
                        }
                    }
                }
            ),
            Tool(
                name="confluence_space_update",
                description="Update a Confluence space",
                inputSchema={
                    "type": "object",
                    "required": ["space_key"],
                    "properties": {
                        "space_key": {
                            "type": "string",
                            "description": "Space key"
                        },
                        "name": {
                            "type": "string",
                            "description": "New space name"
                        },
                        "description": {
                            "type": "string",
                            "description": "New space description"
                        }
                    }
                }
            ),
            Tool(
                name="confluence_space_archive",
                description="Archive a Confluence space",
                inputSchema={
                    "type": "object",
                    "required": ["space_key"],
                    "properties": {
                        "space_key": {
                            "type": "string",
                            "description": "Space key"
                        }
                    }
                }
            ),
            Tool(
                name="confluence_space_restore",
                description="Restore an archived Confluence space",
                inputSchema={
                    "type": "object",
                    "required": ["space_key"],
                    "properties": {
                        "space_key": {
                            "type": "string",
                            "description": "Space key"
                        }
                    }
                }
            ),
            Tool(
                name="confluence_space_permissions_get",
                description="Get permissions for a Confluence space",
                inputSchema={
                    "type": "object",
                    "required": ["space_key"],
                    "properties": {
                        "space_key": {
                            "type": "string",
                            "description": "Space key"
                        }
                    }
                }
            ),
            Tool(
                name="confluence_space_permissions_add",
                description="Add permissions to a Confluence space",
                inputSchema={
                    "type": "object",
                    "required": ["space_key", "type", "subject", "operation", "value"],
                    "properties": {
                        "space_key": {
                            "type": "string",
                            "description": "Space key"
                        },
                        "type": {
                            "type": "string",
                            "enum": ["user", "group"],
                            "description": "Permission type"
                        },
                        "subject": {
                            "type": "string",
                            "description": "User or group name"
                        },
                        "operation": {
                            "type": "string",
                            "enum": ["read", "update", "delete", "create"],
                            "description": "Permission operation"
                        },
                        "value": {
                            "type": "string",
                            "enum": ["true", "false"],
                            "description": "Permission value"
                        }
                    }
                }
            ),
            Tool(
                name="confluence_space_permissions_remove",
                description="Remove permissions from a Confluence space",
                inputSchema={
                    "type": "object",
                    "required": ["space_key", "permission_id"],
                    "properties": {
                        "space_key": {
                            "type": "string",
                            "description": "Space key"
                        },
                        "permission_id": {
                            "type": "string",
                            "description": "Permission ID"
                        }
                    }
                }
            )
        ])
    
    # Template Management Tools
    if is_enabled("template_management"):
        tools.extend([
            Tool(
                name="confluence_templates_get_all",
                description="Get all available Confluence content templates",
                inputSchema={
                    "type": "object",
                    "properties": {}
                }
            ),
            Tool(
                name="confluence_templates_get_blueprints",
                description="Get all available Confluence blueprint templates",
                inputSchema={
                    "type": "object",
                    "properties": {}
                }
            ),
            Tool(
                name="confluence_templates_get_space",
                description="Get templates in a specific Confluence space",
                inputSchema={
                    "type": "object",
                    "required": ["space_key"],
                    "properties": {
                        "space_key": {
                            "type": "string",
                            "description": "Space key"
                        }
                    }
                }
            ),
            Tool(
                name="confluence_templates_get_by_id",
                description="Get a Confluence template by ID",
                inputSchema={
                    "type": "object",
                    "required": ["template_id"],
                    "properties": {
                        "template_id": {
                            "type": "string",
                            "description": "Template ID"
                        }
                    }
                }
            ),
            Tool(
                name="confluence_templates_create",
                description="Create a new Confluence template",
                inputSchema={
                    "type": "object",
                    "required": ["space_key", "name", "template_type", "body"],
                    "properties": {
                        "space_key": {
                            "type": "string",
                            "description": "Space key"
                        },
                        "name": {
                            "type": "string",
                            "description": "Template name"
                        },
                        "template_type": {
                            "type": "string",
                            "enum": ["page", "blogpost"],
                            "description": "Template type"
                        },
                        "body": {
                            "type": "string",
                            "description": "Template body in storage format"
                        },
                        "labels": {
                            "type": "array",
                            "items": {
                                "type": "string"
                            },
                            "description": "List of labels"
                        }
                    }
                }
            ),
            Tool(
                name="confluence_templates_create_page",
                description="Create a page from a Confluence template",
                inputSchema={
                    "type": "object",
                    "required": ["space_key", "title", "template_id"],
                    "properties": {
                        "space_key": {
                            "type": "string",
                            "description": "Space key"
                        },
                        "title": {
                            "type": "string",
                            "description": "Page title"
                        },
                        "template_id": {
                            "type": "string",
                            "description": "Template ID"
                        },
                        "ancestor_id": {
                            "type": "string",
                            "description": "Parent page ID"
                        },
                        "parameters": {
                            "type": "object",
                            "description": "Template parameters"
                        }
                    }
                }
            ),
            Tool(
                name="confluence_templates_create_page_from_blueprint",
                description="Create a page from a Confluence blueprint",
                inputSchema={
                    "type": "object",
                    "required": ["space_key", "title", "blueprint_id"],
                    "properties": {
                        "space_key": {
                            "type": "string",
                            "description": "Space key"
                        },
                        "title": {
                            "type": "string",
                            "description": "Page title"
                        },
                        "blueprint_id": {
                            "type": "string",
                            "description": "Blueprint ID"
                        },
                        "ancestor_id": {
                            "type": "string",
                            "description": "Parent page ID"
                        },
                        "parameters": {
                            "type": "object",
                            "description": "Blueprint parameters"
                        }
                    }
                }
            )
        ])
    
    # Content Management Tools
    if is_enabled("content_management"):
        tools.extend([
            # Content Properties
            Tool(
                name="confluence_content_properties_get",
                description="Get properties for a Confluence content item",
                inputSchema={
                    "type": "object",
                    "required": ["content_id"],
                    "properties": {
                        "content_id": {
                            "type": "string",
                            "description": "Content ID"
                        }
                    }
                }
            ),
            Tool(
                name="confluence_content_property_get",
                description="Get a specific property for a Confluence content item",
                inputSchema={
                    "type": "object",
                    "required": ["content_id", "property_key"],
                    "properties": {
                        "content_id": {
                            "type": "string",
                            "description": "Content ID"
                        },
                        "property_key": {
                            "type": "string",
                            "description": "Property key"
                        }
                    }
                }
            ),
            Tool(
                name="confluence_content_property_set",
                description="Set a property for a Confluence content item",
                inputSchema={
                    "type": "object",
                    "required": ["content_id", "property_key", "value"],
                    "properties": {
                        "content_id": {
                            "type": "string",
                            "description": "Content ID"
                        },
                        "property_key": {
                            "type": "string",
                            "description": "Property key"
                        },
                        "value": {
                            "description": "Property value"
                        }
                    }
                }
            ),
            
            # Content Restrictions
            Tool(
                name="confluence_content_restrictions_get",
                description="Get restrictions for a Confluence content item",
                inputSchema={
                    "type": "object",
                    "required": ["content_id"],
                    "properties": {
                        "content_id": {
                            "type": "string",
                            "description": "Content ID"
                        }
                    }
                }
            ),
            Tool(
                name="confluence_content_restriction_add",
                description="Add a restriction to a Confluence content item",
                inputSchema={
                    "type": "object",
                    "required": ["content_id", "operation", "type", "subject"],
                    "properties": {
                        "content_id": {
                            "type": "string",
                            "description": "Content ID"
                        },
                        "operation": {
                            "type": "string",
                            "enum": ["read", "update"],
                            "description": "Restriction operation"
                        },
                        "type": {
                            "type": "string",
                            "enum": ["user", "group"],
                            "description": "Subject type"
                        },
                        "subject": {
                            "type": "string",
                            "description": "User or group name"
                        }
                    }
                }
            ),
            
            # Labels
            Tool(
                name="confluence_content_labels_get",
                description="Get labels for a Confluence content item",
                inputSchema={
                    "type": "object",
                    "required": ["content_id"],
                    "properties": {
                        "content_id": {
                            "type": "string",
                            "description": "Content ID"
                        }
                    }
                }
            ),
            Tool(
                name="confluence_content_label_add",
                description="Add a label to a Confluence content item",
                inputSchema={
                    "type": "object",
                    "required": ["content_id", "label"],
                    "properties": {
                        "content_id": {
                            "type": "string",
                            "description": "Content ID"
                        },
                        "label": {
                            "type": "string",
                            "description": "Label to add"
                        }
                    }
                }
            ),
            Tool(
                name="confluence_content_search_by_label",
                description="Search for Confluence content by label",
                inputSchema={
                    "type": "object",
                    "required": ["label"],
                    "properties": {
                        "label": {
                            "type": "string",
                            "description": "Label to search for"
                        }
                    }
                }
            ),
            
            # Macros
            Tool(
                name="confluence_macros_get_available",
                description="Get all available Confluence macros",
                inputSchema={
                    "type": "object",
                    "properties": {}
                }
            ),
            Tool(
                name="confluence_macro_add_to_content",
                description="Add a macro to Confluence content",
                inputSchema={
                    "type": "object",
                    "required": ["content_id", "macro_key", "macro_params", "content_version"],
                    "properties": {
                        "content_id": {
                            "type": "string",
                            "description": "Content ID"
                        },
                        "macro_key": {
                            "type": "string",
                            "description": "Macro key"
                        },
                        "macro_params": {
                            "type": "object",
                            "description": "Macro parameters"
                        },
                        "content_version": {
                            "type": "integer",
                            "description": "Content version number"
                        }
                    }
                }
            ),
            
            # Versions
            Tool(
                name="confluence_content_versions_get",
                description="Get all versions of a Confluence content item",
                inputSchema={
                    "type": "object",
                    "required": ["content_id"],
                    "properties": {
                        "content_id": {
                            "type": "string",
                            "description": "Content ID"
                        }
                    }
                }
            ),
            Tool(
                name="confluence_content_versions_compare",
                description="Compare two versions of a Confluence content item",
                inputSchema={
                    "type": "object",
                    "required": ["content_id", "source_version", "target_version"],
                    "properties": {
                        "content_id": {
                            "type": "string",
                            "description": "Content ID"
                        },
                        "source_version": {
                            "type": "integer",
                            "description": "Source version number"
                        },
                        "target_version": {
                            "type": "integer",
                            "description": "Target version number"
                        }
                    }
                }
            ),
            
            # Export
            Tool(
                name="confluence_content_export",
                description="Export Confluence content to a specific format",
                inputSchema={
                    "type": "object",
                    "required": ["content_id"],
                    "properties": {
                        "content_id": {
                            "type": "string",
                            "description": "Content ID"
                        },
                        "export_format": {
                            "type": "string",
                            "enum": ["pdf", "word", "html", "xml"],
                            "description": "Export format"
                        },
                        "save_to_file": {
                            "type": "string",
                            "description": "File path to save the exported content"
                        }
                    }
                }
            ),
            
            # Advanced Content Operations
            Tool(
                name="confluence_create_page_with_attachments",
                description="Create a Confluence page with attachments",
                inputSchema={
                    "type": "object",
                    "required": ["space_key", "title", "body", "attachments"],
                    "properties": {
                        "space_key": {
                            "type": "string",
                            "description": "Space key"
                        },
                        "title": {
                            "type": "string",
                            "description": "Page title"
                        },
                        "body": {
                            "type": "string",
                            "description": "Page body in storage format"
                        },
                        "attachments": {
                            "type": "object",
                            "description": "Dictionary of filename: file_path pairs"
                        },
                        "parent_id": {
                            "type": "string",
                            "description": "Parent page ID"
                        }
                    }
                }
            ),
            Tool(
                name="confluence_add_comment_with_mentions",
                description="Add a comment to Confluence content with user mentions",
                inputSchema={
                    "type": "object",
                    "required": ["content_id", "comment_text", "mentions"],
                    "properties": {
                        "content_id": {
                            "type": "string",
                            "description": "Content ID"
                        },
                        "comment_text": {
                            "type": "string",
                            "description": "Comment text"
                        },
                        "mentions": {
                            "type": "array",
                            "items": {
                                "type": "string"
                            },
                            "description": "List of usernames to mention"
                        }
                    }
                }
            ),
            Tool(
                name="confluence_get_content_children",
                description="Get children of a Confluence content item",
                inputSchema={
                    "type": "object",
                    "required": ["content_id"],
                    "properties": {
                        "content_id": {
                            "type": "string",
                            "description": "Content ID"
                        },
                        "child_type": {
                            "type": "string",
                            "enum": ["comment", "attachment"],
                            "description": "Child type"
                        }
                    }
                }
            )
        ])
    
    return tools


def handle_enhanced_confluence_tool_call(name: str, arguments: Dict, 
                                        space_manager: Optional[ConfluenceSpaceManager] = None,
                                        template_manager: Optional[ConfluenceTemplateManager] = None,
                                        content_manager: Optional[ConfluenceContentManager] = None) -> Dict:
    """Handle enhanced Confluence tool calls."""
    # Initialize managers if needed
    if not all([space_manager, template_manager, content_manager]):
        space_manager, template_manager, content_manager = initialize_enhanced_confluence_managers()
        if not all([space_manager, template_manager, content_manager]):
            return {
                "status": "error",
                "message": "Failed to initialize enhanced Confluence managers. Check your credentials."
            }
    
    # Space Management Tools
    if name == "confluence_space_get_all":
        space_type = arguments.get("space_type")
        status = arguments.get("status")
        label = arguments.get("label")
        return {"spaces": space_manager.get_all_spaces(space_type, status, label)}
    
    elif name == "confluence_space_get":
        space_key = arguments.get("space_key")
        expand = arguments.get("expand")
        return space_manager.get_space(space_key, expand)
    
    elif name == "confluence_space_create":
        key = arguments.get("key")
        name = arguments.get("name")
        description = arguments.get("description")
        is_private = arguments.get("is_private", False)
        return space_manager.create_space(key, name, description, is_private)
    
    elif name == "confluence_space_create_from_template":
        key = arguments.get("key")
        name = arguments.get("name")
        template_key = arguments.get("template_key")
        return space_manager.create_space_from_template(key, name, template_key)
    
    elif name == "confluence_space_update":
        space_key = arguments.get("space_key")
        name = arguments.get("name")
        description = arguments.get("description")
        return space_manager.update_space(space_key, name, description)
    
    elif name == "confluence_space_archive":
        space_key = arguments.get("space_key")
        return space_manager.archive_space(space_key)
    
    elif name == "confluence_space_restore":
        space_key = arguments.get("space_key")
        return space_manager.restore_space(space_key)
    
    elif name == "confluence_space_permissions_get":
        space_key = arguments.get("space_key")
        return space_manager.get_space_permissions(space_key)
    
    elif name == "confluence_space_permissions_add":
        space_key = arguments.get("space_key")
        type_ = arguments.get("type")
        subject = arguments.get("subject")
        operation = arguments.get("operation")
        value = arguments.get("value")
        return space_manager.add_space_permission(space_key, type_, subject, operation, value)
    
    elif name == "confluence_space_permissions_remove":
        space_key = arguments.get("space_key")
        permission_id = arguments.get("permission_id")
        return space_manager.remove_space_permission(space_key, permission_id)
    
    # Template Management Tools
    elif name == "confluence_templates_get_all":
        return {"templates": template_manager.get_content_templates()}
    
    elif name == "confluence_templates_get_blueprints":
        return {"blueprints": template_manager.get_blueprint_templates()}
    
    elif name == "confluence_templates_get_space":
        space_key = arguments.get("space_key")
        return {"templates": template_manager.get_space_templates(space_key)}
    
    elif name == "confluence_templates_get_by_id":
        template_id = arguments.get("template_id")
        return template_manager.get_template_by_id(template_id)
    
    elif name == "confluence_templates_create":
        space_key = arguments.get("space_key")
        name = arguments.get("name")
        template_type = arguments.get("template_type")
        body = arguments.get("body")
        labels = arguments.get("labels", [])
        return template_manager.create_template(space_key, name, template_type, body, labels)
    
    elif name == "confluence_templates_create_page":
        space_key = arguments.get("space_key")
        title = arguments.get("title")
        template_id = arguments.get("template_id")
        ancestor_id = arguments.get("ancestor_id")
        parameters = arguments.get("parameters")
        return template_manager.create_page_from_template(space_key, title, template_id, ancestor_id, parameters)
    
    elif name == "confluence_templates_create_page_from_blueprint":
        space_key = arguments.get("space_key")
        title = arguments.get("title")
        blueprint_id = arguments.get("blueprint_id")
        ancestor_id = arguments.get("ancestor_id")
        parameters = arguments.get("parameters")
        return template_manager.create_page_from_blueprint(space_key, title, blueprint_id, ancestor_id, parameters)
    
    # Content Management Tools - Properties
    elif name == "confluence_content_properties_get":
        content_id = arguments.get("content_id")
        return {"properties": content_manager.get_content_properties(content_id)}
    
    elif name == "confluence_content_property_get":
        content_id = arguments.get("content_id")
        property_key = arguments.get("property_key")
        return content_manager.get_content_property(content_id, property_key)
    
    elif name == "confluence_content_property_set":
        content_id = arguments.get("content_id")
        property_key = arguments.get("property_key")
        value = arguments.get("value")
        return content_manager.set_content_property(content_id, property_key, value)
    
    # Content Management Tools - Restrictions
    elif name == "confluence_content_restrictions_get":
        content_id = arguments.get("content_id")
        return content_manager.get_content_restrictions(content_id)
    
    elif name == "confluence_content_restriction_add":
        content_id = arguments.get("content_id")
        operation = arguments.get("operation")
        type_ = arguments.get("type")
        subject = arguments.get("subject")
        return content_manager.add_content_restriction(content_id, operation, type_, subject)
    
    # Content Management Tools - Labels
    elif name == "confluence_content_labels_get":
        content_id = arguments.get("content_id")
        return {"labels": content_manager.get_content_labels(content_id)}
    
    elif name == "confluence_content_label_add":
        content_id = arguments.get("content_id")
        label = arguments.get("label")
        return content_manager.add_content_label(content_id, label)
    
    elif name == "confluence_content_search_by_label":
        label = arguments.get("label")
        return {"results": content_manager.search_content_by_label(label)}
    
    # Content Management Tools - Macros
    elif name == "confluence_macros_get_available":
        return {"macros": content_manager.get_available_macros()}
    
    elif name == "confluence_macro_add_to_content":
        content_id = arguments.get("content_id")
        macro_key = arguments.get("macro_key")
        macro_params = arguments.get("macro_params")
        content_version = arguments.get("content_version")
        return content_manager.add_macro_to_content(content_id, macro_key, macro_params, content_version)
    
    # Content Management Tools - Versions
    elif name == "confluence_content_versions_get":
        content_id = arguments.get("content_id")
        return {"versions": content_manager.get_content_versions(content_id)}
    
    elif name == "confluence_content_versions_compare":
        content_id = arguments.get("content_id")
        source_version = arguments.get("source_version")
        target_version = arguments.get("target_version")
        return content_manager.compare_content_versions(content_id, source_version, target_version)
    
    # Content Management Tools - Export
    elif name == "confluence_content_export":
        content_id = arguments.get("content_id")
        export_format = arguments.get("export_format", "pdf")
        save_to_file = arguments.get("save_to_file")
        return content_manager.export_content(content_id, export_format, save_to_file)
    
    # Content Management Tools - Advanced
    elif name == "confluence_create_page_with_attachments":
        space_key = arguments.get("space_key")
        title = arguments.get("title")
        body = arguments.get("body")
        attachments_dict = arguments.get("attachments", {})
        parent_id = arguments.get("parent_id")
        
        # Open file objects for each attachment
        attachment_files = {}
        try:
            for filename, file_path in attachments_dict.items():
                with open(file_path, "rb") as f:
                    content = f.read()
                attachment_files[filename] = content
            
            return content_manager.create_page_with_attachments(
                space_key, title, body, attachment_files, parent_id
            )
        finally:
            # Clean up file objects
            for file_obj in attachment_files.values():
                if hasattr(file_obj, 'close'):
                    file_obj.close()
    
    elif name == "confluence_add_comment_with_mentions":
        content_id = arguments.get("content_id")
        comment_text = arguments.get("comment_text")
        mentions = arguments.get("mentions", [])
        return content_manager.add_comment_with_mentions(content_id, comment_text, mentions)
    
    elif name == "confluence_get_content_children":
        content_id = arguments.get("content_id")
        child_type = arguments.get("child_type")
        return {"children": content_manager.get_content_children(content_id, child_type)}
    
    return {
        "status": "error",
        "message": f"Unknown enhanced Confluence tool: {name}"
    }