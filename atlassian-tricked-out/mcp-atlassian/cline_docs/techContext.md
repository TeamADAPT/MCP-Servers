# Technical Context

## Technology Stack
- Python 3.11
- Atlassian API (Jira, Confluence)
- MCP (Model Context Protocol) v1.6.0

## Dependencies
- atlassian-python-api (v4.0.3): For Atlassian API interaction
- beautifulsoup4 (v4.13.3): For HTML parsing
- httpx (v0.28.1): For HTTP requests
- mcp (v1.6.0): For MCP server implementation
- python-dotenv (v1.1.0): For environment variable management
- markdownify (v1.1.0): For HTML to Markdown conversion

## Architecture
- Server component with MCP interface
- Jira integration module (src/mcp_atlassian/jira.py)
- Confluence integration module (src/mcp_atlassian/confluence.py)
- Configuration and preprocessing utilities (src/mcp_atlassian/config.py, src/mcp_atlassian/preprocessing.py)
- Document types for data representation (src/mcp_atlassian/document_types.py)

## Development Environment
- Working Directory: /data-nova/ax/DevOps/mcp/mcp-servers/cicd/mcp-atlassian
- Environment variables for configuration (stored in .env file)
- MCP settings in JSON format (cline_mcp_settings.json)
- Development mode installation for local testing

## Deployment
- Docker containerization available (Dockerfile present)
- Environment variable configuration
- MCP server registration in cline_mcp_settings.json
- Server command: python3 -m mcp_atlassian.server
