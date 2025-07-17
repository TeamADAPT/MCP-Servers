# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands
- **Setup**: `pip install -r requirements.txt` - Install dependencies
- **Build**: `python setup.py build` - Build the project
- **Run Server**: `python -m mcp_atlassian.server` - Run the MCP server
- **Debug**: `npx @modelcontextprotocol/inspector python -m mcp_atlassian.server` - Debug with MCP inspector
- **View Logs**: `tail -n 20 -f ~/Library/Logs/Claude/mcp*.log` - View server logs

## Code Architecture

### Core Components
- **Server Module** (`server.py`): Main MCP server implementation that handles REST endpoints and tool calls
- **Confluence Module** (`confluence.py`): Handles integration with Confluence API
- **Jira Module** (`jira.py`): Handles integration with Jira API
- **Config Module** (`config.py`): Configuration classes for Atlassian services

### Service Architecture
- The server detects available services (Confluence/Jira) based on provided environment variables
- Resources are exposed as URI handlers using format `confluence://{space_key}` or `jira://{project_key}`
- Tool implementations handle specific API operations (search, get, create, update)
- All operations are performed within the permission scope provided by API tokens

### Configuration
- Configuration is handled through environment variables:
  - Confluence: `CONFLUENCE_URL`, `CONFLUENCE_USERNAME`, `CONFLUENCE_API_TOKEN`
  - Jira: `JIRA_URL`, `JIRA_USERNAME`, `JIRA_API_TOKEN`
- The system supports using either Confluence, Jira, or both services

## Code Style
- **Python**: Follow PEP 8 standards with snake_case for variables/functions
- **Error Handling**: Use try/catch blocks with appropriate error logging
- **Docstrings**: Maintain Google-style docstrings for all public functions and classes
- **Type Hints**: Use Python type annotations throughout the codebase

## Security Guidelines
- Never commit API tokens to version control
- Store all sensitive data in environment variables
- Follow the security best practices outlined in SECURITY.md