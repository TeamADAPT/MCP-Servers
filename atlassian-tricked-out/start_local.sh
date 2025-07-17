#!/bin/bash
set -e

# Navigate to server directory
cd "/Threshold/bloom-memory/mcp-servers/atlassian-tricked-out"

# Activate virtual environment
source venv/bin/activate

# Set Python path
export PYTHONPATH="$(pwd)/src:$PYTHONPATH"

# Set required environment variables
export JIRA_URL="https://YOUR-CREDENTIALS@YOUR-DOMAIN//levelup2x.atlassian.net/wiki"
export CONFLUENCE_USERNAME="chase@levelup2x.com"
export CONFLUENCE_API_TOKEN=YOUR-API-TOKEN-HERE
export JSM_URL="https://YOUR-CREDENTIALS@YOUR-DOMAIN