"""
Atlassian Enterprise MCP Server - Advanced analytics, AI, and app integrations.

This server provides enterprise-grade features:
- Authentication and security management
- Analytics and reporting capabilities  
- AI-powered content suggestions and classification
- Marketplace app integrations
- ~22 tools for enterprise automation and insights
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any
from mcp.server import Server
from mcp.types import Resource, Tool, TextContent

# Import Enterprise modules
try:
    from .server_enterprise import get_enterprise_tools, handle_enterprise_tool_call
    ENTERPRISE_AVAILABLE = True
except ImportError:
    ENTERPRISE_AVAILABLE = False
    logger = logging.getLogger("mcp-atlassian-enterprise")
    logger.warning("Enterprise module not available, enterprise features will be disabled")
    # Define dummy functions
    def get_enterprise_tools(): return []
    def handle_enterprise_tool_call(name, arguments): return {}

# Configure logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger("mcp-atlassian-enterprise")
logging.getLogger("mcp.server.lowlevel.server").setLevel(logging.WARNING)


def get_available_services():
    """Determine which ENTERPRISE services are available based on environment variables."""
    # Enterprise features are always available if the module loads
    enterprise_vars = ENTERPRISE_AVAILABLE
    
    # Check for required Atlassian credentials for enterprise features
    atlassian_configured = any([
        all([os.getenv("CONFLUENCE_URL"), os.getenv("CONFLUENCE_USERNAME"), os.getenv("CONFLUENCE_API_TOKEN")]),
        all([os.getenv("JIRA_URL"), os.getenv("JIRA_USERNAME"), os.getenv("JIRA_API_TOKEN")])
    ])

    return {
        "enterprise": enterprise_vars and atlassian_configured
    }


# Initialize ENTERPRISE services only
services = get_available_services()

app = Server("mcp-atlassian-enterprise")


@app.list_tools()
async def list_tools() -> List[Tool]:
    """List available Enterprise tools."""
    tools = []
    
    # Add enterprise tools
    if services.get("enterprise", False):
        try:
            enterprise_tools = get_enterprise_tools()
            tools.extend(enterprise_tools)
            logger.info(f"Added {len(enterprise_tools)} enterprise tools")
        except Exception as e:
            logger.error(f"Error adding enterprise tools: {str(e)}")

    logger.info(f"Loaded {len(tools)} enterprise tools")
    return tools


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Execute Enterprise tools."""
    try:
        # Handle Enterprise tools
        if services.get("enterprise", False):
            result = await handle_enterprise_tool_call(name, arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        # Tool not found
        return [TextContent(type="text", text=f"Tool '{name}' not found or enterprise service not available")]
    
    except Exception as e:
        logger.error(f"Error executing enterprise tool '{name}': {str(e)}")
        return [TextContent(type="text", text=f"Error: {str(e)}")]


if __name__ == "__main__":
    import asyncio
    
    async def main():
        # Add any additional async initialization here
        pass
    
    from mcp.server.stdio import stdio_server
    asyncio.run(stdio_server(app))