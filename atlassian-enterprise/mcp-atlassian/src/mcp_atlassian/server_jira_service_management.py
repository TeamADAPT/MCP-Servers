"""
Jira Service Management (JSM) Server Integration Module

This module provides integration between the MCP server and JSM functionality,
including service desks, requests, approvals, knowledge base, and queues.
"""

import json
import logging
import os
from typing import Dict, List, Optional, Any, Union

from mcp.types import Tool

from .jsm import JiraServiceManager
from .jsm_knowledge_base import JSMKnowledgeBase
from .jsm_queue import JSMQueueManager
from .jsm_approvals import JSMApprovalManager
from .jsm_forms import JSMFormManager
from .feature_flags import is_enabled

logger = logging.getLogger(__name__)

# Check if JSM is available
def get_jsm_available() -> bool:
    """
    Check if JSM client can be initialized.

    Returns:
        True if JSM credentials are available
    """
    # Check for JSM or Jira credentials
    jsm_url = os.environ.get("JSM_URL") or os.environ.get("JIRA_URL")
    jsm_username = os.environ.get("JSM_USERNAME") or os.environ.get("JIRA_USERNAME")
    jsm_api_token = os.environ.get("JSM_API_TOKEN") or os.environ.get("JIRA_API_TOKEN")
    
    return all([jsm_url, jsm_username, jsm_api_token])

# Initialize services
def initialize_jsm_service() -> Optional[JiraServiceManager]:
    """
    Initialize the JSM client.

    Returns:
        JSM client or None if initialization fails
    """
    if not get_jsm_available():
        return None
        
    try:
        return JiraServiceManager()
    except Exception as e:
        logger.error(f"Error initializing JSM client: {e}")
        return None

# Initialize specialized services if credentials are available
jsm_service = initialize_jsm_service()

jsm_kb_service = JSMKnowledgeBase(jsm_client=jsm_service) if jsm_service and is_enabled("jsm_knowledge_base") else None
jsm_queue_service = JSMQueueManager(jsm_client=jsm_service) if jsm_service and is_enabled("jsm_queue") else None
jsm_approval_service = JSMApprovalManager(jsm_client=jsm_service) if jsm_service and is_enabled("jsm_approvals") else None
jsm_form_service = JSMFormManager(jsm_client=jsm_service) if jsm_service and is_enabled("jsm_forms") else None

def get_jsm_tools() -> List[Tool]:
    """
    Get all JSM tools.

    Returns:
        List of Tool objects
    """
    tools = []
    
    # Basic JSM tools
    if jsm_service:
        tools.extend([
            # Service Desk
            Tool(
                name="jsm_get_service_desks",
                description="Get all service desks",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "start": {"type": "number", "description": "Starting index for pagination"},
                        "limit": {"type": "number", "description": "Maximum number of results to return"}
                    }
                }
            ),
            Tool(
                name="jsm_get_service_desk",
                description="Get details about a specific service desk",
                inputSchema={
                    "type": "object",
                    "required": ["service_desk_id"],
                    "properties": {
                        "service_desk_id": {"type": "string", "description": "Service desk ID"}
                    }
                }
            ),
            
            # Request Types
            Tool(
                name="jsm_get_request_types",
                description="Get request types for a service desk",
                inputSchema={
                    "type": "object",
                    "required": ["service_desk_id"],
                    "properties": {
                        "service_desk_id": {"type": "string", "description": "Service desk ID"},
                        "start": {"type": "number", "description": "Starting index for pagination"},
                        "limit": {"type": "number", "description": "Maximum number of results to return"}
                    }
                }
            ),
            Tool(
                name="jsm_get_request_type_fields",
                description="Get fields for a request type",
                inputSchema={
                    "type": "object",
                    "required": ["service_desk_id", "request_type_id"],
                    "properties": {
                        "service_desk_id": {"type": "string", "description": "Service desk ID"},
                        "request_type_id": {"type": "string", "description": "Request type ID"}
                    }
                }
            ),
            
            # Customer Requests
            Tool(
                name="jsm_create_customer_request",
                description="Create a customer request (service desk ticket)",
                inputSchema={
                    "type": "object",
                    "required": ["service_desk_id", "request_type_id", "summary"],
                    "properties": {
                        "service_desk_id": {"type": "string", "description": "Service desk ID"},
                        "request_type_id": {"type": "string", "description": "Request type ID"},
                        "summary": {"type": "string", "description": "Request summary"},
                        "description": {"type": "string", "description": "Request description"},
                        "custom_fields": {"type": "object", "description": "Custom fields as {field_id: field_value}"}
                    }
                }
            ),
            Tool(
                name="jsm_get_customer_requests",
                description="Get customer requests",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "service_desk_id": {"type": "string", "description": "Optional service desk ID to filter by"},
                        "request_status": {"type": "string", "enum": ["OPEN", "CLOSED"], "description": "Optional status to filter by"},
                        "search_term": {"type": "string", "description": "Optional search term"},
                        "start": {"type": "number", "description": "Starting index for pagination"},
                        "limit": {"type": "number", "description": "Maximum number of results to return"}
                    }
                }
            ),
            Tool(
                name="jsm_get_customer_request",
                description="Get a specific customer request",
                inputSchema={
                    "type": "object",
                    "required": ["request_id"],
                    "properties": {
                        "request_id": {"type": "string", "description": "Request ID"}
                    }
                }
            ),
            
            # Request Participants
            Tool(
                name="jsm_get_request_participants",
                description="Get participants for a request",
                inputSchema={
                    "type": "object",
                    "required": ["request_id"],
                    "properties": {
                        "request_id": {"type": "string", "description": "Request ID"}
                    }
                }
            ),
            Tool(
                name="jsm_add_request_participant",
                description="Add a participant to a request",
                inputSchema={
                    "type": "object",
                    "required": ["request_id", "account_id"],
                    "properties": {
                        "request_id": {"type": "string", "description": "Request ID"},
                        "account_id": {"type": "string", "description": "User account ID"}
                    }
                }
            ),
            Tool(
                name="jsm_remove_request_participant",
                description="Remove a participant from a request",
                inputSchema={
                    "type": "object",
                    "required": ["request_id", "account_id"],
                    "properties": {
                        "request_id": {"type": "string", "description": "Request ID"},
                        "account_id": {"type": "string", "description": "User account ID"}
                    }
                }
            ),
            
            # SLA
            Tool(
                name="jsm_get_request_sla",
                description="Get SLA information for a request",
                inputSchema={
                    "type": "object",
                    "required": ["request_id"],
                    "properties": {
                        "request_id": {"type": "string", "description": "Request ID"}
                    }
                }
            ),
            
            # Organizations
            Tool(
                name="jsm_get_organizations",
                description="Get organizations for the user",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "service_desk_id": {"type": "string", "description": "Optional service desk ID to filter by"}
                    }
                }
            ),
            Tool(
                name="jsm_add_organization",
                description="Add an organization to a service desk",
                inputSchema={
                    "type": "object",
                    "required": ["service_desk_id", "organization_id"],
                    "properties": {
                        "service_desk_id": {"type": "string", "description": "Service desk ID"},
                        "organization_id": {"type": "string", "description": "Organization ID"}
                    }
                }
            ),
            Tool(
                name="jsm_remove_organization",
                description="Remove an organization from a service desk",
                inputSchema={
                    "type": "object",
                    "required": ["service_desk_id", "organization_id"],
                    "properties": {
                        "service_desk_id": {"type": "string", "description": "Service desk ID"},
                        "organization_id": {"type": "string", "description": "Organization ID"}
                    }
                }
            )
        ])
    
    # Knowledge Base tools
    if jsm_kb_service:
        tools.extend([
            # Knowledge Base
            Tool(
                name="jsm_get_knowledge_bases",
                description="Get all knowledge bases",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "start": {"type": "number", "description": "Starting index for pagination"},
                        "limit": {"type": "number", "description": "Maximum number of results to return"}
                    }
                }
            ),
            Tool(
                name="jsm_get_knowledge_base",
                description="Get a specific knowledge base",
                inputSchema={
                    "type": "object",
                    "required": ["knowledge_base_id"],
                    "properties": {
                        "knowledge_base_id": {"type": "string", "description": "Knowledge base ID"}
                    }
                }
            ),
            
            # Articles
            Tool(
                name="jsm_search_articles",
                description="Search for articles",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Optional search query"},
                        "knowledge_base_id": {"type": "string", "description": "Optional knowledge base ID"},
                        "highlight": {"type": "boolean", "description": "Whether to highlight matched terms"},
                        "start": {"type": "number", "description": "Starting index for pagination"},
                        "limit": {"type": "number", "description": "Maximum number of results to return"}
                    }
                }
            ),
            Tool(
                name="jsm_get_article",
                description="Get a specific article",
                inputSchema={
                    "type": "object",
                    "required": ["article_id"],
                    "properties": {
                        "article_id": {"type": "string", "description": "Article ID"}
                    }
                }
            ),
            Tool(
                name="jsm_create_article",
                description="Create a new article",
                inputSchema={
                    "type": "object",
                    "required": ["knowledge_base_id", "title", "body"],
                    "properties": {
                        "knowledge_base_id": {"type": "string", "description": "Knowledge base ID"},
                        "title": {"type": "string", "description": "Article title"},
                        "body": {"type": "string", "description": "Article body (HTML format)"},
                        "draft": {"type": "boolean", "description": "Whether to create as draft"},
                        "labels": {"type": "array", "items": {"type": "string"}, "description": "Optional list of labels"}
                    }
                }
            ),
            Tool(
                name="jsm_update_article",
                description="Update an article",
                inputSchema={
                    "type": "object",
                    "required": ["article_id"],
                    "properties": {
                        "article_id": {"type": "string", "description": "Article ID"},
                        "title": {"type": "string", "description": "Optional new title"},
                        "body": {"type": "string", "description": "Optional new body"},
                        "draft": {"type": "boolean", "description": "Optional draft status"},
                        "labels": {"type": "array", "items": {"type": "string"}, "description": "Optional new labels"}
                    }
                }
            ),
            Tool(
                name="jsm_delete_article",
                description="Delete an article",
                inputSchema={
                    "type": "object",
                    "required": ["article_id"],
                    "properties": {
                        "article_id": {"type": "string", "description": "Article ID"}
                    }
                }
            ),
            
            # Article-Request Integration
            Tool(
                name="jsm_get_linked_articles",
                description="Get articles linked to a request",
                inputSchema={
                    "type": "object",
                    "required": ["request_id"],
                    "properties": {
                        "request_id": {"type": "string", "description": "Request ID"},
                        "start": {"type": "number", "description": "Starting index for pagination"},
                        "limit": {"type": "number", "description": "Maximum number of results to return"}
                    }
                }
            ),
            Tool(
                name="jsm_link_article_to_request",
                description="Link an article to a request",
                inputSchema={
                    "type": "object",
                    "required": ["request_id", "article_id"],
                    "properties": {
                        "request_id": {"type": "string", "description": "Request ID"},
                        "article_id": {"type": "string", "description": "Article ID"}
                    }
                }
            ),
            Tool(
                name="jsm_unlink_article_from_request",
                description="Unlink an article from a request",
                inputSchema={
                    "type": "object",
                    "required": ["request_id", "article_id"],
                    "properties": {
                        "request_id": {"type": "string", "description": "Request ID"},
                        "article_id": {"type": "string", "description": "Article ID"}
                    }
                }
            ),
            
            # Suggestions
            Tool(
                name="jsm_suggest_articles",
                description="Get article suggestions for a request type",
                inputSchema={
                    "type": "object",
                    "required": ["service_desk_id", "request_type_id"],
                    "properties": {
                        "service_desk_id": {"type": "string", "description": "Service desk ID"},
                        "request_type_id": {"type": "string", "description": "Request type ID"},
                        "query": {"type": "string", "description": "Optional search query"},
                        "limit": {"type": "number", "description": "Maximum number of results to return"}
                    }
                }
            )
        ])
    
    # Queue tools
    if jsm_queue_service:
        tools.extend([
            # Queue Operations
            Tool(
                name="jsm_get_queues",
                description="Get queues for a service desk",
                inputSchema={
                    "type": "object",
                    "required": ["service_desk_id"],
                    "properties": {
                        "service_desk_id": {"type": "string", "description": "Service desk ID"},
                        "include_counts": {"type": "boolean", "description": "Whether to include issue counts"}
                    }
                }
            ),
            Tool(
                name="jsm_get_queue_issues",
                description="Get issues in a queue",
                inputSchema={
                    "type": "object",
                    "required": ["service_desk_id", "queue_id"],
                    "properties": {
                        "service_desk_id": {"type": "string", "description": "Service desk ID"},
                        "queue_id": {"type": "string", "description": "Queue ID"},
                        "start": {"type": "number", "description": "Starting index for pagination"},
                        "limit": {"type": "number", "description": "Maximum number of results to return"},
                        "expand": {"type": "string", "description": "Optional fields to expand"}
                    }
                }
            ),
            Tool(
                name="jsm_create_custom_queue",
                description="Create a custom queue for a service desk",
                inputSchema={
                    "type": "object",
                    "required": ["service_desk_id", "name", "jql"],
                    "properties": {
                        "service_desk_id": {"type": "string", "description": "Service desk ID"},
                        "name": {"type": "string", "description": "Queue name"},
                        "jql": {"type": "string", "description": "JQL query for the queue"},
                        "description": {"type": "string", "description": "Optional queue description"}
                    }
                }
            ),
            Tool(
                name="jsm_update_custom_queue",
                description="Update a custom queue",
                inputSchema={
                    "type": "object",
                    "required": ["service_desk_id", "queue_id"],
                    "properties": {
                        "service_desk_id": {"type": "string", "description": "Service desk ID"},
                        "queue_id": {"type": "string", "description": "Queue ID"},
                        "name": {"type": "string", "description": "Optional new queue name"},
                        "jql": {"type": "string", "description": "Optional new JQL query"},
                        "description": {"type": "string", "description": "Optional new description"}
                    }
                }
            ),
            Tool(
                name="jsm_delete_custom_queue",
                description="Delete a custom queue",
                inputSchema={
                    "type": "object",
                    "required": ["service_desk_id", "queue_id"],
                    "properties": {
                        "service_desk_id": {"type": "string", "description": "Service desk ID"},
                        "queue_id": {"type": "string", "description": "Queue ID"}
                    }
                }
            ),
            
            # Queue Assignment
            Tool(
                name="jsm_assign_issue_to_queue",
                description="Assign an issue to a queue by updating fields based on the queue's JQL",
                inputSchema={
                    "type": "object",
                    "required": ["service_desk_id", "queue_id", "issue_id"],
                    "properties": {
                        "service_desk_id": {"type": "string", "description": "Service desk ID"},
                        "queue_id": {"type": "string", "description": "Queue ID"},
                        "issue_id": {"type": "string", "description": "Issue ID"}
                    }
                }
            ),
            
            # Queue Metrics
            Tool(
                name="jsm_get_queue_metrics",
                description="Get metrics for a queue",
                inputSchema={
                    "type": "object",
                    "required": ["service_desk_id", "queue_id"],
                    "properties": {
                        "service_desk_id": {"type": "string", "description": "Service desk ID"},
                        "queue_id": {"type": "string", "description": "Queue ID"},
                        "start_date": {"type": "string", "description": "Optional start date (ISO format)"},
                        "end_date": {"type": "string", "description": "Optional end date (ISO format)"}
                    }
                }
            )
        ])
    
    # Approval tools
    if jsm_approval_service:
        tools.extend([
            # Basic Approval Operations
            Tool(
                name="jsm_get_request_approvals",
                description="Get approvals for a request",
                inputSchema={
                    "type": "object",
                    "required": ["request_id"],
                    "properties": {
                        "request_id": {"type": "string", "description": "Request ID"},
                        "expand": {"type": "string", "description": "Optional fields to expand"}
                    }
                }
            ),
            Tool(
                name="jsm_get_approval_details",
                description="Get details for a specific approval",
                inputSchema={
                    "type": "object",
                    "required": ["request_id", "approval_id"],
                    "properties": {
                        "request_id": {"type": "string", "description": "Request ID"},
                        "approval_id": {"type": "string", "description": "Approval ID"}
                    }
                }
            ),
            Tool(
                name="jsm_answer_approval",
                description="Answer an approval request",
                inputSchema={
                    "type": "object",
                    "required": ["request_id", "approval_id", "decision"],
                    "properties": {
                        "request_id": {"type": "string", "description": "Request ID"},
                        "approval_id": {"type": "string", "description": "Approval ID"},
                        "decision": {"type": "string", "enum": ["approve", "decline"], "description": "The decision"},
                        "comment": {"type": "string", "description": "Optional comment"}
                    }
                }
            ),
            
            # Multi-Level Approval Operations
            Tool(
                name="jsm_create_approval_level",
                description="Create an approval level for an issue",
                inputSchema={
                    "type": "object",
                    "required": ["issue_id", "approvers", "level_name"],
                    "properties": {
                        "issue_id": {"type": "string", "description": "The issue ID"},
                        "approvers": {"type": "array", "items": {"type": "string"}, "description": "List of approver account IDs"},
                        "level_name": {"type": "string", "description": "Name for the approval level"},
                        "approval_type": {"type": "string", "enum": ["ANY_APPROVER", "ALL_APPROVERS"], "description": "Approval type"}
                    }
                }
            ),
            Tool(
                name="jsm_get_approval_levels",
                description="Get all approval levels for an issue",
                inputSchema={
                    "type": "object",
                    "required": ["issue_id"],
                    "properties": {
                        "issue_id": {"type": "string", "description": "The issue ID"}
                    }
                }
            ),
            
            # Approval Workflow Operations
            Tool(
                name="jsm_create_approval_workflow",
                description="Create an approval workflow for a service desk request type",
                inputSchema={
                    "type": "object",
                    "required": ["project_key", "request_type_id", "approval_config"],
                    "properties": {
                        "project_key": {"type": "string", "description": "The project key"},
                        "request_type_id": {"type": "string", "description": "The request type ID"},
                        "approval_config": {"type": "object", "description": "Approval workflow configuration"}
                    }
                }
            ),
            Tool(
                name="jsm_get_approval_workflow",
                description="Get approval workflow configuration for a project",
                inputSchema={
                    "type": "object",
                    "required": ["project_key", "request_type_id"],
                    "properties": {
                        "project_key": {"type": "string", "description": "The project key"},
                        "request_type_id": {"type": "string", "description": "The request type ID"}
                    }
                }
            ),
            
            # Approval Analytics
            Tool(
                name="jsm_get_approval_metrics",
                description="Get approval metrics for a service desk",
                inputSchema={
                    "type": "object",
                    "required": ["service_desk_id"],
                    "properties": {
                        "service_desk_id": {"type": "string", "description": "The service desk ID"},
                        "start_date": {"type": "string", "description": "Optional start date (ISO format)"},
                        "end_date": {"type": "string", "description": "Optional end date (ISO format)"}
                    }
                }
            )
        ])
    
    # Form tools
    if jsm_form_service:
        tools.extend([
            # Custom Fields
            Tool(
                name="jsm_get_custom_fields",
                description="Get all custom fields",
                inputSchema={
                    "type": "object",
                    "properties": {}
                }
            ),
            Tool(
                name="jsm_create_custom_field",
                description="Create a custom field",
                inputSchema={
                    "type": "object",
                    "required": ["name", "description", "type_key"],
                    "properties": {
                        "name": {"type": "string", "description": "Field name"},
                        "description": {"type": "string", "description": "Field description"},
                        "type_key": {"type": "string", "description": "Field type key (text, number, select, etc.)"},
                        "context_project_ids": {"type": "array", "items": {"type": "string"}, "description": "Optional list of project IDs for field context"},
                        "context_issue_type_ids": {"type": "array", "items": {"type": "string"}, "description": "Optional list of issue type IDs for field context"}
                    }
                }
            ),
            Tool(
                name="jsm_configure_field_options",
                description="Configure options for a select/multiselect field",
                inputSchema={
                    "type": "object",
                    "required": ["field_id", "options"],
                    "properties": {
                        "field_id": {"type": "string", "description": "The field ID"},
                        "options": {"type": "array", "items": {"type": "object"}, "description": 'List of option dictionaries with "value" and optionally "disabled" keys'}
                    }
                }
            ),
            
            # Form Configuration
            Tool(
                name="jsm_get_form_configuration",
                description="Get form configuration for a request type",
                inputSchema={
                    "type": "object",
                    "required": ["service_desk_id", "request_type_id"],
                    "properties": {
                        "service_desk_id": {"type": "string", "description": "The service desk ID"},
                        "request_type_id": {"type": "string", "description": "The request type ID"}
                    }
                }
            ),
            Tool(
                name="jsm_update_form_field_order",
                description="Update the order of fields in a form",
                inputSchema={
                    "type": "object",
                    "required": ["service_desk_id", "request_type_id", "field_order"],
                    "properties": {
                        "service_desk_id": {"type": "string", "description": "The service desk ID"},
                        "request_type_id": {"type": "string", "description": "The request type ID"},
                        "field_order": {"type": "array", "items": {"type": "string"}, "description": "List of field IDs in desired order"}
                    }
                }
            ),
            Tool(
                name="jsm_configure_field_requirements",
                description="Configure which fields are required or optional",
                inputSchema={
                    "type": "object",
                    "required": ["service_desk_id", "request_type_id", "required_fields", "optional_fields"],
                    "properties": {
                        "service_desk_id": {"type": "string", "description": "The service desk ID"},
                        "request_type_id": {"type": "string", "description": "The request type ID"},
                        "required_fields": {"type": "array", "items": {"type": "string"}, "description": "List of required field IDs"},
                        "optional_fields": {"type": "array", "items": {"type": "string"}, "description": "List of optional field IDs"}
                    }
                }
            ),
            
            # Form Validation
            Tool(
                name="jsm_validate_form_data",
                description="Validate form data against field requirements",
                inputSchema={
                    "type": "object",
                    "required": ["service_desk_id", "request_type_id", "form_data"],
                    "properties": {
                        "service_desk_id": {"type": "string", "description": "The service desk ID"},
                        "request_type_id": {"type": "string", "description": "The request type ID"},
                        "form_data": {"type": "object", "description": "Form data as field_id: value dict"}
                    }
                }
            )
        ])
    
    return tools

def handle_jsm_tool_call(name: str, arguments: Dict) -> Dict:
    """
    Handle JSM tool calls.

    Args:
        name: Tool name
        arguments: Tool arguments

    Returns:
        Tool result
    """
    # Check if JSM is available
    if not jsm_service:
        return {
            "status": "error",
            "message": "JSM is not available. Set the JSM_URL/JSM_USERNAME/JSM_API_TOKEN environment variables."
        }
    
    try:
        # Service Desk Operations
        if name == "jsm_get_service_desks":
            start = arguments.get("start", 0)
            limit = arguments.get("limit", 50)
            return {"service_desks": jsm_service.get_service_desks(start, limit)}
            
        elif name == "jsm_get_service_desk":
            service_desk_id = arguments.get("service_desk_id")
            return jsm_service.get_service_desk(service_desk_id)
            
        # Request Type Operations
        elif name == "jsm_get_request_types":
            service_desk_id = arguments.get("service_desk_id")
            start = arguments.get("start", 0)
            limit = arguments.get("limit", 50)
            return {"request_types": jsm_service.get_request_types(service_desk_id, start, limit)}
            
        elif name == "jsm_get_request_type_fields":
            service_desk_id = arguments.get("service_desk_id")
            request_type_id = arguments.get("request_type_id")
            return {"fields": jsm_service.get_request_type_fields(service_desk_id, request_type_id)}
            
        # Customer Request Operations
        elif name == "jsm_create_customer_request":
            service_desk_id = arguments.get("service_desk_id")
            request_type_id = arguments.get("request_type_id")
            summary = arguments.get("summary")
            description = arguments.get("description")
            custom_fields = arguments.get("custom_fields")
            return jsm_service.create_customer_request(
                service_desk_id, request_type_id, summary, description, custom_fields
            )
            
        elif name == "jsm_get_customer_requests":
            service_desk_id = arguments.get("service_desk_id")
            request_status = arguments.get("request_status")
            search_term = arguments.get("search_term")
            start = arguments.get("start", 0)
            limit = arguments.get("limit", 50)
            return {"requests": jsm_service.get_customer_requests(
                service_desk_id, request_status, search_term, start, limit
            )}
            
        elif name == "jsm_get_customer_request":
            request_id = arguments.get("request_id")
            return jsm_service.get_customer_request(request_id)
            
        # Request Participants Operations
        elif name == "jsm_get_request_participants":
            request_id = arguments.get("request_id")
            return {"participants": jsm_service.get_request_participants(request_id)}
            
        elif name == "jsm_add_request_participant":
            request_id = arguments.get("request_id")
            account_id = arguments.get("account_id")
            return jsm_service.add_request_participant(request_id, account_id)
            
        elif name == "jsm_remove_request_participant":
            request_id = arguments.get("request_id")
            account_id = arguments.get("account_id")
            return jsm_service.remove_request_participant(request_id, account_id)
            
        # SLA Operations
        elif name == "jsm_get_request_sla":
            request_id = arguments.get("request_id")
            return {"sla": jsm_service.get_request_sla(request_id)}
            
        # Organizations Operations
        elif name == "jsm_get_organizations":
            service_desk_id = arguments.get("service_desk_id")
            return {"organizations": jsm_service.get_organizations(service_desk_id)}
            
        elif name == "jsm_add_organization":
            service_desk_id = arguments.get("service_desk_id")
            organization_id = arguments.get("organization_id")
            return jsm_service.add_organization(service_desk_id, organization_id)
            
        elif name == "jsm_remove_organization":
            service_desk_id = arguments.get("service_desk_id")
            organization_id = arguments.get("organization_id")
            return jsm_service.remove_organization(service_desk_id, organization_id)
            
        # Knowledge Base Operations
        elif name == "jsm_get_knowledge_bases":
            if not jsm_kb_service:
                return {"status": "error", "message": "Knowledge Base module not enabled"}
            start = arguments.get("start", 0)
            limit = arguments.get("limit", 50)
            return {"knowledge_bases": jsm_kb_service.get_knowledge_bases(start, limit)}
            
        elif name == "jsm_get_knowledge_base":
            if not jsm_kb_service:
                return {"status": "error", "message": "Knowledge Base module not enabled"}
            knowledge_base_id = arguments.get("knowledge_base_id")
            return jsm_kb_service.get_knowledge_base(knowledge_base_id)
            
        # Article Operations
        elif name == "jsm_search_articles":
            if not jsm_kb_service:
                return {"status": "error", "message": "Knowledge Base module not enabled"}
            query = arguments.get("query")
            knowledge_base_id = arguments.get("knowledge_base_id")
            highlight = arguments.get("highlight", False)
            start = arguments.get("start", 0)
            limit = arguments.get("limit", 50)
            return {"articles": jsm_kb_service.search_articles(
                query, knowledge_base_id, highlight, start, limit
            )}
            
        elif name == "jsm_get_article":
            if not jsm_kb_service:
                return {"status": "error", "message": "Knowledge Base module not enabled"}
            article_id = arguments.get("article_id")
            return jsm_kb_service.get_article(article_id)
            
        elif name == "jsm_create_article":
            if not jsm_kb_service:
                return {"status": "error", "message": "Knowledge Base module not enabled"}
            knowledge_base_id = arguments.get("knowledge_base_id")
            title = arguments.get("title")
            body = arguments.get("body")
            draft = arguments.get("draft", False)
            labels = arguments.get("labels")
            return jsm_kb_service.create_article(knowledge_base_id, title, body, draft, labels)
            
        elif name == "jsm_update_article":
            if not jsm_kb_service:
                return {"status": "error", "message": "Knowledge Base module not enabled"}
            article_id = arguments.get("article_id")
            title = arguments.get("title")
            body = arguments.get("body")
            draft = arguments.get("draft")
            labels = arguments.get("labels")
            return jsm_kb_service.update_article(article_id, title, body, draft, labels)
            
        elif name == "jsm_delete_article":
            if not jsm_kb_service:
                return {"status": "error", "message": "Knowledge Base module not enabled"}
            article_id = arguments.get("article_id")
            return jsm_kb_service.delete_article(article_id)
            
        # Article-Request Integration
        elif name == "jsm_get_linked_articles":
            if not jsm_kb_service:
                return {"status": "error", "message": "Knowledge Base module not enabled"}
            request_id = arguments.get("request_id")
            start = arguments.get("start", 0)
            limit = arguments.get("limit", 50)
            return {"articles": jsm_kb_service.get_linked_articles(request_id, start, limit)}
            
        elif name == "jsm_link_article_to_request":
            if not jsm_kb_service:
                return {"status": "error", "message": "Knowledge Base module not enabled"}
            request_id = arguments.get("request_id")
            article_id = arguments.get("article_id")
            return jsm_kb_service.link_article_to_request(request_id, article_id)
            
        elif name == "jsm_unlink_article_from_request":
            if not jsm_kb_service:
                return {"status": "error", "message": "Knowledge Base module not enabled"}
            request_id = arguments.get("request_id")
            article_id = arguments.get("article_id")
            return jsm_kb_service.unlink_article_from_request(request_id, article_id)
            
        # Suggestions
        elif name == "jsm_suggest_articles":
            if not jsm_kb_service:
                return {"status": "error", "message": "Knowledge Base module not enabled"}
            service_desk_id = arguments.get("service_desk_id")
            request_type_id = arguments.get("request_type_id")
            query = arguments.get("query")
            limit = arguments.get("limit", 5)
            return {"articles": jsm_kb_service.suggest_articles(
                service_desk_id, request_type_id, query, limit
            )}
            
        # Queue Operations
        elif name == "jsm_get_queues":
            if not jsm_queue_service:
                return {"status": "error", "message": "Queue module not enabled"}
            service_desk_id = arguments.get("service_desk_id")
            include_counts = arguments.get("include_counts", False)
            return {"queues": jsm_queue_service.get_queues(service_desk_id, include_counts)}
            
        elif name == "jsm_get_queue_issues":
            if not jsm_queue_service:
                return {"status": "error", "message": "Queue module not enabled"}
            service_desk_id = arguments.get("service_desk_id")
            queue_id = arguments.get("queue_id")
            start = arguments.get("start", 0)
            limit = arguments.get("limit", 50)
            expand = arguments.get("expand")
            return {"issues": jsm_queue_service.get_queue_issues(
                service_desk_id, queue_id, start, limit, expand
            )}
            
        elif name == "jsm_create_custom_queue":
            if not jsm_queue_service:
                return {"status": "error", "message": "Queue module not enabled"}
            service_desk_id = arguments.get("service_desk_id")
            name = arguments.get("name")
            jql = arguments.get("jql")
            description = arguments.get("description")
            return jsm_queue_service.create_custom_queue(service_desk_id, name, jql, description)
            
        elif name == "jsm_update_custom_queue":
            if not jsm_queue_service:
                return {"status": "error", "message": "Queue module not enabled"}
            service_desk_id = arguments.get("service_desk_id")
            queue_id = arguments.get("queue_id")
            name = arguments.get("name")
            jql = arguments.get("jql")
            description = arguments.get("description")
            return jsm_queue_service.update_custom_queue(
                service_desk_id, queue_id, name, jql, description
            )
            
        elif name == "jsm_delete_custom_queue":
            if not jsm_queue_service:
                return {"status": "error", "message": "Queue module not enabled"}
            service_desk_id = arguments.get("service_desk_id")
            queue_id = arguments.get("queue_id")
            return jsm_queue_service.delete_custom_queue(service_desk_id, queue_id)
            
        # Queue Assignment
        elif name == "jsm_assign_issue_to_queue":
            if not jsm_queue_service:
                return {"status": "error", "message": "Queue module not enabled"}
            service_desk_id = arguments.get("service_desk_id")
            queue_id = arguments.get("queue_id")
            issue_id = arguments.get("issue_id")
            return jsm_queue_service.assign_issue_to_queue(service_desk_id, queue_id, issue_id)
            
        # Queue Metrics
        elif name == "jsm_get_queue_metrics":
            if not jsm_queue_service:
                return {"status": "error", "message": "Queue module not enabled"}
            service_desk_id = arguments.get("service_desk_id")
            queue_id = arguments.get("queue_id")
            start_date = arguments.get("start_date")
            end_date = arguments.get("end_date")
            
            from datetime import datetime
            if start_date:
                start_date = datetime.fromisoformat(start_date.replace("Z", "+00:00"))
            if end_date:
                end_date = datetime.fromisoformat(end_date.replace("Z", "+00:00"))
                
            return jsm_queue_service.get_queue_metrics(
                service_desk_id, queue_id, start_date, end_date
            )
            
        # Approval Operations
        elif name == "jsm_get_request_approvals":
            if not jsm_approval_service:
                return {"status": "error", "message": "Approval module not enabled"}
            request_id = arguments.get("request_id")
            expand = arguments.get("expand")
            return {"approvals": jsm_approval_service.get_request_approvals(request_id, expand)}
            
        elif name == "jsm_get_approval_details":
            if not jsm_approval_service:
                return {"status": "error", "message": "Approval module not enabled"}
            request_id = arguments.get("request_id")
            approval_id = arguments.get("approval_id")
            return jsm_approval_service.get_approval_details(request_id, approval_id)
            
        elif name == "jsm_answer_approval":
            if not jsm_approval_service:
                return {"status": "error", "message": "Approval module not enabled"}
            request_id = arguments.get("request_id")
            approval_id = arguments.get("approval_id")
            decision = arguments.get("decision")
            comment = arguments.get("comment")
            return jsm_approval_service.answer_approval(request_id, approval_id, decision, comment)
            
        # Multi-Level Approval Operations
        elif name == "jsm_create_approval_level":
            if not jsm_approval_service:
                return {"status": "error", "message": "Approval module not enabled"}
            issue_id = arguments.get("issue_id")
            approvers = arguments.get("approvers")
            level_name = arguments.get("level_name")
            approval_type = arguments.get("approval_type", "ANY_APPROVER")
            return jsm_approval_service.create_approval_level(
                issue_id, approvers, level_name, approval_type
            )
            
        elif name == "jsm_get_approval_levels":
            if not jsm_approval_service:
                return {"status": "error", "message": "Approval module not enabled"}
            issue_id = arguments.get("issue_id")
            return {"levels": jsm_approval_service.get_approval_levels(issue_id)}
            
        # Approval Workflow Operations
        elif name == "jsm_create_approval_workflow":
            if not jsm_approval_service:
                return {"status": "error", "message": "Approval module not enabled"}
            project_key = arguments.get("project_key")
            request_type_id = arguments.get("request_type_id")
            approval_config = arguments.get("approval_config")
            return jsm_approval_service.create_approval_workflow(
                project_key, request_type_id, approval_config
            )
            
        elif name == "jsm_get_approval_workflow":
            if not jsm_approval_service:
                return {"status": "error", "message": "Approval module not enabled"}
            project_key = arguments.get("project_key")
            request_type_id = arguments.get("request_type_id")
            return jsm_approval_service.get_approval_workflow(project_key, request_type_id)
            
        # Approval Analytics
        elif name == "jsm_get_approval_metrics":
            if not jsm_approval_service:
                return {"status": "error", "message": "Approval module not enabled"}
            service_desk_id = arguments.get("service_desk_id")
            start_date = arguments.get("start_date")
            end_date = arguments.get("end_date")
            
            from datetime import datetime
            if start_date:
                start_date = datetime.fromisoformat(start_date.replace("Z", "+00:00"))
            if end_date:
                end_date = datetime.fromisoformat(end_date.replace("Z", "+00:00"))
                
            return jsm_approval_service.get_approval_metrics(
                service_desk_id, start_date, end_date
            )
            
        # Form Operations
        elif name == "jsm_get_custom_fields":
            if not jsm_form_service:
                return {"status": "error", "message": "Form module not enabled"}
            return {"fields": jsm_form_service.get_custom_fields()}
            
        elif name == "jsm_create_custom_field":
            if not jsm_form_service:
                return {"status": "error", "message": "Form module not enabled"}
            name = arguments.get("name")
            description = arguments.get("description")
            type_key = arguments.get("type_key")
            context_project_ids = arguments.get("context_project_ids")
            context_issue_type_ids = arguments.get("context_issue_type_ids")
            return jsm_form_service.create_custom_field(
                name, description, type_key, context_project_ids, context_issue_type_ids
            )
            
        elif name == "jsm_configure_field_options":
            if not jsm_form_service:
                return {"status": "error", "message": "Form module not enabled"}
            field_id = arguments.get("field_id")
            options = arguments.get("options")
            return jsm_form_service.configure_field_options(field_id, options)
            
        # Form Configuration
        elif name == "jsm_get_form_configuration":
            if not jsm_form_service:
                return {"status": "error", "message": "Form module not enabled"}
            service_desk_id = arguments.get("service_desk_id")
            request_type_id = arguments.get("request_type_id")
            return jsm_form_service.get_form_configuration(service_desk_id, request_type_id)
            
        elif name == "jsm_update_form_field_order":
            if not jsm_form_service:
                return {"status": "error", "message": "Form module not enabled"}
            service_desk_id = arguments.get("service_desk_id")
            request_type_id = arguments.get("request_type_id")
            field_order = arguments.get("field_order")
            return jsm_form_service.update_form_field_order(
                service_desk_id, request_type_id, field_order
            )
            
        elif name == "jsm_configure_field_requirements":
            if not jsm_form_service:
                return {"status": "error", "message": "Form module not enabled"}
            service_desk_id = arguments.get("service_desk_id")
            request_type_id = arguments.get("request_type_id")
            required_fields = arguments.get("required_fields")
            optional_fields = arguments.get("optional_fields")
            return jsm_form_service.configure_field_requirements(
                service_desk_id, request_type_id, required_fields, optional_fields
            )
            
        # Form Validation
        elif name == "jsm_validate_form_data":
            if not jsm_form_service:
                return {"status": "error", "message": "Form module not enabled"}
            service_desk_id = arguments.get("service_desk_id")
            request_type_id = arguments.get("request_type_id")
            form_data = arguments.get("form_data")
            return jsm_form_service.validate_form_data(
                service_desk_id, request_type_id, form_data
            )
            
        # Unknown tool
        else:
            return {
                "status": "error",
                "message": f"Unknown JSM tool: {name}"
            }
            
    except Exception as e:
        logger.error(f"Error handling JSM tool call: {e}")
        return {
            "status": "error",
            "message": f"Error: {str(e)}"
        }