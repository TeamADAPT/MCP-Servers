"""
Enterprise server module for MCP Atlassian.

This module extends the base server functionality with enterprise-grade features
including authentication, analytics, AI capabilities, and app integrations.
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any

from mcp.types import Tool

from .auth import auth_manager
from .analytics import analytics_manager
from .ai_capabilities import ai_capabilities_manager
from .marketplace_integration import app_integration_manager

# Configure logging
logger = logging.getLogger("mcp-atlassian.server_enterprise")


def get_enterprise_tools() -> List[Tool]:
    """Get the enterprise tools for MCP Atlassian."""
    tools = []
    
    # Authentication and Security tools
    tools.extend([
        Tool(
            name="atlassian_auth_status",
            description="Get authentication status for Atlassian services",
            inputSchema={
                "type": "object",
                "properties": {
                    "service": {
                        "type": "string",
                        "description": "Service to check (jira, confluence, bitbucket)",
                        "enum": ["jira", "confluence", "bitbucket"]
                    }
                },
                "required": ["service"]
            }
        ),
        Tool(
            name="atlassian_refresh_auth",
            description="Refresh authentication tokens for Atlassian services",
            inputSchema={
                "type": "object",
                "properties": {
                    "service": {
                        "type": "string",
                        "description": "Service to refresh (jira, confluence, bitbucket)",
                        "enum": ["jira", "confluence", "bitbucket"]
                    },
                    "user_id": {
                        "type": "string",
                        "description": "User ID to refresh tokens for (defaults to current user)"
                    }
                },
                "required": ["service"]
            }
        ),
        Tool(
            name="atlassian_revoke_auth",
            description="Revoke authentication tokens for Atlassian services",
            inputSchema={
                "type": "object",
                "properties": {
                    "service": {
                        "type": "string",
                        "description": "Service to revoke (jira, confluence, bitbucket)",
                        "enum": ["jira", "confluence", "bitbucket"]
                    },
                    "user_id": {
                        "type": "string",
                        "description": "User ID to revoke tokens for (defaults to current user)"
                    }
                },
                "required": ["service"]
            }
        ),
        Tool(
            name="atlassian_get_audit_logs",
            description="Get audit logs for security events",
            inputSchema={
                "type": "object",
                "properties": {
                    "service": {
                        "type": "string",
                        "description": "Service to get logs for (jira, confluence, bitbucket, all)",
                        "enum": ["jira", "confluence", "bitbucket", "all"]
                    },
                    "days": {
                        "type": "integer",
                        "description": "Number of days of logs to retrieve",
                        "default": 7
                    },
                    "event_type": {
                        "type": "string",
                        "description": "Filter by event type"
                    },
                    "user_id": {
                        "type": "string",
                        "description": "Filter by user ID"
                    }
                },
                "required": ["service"]
            }
        )
    ])
    
    # Analytics tools
    tools.extend([
        Tool(
            name="analytics_project_metrics",
            description="Get comprehensive project metrics",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_key": {
                        "type": "string",
                        "description": "Jira project key"
                    }
                },
                "required": ["project_key"]
            }
        ),
        Tool(
            name="analytics_time_tracking",
            description="Analyze time tracking data for a project",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_key": {
                        "type": "string",
                        "description": "Jira project key"
                    }
                },
                "required": ["project_key"]
            }
        ),
        Tool(
            name="analytics_issue_patterns",
            description="Detect patterns in project issues using AI",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_key": {
                        "type": "string",
                        "description": "Jira project key"
                    }
                },
                "required": ["project_key"]
            }
        ),
        Tool(
            name="analytics_trend_report",
            description="Generate a trend report for a project",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_key": {
                        "type": "string",
                        "description": "Jira project key"
                    },
                    "time_range": {
                        "type": "string",
                        "description": "Time range to analyze (e.g., 1w, 1m, 3m, 6m, 1y)",
                        "default": "3m"
                    }
                },
                "required": ["project_key"]
            }
        ),
        Tool(
            name="analytics_generate_report",
            description="Generate a custom analytics report",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_key": {
                        "type": "string",
                        "description": "Jira project key"
                    },
                    "report_type": {
                        "type": "string",
                        "description": "Type of report to generate",
                        "enum": ["comprehensive", "velocity", "efficiency", "quality"],
                        "default": "comprehensive"
                    }
                },
                "required": ["project_key"]
            }
        ),
        Tool(
            name="analytics_publish_report",
            description="Publish an analytics report to Confluence",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_key": {
                        "type": "string",
                        "description": "Jira project key"
                    },
                    "space_key": {
                        "type": "string",
                        "description": "Confluence space key"
                    },
                    "title": {
                        "type": "string",
                        "description": "Page title"
                    },
                    "report_type": {
                        "type": "string",
                        "description": "Type of report to publish",
                        "enum": ["comprehensive", "velocity", "efficiency", "quality"],
                        "default": "comprehensive"
                    }
                },
                "required": ["project_key", "space_key", "title"]
            }
        )
    ])
    
    # AI Capabilities tools
    tools.extend([
        Tool(
            name="ai_train_issue_classifier",
            description="Train an AI model to classify issues",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_key": {
                        "type": "string",
                        "description": "Jira project key to use for training"
                    },
                    "model_type": {
                        "type": "string",
                        "description": "Type of classifier to train",
                        "enum": ["issue_type", "priority", "component"],
                        "default": "issue_type"
                    }
                },
                "required": ["project_key"]
            }
        ),
        Tool(
            name="ai_classify_issue",
            description="Classify an issue using a trained AI model",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_key": {
                        "type": "string",
                        "description": "Project key associated with the model"
                    },
                    "text": {
                        "type": "string",
                        "description": "Issue text to classify (summary + description)"
                    },
                    "model_type": {
                        "type": "string",
                        "description": "Type of classifier to use",
                        "enum": ["issue_type", "priority", "component"],
                        "default": "issue_type"
                    }
                },
                "required": ["project_key", "text"]
            }
        ),
        Tool(
            name="ai_suggest_content",
            description="Get AI-generated content suggestions based on similar issues",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_key": {
                        "type": "string",
                        "description": "Jira project key to search for similar content"
                    },
                    "query": {
                        "type": "string",
                        "description": "Query text (e.g. issue summary)"
                    },
                    "content_type": {
                        "type": "string",
                        "description": "Type of content to suggest",
                        "enum": ["description", "comment", "solution"],
                        "default": "description"
                    }
                },
                "required": ["project_key", "query"]
            }
        ),
        Tool(
            name="ai_analyze_sentiment",
            description="Analyze sentiment in text or issue comments",
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "Text to analyze"
                    },
                    "issue_key": {
                        "type": "string",
                        "description": "Jira issue key to analyze comments from"
                    }
                }
            }
        ),
        Tool(
            name="ai_train_sla_predictor",
            description="Train an AI model to predict SLA breaches",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_key": {
                        "type": "string",
                        "description": "Jira project key to use for training"
                    }
                },
                "required": ["project_key"]
            }
        ),
        Tool(
            name="ai_predict_sla",
            description="Predict SLA breach risk for an issue",
            inputSchema={
                "type": "object",
                "properties": {
                    "issue_key": {
                        "type": "string",
                        "description": "Jira issue key to predict"
                    }
                },
                "required": ["issue_key"]
            }
        )
    ])
    
    # Marketplace App Integration tools
    tools.extend([
        Tool(
            name="app_get_available",
            description="Get available marketplace app integrations",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="app_configure",
            description="Configure a marketplace app integration",
            inputSchema={
                "type": "object",
                "properties": {
                    "app_key": {
                        "type": "string",
                        "description": "Unique key for the app"
                    },
                    "config": {
                        "type": "object",
                        "description": "Configuration parameters"
                    }
                },
                "required": ["app_key", "config"]
            }
        ),
        Tool(
            name="app_get_capabilities",
            description="Get capabilities for a marketplace app",
            inputSchema={
                "type": "object",
                "properties": {
                    "app_key": {
                        "type": "string",
                        "description": "Unique key for the app"
                    }
                },
                "required": ["app_key"]
            }
        ),
        Tool(
            name="app_execute_capability",
            description="Execute a marketplace app capability",
            inputSchema={
                "type": "object",
                "properties": {
                    "app_key": {
                        "type": "string",
                        "description": "Unique key for the app"
                    },
                    "capability_id": {
                        "type": "string",
                        "description": "ID of the capability to execute"
                    },
                    "params": {
                        "type": "object",
                        "description": "Parameters for the capability"
                    }
                },
                "required": ["app_key", "capability_id", "params"]
            }
        ),
        Tool(
            name="app_get_status",
            description="Get status information for a marketplace app",
            inputSchema={
                "type": "object",
                "properties": {
                    "app_key": {
                        "type": "string",
                        "description": "Unique key for the app"
                    }
                },
                "required": ["app_key"]
            }
        ),
        Tool(
            name="app_remove_configuration",
            description="Remove configuration for a marketplace app",
            inputSchema={
                "type": "object",
                "properties": {
                    "app_key": {
                        "type": "string",
                        "description": "Unique key for the app"
                    }
                },
                "required": ["app_key"]
            }
        )
    ])
    
    return tools


def handle_enterprise_tool_call(name: str, arguments: Any) -> Any:
    """
    Handle calls to enterprise tools.
    
    Args:
        name: Tool name
        arguments: Tool arguments
        
    Returns:
        Tool result
    """
    # Authentication and Security tools
    if name == "atlassian_auth_status":
        service = arguments["service"]
        user_id = arguments.get("user_id", "default")
        
        # Get authentication status
        token_data = auth_manager.token_manager.get_token(service, user_id)
        
        if token_data:
            expires_at = token_data.get("expires_at", 0)
            import time
            expires_in = max(0, expires_at - time.time())
            
            return {
                "service": service,
                "user_id": user_id,
                "authenticated": True,
                "expires_in_seconds": int(expires_in),
                "scopes": token_data.get("scope", "").split()
            }
        else:
            return {
                "service": service,
                "user_id": user_id,
                "authenticated": False
            }
    
    elif name == "atlassian_refresh_auth":
        service = arguments["service"]
        user_id = arguments.get("user_id", "default")
        
        # Refresh authentication
        success = auth_manager.refresh_credentials(service, user_id)
        
        if success:
            token_data = auth_manager.token_manager.get_token(service, user_id)
            import time
            expires_in = max(0, token_data.get("expires_at", 0) - time.time())
            
            return {
                "success": True,
                "service": service,
                "user_id": user_id,
                "expires_in_seconds": int(expires_in),
                "message": f"Authentication refreshed successfully for {service}"
            }
        else:
            return {
                "success": False,
                "service": service,
                "user_id": user_id,
                "message": f"Failed to refresh authentication for {service}"
            }
    
    elif name == "atlassian_revoke_auth":
        service = arguments["service"]
        user_id = arguments.get("user_id", "default")
        
        # Revoke authentication
        success = auth_manager.revoke_credentials(service, user_id)
        
        return {
            "success": success,
            "service": service,
            "user_id": user_id,
            "message": f"Authentication {'revoked successfully' if success else 'could not be revoked'} for {service}"
        }
    
    elif name == "atlassian_get_audit_logs":
        # This is a simplified implementation. In a real-world scenario,
        # you would likely query a database or external audit log service.
        service = arguments["service"]
        days = arguments.get("days", 7)
        event_type = arguments.get("event_type")
        user_id = arguments.get("user_id")
        
        # Get logs from the audit logger
        import os
        log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "logs")
        
        # List log files
        import glob
        log_files = glob.glob(os.path.join(log_dir, "auth-audit-*.log"))
        
        # Filter and read logs
        logs = []
        
        for log_file in log_files:
            try:
                with open(log_file, "r") as f:
                    for line in f:
                        # Parse log line
                        if "event_type" in line and "user" in line:
                            # Simple filtering
                            if event_type and event_type not in line:
                                continue
                            if user_id and user_id not in line:
                                continue
                            if service != "all" and service not in line:
                                continue
                                
                            logs.append(line.strip())
            except Exception as e:
                logger.error(f"Error reading audit log file {log_file}: {str(e)}")
        
        return {
            "service": service,
            "days": days,
            "logs": logs,
            "count": len(logs)
        }
    
    # Analytics tools
    elif name == "analytics_project_metrics":
        project_key = arguments["project_key"]
        metrics = analytics_manager.get_project_metrics(project_key)
        return metrics
    
    elif name == "analytics_time_tracking":
        project_key = arguments["project_key"]
        analysis = analytics_manager.analyze_time_tracking(project_key)
        return analysis
    
    elif name == "analytics_issue_patterns":
        project_key = arguments["project_key"]
        patterns = analytics_manager.detect_issue_patterns(project_key)
        return patterns
    
    elif name == "analytics_trend_report":
        project_key = arguments["project_key"]
        time_range = arguments.get("time_range", "3m")
        report = analytics_manager.generate_trend_report(project_key, time_range)
        return report
    
    elif name == "analytics_generate_report":
        project_key = arguments["project_key"]
        report_type = arguments.get("report_type", "comprehensive")
        report = analytics_manager.generate_custom_report(
            project_key=project_key,
            report_type=report_type
        )
        return report
    
    elif name == "analytics_publish_report":
        project_key = arguments["project_key"]
        space_key = arguments["space_key"]
        title = arguments["title"]
        report_type = arguments.get("report_type", "comprehensive")
        
        # Generate the report
        report = analytics_manager.generate_custom_report(
            project_key=project_key,
            report_type=report_type
        )
        
        # Publish to Confluence
        result = analytics_manager.publish_report_to_confluence(
            report=report,
            space_key=space_key,
            title=title
        )
        
        return result
    
    # AI Capabilities tools
    elif name == "ai_train_issue_classifier":
        project_key = arguments["project_key"]
        model_type = arguments.get("model_type", "issue_type")
        result = ai_capabilities_manager.train_issue_classifier(
            project_key=project_key,
            model_type=model_type
        )
        return result
    
    elif name == "ai_classify_issue":
        project_key = arguments["project_key"]
        text = arguments["text"]
        model_type = arguments.get("model_type", "issue_type")
        result = ai_capabilities_manager.classify_issue(
            project_key=project_key,
            text=text,
            model_type=model_type
        )
        return result
    
    elif name == "ai_suggest_content":
        project_key = arguments["project_key"]
        query = arguments["query"]
        content_type = arguments.get("content_type", "description")
        result = ai_capabilities_manager.suggest_content(
            project_key=project_key,
            query=query,
            content_type=content_type
        )
        return result
    
    elif name == "ai_analyze_sentiment":
        text = arguments.get("text")
        issue_key = arguments.get("issue_key")
        
        if not text and not issue_key:
            return {"error": "Either text or issue_key must be provided"}
            
        result = ai_capabilities_manager.analyze_sentiment(
            text=text,
            issue_key=issue_key
        )
        return result
    
    elif name == "ai_train_sla_predictor":
        project_key = arguments["project_key"]
        result = ai_capabilities_manager.train_sla_predictor(
            project_key=project_key
        )
        return result
    
    elif name == "ai_predict_sla":
        issue_key = arguments["issue_key"]
        result = ai_capabilities_manager.predict_sla(
            issue_key=issue_key
        )
        return result
    
    # Marketplace App Integration tools
    elif name == "app_get_available":
        apps = app_integration_manager.get_available_apps()
        return {
            "apps": apps,
            "count": len(apps)
        }
    
    elif name == "app_configure":
        app_key = arguments["app_key"]
        config = arguments["config"]
        result = app_integration_manager.configure_app(app_key, config)
        return result
    
    elif name == "app_get_capabilities":
        app_key = arguments["app_key"]
        result = app_integration_manager.get_app_capabilities(app_key)
        return result
    
    elif name == "app_execute_capability":
        app_key = arguments["app_key"]
        capability_id = arguments["capability_id"]
        params = arguments["params"]
        result = app_integration_manager.execute_capability(app_key, capability_id, params)
        return result
    
    elif name == "app_get_status":
        app_key = arguments["app_key"]
        result = app_integration_manager.get_app_status(app_key)
        return result
    
    elif name == "app_remove_configuration":
        app_key = arguments["app_key"]
        result = app_integration_manager.remove_app_configuration(app_key)
        return result
    
    # Unknown tool
    return {"error": f"Unknown enterprise tool: {name}"}