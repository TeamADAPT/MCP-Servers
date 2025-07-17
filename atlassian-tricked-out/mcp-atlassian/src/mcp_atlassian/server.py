import json
import logging
import os
from collections.abc import Sequence
from typing import Any, Dict

from mcp.server import Server
from mcp.types import Resource, TextContent, Tool
from pydantic import AnyUrl

from .confluence import ConfluenceFetcher
from .jira import JiraFetcher
from .feature_flags import is_enabled, get_all_flags, enable_feature, disable_feature, reset_runtime_overrides
from .server_tools import (
    verify_feature_availability, 
    safe_import_module_tools, 
    runtime_check_api_availability,
    handle_tool_exception,
    create_availability_check_report
)
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
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger("mcp-atlassian")
logging.getLogger("mcp.server.lowlevel.server").setLevel(logging.WARNING)

# We'll try to import the enhanced modules, but handle it if they're not available
try:
    from .server_enhanced_jira import (
        get_enhanced_jira_tools,
        handle_enhanced_jira_tool_call,
        get_enhanced_jira_available,
    )
    ENHANCED_JIRA_MODULE_AVAILABLE = True
except ImportError as e:
    ENHANCED_JIRA_MODULE_AVAILABLE = False
    logger.warning(f"Enhanced Jira module not available, enhanced Jira features will be disabled: {e}")
    # Define dummy functions
    def get_enhanced_jira_tools(): return []
    def handle_enhanced_jira_tool_call(name, arguments): 
        return {"status": STATUS_ERROR, "message": "Enhanced Jira module not available"}
    def get_enhanced_jira_available(): return False

try:
    from .server_jira_service_management import (
        get_jsm_tools,
        handle_jsm_tool_call,
        get_jsm_available,
    )
    JSM_MODULE_AVAILABLE = True
except ImportError as e:
    JSM_MODULE_AVAILABLE = False
    logger.warning(f"JSM module not available, JSM features will be disabled: {e}")
    # Define dummy functions
    def get_jsm_tools(): return []
    def handle_jsm_tool_call(name, arguments): 
        return {"status": STATUS_ERROR, "message": "JSM module not available"}
    def get_jsm_available(): return False
    
# Try to import enhanced Confluence module
try:
    from .server_enhanced_confluence import (
        get_enhanced_confluence_tools,
        handle_enhanced_confluence_tool_call,
        get_enhanced_confluence_available,
    )
    ENHANCED_CONFLUENCE_MODULE_AVAILABLE = True
except ImportError as e:
    ENHANCED_CONFLUENCE_MODULE_AVAILABLE = False
    logger.warning(f"Enhanced Confluence module not available, enhanced Confluence features will be disabled: {e}")
    # Define dummy functions
    def get_enhanced_confluence_tools(): return []
    def handle_enhanced_confluence_tool_call(name, arguments): 
        return {"status": STATUS_ERROR, "message": "Enhanced Confluence module not available"}
    def get_enhanced_confluence_available(): return False

# Try to import enterprise modules
try:
    from .server_enterprise import (
        get_enterprise_tools,
        handle_enterprise_tool_call,
        get_enterprise_available,
    )
    ENTERPRISE_MODULE_AVAILABLE = True
except ImportError as e:
    ENTERPRISE_MODULE_AVAILABLE = False
    logger.warning(f"Enterprise module not available, enterprise features will be disabled: {e}")
    # Define dummy functions
    def get_enterprise_tools(): return []
    def handle_enterprise_tool_call(name, arguments): 
        return {"status": STATUS_ERROR, "message": "Enterprise module not available"}
    def get_enterprise_available(): return False
    
# Try to import bitbucket modules
try:
    from .server_bitbucket import (
        get_bitbucket_tools,
        handle_bitbucket_tool_call,
        get_bitbucket_available,
    )
    BITBUCKET_MODULE_AVAILABLE = True
except ImportError as e:
    BITBUCKET_MODULE_AVAILABLE = False
    logger.warning(f"Bitbucket module not available, Bitbucket features will be disabled: {e}")
    # Define dummy functions
    def get_bitbucket_tools(): return []
    def handle_bitbucket_tool_call(name, arguments): 
        return {"status": STATUS_ERROR, "message": "Bitbucket module not available"}
    def get_bitbucket_available(): return False


def get_available_services() -> Dict[str, bool]:
    """Determine which services are available based on environment variables and feature flags."""
    # Core services based on environment variables
    confluence_vars = all(
        [os.getenv("CONFLUENCE_URL"), os.getenv("CONFLUENCE_USERNAME"), os.getenv("CONFLUENCE_API_TOKEN")]
    )

    jira_vars = all([os.getenv("JIRA_URL"), os.getenv("JIRA_USERNAME"), os.getenv("JIRA_API_TOKEN")])
    
    services = {
        "confluence": confluence_vars,
        "jira": jira_vars,
    }
    
    # Extended services based on feature flags and environment variables
    # Enhanced Jira
    enhanced_jira_available = (
        ENHANCED_JIRA_MODULE_AVAILABLE and
        jira_vars and 
        is_enabled("enhanced_jira")
    )
    
    # Enhanced Confluence
    enhanced_confluence_available = (
        ENHANCED_CONFLUENCE_MODULE_AVAILABLE and 
        confluence_vars and 
        is_enabled("enhanced_confluence") and
        get_enhanced_confluence_available()
    )
    
    # JSM capabilities
    jsm_available = (
        JSM_MODULE_AVAILABLE and
        is_enabled("jsm") and
        get_jsm_available()
    )
    
    # Enterprise features
    enterprise_available = (
        ENTERPRISE_MODULE_AVAILABLE and
        is_enabled("enterprise") and
        get_enterprise_available()
    )
    
    # Add feature-flagged services
    services.update({
        # Extended features
        "enhanced_jira": enhanced_jira_available,
        "enhanced_confluence": enhanced_confluence_available,
        "jsm": jsm_available,
        "enterprise": enterprise_available,
        
        # Additional feature flags checked at tool registration time
        "space_management": enhanced_confluence_available and is_enabled("space_management"),
        "template_management": enhanced_confluence_available and is_enabled("template_management"),
        "content_management": enhanced_confluence_available and is_enabled("content_management"),
        "jsm_approvals": jsm_available and is_enabled("jsm_approvals"),
        "jsm_forms": jsm_available and is_enabled("jsm_forms"),
        "jsm_knowledge_base": jsm_available and is_enabled("jsm_knowledge_base"),
        "jsm_queue": jsm_available and is_enabled("jsm_queue"),
        "analytics": enterprise_available and is_enabled("analytics"),
        "ai_capabilities": enterprise_available and is_enabled("ai_capabilities"),
        "marketplace_integration": enterprise_available and is_enabled("marketplace_integration"),
    })
    
    # Log available services
    enabled_services = [name for name, available in services.items() if available]
    logger.info(f"Available services: {', '.join(enabled_services)}")
    
    return services


# Initialize services based on available credentials
services = get_available_services()
confluence_fetcher = ConfluenceFetcher() if services["confluence"] else None
jira_fetcher = JiraFetcher() if services["jira"] else None
app = Server("mcp-atlassian")

# Log feature flag status
logger.info(f"Feature flags status: {get_all_flags()}")


@app.list_resources()
async def list_resources() -> list[Resource]:
    """List available Confluence spaces and Jira projects as resources."""
    resources = []

    # Add Confluence spaces
    if confluence_fetcher:
        spaces_response = confluence_fetcher.get_spaces()
        if isinstance(spaces_response, dict) and "results" in spaces_response:
            spaces = spaces_response["results"]
            resources.extend(
                [
                    Resource(
                        uri=AnyUrl(f"confluence://{space['key']}"),
                        name=f"Confluence Space: {space['name']}",
                        mimeType="text/plain",
                        description=space.get("description", {}).get("plain", {}).get("value", ""),
                    )
                    for space in spaces
                ]
            )

    # Add Jira projects
    if jira_fetcher:
        try:
            projects = jira_fetcher.jira.projects()
            resources.extend(
                [
                    Resource(
                        uri=AnyUrl(f"jira://{project['key']}"),
                        name=f"Jira Project: {project['name']}",
                        mimeType="text/plain",
                        description=project.get("description", ""),
                    )
                    for project in projects
                ]
            )
        except Exception as e:
            logger.error(f"Error fetching Jira projects: {str(e)}")

    return resources


@app.read_resource()
async def read_resource(uri: AnyUrl) -> str:
    """Read content from Confluence or Jira."""
    uri_str = str(uri)

    # Handle Confluence resources
    if uri_str.startswith("confluence://"):
        if not services["confluence"]:
            raise ValueError("Confluence is not configured. Please provide Confluence credentials.")
        parts = uri_str.replace("confluence://", "").split("/")

        # Handle space listing
        if len(parts) == 1:
            space_key = parts[0]
            documents = confluence_fetcher.get_space_pages(space_key)
            content = []
            for doc in documents:
                content.append(f"# {doc.metadata['title']}\n\n{doc.page_content}\n---")
            return "\n\n".join(content)

        # Handle specific page
        elif len(parts) >= 3 and parts[1] == "pages":
            space_key = parts[0]
            title = parts[2]
            doc = confluence_fetcher.get_page_by_title(space_key, title)

            if not doc:
                raise ValueError(f"Page not found: {title}")

            return doc.page_content

    # Handle Jira resources
    elif uri_str.startswith("jira://"):
        if not services["jira"]:
            raise ValueError("Jira is not configured. Please provide Jira credentials.")
        parts = uri_str.replace("jira://", "").split("/")

        # Handle project listing
        if len(parts) == 1:
            project_key = parts[0]
            issues = jira_fetcher.get_project_issues(project_key)
            content = []
            for issue in issues:
                content.append(f"# {issue.metadata['key']}: {issue.metadata['title']}\n\n{issue.page_content}\n---")
            return "\n\n".join(content)

        # Handle specific issue
        elif len(parts) >= 3 and parts[1] == "issues":
            issue_key = parts[2]
            issue = jira_fetcher.get_issue(issue_key)
            return issue.page_content

    raise ValueError(f"Invalid resource URI: {uri}")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available Confluence and Jira tools, along with feature-flagged enhanced tools."""
    tools = []

    # Add Confluence tools
    if confluence_fetcher:
        tools.extend(
            [
                Tool(
                    name="confluence_search",
                    description="Search Confluence content using CQL",
                    category=TOOL_CATEGORY_CONFLUENCE,
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "CQL query string (e.g. 'type=page AND space=DEV')",
                            },
                            "limit": {
                                "type": "number",
                                "description": "Maximum number of results (1-50)",
                                "default": 10,
                                "minimum": 1,
                                "maximum": 50,
                            },
                        },
                        "required": ["query"],
                    },
                ),
                Tool(
                    name="confluence_get_page",
                    description="Get content of a specific Confluence page by ID",
                    category=TOOL_CATEGORY_CONFLUENCE,
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "page_id": {"type": "string", "description": "Confluence page ID"},
                            "include_metadata": {
                                "type": "boolean",
                                "description": "Whether to include page metadata",
                                "default": True,
                            },
                        },
                        "required": ["page_id"],
                    },
                ),
                Tool(
                    name="confluence_get_comments",
                    description="Get comments for a specific Confluence page",
                    category=TOOL_CATEGORY_CONFLUENCE,
                    inputSchema={
                        "type": "object",
                        "properties": {"page_id": {"type": "string", "description": "Confluence page ID"}},
                        "required": ["page_id"],
                    },
                ),
                Tool(
                    name="confluence_create_page",
                    description="Create a new Confluence page with markdown content",
                    category=TOOL_CATEGORY_CONFLUENCE,
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "space_key": {"type": "string", "description": "The space key where the page will be created"},
                            "title": {"type": "string", "description": "The title of the page"},
                            "content": {"type": "string", "description": "The content of the page in markdown format"},
                            "parent_id": {"type": "string", "description": "Optional parent page ID for hierarchical organization"},
                            "content_type": {
                                "type": "string", 
                                "description": "The type of content",
                                "default": "markdown",
                                "enum": ["markdown", "storage"]
                            }
                        },
                        "required": ["space_key", "title", "content"],
                    },
                ),
                Tool(
                    name="confluence_create_page_from_file",
                    description="Create a new Confluence page from a markdown file",
                    category=TOOL_CATEGORY_CONFLUENCE,
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "space_key": {"type": "string", "description": "The space key where the page will be created"},
                            "title": {"type": "string", "description": "The title of the page"},
                            "file_path": {"type": "string", "description": "Path to the markdown file"},
                            "parent_id": {"type": "string", "description": "Optional parent page ID for hierarchical organization"}
                        },
                        "required": ["space_key", "title", "file_path"],
                    },
                ),
                Tool(
                    name="confluence_attach_file",
                    description="Attach a file to a Confluence page",
                    category=TOOL_CATEGORY_CONFLUENCE,
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "page_id": {"type": "string", "description": "The ID of the page to attach the file to"},
                            "file_path": {"type": "string", "description": "Path to the file to attach"},
                            "comment": {"type": "string", "description": "Optional comment for the attachment"}
                        },
                        "required": ["page_id", "file_path"],
                    },
                ),
                Tool(
                    name="confluence_get_page_history",
                    description="Get the version history of a Confluence page",
                    category=TOOL_CATEGORY_CONFLUENCE,
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "page_id": {"type": "string", "description": "The ID of the page to get the history for"},
                            "limit": {"type": "number", "description": "Maximum number of versions to return", "default": 10}
                        },
                        "required": ["page_id"],
                    },
                ),
                Tool(
                    name="confluence_restore_page_version",
                    description="Restore a Confluence page to a previous version",
                    category=TOOL_CATEGORY_CONFLUENCE,
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "page_id": {"type": "string", "description": "The ID of the page to restore"},
                            "version_number": {"type": "number", "description": "The version number to restore to"}
                        },
                        "required": ["page_id", "version_number"],
                    },
                ),
                Tool(
                    name="confluence_update_page",
                    description="Update an existing Confluence page",
                    category=TOOL_CATEGORY_CONFLUENCE,
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "page_id": {"type": "string", "description": "The ID of the page to update"},
                            "title": {"type": "string", "description": "Optional new title for the page"},
                            "content": {"type": "string", "description": "Optional new content for the page"},
                            "content_type": {
                                "type": "string", 
                                "description": "The type of content",
                                "default": "markdown",
                                "enum": ["markdown", "storage"]
                            },
                            "message": {"type": "string", "description": "Optional message for the update"}
                        },
                        "required": ["page_id"],
                    },
                ),
                Tool(
                    name="confluence_move_page",
                    description="Move a Confluence page to a different parent or space",
                    category=TOOL_CATEGORY_CONFLUENCE,
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "page_id": {"type": "string", "description": "The ID of the page to move"},
                            "target_parent_id": {"type": "string", "description": "Optional ID of the new parent page"},
                            "target_space_key": {"type": "string", "description": "Optional key of the new space"},
                            "position": {"type": "number", "description": "Optional position among siblings (0-based index)"}
                        },
                        "required": ["page_id"],
                    },
                ),
                Tool(
                    name="confluence_get_page_tree",
                    description="Get a hierarchical tree of pages in a space",
                    category=TOOL_CATEGORY_CONFLUENCE,
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "space_key": {"type": "string", "description": "The space key"},
                            "root_page_id": {"type": "string", "description": "Optional ID of the root page (if not provided, gets the space root)"},
                            "depth": {"type": "number", "description": "Maximum depth of the tree (1-5)", "default": 3, "minimum": 1, "maximum": 5},
                            "expand": {"type": "string", "description": "Optional fields to expand"}
                        },
                        "required": ["space_key"],
                    },
                ),
            ]
        )

    # Add Jira tools
    if jira_fetcher:
        tools.extend(
            [
                Tool(
                    name="jira_get_issue",
                    description="Get details of a specific Jira issue",
                    category=TOOL_CATEGORY_JIRA,
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "issue_key": {"type": "string", "description": "Jira issue key (e.g., 'PROJ-123')"},
                            "expand": {"type": "string", "description": "Optional fields to expand", "default": None},
                        },
                        "required": ["issue_key"],
                    },
                ),
                Tool(
                    name="jira_search",
                    description="Search Jira issues using JQL",
                    category=TOOL_CATEGORY_JIRA,
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "jql": {"type": "string", "description": "JQL query string"},
                            "fields": {
                                "type": "string",
                                "description": "Comma-separated fields to return",
                                "default": "*all",
                            },
                            "limit": {
                                "type": "number",
                                "description": "Maximum number of results (1-50)",
                                "default": 10,
                                "minimum": 1,
                                "maximum": 50,
                            },
                        },
                        "required": ["jql"],
                    },
                ),
                Tool(
                    name="jira_get_project_issues",
                    description="Get all issues for a specific Jira project",
                    category=TOOL_CATEGORY_JIRA,
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "project_key": {"type": "string", "description": "The project key"},
                            "limit": {
                                "type": "number",
                                "description": "Maximum number of results (1-50)",
                                "default": 10,
                                "minimum": 1,
                                "maximum": 50,
                            },
                        },
                        "required": ["project_key"],
                    },
                ),
                Tool(
                    name="jira_create_project",
                    description="Create a new Jira project",
                    category=TOOL_CATEGORY_JIRA,
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "key": {"type": "string", "description": "The project key (must be uppercase, e.g., 'MOXY')"},
                            "name": {"type": "string", "description": "The project name"},
                            "project_type": {
                                "type": "string",
                                "description": "The project type",
                                "default": "software",
                                "enum": ["software", "business", "service_desk"],
                            },
                            "template": {
                                "type": "string",
                                "description": "The project template",
                                "default": "com.pyxis.greenhopper.jira:basic-software-development-template",
                            },
                        },
                        "required": ["key", "name"],
                    },
                ),
                Tool(
                    name="jira_create_issue",
                    description="Create a new Jira issue or subtask",
                    category=TOOL_CATEGORY_JIRA,
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "project_key": {"type": "string", "description": "The project key (e.g., 'MOXY')"},
                            "summary": {"type": "string", "description": "The issue summary/title"},
                            "issue_type": {
                                "type": "string",
                                "description": "The issue type",
                                "default": "Task",
                                "enum": ["Task", "Bug", "Story", "Subtask"],
                            },
                            "description": {
                                "type": "string",
                                "description": "The issue description",
                                "default": "",
                            },
                            "labels": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "List of labels to apply to the issue",
                            },
                            "priority": {
                                "type": "string",
                                "description": "The issue priority",
                                "default": "Medium",
                                "enum": ["Highest", "High", "Medium", "Low", "Lowest"],
                            },
                            "parent_key": {
                                "type": "string",
                                "description": "The parent issue key (for subtasks)",
                            },
                            "epic_link": {
                                "type": "string",
                                "description": "The Epic issue key to link this issue to (for Stories)",
                            },
                            "name": {
                                "type": "string",
                                "description": "REQUIRED: The name value for the custom field",
                            },
                            "dept": {
                                "type": "string",
                                "description": "REQUIRED: The department value for the custom field",
                            },
                        },
                        "required": ["project_key", "summary", "name", "dept"],
                    },
                ),
                Tool(
                    name="jira_get_issue_link_types",
                    description="Get all available issue link types",
                    category=TOOL_CATEGORY_JIRA,
                    inputSchema={
                        "type": "object",
                        "properties": {},
                        "required": [],
                    },
                ),
                Tool(
                    name="jira_create_issue_link",
                    description="Create a link between two Jira issues",
                    category=TOOL_CATEGORY_JIRA,
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "link_type": {
                                "type": "string",
                                "description": "The type of link (e.g., 'Relates', 'Blocks', 'is blocked by')",
                                "default": "Relates"
                            },
                            "outward_issue": {
                                "type": "string",
                                "description": "The issue key that is the source of the link"
                            },
                            "inward_issue": {
                                "type": "string",
                                "description": "The issue key that is the target of the link"
                            }
                        },
                        "required": ["outward_issue", "inward_issue"],
                    },
                ),
                Tool(
                    name="jira_update_issue",
                    description="Update an existing Jira issue",
                    category=TOOL_CATEGORY_JIRA,
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "issue_key": {
                                "type": "string",
                                "description": "The issue key to update (e.g., 'PROJ-123')"
                            },
                            "summary": {
                                "type": "string",
                                "description": "Optional new summary/title"
                            },
                            "description": {
                                "type": "string",
                                "description": "Optional new description"
                            },
                            "issue_type": {
                                "type": "string",
                                "description": "Optional new issue type"
                            },
                            "priority": {
                                "type": "string",
                                "description": "Optional new priority",
                                "enum": ["Highest", "High", "Medium", "Low", "Lowest"]
                            },
                            "fields": {
                                "type": "object",
                                "description": "Optional dictionary of additional fields to update"
                            }
                        },
                        "required": ["issue_key"],
                    },
                ),
                Tool(
                    name="jira_transition_issue",
                    description="Transition an issue to a different status",
                    category=TOOL_CATEGORY_JIRA,
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "issue_key": {
                                "type": "string",
                                "description": "The issue key to transition (e.g., 'PROJ-123')"
                            },
                            "transition_name": {
                                "type": "string",
                                "description": "The name of the transition to perform (e.g., 'In Progress', 'Done')"
                            }
                        },
                        "required": ["issue_key", "transition_name"],
                    },
                ),
                Tool(
                    name="jira_add_comment",
                    description="Add a comment to an issue",
                    category=TOOL_CATEGORY_JIRA,
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "issue_key": {
                                "type": "string",
                                "description": "The issue key to comment on (e.g., 'PROJ-123')"
                            },
                            "comment": {
                                "type": "string",
                                "description": "The comment text"
                            }
                        },
                        "required": ["issue_key", "comment"],
                    },
                ),
                Tool(
                    name="jira_create_epic",
                    description="Create a new Epic in Jira",
                    category=TOOL_CATEGORY_JIRA,
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "project_key": {
                                "type": "string",
                                "description": "The project key (e.g., 'MOXY')"
                            },
                            "summary": {
                                "type": "string",
                                "description": "The Epic summary/title"
                            },
                            "description": {
                                "type": "string",
                                "description": "The Epic description",
                                "default": ""
                            },
                            "priority": {
                                "type": "string",
                                "description": "The Epic priority",
                                "default": "Medium",
                                "enum": ["Highest", "High", "Medium", "Low", "Lowest"]
                            },
                            "epic_name": {
                                "type": "string",
                                "description": "Optional short name for the Epic (displayed on the Epic card)"
                            },
                            "epic_color": {
                                "type": "string",
                                "description": "Optional color for the Epic (e.g., 'ghx-label-1', 'ghx-label-2', etc.)"
                            },
                            "name": {
                                "type": "string",
                                "description": "REQUIRED: The name value for the custom field"
                            },
                            "dept": {
                                "type": "string",
                                "description": "REQUIRED: The department value for the custom field"
                            }
                        },
                        "required": ["project_key", "summary", "name", "dept"],
                    },
                ),
                Tool(
                    name="jira_get_epic_issues",
                    description="Get all issues linked to an Epic in a structured format",
                    category=TOOL_CATEGORY_JIRA,
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "epic_key": {
                                "type": "string",
                                "description": "The Epic issue key (e.g., 'PROJ-123')"
                            },
                            "include_subtasks": {
                                "type": "boolean",
                                "description": "Whether to include subtasks of issues linked to the Epic",
                                "default": True
                            }
                        },
                        "required": ["epic_key"],
                    },
                ),
                Tool(
                    name="jira_update_epic_progress",
                    description="Update Epic progress tracking based on linked issues",
                    category=TOOL_CATEGORY_JIRA,
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "epic_key": {
                                "type": "string",
                                "description": "The Epic issue key (e.g., 'PROJ-123')"
                            }
                        },
                        "required": ["epic_key"],
                    },
                ),
                Tool(
                    name="jira_get_issue_attachments",
                    description="Get all attachments for an issue",
                    category=TOOL_CATEGORY_JIRA,
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "issue_key": {
                                "type": "string",
                                "description": "The issue key (e.g., 'PROJ-123')"
                            }
                        },
                        "required": ["issue_key"],
                    },
                ),
                Tool(
                    name="jira_attach_file_to_issue",
                    description="Attach a file to a Jira issue",
                    category=TOOL_CATEGORY_JIRA,
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "issue_key": {
                                "type": "string",
                                "description": "The issue key (e.g., 'PROJ-123')"
                            },
                            "file_path": {
                                "type": "string",
                                "description": "Path to the file to attach"
                            },
                            "comment": {
                                "type": "string",
                                "description": "Optional comment for the attachment"
                            }
                        },
                        "required": ["issue_key", "file_path"],
                    },
                ),
                Tool(
                    name="jira_get_issue_transitions",
                    description="Get available transitions for an issue",
                    category=TOOL_CATEGORY_JIRA,
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "issue_key": {
                                "type": "string",
                                "description": "The issue key (e.g., 'PROJ-123')"
                            }
                        },
                        "required": ["issue_key"],
                    },
                ),
            ]
        )
    
    # Add system diagnostic tools 
    tools.extend([
        Tool(
            name="mcp_atlassian_diagnostics",
            description="Run diagnostics on the MCP Atlassian integration",
            category="System",
            inputSchema={
                "type": "object",
                "properties": {
                    "detailed": {
                        "type": "boolean", 
                        "description": "Whether to include detailed information",
                        "default": False
                    }
                }
            }
        ),
        Tool(
            name="mcp_atlassian_toggle_feature",
            description="Enable or disable a feature",
            category="System",
            inputSchema={
                "type": "object",
                "properties": {
                    "feature_name": {
                        "type": "string",
                        "description": "Name of the feature to toggle"
                    },
                    "enable": {
                        "type": "boolean",
                        "description": "Whether to enable or disable the feature"
                    }
                },
                "required": ["feature_name", "enable"]
            }
        ),
        Tool(
            name="mcp_atlassian_list_features",
            description="List all available features and their status",
            category="System",
            inputSchema={
                "type": "object",
                "properties": {
                    "group_by_category": {
                        "type": "boolean",
                        "description": "Whether to group features by category",
                        "default": True
                    }
                }
            }
        )
    ])
    
    # Add Enhanced Jira tools if enabled
    if services.get("enhanced_jira", False):
        logger.info("Adding enhanced Jira tools")
        tools.extend(safe_import_module_tools(
            "server_enhanced_jira", 
            "get_enhanced_jira_tools", 
            "enhanced_jira"
        ))
    
    # Add Enhanced Confluence tools if enabled
    if services.get("enhanced_confluence", False):
        logger.info("Adding enhanced Confluence tools")
        tools.extend(safe_import_module_tools(
            "server_enhanced_confluence", 
            "get_enhanced_confluence_tools", 
            "enhanced_confluence"
        ))
    
    # Add JSM tools if enabled
    if services.get("jsm", False):
        logger.info("Adding JSM tools")
        tools.extend(safe_import_module_tools(
            "server_jira_service_management", 
            "get_jsm_tools", 
            "jsm"
        ))
    
    # Add Bitbucket tools if enabled
    if services.get("bitbucket", False):
        logger.info("Adding Bitbucket tools")
        tools.extend(safe_import_module_tools(
            "server_bitbucket", 
            "get_bitbucket_tools", 
            "bitbucket"
        ))
    
    # Add Enterprise tools if enabled
    if services.get("enterprise", False):
        logger.info("Adding Enterprise tools")
        tools.extend(safe_import_module_tools(
            "server_enterprise", 
            "get_enterprise_tools", 
            "enterprise"
        ))

    return tools


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> Sequence[TextContent]:
    """Handle tool calls for Confluence and Jira operations, including enhanced features."""
    try:
        # Handle Confluence tools
        if name == "confluence_search":
            limit = min(int(arguments.get("limit", 10)), 50)
            documents = confluence_fetcher.search(arguments["query"], limit)
            search_results = [
                {
                    "page_id": doc.metadata["page_id"],
                    "title": doc.metadata["title"],
                    "space": doc.metadata["space"],
                    "url": doc.metadata["url"],
                    "last_modified": doc.metadata["last_modified"],
                    "type": doc.metadata["type"],
                    "excerpt": doc.page_content,
                }
                for doc in documents
            ]

            return [TextContent(type="text", text=json.dumps(search_results, indent=2))]

        elif name == "confluence_get_page":
            doc = confluence_fetcher.get_page_content(arguments["page_id"])
            include_metadata = arguments.get("include_metadata", True)

            if include_metadata:
                result = {"content": doc.page_content, "metadata": doc.metadata}
            else:
                result = {"content": doc.page_content}

            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "confluence_get_comments":
            comments = confluence_fetcher.get_page_comments(arguments["page_id"])
            formatted_comments = [
                {
                    "author": comment.metadata["author_name"],
                    "created": comment.metadata["last_modified"],
                    "content": comment.page_content,
                }
                for comment in comments
            ]

            return [TextContent(type="text", text=json.dumps(formatted_comments, indent=2))]
            
        elif name == "confluence_create_page":
            space_key = arguments["space_key"]
            title = arguments["title"]
            content = arguments["content"]
            parent_id = arguments.get("parent_id")
            content_type = arguments.get("content_type", "markdown")
            
            result = confluence_fetcher.create_page(
                space_key=space_key,
                title=title,
                content=content,
                parent_id=parent_id,
                content_type=content_type
            )
            
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
        elif name == "confluence_create_page_from_file":
            space_key = arguments["space_key"]
            title = arguments["title"]
            file_path = arguments["file_path"]
            parent_id = arguments.get("parent_id")
            
            result = confluence_fetcher.create_page_from_file(
                space_key=space_key,
                title=title,
                file_path=file_path,
                parent_id=parent_id
            )
            
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
        elif name == "confluence_attach_file":
            page_id = arguments["page_id"]
            file_path = arguments["file_path"]
            comment = arguments.get("comment")
            
            result = confluence_fetcher.attach_file(
                page_id=page_id,
                file_path=file_path,
                comment=comment
            )
            
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
        elif name == "confluence_get_page_history":
            page_id = arguments["page_id"]
            limit = min(int(arguments.get("limit", 10)), 50)
            
            result = confluence_fetcher.get_page_history(
                page_id=page_id,
                limit=limit
            )
            
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
        elif name == "confluence_restore_page_version":
            page_id = arguments["page_id"]
            version_number = int(arguments["version_number"])
            
            result = confluence_fetcher.restore_page_version(
                page_id=page_id,
                version_number=version_number
            )
            
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
        elif name == "confluence_update_page":
            page_id = arguments["page_id"]
            title = arguments.get("title")
            content = arguments.get("content")
            content_type = arguments.get("content_type", "markdown")
            message = arguments.get("message")
            
            result = confluence_fetcher.update_page(
                page_id=page_id,
                title=title,
                content=content,
                content_type=content_type,
                message=message
            )
            
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
        elif name == "confluence_move_page":
            page_id = arguments["page_id"]
            target_parent_id = arguments.get("target_parent_id")
            target_space_key = arguments.get("target_space_key")
            position = arguments.get("position")
            
            result = confluence_fetcher.move_page(
                page_id=page_id,
                target_parent_id=target_parent_id,
                target_space_key=target_space_key,
                position=position
            )
            
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
        elif name == "confluence_get_page_tree":
            space_key = arguments["space_key"]
            root_page_id = arguments.get("root_page_id")
            depth = arguments.get("depth", 3)
            expand = arguments.get("expand")
            
            result = confluence_fetcher.get_page_tree(
                space_key=space_key,
                root_page_id=root_page_id,
                depth=depth,
                expand=expand
            )
            
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        # Handle Jira tools
        elif name == "jira_get_issue":
            doc = jira_fetcher.get_issue(arguments["issue_key"], expand=arguments.get("expand"))
            result = {"content": doc.page_content, "metadata": doc.metadata}
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "jira_search":
            limit = min(int(arguments.get("limit", 10)), 50)
            documents = jira_fetcher.search_issues(
                arguments["jql"], fields=arguments.get("fields", "*all"), limit=limit
            )
            search_results = [
                {
                    "key": doc.metadata["key"],
                    "title": doc.metadata["title"],
                    "type": doc.metadata["type"],
                    "status": doc.metadata["status"],
                    "created_date": doc.metadata["created_date"],
                    "priority": doc.metadata["priority"],
                    "link": doc.metadata["link"],
                    "excerpt": doc.page_content[:500] + "..." if len(doc.page_content) > 500 else doc.page_content,
                }
                for doc in documents
            ]
            return [TextContent(type="text", text=json.dumps(search_results, indent=2))]

        elif name == "jira_get_project_issues":
            limit = min(int(arguments.get("limit", 10)), 50)
            documents = jira_fetcher.get_project_issues(arguments["project_key"], limit=limit)
            project_issues = [
                {
                    "key": doc.metadata["key"],
                    "title": doc.metadata["title"],
                    "type": doc.metadata["type"],
                    "status": doc.metadata["status"],
                    "created_date": doc.metadata["created_date"],
                    "link": doc.metadata["link"],
                }
                for doc in documents
            ]
            return [TextContent(type="text", text=json.dumps(project_issues, indent=2))]
            
        elif name == "jira_create_project":
            key = arguments["key"]
            name = arguments["name"]
            project_type = arguments.get("project_type", "software")
            template = arguments.get("template", "com.pyxis.greenhopper.jira:basic-software-development-template")
            
            response = jira_fetcher.create_project(key, name, project_type, template)
            
            result = {
                "success": True,
                "message": f"Project {key} created successfully",
                "project": {
                    "key": key,
                    "name": name,
                    "project_type": project_type,
                    "template": template,
                    "url": f"{jira_fetcher.config.url.rstrip('/')}/projects/{key}"
                }
            }
            
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
        elif name == "jira_create_issue":
            project_key = arguments["project_key"]
            summary = arguments["summary"]
            issue_type = arguments.get("issue_type", "Task")
            description = arguments.get("description", "")
            labels = arguments.get("labels", [])
            priority = arguments.get("priority", "Medium")
            parent_key = arguments.get("parent_key")
            name = arguments["name"]
            dept = arguments["dept"]
            
            epic_link = arguments.get("epic_link")
            
            result = jira_fetcher.create_issue(
                project_key=project_key,
                summary=summary,
                issue_type=issue_type,
                description=description,
                labels=labels,
                priority=priority,
                parent_key=parent_key,
                epic_link=epic_link,
                name=name,
                dept=dept
            )
            
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
        elif name == "jira_get_issue_link_types":
            link_types = jira_fetcher.get_issue_link_types()
            
            result = {
                "link_types": link_types
            }
            
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
        elif name == "jira_create_issue_link":
            link_type = arguments.get("link_type", "Relates")
            outward_issue = arguments["outward_issue"]
            inward_issue = arguments["inward_issue"]
            
            jira_fetcher.create_issue_link(
                link_type=link_type,
                outward_issue=outward_issue,
                inward_issue=inward_issue
            )
            
            result = {
                "success": True,
                "message": f"Created link between {outward_issue} and {inward_issue}",
                "link_type": link_type,
                "outward_issue": outward_issue,
                "inward_issue": inward_issue
            }
            
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
        elif name == "jira_update_issue":
            issue_key = arguments["issue_key"]
            summary = arguments.get("summary")
            description = arguments.get("description")
            issue_type = arguments.get("issue_type")
            priority = arguments.get("priority")
            fields = arguments.get("fields")
            
            result = jira_fetcher.update_issue(
                issue_key=issue_key,
                summary=summary,
                description=description,
                issue_type=issue_type,
                priority=priority,
                fields=fields
            )
            
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
        elif name == "jira_transition_issue":
            issue_key = arguments["issue_key"]
            transition_name = arguments["transition_name"]
            
            result = jira_fetcher.transition_issue(
                issue_key=issue_key,
                transition_name=transition_name
            )
            
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
        elif name == "jira_add_comment":
            issue_key = arguments["issue_key"]
            comment = arguments["comment"]
            
            result = jira_fetcher.add_comment(
                issue_key=issue_key,
                comment=comment
            )
            
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
        elif name == "jira_create_epic":
            project_key = arguments["project_key"]
            summary = arguments["summary"]
            description = arguments.get("description", "")
            priority = arguments.get("priority", "Medium")
            epic_name = arguments.get("epic_name")
            epic_color = arguments.get("epic_color")
            name = arguments["name"]
            dept = arguments["dept"]
            
            result = jira_fetcher.create_epic(
                project_key=project_key,
                summary=summary,
                description=description,
                priority=priority,
                epic_name=epic_name,
                epic_color=epic_color,
                name=name,
                dept=dept
            )
            
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
        elif name == "jira_get_epic_issues":
            epic_key = arguments["epic_key"]
            include_subtasks = arguments.get("include_subtasks", True)
            
            result = jira_fetcher.get_epic_issues(
                epic_key=epic_key,
                include_subtasks=include_subtasks
            )
            
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
        elif name == "jira_update_epic_progress":
            epic_key = arguments["epic_key"]
            
            result = jira_fetcher.update_epic_progress(
                epic_key=epic_key
            )
            
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
        elif name == "jira_get_issue_attachments":
            issue_key = arguments["issue_key"]
            
            result = jira_fetcher.get_issue_attachments(
                issue_key=issue_key
            )
            
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
        elif name == "jira_attach_file_to_issue":
            issue_key = arguments["issue_key"]
            file_path = arguments["file_path"]
            comment = arguments.get("comment")
            
            result = jira_fetcher.attach_file_to_issue(
                issue_key=issue_key,
                file_path=file_path,
                comment=comment
            )
            
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
        elif name == "jira_get_issue_transitions":
            issue_key = arguments["issue_key"]
            
            result = jira_fetcher.get_issue_transitions(
                issue_key=issue_key
            )
            
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        # Handle Enhanced Jira tools
        elif name.startswith("jira_enhanced_") or name.startswith("jira_get_custom_") or name.startswith("jira_set_") or name == "jira_create_global_field_context" or name == "jira_assign_field_to_projects":
            # Check if enhanced Jira is available
            if not services.get("enhanced_jira", False):
                return [TextContent(type="text", text=json.dumps(
                    {"status": STATUS_ERROR, "message": "Enhanced Jira tools are not enabled"}, 
                    indent=2
                ))]
                
            # Call the handler from server_enhanced_jira.py
            result = handle_enhanced_jira_tool_call(name, arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
        # Handle Enhanced Confluence tools
        elif name.startswith("confluence_enhanced_") or name.startswith("confluence_space_") or name.startswith("confluence_template_") or name.startswith("confluence_content_"):
            # Check if enhanced Confluence is available
            if not services.get("enhanced_confluence", False):
                return [TextContent(type="text", text=json.dumps(
                    {"status": STATUS_ERROR, "message": "Enhanced Confluence tools are not enabled"}, 
                    indent=2
                ))]
                
            # Call the handler from server_enhanced_confluence.py
            result = handle_enhanced_confluence_tool_call(name, arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
        # Handle JSM tools
        elif name.startswith("jsm_"):
            # Check if JSM is available
            if not services.get("jsm", False):
                return [TextContent(type="text", text=json.dumps(
                    {"status": STATUS_ERROR, "message": "JSM tools are not enabled"}, 
                    indent=2
                ))]
                
            # Call the handler from server_jira_service_management.py
            result = handle_jsm_tool_call(name, arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
        # Handle Enterprise tools
        elif name.startswith("enterprise_") or name.startswith("analytics_") or name.startswith("ai_") or name.startswith("marketplace_"):
            # Check if Enterprise features are available
            if not services.get("enterprise", False):
                return [TextContent(type="text", text=json.dumps(
                    {"status": STATUS_ERROR, "message": "Enterprise tools are not enabled"}, 
                    indent=2
                ))]
                
            # Call the handler from server_enterprise.py
            result = handle_enterprise_tool_call(name, arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
        # Handle Bitbucket tools
        elif name.startswith("bitbucket_"):
            # Check if Bitbucket features are available
            if not services.get("bitbucket", False):
                return [TextContent(type="text", text=json.dumps(
                    {"status": STATUS_ERROR, "message": "Bitbucket tools are not enabled"}, 
                    indent=2
                ))]
                
            # Call the handler from server_bitbucket.py
            result = handle_bitbucket_tool_call(name, arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        # Handle diagnostic tools
        elif name == "mcp_atlassian_diagnostics":
            # Import here to avoid circular imports
            from .diagnostics import run_diagnostics, format_diagnostics_report
            
            detailed = arguments.get("detailed", False)
            diagnostics = run_diagnostics()
            
            # Format the report
            report = format_diagnostics_report(diagnostics)
            
            if detailed:
                # Return full diagnostics data
                return [TextContent(type="text", text=json.dumps(diagnostics, indent=2))]
            else:
                # Return formatted report
                return [TextContent(type="text", text=report)]
        
        elif name == "mcp_atlassian_toggle_feature":
            feature_name = arguments.get("feature_name")
            enable = arguments.get("enable", False)
            
            if not feature_name:
                return [TextContent(type="text", text=json.dumps(
                    {"status": STATUS_ERROR, "message": "Feature name is required"}, 
                    indent=2
                ))]
            
            # Toggle feature
            if enable:
                success = enable_feature(feature_name)
                message = f"Feature '{feature_name}' enabled" if success else f"Failed to enable feature '{feature_name}'"
            else:
                success = disable_feature(feature_name)
                message = f"Feature '{feature_name}' disabled" if success else f"Failed to disable feature '{feature_name}'"
            
            # Get updated services
            services = get_available_services()
            globals()['services'] = services
            
            result = {
                "status": STATUS_SUCCESS if success else STATUS_ERROR,
                "message": message,
                "feature": feature_name,
                "enabled": is_enabled(feature_name)
            }
            
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "mcp_atlassian_list_features":
            group_by_category = arguments.get("group_by_category", True)
            
            # Get feature flags
            flags = get_all_flags()
            
            if group_by_category:
                # Import feature groups
                from .feature_flags import get_feature_groups
                feature_groups = get_feature_groups()
                
                result = {
                    "status": STATUS_SUCCESS,
                    "grouped_features": {},
                    "ungrouped_features": {}
                }
                
                # Group features by category
                for group_name, group_flags in feature_groups.items():
                    result["grouped_features"][group_name] = {}
                    for flag in group_flags:
                        if flag in flags:
                            result["grouped_features"][group_name][flag] = flags[flag]
                
                # Find ungrouped features
                grouped_flags = set()
                for group_flags in feature_groups.values():
                    grouped_flags.update(group_flags)
                
                for flag, enabled in flags.items():
                    if flag not in grouped_flags:
                        result["ungrouped_features"][flag] = enabled
                
                return [TextContent(type="text", text=json.dumps(result, indent=2))]
            else:
                # Return flat list
                result = {
                    "status": STATUS_SUCCESS,
                    "features": flags
                }
                
                return [TextContent(type="text", text=json.dumps(result, indent=2))]

        # Unknown tool
        raise ValueError(f"Unknown tool: {name}")

    except Exception as e:
        logger.error(f"Tool execution error: {str(e)}")
        raise RuntimeError(f"Tool execution failed: {str(e)}")


async def main():
    # Import here to avoid issues with event loops
    from mcp.server.stdio import stdio_server

    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
