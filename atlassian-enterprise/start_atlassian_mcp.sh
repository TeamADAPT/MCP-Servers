#!/bin/bash
set -e

# Navigate to server directory
cd "/data-nova/ax/DevOps/mcp/mcp-servers/cicd/mcp-atlassian-archive-20250514"

# Activate virtual environment
source venv/bin/activate

# Set Python path
export PYTHONPATH="$(pwd)/src:$PYTHONPATH"

# Set required environment variables from MCP settings
export JIRA_URL="${JIRA_URL:-https://YOUR-CREDENTIALS@YOUR-DOMAIN//levelup2x.atlassian.net/wiki}"
export CONFLUENCE_USERNAME="${CONFLUENCE_USERNAME:-chase@levelup2x.com}"
export JSM_URL="${JSM_URL:-https://YOUR-CREDENTIALS@YOUR-DOMAIN/src')
from mcp_atlassian.server import main
asyncio.run(main())
"
