"""JSM Tool Registration for MCP-Atlassian Server.

This module contains JSM (Jira Service Management) tools registration for the MCP-Atlassian server.
It defines the tools and provides handlers for JSM operations.

Usage:
    Import this module in server.py to add JSM tools to the MCP-Atlassian server.
"""

from mcp.types import TextContent, Tool
import json
import logging
import os

from .jsm import JiraServiceManager
from .jsm_knowledge_base import JSMKnowledgeBase
from .jsm_queue import JSMQueueManager
from .jsm_approvals import JSMApprovalManager
from .jsm_forms import JSMFormManager

# Configure logging
logger = logging.getLogger("mcp-jsm")

def get_jsm_available():
    """Determine if JSM service is available based on environment variables."""
    jsm_vars = all([
        os.getenv("JSM_URL") or os.getenv("JIRA_URL"),
        os.getenv("JSM_USERNAME") or os.getenv("JIRA_USERNAME"),
        os.getenv("JSM_API_TOKEN") or os.getenv("JIRA_API_TOKEN")
    ])
    return jsm_vars

def initialize_jsm_service():
    """Initialize JSM service if credentials are available."""
    if get_jsm_available():
        return JiraServiceManager()
    return None

# Initialize JSM service and advanced modules
jsm_service = initialize_jsm_service()
jsm_kb_service = None
jsm_queue_service = None
jsm_approval_service = None
jsm_form_service = None

if jsm_service:
    jsm_kb_service = JSMKnowledgeBase(jsm_client=jsm_service)
    jsm_queue_service = JSMQueueManager(jsm_client=jsm_service)
    jsm_approval_service = JSMApprovalManager(jsm_client=jsm_service)
    jsm_form_service = JSMFormManager(jsm_client=jsm_service)

def get_jsm_tools():
    """Get JSM tools to register with the MCP server."""
    if not jsm_service:
        return []
        
    tools = [
        # Service Desk Tools
        Tool(
            name="jsm_get_service_desks",
            description="Get all service desks available to the user",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "number",
                        "description": "Maximum number of results (1-50)",
                        "default": 10,
                        "minimum": 1,
                        "maximum": 50
                    }
                }
            }
        ),
        Tool(
            name="jsm_get_service_desk",
            description="Get details about a specific service desk",
            inputSchema={
                "type": "object",
                "properties": {
                    "service_desk_id": {
                        "type": "string",
                        "description": "The ID of the service desk"
                    }
                },
                "required": ["service_desk_id"]
            }
        ),
        
        # Request Type Tools
        Tool(
            name="jsm_get_request_types",
            description="Get available request types for a service desk",
            inputSchema={
                "type": "object",
                "properties": {
                    "service_desk_id": {
                        "type": "string",
                        "description": "The ID of the service desk"
                    },
                    "limit": {
                        "type": "number",
                        "description": "Maximum number of results (1-50)",
                        "default": 10,
                        "minimum": 1,
                        "maximum": 50
                    }
                },
                "required": ["service_desk_id"]
            }
        ),
        Tool(
            name="jsm_get_request_type_fields",
            description="Get fields for a request type",
            inputSchema={
                "type": "object",
                "properties": {
                    "service_desk_id": {
                        "type": "string",
                        "description": "The ID of the service desk"
                    },
                    "request_type_id": {
                        "type": "string",
                        "description": "The ID of the request type"
                    }
                },
                "required": ["service_desk_id", "request_type_id"]
            }
        ),
        
        # Customer Request Tools
        Tool(
            name="jsm_create_customer_request",
            description="Create a customer request (service desk ticket)",
            inputSchema={
                "type": "object",
                "properties": {
                    "service_desk_id": {
                        "type": "string",
                        "description": "The ID of the service desk"
                    },
                    "request_type_id": {
                        "type": "string",
                        "description": "The ID of the request type"
                    },
                    "summary": {
                        "type": "string",
                        "description": "The summary of the request"
                    },
                    "description": {
                        "type": "string",
                        "description": "The description of the request"
                    },
                    "request_field_values": {
                        "type": "object",
                        "description": "Dictionary of field values for the request"
                    },
                    "attachments": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of attachment IDs to attach to the request"
                    },
                    "name": {
                        "type": "string",
                        "description": "Name value for custom field (if required by the service desk)"
                    },
                    "dept": {
                        "type": "string",
                        "description": "Department value for custom field (if required by the service desk)"
                    }
                },
                "required": ["service_desk_id", "request_type_id", "summary", "description"]
            }
        ),
        Tool(
            name="jsm_get_customer_requests",
            description="Get customer requests with optional filtering",
            inputSchema={
                "type": "object",
                "properties": {
                    "service_desk_id": {
                        "type": "string",
                        "description": "Filter by service desk ID"
                    },
                    "request_type_id": {
                        "type": "string",
                        "description": "Filter by request type ID"
                    },
                    "status": {
                        "type": "string",
                        "description": "Filter by request status"
                    },
                    "limit": {
                        "type": "number",
                        "description": "Maximum number of results (1-50)",
                        "default": 10,
                        "minimum": 1,
                        "maximum": 50
                    },
                    "expand": {
                        "type": "string",
                        "description": "Fields to expand in the response"
                    }
                }
            }
        ),
        Tool(
            name="jsm_get_customer_request",
            description="Get details about a specific customer request",
            inputSchema={
                "type": "object",
                "properties": {
                    "issue_id_or_key": {
                        "type": "string",
                        "description": "The ID or key of the issue"
                    },
                    "expand": {
                        "type": "string",
                        "description": "Fields to expand in the response"
                    }
                },
                "required": ["issue_id_or_key"]
            }
        ),
        
        # Request Participants Tools
        Tool(
            name="jsm_get_request_participants",
            description="Get participants for a customer request",
            inputSchema={
                "type": "object",
                "properties": {
                    "issue_id_or_key": {
                        "type": "string",
                        "description": "The ID or key of the issue"
                    }
                },
                "required": ["issue_id_or_key"]
            }
        ),
        Tool(
            name="jsm_add_request_participant",
            description="Add a participant to a customer request",
            inputSchema={
                "type": "object",
                "properties": {
                    "issue_id_or_key": {
                        "type": "string",
                        "description": "The ID or key of the issue"
                    },
                    "account_id": {
                        "type": "string",
                        "description": "The account ID of the user to add"
                    }
                },
                "required": ["issue_id_or_key", "account_id"]
            }
        ),
        Tool(
            name="jsm_remove_request_participant",
            description="Remove a participant from a customer request",
            inputSchema={
                "type": "object",
                "properties": {
                    "issue_id_or_key": {
                        "type": "string",
                        "description": "The ID or key of the issue"
                    },
                    "account_id": {
                        "type": "string",
                        "description": "The account ID of the user to remove"
                    }
                },
                "required": ["issue_id_or_key", "account_id"]
            }
        ),
        
        # SLA Tools
        Tool(
            name="jsm_get_request_sla",
            description="Get SLA information for a request",
            inputSchema={
                "type": "object",
                "properties": {
                    "issue_id_or_key": {
                        "type": "string",
                        "description": "The ID or key of the issue"
                    }
                },
                "required": ["issue_id_or_key"]
            }
        ),
        
        # Queues Tools
        Tool(
            name="jsm_get_queues",
            description="Get queues for a service desk",
            inputSchema={
                "type": "object",
                "properties": {
                    "service_desk_id": {
                        "type": "string",
                        "description": "The ID of the service desk"
                    },
                    "limit": {
                        "type": "number",
                        "description": "Maximum number of results (1-50)",
                        "default": 10,
                        "minimum": 1,
                        "maximum": 50
                    }
                },
                "required": ["service_desk_id"]
            }
        ),
        Tool(
            name="jsm_get_queue_issues",
            description="Get issues in a queue",
            inputSchema={
                "type": "object",
                "properties": {
                    "service_desk_id": {
                        "type": "string",
                        "description": "The ID of the service desk"
                    },
                    "queue_id": {
                        "type": "string",
                        "description": "The ID of the queue"
                    },
                    "limit": {
                        "type": "number",
                        "description": "Maximum number of results (1-50)",
                        "default": 10,
                        "minimum": 1,
                        "maximum": 50
                    }
                },
                "required": ["service_desk_id", "queue_id"]
            }
        ),
        
        # Organizations Tools
        Tool(
            name="jsm_get_organizations",
            description="Get organizations",
            inputSchema={
                "type": "object",
                "properties": {
                    "service_desk_id": {
                        "type": "string",
                        "description": "Filter by service desk ID"
                    },
                    "limit": {
                        "type": "number",
                        "description": "Maximum number of results (1-50)",
                        "default": 10,
                        "minimum": 1,
                        "maximum": 50
                    }
                }
            }
        ),
        Tool(
            name="jsm_add_organization",
            description="Add an organization to a service desk",
            inputSchema={
                "type": "object",
                "properties": {
                    "service_desk_id": {
                        "type": "string",
                        "description": "The ID of the service desk"
                    },
                    "organization_id": {
                        "type": "string",
                        "description": "The ID of the organization to add"
                    }
                },
                "required": ["service_desk_id", "organization_id"]
            }
        ),
        Tool(
            name="jsm_remove_organization",
            description="Remove an organization from a service desk",
            inputSchema={
                "type": "object",
                "properties": {
                    "service_desk_id": {
                        "type": "string",
                        "description": "The ID of the service desk"
                    },
                    "organization_id": {
                        "type": "string",
                        "description": "The ID of the organization to remove"
                    }
                },
                "required": ["service_desk_id", "organization_id"]
            }
        ),
        
        # Basic Approvals Tools
        Tool(
            name="jsm_get_request_approvals",
            description="Get approvals for a request",
            inputSchema={
                "type": "object",
                "properties": {
                    "issue_id_or_key": {
                        "type": "string",
                        "description": "The ID or key of the issue"
                    },
                    "expand": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Fields to expand in the response"
                    }
                },
                "required": ["issue_id_or_key"]
            }
        ),
        Tool(
            name="jsm_get_approval_details",
            description="Get detailed information about a specific approval",
            inputSchema={
                "type": "object",
                "properties": {
                    "issue_id_or_key": {
                        "type": "string",
                        "description": "The ID or key of the issue"
                    },
                    "approval_id": {
                        "type": "string",
                        "description": "The ID of the approval"
                    }
                },
                "required": ["issue_id_or_key", "approval_id"]
            }
        ),
        Tool(
            name="jsm_answer_approval",
            description="Answer an approval for a request",
            inputSchema={
                "type": "object",
                "properties": {
                    "issue_id_or_key": {
                        "type": "string",
                        "description": "The ID or key of the issue"
                    },
                    "approval_id": {
                        "type": "string",
                        "description": "The ID of the approval"
                    },
                    "decision": {
                        "type": "string",
                        "description": "The decision (approve or decline)",
                        "enum": ["approve", "decline"]
                    },
                    "comment": {
                        "type": "string",
                        "description": "Optional comment explaining the decision"
                    }
                },
                "required": ["issue_id_or_key", "approval_id", "decision"]
            }
        ),
        
        # Advanced Approval Tools
        Tool(
            name="jsm_create_approval_level",
            description="Create a new approval level for an issue",
            inputSchema={
                "type": "object",
                "properties": {
                    "issue_id_or_key": {
                        "type": "string",
                        "description": "The ID or key of the issue"
                    },
                    "approver_account_ids": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of account IDs for approvers"
                    },
                    "level_name": {
                        "type": "string",
                        "description": "Name for this approval level"
                    },
                    "approval_type": {
                        "type": "string",
                        "description": "Type of approval required",
                        "enum": ["any_approver", "all_approvers"],
                        "default": "any_approver"
                    }
                },
                "required": ["issue_id_or_key", "approver_account_ids", "level_name"]
            }
        ),
        Tool(
            name="jsm_get_approval_levels",
            description="Get all approval levels for an issue",
            inputSchema={
                "type": "object",
                "properties": {
                    "issue_id_or_key": {
                        "type": "string",
                        "description": "The ID or key of the issue"
                    }
                },
                "required": ["issue_id_or_key"]
            }
        ),
        Tool(
            name="jsm_get_approval_metrics",
            description="Get approval metrics for a service desk",
            inputSchema={
                "type": "object",
                "properties": {
                    "service_desk_id": {
                        "type": "string",
                        "description": "The ID of the service desk"
                    },
                    "time_period": {
                        "type": "string",
                        "description": "Time period for metrics (e.g., '1d', '1w', '1m')",
                        "default": "1m"
                    }
                },
                "required": ["service_desk_id"]
            }
        )
    ]
    
    # Knowledge Base Tools
    if jsm_kb_service:
        tools.extend([
            Tool(
                name="jsm_get_knowledge_bases",
                description="Get all knowledge bases available to the user",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "limit": {
                            "type": "number",
                            "description": "Maximum number of results (1-50)",
                            "default": 10,
                            "minimum": 1,
                            "maximum": 50
                        }
                    }
                }
            ),
            Tool(
                name="jsm_get_knowledge_base",
                description="Get details about a specific knowledge base",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "knowledge_base_id": {
                            "type": "string",
                            "description": "The ID of the knowledge base"
                        }
                    },
                    "required": ["knowledge_base_id"]
                }
            ),
            Tool(
                name="jsm_search_articles",
                description="Search knowledge base articles",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query string"
                        },
                        "knowledge_base_id": {
                            "type": "string",
                            "description": "Optional knowledge base ID to scope the search"
                        },
                        "limit": {
                            "type": "number",
                            "description": "Maximum number of results (1-50)",
                            "default": 10,
                            "minimum": 1,
                            "maximum": 50
                        }
                    },
                    "required": ["query"]
                }
            ),
            Tool(
                name="jsm_get_article",
                description="Get details about a specific knowledge base article",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "article_id": {
                            "type": "string",
                            "description": "The ID of the article"
                        }
                    },
                    "required": ["article_id"]
                }
            ),
            Tool(
                name="jsm_create_article",
                description="Create a new knowledge base article",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "knowledge_base_id": {
                            "type": "string",
                            "description": "The ID of the knowledge base"
                        },
                        "title": {
                            "type": "string",
                            "description": "Article title"
                        },
                        "body": {
                            "type": "string",
                            "description": "Article body content (HTML format)"
                        },
                        "draft": {
                            "type": "boolean",
                            "description": "Whether to create as draft",
                            "default": False
                        },
                        "labels": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Optional list of labels to apply to the article"
                        }
                    },
                    "required": ["knowledge_base_id", "title", "body"]
                }
            ),
            Tool(
                name="jsm_update_article",
                description="Update an existing knowledge base article",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "article_id": {
                            "type": "string",
                            "description": "The ID of the article to update"
                        },
                        "title": {
                            "type": "string",
                            "description": "Optional new article title"
                        },
                        "body": {
                            "type": "string",
                            "description": "Optional new article body content (HTML format)"
                        },
                        "draft": {
                            "type": "boolean",
                            "description": "Optional new draft status"
                        },
                        "labels": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Optional new list of labels"
                        }
                    },
                    "required": ["article_id"]
                }
            ),
            Tool(
                name="jsm_delete_article",
                description="Delete a knowledge base article",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "article_id": {
                            "type": "string",
                            "description": "The ID of the article to delete"
                        }
                    },
                    "required": ["article_id"]
                }
            ),
            Tool(
                name="jsm_get_linked_articles",
                description="Get articles linked to a customer request",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "issue_id_or_key": {
                            "type": "string",
                            "description": "The ID or key of the issue"
                        },
                        "limit": {
                            "type": "number",
                            "description": "Maximum number of results (1-50)",
                            "default": 10,
                            "minimum": 1,
                            "maximum": 50
                        }
                    },
                    "required": ["issue_id_or_key"]
                }
            ),
            Tool(
                name="jsm_link_article_to_request",
                description="Link a knowledge base article to a customer request",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "issue_id_or_key": {
                            "type": "string",
                            "description": "The ID or key of the issue"
                        },
                        "article_id": {
                            "type": "string",
                            "description": "The ID of the article to link"
                        }
                    },
                    "required": ["issue_id_or_key", "article_id"]
                }
            ),
            Tool(
                name="jsm_unlink_article_from_request",
                description="Unlink a knowledge base article from a customer request",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "issue_id_or_key": {
                            "type": "string",
                            "description": "The ID or key of the issue"
                        },
                        "article_id": {
                            "type": "string",
                            "description": "The ID of the article to unlink"
                        }
                    },
                    "required": ["issue_id_or_key", "article_id"]
                }
            ),
            Tool(
                name="jsm_suggest_articles",
                description="Get article suggestions for a service desk request type",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "service_desk_id": {
                            "type": "string",
                            "description": "The ID of the service desk"
                        },
                        "request_type_id": {
                            "type": "string",
                            "description": "The ID of the request type"
                        },
                        "query": {
                            "type": "string",
                            "description": "Search query for relevant articles"
                        },
                        "limit": {
                            "type": "number",
                            "description": "Maximum number of results (1-50)",
                            "default": 5,
                            "minimum": 1,
                            "maximum": 50
                        }
                    },
                    "required": ["service_desk_id", "request_type_id", "query"]
                }
            )
        ])
    
    # Advanced Queue Management Tools
    if jsm_queue_service:
        tools.extend([
            Tool(
                name="jsm_get_queues_with_count",
                description="Get queues for a service desk with issue counts",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "service_desk_id": {
                            "type": "string",
                            "description": "The ID of the service desk"
                        },
                        "include_count": {
                            "type": "boolean",
                            "description": "Whether to include issue count for each queue",
                            "default": True
                        },
                        "limit": {
                            "type": "number",
                            "description": "Maximum number of results (1-50)",
                            "default": 10,
                            "minimum": 1,
                            "maximum": 50
                        }
                    },
                    "required": ["service_desk_id"]
                }
            ),
            Tool(
                name="jsm_get_queue_issues_advanced",
                description="Get issues in a queue with advanced filtering options",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "service_desk_id": {
                            "type": "string",
                            "description": "The ID of the service desk"
                        },
                        "queue_id": {
                            "type": "string",
                            "description": "The ID of the queue"
                        },
                        "order_by": {
                            "type": "string",
                            "description": "Field to order results by (e.g., 'created', '-priority')"
                        },
                        "expand": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of fields to expand in the response"
                        },
                        "limit": {
                            "type": "number",
                            "description": "Maximum number of results (1-50)",
                            "default": 10,
                            "minimum": 1,
                            "maximum": 50
                        }
                    },
                    "required": ["service_desk_id", "queue_id"]
                }
            ),
            Tool(
                name="jsm_create_custom_queue",
                description="Create a custom queue with JQL filter for a service desk",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "service_desk_id": {
                            "type": "string",
                            "description": "The ID of the service desk"
                        },
                        "name": {
                            "type": "string",
                            "description": "Queue name"
                        },
                        "jql_filter": {
                            "type": "string",
                            "description": "JQL query to filter issues in the queue"
                        },
                        "description": {
                            "type": "string",
                            "description": "Optional queue description"
                        }
                    },
                    "required": ["service_desk_id", "name", "jql_filter"]
                }
            ),
            Tool(
                name="jsm_update_custom_queue",
                description="Update a custom queue",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "filter_id": {
                            "type": "string",
                            "description": "The ID of the filter/queue to update"
                        },
                        "name": {
                            "type": "string",
                            "description": "Optional new queue name"
                        },
                        "jql_filter": {
                            "type": "string",
                            "description": "Optional new JQL query"
                        },
                        "description": {
                            "type": "string",
                            "description": "Optional new description"
                        }
                    },
                    "required": ["filter_id"]
                }
            ),
            Tool(
                name="jsm_delete_custom_queue",
                description="Delete a custom queue",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "filter_id": {
                            "type": "string",
                            "description": "The ID of the filter/queue to delete"
                        }
                    },
                    "required": ["filter_id"]
                }
            ),
            Tool(
                name="jsm_assign_issue_to_queue",
                description="Assign an issue to a specific queue",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "issue_id_or_key": {
                            "type": "string",
                            "description": "The ID or key of the issue"
                        },
                        "queue_id": {
                            "type": "string",
                            "description": "The ID of the target queue"
                        }
                    },
                    "required": ["issue_id_or_key", "queue_id"]
                }
            ),
            Tool(
                name="jsm_get_queue_metrics",
                description="Get performance metrics for a queue",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "service_desk_id": {
                            "type": "string",
                            "description": "The ID of the service desk"
                        },
                        "queue_id": {
                            "type": "string",
                            "description": "The ID of the queue"
                        },
                        "time_period": {
                            "type": "string",
                            "description": "Time period for metrics (e.g., '1d', '1w', '1m')",
                            "default": "1w"
                        }
                    },
                    "required": ["service_desk_id", "queue_id"]
                }
            )
        ])
    
    # Form Management Tools
    if jsm_form_service:
        tools.extend([
            Tool(
                name="jsm_get_custom_fields",
                description="Get all custom fields available in the instance",
                inputSchema={
                    "type": "object",
                    "properties": {}
                }
            ),
            Tool(
                name="jsm_create_custom_field",
                description="Create a new custom field for use in JSM forms",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "Name of the custom field"
                        },
                        "description": {
                            "type": "string",
                            "description": "Description of the custom field"
                        },
                        "field_type": {
                            "type": "string",
                            "description": "Type of field",
                            "enum": ["text", "textarea", "select", "multiselect", "datepicker", "datetime", "number", "checkbox", "radio", "url", "userpicker", "multipicker", "cascading"]
                        }
                    },
                    "required": ["name", "description", "field_type"]
                }
            ),
            Tool(
                name="jsm_configure_field_options",
                description="Configure options for a select/multiselect field",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "field_id": {
                            "type": "string",
                            "description": "The ID of the custom field"
                        },
                        "options": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "value": {
                                        "type": "string",
                                        "description": "Option value"
                                    },
                                    "disabled": {
                                        "type": "boolean",
                                        "description": "Whether the option is disabled"
                                    }
                                },
                                "required": ["value"]
                            },
                            "description": "List of option configurations"
                        }
                    },
                    "required": ["field_id", "options"]
                }
            ),
            Tool(
                name="jsm_get_form_configuration",
                description="Get the form configuration for a request type",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "service_desk_id": {
                            "type": "string",
                            "description": "The ID of the service desk"
                        },
                        "request_type_id": {
                            "type": "string",
                            "description": "The ID of the request type"
                        }
                    },
                    "required": ["service_desk_id", "request_type_id"]
                }
            ),
            Tool(
                name="jsm_update_form_field_order",
                description="Update the order of fields in a request type form",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "service_desk_id": {
                            "type": "string",
                            "description": "The ID of the service desk"
                        },
                        "request_type_id": {
                            "type": "string",
                            "description": "The ID of the request type"
                        },
                        "field_order": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of field IDs in desired order"
                        }
                    },
                    "required": ["service_desk_id", "request_type_id", "field_order"]
                }
            ),
            Tool(
                name="jsm_configure_field_requirements",
                description="Configure field requirements for a request type form",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "service_desk_id": {
                            "type": "string",
                            "description": "The ID of the service desk"
                        },
                        "request_type_id": {
                            "type": "string",
                            "description": "The ID of the request type"
                        },
                        "field_requirements": {
                            "type": "object",
                            "description": "Dictionary mapping field IDs to requirement configs"
                        }
                    },
                    "required": ["service_desk_id", "request_type_id", "field_requirements"]
                }
            ),
            Tool(
                name="jsm_validate_form_data",
                description="Validate form data against field requirements",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "service_desk_id": {
                            "type": "string",
                            "description": "The ID of the service desk"
                        },
                        "request_type_id": {
                            "type": "string",
                            "description": "The ID of the request type"
                        },
                        "form_data": {
                            "type": "object",
                            "description": "Dictionary of form field values"
                        }
                    },
                    "required": ["service_desk_id", "request_type_id", "form_data"]
                }
            )
        ])
    
    return tools

def handle_jsm_tool_call(name: str, arguments: dict):
    """Handle JSM tool calls."""
    if not jsm_service:
        raise ValueError("JSM service is not available. Please provide JSM credentials.")
    
    try:
        # Service Desk Operations
        if name == "jsm_get_service_desks":
            limit = min(int(arguments.get("limit", 10)), 50)
            result = jsm_service.get_service_desks(limit=limit)
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
        elif name == "jsm_get_service_desk":
            service_desk_id = arguments["service_desk_id"]
            result = jsm_service.get_service_desk(service_desk_id=service_desk_id)
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
        # Request Type Operations
        elif name == "jsm_get_request_types":
            service_desk_id = arguments["service_desk_id"]
            limit = min(int(arguments.get("limit", 10)), 50)
            result = jsm_service.get_request_types(
                service_desk_id=service_desk_id,
                limit=limit
            )
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
        elif name == "jsm_get_request_type_fields":
            service_desk_id = arguments["service_desk_id"]
            request_type_id = arguments["request_type_id"]
            result = jsm_service.get_request_type_fields(
                service_desk_id=service_desk_id,
                request_type_id=request_type_id
            )
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
        # Customer Request Operations
        elif name == "jsm_create_customer_request":
            service_desk_id = arguments["service_desk_id"]
            request_type_id = arguments["request_type_id"]
            summary = arguments["summary"]
            description = arguments["description"]
            request_field_values = arguments.get("request_field_values")
            attachments = arguments.get("attachments")
            name = arguments.get("name")
            dept = arguments.get("dept")
            
            result = jsm_service.create_customer_request(
                service_desk_id=service_desk_id,
                request_type_id=request_type_id,
                summary=summary,
                description=description,
                request_field_values=request_field_values,
                attachments=attachments,
                name=name,
                dept=dept
            )
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
        elif name == "jsm_get_customer_requests":
            service_desk_id = arguments.get("service_desk_id")
            request_type_id = arguments.get("request_type_id")
            status = arguments.get("status")
            limit = min(int(arguments.get("limit", 10)), 50)
            expand = arguments.get("expand")
            
            result = jsm_service.get_customer_requests(
                service_desk_id=service_desk_id,
                request_type_id=request_type_id,
                status=status,
                limit=limit,
                expand=expand
            )
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
        elif name == "jsm_get_customer_request":
            issue_id_or_key = arguments["issue_id_or_key"]
            expand = arguments.get("expand")
            
            result = jsm_service.get_customer_request(
                issue_id_or_key=issue_id_or_key,
                expand=expand
            )
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
        # Request Participants Operations
        elif name == "jsm_get_request_participants":
            issue_id_or_key = arguments["issue_id_or_key"]
            
            result = jsm_service.get_request_participants(
                issue_id_or_key=issue_id_or_key
            )
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
        elif name == "jsm_add_request_participant":
            issue_id_or_key = arguments["issue_id_or_key"]
            account_id = arguments["account_id"]
            
            result = jsm_service.add_request_participant(
                issue_id_or_key=issue_id_or_key,
                account_id=account_id
            )
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
        elif name == "jsm_remove_request_participant":
            issue_id_or_key = arguments["issue_id_or_key"]
            account_id = arguments["account_id"]
            
            result = jsm_service.remove_request_participant(
                issue_id_or_key=issue_id_or_key,
                account_id=account_id
            )
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
        # SLA Operations
        elif name == "jsm_get_request_sla":
            issue_id_or_key = arguments["issue_id_or_key"]
            
            result = jsm_service.get_request_sla(
                issue_id_or_key=issue_id_or_key
            )
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
        # Queues Operations
        elif name == "jsm_get_queues":
            service_desk_id = arguments["service_desk_id"]
            limit = min(int(arguments.get("limit", 10)), 50)
            
            result = jsm_service.get_queues(
                service_desk_id=service_desk_id,
                limit=limit
            )
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
        elif name == "jsm_get_queue_issues":
            service_desk_id = arguments["service_desk_id"]
            queue_id = arguments["queue_id"]
            limit = min(int(arguments.get("limit", 10)), 50)
            
            result = jsm_service.get_queue_issues(
                service_desk_id=service_desk_id,
                queue_id=queue_id,
                limit=limit
            )
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
        # Organizations Operations
        elif name == "jsm_get_organizations":
            service_desk_id = arguments.get("service_desk_id")
            limit = min(int(arguments.get("limit", 10)), 50)
            
            result = jsm_service.get_organizations(
                service_desk_id=service_desk_id,
                limit=limit
            )
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
        elif name == "jsm_add_organization":
            service_desk_id = arguments["service_desk_id"]
            organization_id = arguments["organization_id"]
            
            result = jsm_service.add_organization(
                service_desk_id=service_desk_id,
                organization_id=organization_id
            )
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
        elif name == "jsm_remove_organization":
            service_desk_id = arguments["service_desk_id"]
            organization_id = arguments["organization_id"]
            
            result = jsm_service.remove_organization(
                service_desk_id=service_desk_id,
                organization_id=organization_id
            )
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
        # Basic Approvals Operations
        elif name == "jsm_get_request_approvals":
            issue_id_or_key = arguments["issue_id_or_key"]
            expand = arguments.get("expand")
            
            if jsm_approval_service and expand:
                result = jsm_approval_service.get_request_approvals(
                    issue_id_or_key=issue_id_or_key,
                    expand=expand
                )
            else:
                result = jsm_service.get_request_approvals(
                    issue_id_or_key=issue_id_or_key
                )
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
        elif name == "jsm_get_approval_details":
            issue_id_or_key = arguments["issue_id_or_key"]
            approval_id = arguments["approval_id"]
            
            if jsm_approval_service:
                result = jsm_approval_service.get_approval_details(
                    issue_id_or_key=issue_id_or_key,
                    approval_id=approval_id
                )
            else:
                result = jsm_service.get_request_approvals(
                    issue_id_or_key=issue_id_or_key
                )
                # Filter to just the requested approval
                if "values" in result:
                    for approval in result["values"]:
                        if approval.get("id") == approval_id:
                            result = approval
                            break
                        
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
        elif name == "jsm_answer_approval":
            issue_id_or_key = arguments["issue_id_or_key"]
            approval_id = arguments["approval_id"]
            decision = arguments["decision"]
            comment = arguments.get("comment")
            
            if jsm_approval_service and comment:
                result = jsm_approval_service.answer_approval(
                    issue_id_or_key=issue_id_or_key,
                    approval_id=approval_id,
                    decision=decision,
                    comment=comment
                )
            else:
                result = jsm_service.answer_approval(
                    issue_id_or_key=issue_id_or_key,
                    approval_id=approval_id,
                    decision=decision
                )
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        # Advanced Approval Operations
        elif name == "jsm_create_approval_level" and jsm_approval_service:
            issue_id_or_key = arguments["issue_id_or_key"]
            approver_account_ids = arguments["approver_account_ids"]
            level_name = arguments["level_name"]
            approval_type = arguments.get("approval_type", "any_approver")
            
            result = jsm_approval_service.create_approval_level(
                issue_id_or_key=issue_id_or_key,
                approver_account_ids=approver_account_ids,
                level_name=level_name,
                approval_type=approval_type
            )
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
        elif name == "jsm_get_approval_levels" and jsm_approval_service:
            issue_id_or_key = arguments["issue_id_or_key"]
            
            result = jsm_approval_service.get_approval_levels(
                issue_id_or_key=issue_id_or_key
            )
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
        elif name == "jsm_get_approval_metrics" and jsm_approval_service:
            service_desk_id = arguments["service_desk_id"]
            time_period = arguments.get("time_period", "1m")
            
            result = jsm_approval_service.get_approval_metrics(
                service_desk_id=service_desk_id,
                time_period=time_period
            )
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
        # Knowledge Base Operations
        elif name == "jsm_get_knowledge_bases" and jsm_kb_service:
            limit = min(int(arguments.get("limit", 10)), 50)
            
            result = jsm_kb_service.get_knowledge_bases(
                limit=limit
            )
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
        elif name == "jsm_get_knowledge_base" and jsm_kb_service:
            knowledge_base_id = arguments["knowledge_base_id"]
            
            result = jsm_kb_service.get_knowledge_base(
                knowledge_base_id=knowledge_base_id
            )
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
        elif name == "jsm_search_articles" and jsm_kb_service:
            query = arguments["query"]
            knowledge_base_id = arguments.get("knowledge_base_id")
            limit = min(int(arguments.get("limit", 10)), 50)
            
            result = jsm_kb_service.search_articles(
                query=query,
                knowledge_base_id=knowledge_base_id,
                limit=limit
            )
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
        elif name == "jsm_get_article" and jsm_kb_service:
            article_id = arguments["article_id"]
            
            result = jsm_kb_service.get_article(
                article_id=article_id
            )
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
        elif name == "jsm_create_article" and jsm_kb_service:
            knowledge_base_id = arguments["knowledge_base_id"]
            title = arguments["title"]
            body = arguments["body"]
            draft = arguments.get("draft", False)
            labels = arguments.get("labels")
            
            result = jsm_kb_service.create_article(
                knowledge_base_id=knowledge_base_id,
                title=title,
                body=body,
                draft=draft,
                labels=labels
            )
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
        elif name == "jsm_update_article" and jsm_kb_service:
            article_id = arguments["article_id"]
            title = arguments.get("title")
            body = arguments.get("body")
            draft = arguments.get("draft")
            labels = arguments.get("labels")
            
            result = jsm_kb_service.update_article(
                article_id=article_id,
                title=title,
                body=body,
                draft=draft,
                labels=labels
            )
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
        elif name == "jsm_delete_article" and jsm_kb_service:
            article_id = arguments["article_id"]
            
            result = jsm_kb_service.delete_article(
                article_id=article_id
            )
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
        elif name == "jsm_get_linked_articles" and jsm_kb_service:
            issue_id_or_key = arguments["issue_id_or_key"]
            limit = min(int(arguments.get("limit", 10)), 50)
            
            result = jsm_kb_service.get_linked_articles(
                issue_id_or_key=issue_id_or_key,
                limit=limit
            )
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
        elif name == "jsm_link_article_to_request" and jsm_kb_service:
            issue_id_or_key = arguments["issue_id_or_key"]
            article_id = arguments["article_id"]
            
            result = jsm_kb_service.link_article_to_request(
                issue_id_or_key=issue_id_or_key,
                article_id=article_id
            )
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
        elif name == "jsm_unlink_article_from_request" and jsm_kb_service:
            issue_id_or_key = arguments["issue_id_or_key"]
            article_id = arguments["article_id"]
            
            result = jsm_kb_service.unlink_article_from_request(
                issue_id_or_key=issue_id_or_key,
                article_id=article_id
            )
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
        elif name == "jsm_suggest_articles" and jsm_kb_service:
            service_desk_id = arguments["service_desk_id"]
            request_type_id = arguments["request_type_id"]
            query = arguments["query"]
            limit = min(int(arguments.get("limit", 5)), 50)
            
            result = jsm_kb_service.suggest_articles(
                service_desk_id=service_desk_id,
                request_type_id=request_type_id,
                query=query,
                limit=limit
            )
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
        # Advanced Queue Management Operations
        elif name == "jsm_get_queues_with_count" and jsm_queue_service:
            service_desk_id = arguments["service_desk_id"]
            include_count = arguments.get("include_count", True)
            limit = min(int(arguments.get("limit", 10)), 50)
            
            result = jsm_queue_service.get_queues(
                service_desk_id=service_desk_id,
                include_count=include_count,
                limit=limit
            )
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
        elif name == "jsm_get_queue_issues_advanced" and jsm_queue_service:
            service_desk_id = arguments["service_desk_id"]
            queue_id = arguments["queue_id"]
            order_by = arguments.get("order_by")
            expand = arguments.get("expand")
            limit = min(int(arguments.get("limit", 10)), 50)
            
            result = jsm_queue_service.get_queue_issues(
                service_desk_id=service_desk_id,
                queue_id=queue_id,
                order_by=order_by,
                expand=expand,
                limit=limit
            )
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
        elif name == "jsm_create_custom_queue" and jsm_queue_service:
            service_desk_id = arguments["service_desk_id"]
            name = arguments["name"]
            jql_filter = arguments["jql_filter"]
            description = arguments.get("description")
            
            result = jsm_queue_service.create_custom_queue(
                service_desk_id=service_desk_id,
                name=name,
                jql_filter=jql_filter,
                description=description
            )
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
        elif name == "jsm_update_custom_queue" and jsm_queue_service:
            filter_id = arguments["filter_id"]
            name = arguments.get("name")
            jql_filter = arguments.get("jql_filter")
            description = arguments.get("description")
            
            result = jsm_queue_service.update_custom_queue(
                filter_id=filter_id,
                name=name,
                jql_filter=jql_filter,
                description=description
            )
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
        elif name == "jsm_delete_custom_queue" and jsm_queue_service:
            filter_id = arguments["filter_id"]
            
            result = jsm_queue_service.delete_custom_queue(
                filter_id=filter_id
            )
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
        elif name == "jsm_assign_issue_to_queue" and jsm_queue_service:
            issue_id_or_key = arguments["issue_id_or_key"]
            queue_id = arguments["queue_id"]
            
            result = jsm_queue_service.assign_issue_to_queue(
                issue_id_or_key=issue_id_or_key,
                queue_id=queue_id
            )
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
        elif name == "jsm_get_queue_metrics" and jsm_queue_service:
            service_desk_id = arguments["service_desk_id"]
            queue_id = arguments["queue_id"]
            time_period = arguments.get("time_period", "1w")
            
            result = jsm_queue_service.get_queue_metrics(
                service_desk_id=service_desk_id,
                queue_id=queue_id,
                time_period=time_period
            )
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
        # Form Management Operations
        elif name == "jsm_get_custom_fields" and jsm_form_service:
            result = jsm_form_service.get_custom_fields()
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
        elif name == "jsm_create_custom_field" and jsm_form_service:
            name = arguments["name"]
            description = arguments["description"]
            field_type = arguments["field_type"]
            
            result = jsm_form_service.create_custom_field(
                name=name,
                description=description,
                field_type=field_type
            )
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
        elif name == "jsm_configure_field_options" and jsm_form_service:
            field_id = arguments["field_id"]
            options = arguments["options"]
            
            result = jsm_form_service.configure_field_options(
                field_id=field_id,
                options=options
            )
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
        elif name == "jsm_get_form_configuration" and jsm_form_service:
            service_desk_id = arguments["service_desk_id"]
            request_type_id = arguments["request_type_id"]
            
            result = jsm_form_service.get_form_configuration(
                service_desk_id=service_desk_id,
                request_type_id=request_type_id
            )
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
        elif name == "jsm_update_form_field_order" and jsm_form_service:
            service_desk_id = arguments["service_desk_id"]
            request_type_id = arguments["request_type_id"]
            field_order = arguments["field_order"]
            
            result = jsm_form_service.update_form_field_order(
                service_desk_id=service_desk_id,
                request_type_id=request_type_id,
                field_order=field_order
            )
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
        elif name == "jsm_configure_field_requirements" and jsm_form_service:
            service_desk_id = arguments["service_desk_id"]
            request_type_id = arguments["request_type_id"]
            field_requirements = arguments["field_requirements"]
            
            result = jsm_form_service.configure_field_requirements(
                service_desk_id=service_desk_id,
                request_type_id=request_type_id,
                field_requirements=field_requirements
            )
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
        elif name == "jsm_validate_form_data" and jsm_form_service:
            service_desk_id = arguments["service_desk_id"]
            request_type_id = arguments["request_type_id"]
            form_data = arguments["form_data"]
            
            result = jsm_form_service.validate_form_data(
                service_desk_id=service_desk_id,
                request_type_id=request_type_id,
                form_data=form_data
            )
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
        # Unknown tool
        raise ValueError(f"Unknown JSM tool: {name}")
            
    except Exception as e:
        logger.error(f"JSM tool execution error: {str(e)}")
        raise RuntimeError(f"JSM tool execution failed: {str(e)}")