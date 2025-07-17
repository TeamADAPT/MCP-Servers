# Atlassian MCP Server Setup Documentation

## Overview

This document provides comprehensive information about the Atlassian MCP server setup, configuration, and usage. The server integrates Atlassian Cloud products (Jira and Confluence) with the Model Context Protocol (MCP) framework, allowing AI assistants to interact with Atlassian services.

## Server Information

- **Server Name**: github.com/pashpashpash/mcp-atlassian
- **Version**: 0.1.8
- **Working Directory**: /data-nova/ax/DevOps/mcp/mcp-servers/cicd/mcp-atlassian
- **Runtime**: Python 3.11
- **Atlassian Instance**: levelup2x.atlassian.net

## Configuration

### Environment Variables

The server uses the following environment variables for authentication:

```
CONFLUENCE_URL=https://YOUR-CREDENTIALS@YOUR-DOMAIN//levelup2x.atlassian.net
JIRA_USERNAME=chase@levelup2x.com
JIRA_API_TOKEN=YOUR-API-TOKEN-HERE
```

These variables are stored in the `.env` file and are also configured in the MCP settings.

### MCP Settings

The server is configured in two locations:

1. **Local MCP Settings**: `cline_mcp_settings.json` in the project directory
2. **Global MCP Settings**: `/home/x/.config/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json`

Both configurations include:
- Command and arguments to run the server
- Environment variables for authentication
- Auto-approve settings for all tools
- Timeout and transport settings

## Dependencies

The server requires the following Python dependencies:

- atlassian-python-api (v4.0.3)
- beautifulsoup4 (v4.13.3)
- httpx (v0.28.1)
- mcp (v1.6.0)
- python-dotenv (v1.1.0)
- markdownify (v1.1.0)

## Available Tools

### Confluence Tools

| Tool Name | Description |
|-----------|-------------|
| confluence_search | Search Confluence content using CQL |
| confluence_get_page | Get content of a specific Confluence page by ID |
| confluence_get_comments | Get comments for a specific Confluence page |
| confluence_create_page | Create a new Confluence page with markdown content |
| confluence_create_page_from_file | Create a new Confluence page from a markdown file |
| confluence_attach_file | Attach a file to a Confluence page |
| confluence_get_page_history | Get the version history of a Confluence page |
| confluence_restore_page_version | Restore a Confluence page to a previous version |
| confluence_update_page | Update an existing Confluence page |
| confluence_move_page | Move a Confluence page to a different parent or space |
| confluence_get_page_tree | Get a hierarchical tree of pages in a space |

### Jira Tools

| Tool Name | Description |
|-----------|-------------|
| jira_get_issue | Get details of a specific Jira issue |
| jira_search | Search Jira issues using JQL |
| jira_get_project_issues | Get all issues for a specific Jira project |
| jira_create_project | Create a new Jira project |
| jira_create_issue | Create a new Jira issue or subtask |
| jira_get_issue_link_types | Get all available issue link types |
| jira_create_issue_link | Create a link between two Jira issues |
| jira_update_issue | Update an existing Jira issue |
| jira_transition_issue | Transition an issue to a different status |
| jira_add_comment | Add a comment to an issue |
| jira_create_epic | Create a new Epic in Jira |
| jira_get_epic_issues | Get all issues linked to an Epic in a structured format |
| jira_update_epic_progress | Update Epic progress tracking based on linked issues |
| jira_get_issue_attachments | Get all attachments for an issue |
| jira_attach_file_to_issue | Attach a file to a Jira issue |
| jira_get_issue_transitions | Get available transitions for an issue |

## Available Resources

### Confluence Resources

- `confluence://{space_key}`: Access Confluence spaces
- Example: `confluence://ADAPT`

### Jira Resources

- `jira://{project_key}`: Access Jira projects
- Example: `jira://ADAPT`

## Usage Examples

### Searching Jira Issues

```json
{
  "server_name": "github.com/pashpashpash/mcp-atlassian",
  "tool_name": "jira_search",
  "arguments": {
    "jql": "project = ADAPT ORDER BY created DESC",
    "limit": 5
  }
}
```

### Searching Confluence Pages

```json
{
  "server_name": "github.com/pashpashpash/mcp-atlassian",
  "tool_name": "confluence_search",
  "arguments": {
    "query": "type=page AND space=ADAPT",
    "limit": 5
  }
}
```

## Server Management

### Starting the Server

```bash
cd /data-nova/ax/DevOps/mcp/mcp-servers/cicd/mcp-atlassian
python3 -m mcp_atlassian.server
```

### Troubleshooting

If you encounter issues with auto-approve not working:

1. Check both local and global MCP settings files
2. Ensure all tools are listed in the autoApprove array
3. Verify that the server is running
4. Check that the environment variables are correctly set

## Security Considerations

- API tokens are stored in environment variables and MCP settings
- Never share API tokens or commit them to version control
- Use the minimum required permissions for API tokens
- Consider rotating API tokens periodically

## Maintenance

- Update dependencies regularly
- Monitor Atlassian API changes
- Check logs for errors or warnings
- Keep environment variables and MCP settings in sync
