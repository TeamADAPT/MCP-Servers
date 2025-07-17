# MCP-Atlassian: Comprehensive Setup Documentation

## Overview

This document provides detailed setup instructions for the enhanced MCP-Atlassian server. This server integrates the full Atlassian Cloud ecosystem (Jira, Confluence, Jira Service Management, and Bitbucket) with the Model Context Protocol (MCP) framework, allowing AI assistants to interact with all Atlassian services with enterprise-grade features.

## Server Information

- **Server Name**: github.com/pashpashpash/mcp-atlassian
- **Version**: 0.3.0 (Enhanced Edition)
- **Working Directory**: /data-nova/ax/DevOps/mcp/mcp-servers/cicd/mcp-atlassian
- **Runtime**: Python 3.11+
- **Atlassian Instance**: Your Atlassian Cloud instance (e.g., yourcompany.atlassian.net)

## Configuration

### Environment Variables

The enhanced server uses a comprehensive set of environment variables for configuration:

```bash
# Core Configuration
MCP_PORT=8080
MCP_HOST=localhost
MCP_LOG_LEVEL=INFO

# Jira Configuration
JIRA_URL=https://YOUR-CREDENTIALS@YOUR-DOMAIN//your-domain.atlassian.net/wiki
CONFLUENCE_USERNAME=your-email@example.com
CONFLUENCE_API_TOKEN=YOUR-API-TOKEN-HERE

# JSM Configuration (optional, can use Jira credentials)
JSM_URL=https://YOUR-CREDENTIALS@YOUR-DOMAIN//api.bitbucket.org/2.0
BITBUCKET_USERNAME=your-username
BITBUCKET_APP_PASSWORD=your-app-password

# Enterprise Features (optional)
ENABLE_ANALYTICS=true
ENABLE_AI_CAPABILITIES=true
ENABLE_MARKETPLACE_INTEGRATION=true
ENABLE_ENHANCED_CONFLUENCE=true

# OAuth Configuration (for enterprise features)
ATLASSIAN_CLIENT_ID=your-oauth-client-id
ATLASSIAN_CLIENT_SECRET=your-oauth-client-secret
OAUTH_REDIRECT_URL=http://localhost:8080/oauth/callback

# Security Configuration
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60
CIRCUIT_BREAKER_THRESHOLD=5
CIRCUIT_BREAKER_TIMEOUT=30
```

These variables should be stored in a `.env` file in the project root directory and can also be configured in the MCP settings.

### MCP Settings

The server can be configured in two locations:

1. **Local MCP Settings**: `cline_mcp_settings.json` in the project directory
2. **Global MCP Settings**: Usually found in the Claude IDE configuration directory

Both configurations should include:
- Command and arguments to run the server
- Environment variables for authentication
- Auto-approve settings for all tools
- Timeout and transport settings

#### Sample MCP Settings

```json
{
  "servers": {
    "github.com/pashpashpash/mcp-atlassian": {
      "command": "python3",
      "args": ["-m", "src.mcp_atlassian.server"],
      "cwd": "/path/to/mcp-atlassian",
      "env": {
        "JIRA_URL": "https://YOUR-CREDENTIALS@YOUR-DOMAIN//your-domain.atlassian.net/wiki",
        "CONFLUENCE_USERNAME": "your-email@example.com",
        "CONFLUENCE_API_TOKEN": "your-api-token",
        "BITBUCKET_URL": "https://api.bitbucket.org/2.0",
        "BITBUCKET_USERNAME": "your-username",
        "BITBUCKET_APP_PASSWORD": "your-app-password",
        "ENABLE_ANALYTICS": "true",
        "ENABLE_AI_CAPABILITIES": "true",
        "ENABLE_ENHANCED_CONFLUENCE": "true"
      },
      "autoApprove": ["*"],
      "timeout": 30000,
      "transport": "stdio"
    }
  }
}

## Dependencies

The enhanced server requires the following Python dependencies:

- atlassian-python-api (v4.0.3+)
- beautifulsoup4 (v4.13.3+)
- httpx (v0.28.1+)
- mcp (v1.6.0+)
- python-dotenv (v1.1.0+)
- markdownify (v1.1.0+)
- jwt (v2.6.0+)
- requests (v2.28.0+)
- pydantic (v2.0.0+)
- langchain (v0.0.300+, for AI capabilities)
- redis (v4.5.5+, for caching)

## Installation

To install all dependencies, run:

```bash
pip install -r requirements.txt
```

Or if you prefer to use Poetry:

```bash
poetry install
```

## Available Tools

The enhanced MCP-Atlassian server provides over 100 tools across all Atlassian products. Here's a summary of the main tool categories:

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

### Enhanced Confluence Tools

| Tool Name | Description |
|-----------|-------------|
| confluence_space_create | Create a new Confluence space with templates |
| confluence_space_archive | Archive an existing Confluence space |
| confluence_space_restore | Restore an archived Confluence space |
| confluence_space_get_settings | Get space settings and permissions |
| confluence_templates_list | List available page templates |
| confluence_templates_create | Create a new page template |
| confluence_templates_apply | Apply a template to a page |
| confluence_content_analyze | Analyze content using AI capabilities |
| confluence_content_extract_structure | Extract structure from a page |
| confluence_content_generate | Generate content using AI |

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
| jira_set_custom_fields_global | Configure custom fields globally |
| jira_get_custom_fields | Get a list of all custom fields |

### Jira Service Management (JSM) Tools

| Tool Name | Description |
|-----------|-------------|
| jsm_get_service_desks | Get all service desks |
| jsm_get_service_desk | Get details of a specific service desk |
| jsm_get_request_types | Get all request types for a service desk |
| jsm_get_request_type | Get details of a specific request type |
| jsm_create_customer_request | Create a new customer request |
| jsm_get_customer_request | Get details of a specific customer request |
| jsm_get_customer_requests | Get all customer requests for a service desk |
| jsm_add_request_comment | Add a comment to a customer request |
| jsm_get_request_status | Get the status of a customer request |
| jsm_get_request_participants | Get participants of a customer request |
| jsm_add_request_participants | Add participants to a customer request |
| jsm_get_request_fields | Get fields for a request type |
| jsm_get_queues | Get all queues for a service desk |
| jsm_get_queue_issues | Get all issues in a queue |
| jsm_get_organizations | Get all organizations |
| jsm_get_knowledge_base | Get knowledge base articles |

### Bitbucket Tools

| Tool Name | Description |
|-----------|-------------|
| bitbucket_list_repositories | List all repositories in the workspace |
| bitbucket_get_repository | Get details of a specific repository |
| bitbucket_create_repository | Create a new repository |
| bitbucket_update_repository | Update an existing repository |
| bitbucket_delete_repository | Delete a repository |
| bitbucket_list_branches | List all branches in a repository |
| bitbucket_get_branch | Get details of a specific branch |
| bitbucket_create_branch | Create a new branch |
| bitbucket_delete_branch | Delete a branch |
| bitbucket_list_commits | List commits in a repository |
| bitbucket_get_commit | Get details of a specific commit |
| bitbucket_get_commit_diff | Get the diff for a specific commit |
| bitbucket_list_pull_requests | List pull requests in a repository |
| bitbucket_get_pull_request | Get details of a specific pull request |
| bitbucket_create_pull_request | Create a new pull request |
| bitbucket_update_pull_request | Update an existing pull request |
| bitbucket_merge_pull_request | Merge a pull request |
| bitbucket_decline_pull_request | Decline a pull request |
| bitbucket_approve_pull_request | Approve a pull request |
| bitbucket_get_pipeline_config | Get the pipeline configuration |
| bitbucket_enable_pipelines | Enable pipelines for a repository |
| bitbucket_run_pipeline | Run a pipeline on a branch |

### Enterprise Tools

| Tool Name | Description |
|-----------|-------------|
| analytics_get_user_activity | Get user activity metrics |
| analytics_get_project_metrics | Get project performance metrics |
| analytics_generate_report | Generate a comprehensive activity report |
| ai_classify_issue | Classify an issue using AI |
| ai_suggest_related_issues | Suggest related issues using AI |
| ai_summarize_content | Summarize content using AI |
| ai_generate_content | Generate content for documentation |
| app_marketplace_search | Search the Atlassian Marketplace |
| app_marketplace_get_app | Get details of a specific Marketplace app |
| security_configure_rate_limiting | Configure rate limiting settings |
| security_configure_circuit_breaker | Configure circuit breaker settings |
| security_audit_log | Get security audit logs |

## Available Resources

The enhanced MCP-Atlassian server provides access to a wide range of resources across all Atlassian products:

### Confluence Resources

- `confluence://{space_key}`: Access Confluence spaces
  - Example: `confluence://DOCS`
- `confluence://{space_key}/pages/{title}`: Access specific Confluence pages
  - Example: `confluence://DOCS/pages/Project Guidelines`

### Jira Resources

- `jira://{project_key}`: Access Jira projects
  - Example: `jira://PROJ`
- `jira://{project_key}/issues/{issue_key}`: Access specific Jira issues
  - Example: `jira://PROJ/issues/PROJ-123`

### Bitbucket Resources

- `bitbucket://{repo_slug}`: Access Bitbucket repositories
  - Example: `bitbucket://api-service`
- `bitbucket://{repo_slug}/branches/{branch_name}`: Access specific branches
  - Example: `bitbucket://api-service/branches/feature/login`
- `bitbucket://{repo_slug}/pullrequests/{pr_id}`: Access specific pull requests
  - Example: `bitbucket://api-service/pullrequests/123`

### JSM Resources

- `jsm://{service_desk_id}`: Access JSM service desks
  - Example: `jsm://10`
- `jsm://{service_desk_id}/requests/{request_id}`: Access specific customer requests
  - Example: `jsm://10/requests/123`
- `jsm://{service_desk_id}/knowledge`: Access knowledge base for a service desk
  - Example: `jsm://10/knowledge`

## Usage Examples

### Basic Operations

#### Searching Jira Issues

```json
{
  "server_name": "github.com/pashpashpash/mcp-atlassian",
  "tool_name": "jira_search",
  "arguments": {
    "jql": "project = PROJ AND status = 'In Progress' ORDER BY priority DESC",
    "limit": 10
  }
}
```

#### Creating a Confluence Page

```json
{
  "server_name": "github.com/pashpashpash/mcp-atlassian",
  "tool_name": "confluence_create_page",
  "arguments": {
    "space_key": "DOCS",
    "title": "Project Guidelines",
    "content": "# Project Guidelines\n\nThis document outlines standard project guidelines...",
    "parent_id": "12345"
  }
}
```

### Advanced Operations

#### Creating an Epic with Linked Stories

```json
{
  "server_name": "github.com/pashpashpash/mcp-atlassian",
  "tool_name": "jira_create_epic",
  "arguments": {
    "project_key": "PROJ",
    "summary": "Authentication System Redesign",
    "description": "Implement a new OAuth2-based authentication system",
    "epic_name": "Auth Redesign",
    "name": "Jane Doe",
    "dept": "Engineering"
  }
}
```

Then create and link stories:

```json
{
  "server_name": "github.com/pashpashpash/mcp-atlassian",
  "tool_name": "jira_create_issue",
  "arguments": {
    "project_key": "PROJ",
    "summary": "Implement OAuth2 Provider Integration",
    "description": "Integrate with OAuth2 providers like Google and GitHub",
    "issue_type": "Story",
    "epic_link": "PROJ-123",
    "name": "Jane Doe",
    "dept": "Engineering"
  }
}
```

#### Working with Bitbucket Repositories

```json
{
  "server_name": "github.com/pashpashpash/mcp-atlassian",
  "tool_name": "bitbucket_create_branch",
  "arguments": {
    "repo_slug": "api-service",
    "branch_name": "feature/oauth-integration",
    "target_hash": "a1b2c3d4e5f6"
  }
}
```

#### Creating a JSM Customer Request

```json
{
  "server_name": "github.com/pashpashpash/mcp-atlassian",
  "tool_name": "jsm_create_customer_request",
  "arguments": {
    "service_desk_id": "10",
    "request_type_id": "25",
    "summary": "Need Database Access",
    "description": "I require read access to the production database for troubleshooting."
  }
}
```

#### Generating Analytics Reports

```json
{
  "server_name": "github.com/pashpashpash/mcp-atlassian",
  "tool_name": "analytics_generate_report",
  "arguments": {
    "report_type": "project_performance",
    "project_key": "PROJ",
    "start_date": "2025-01-01",
    "end_date": "2025-05-01",
    "include_metrics": ["velocity", "cycle_time", "defect_rate"]
  }
}
```

#### Utilizing AI Capabilities

```json
{
  "server_name": "github.com/pashpashpash/mcp-atlassian",
  "tool_name": "ai_suggest_related_issues",
  "arguments": {
    "issue_key": "PROJ-123",
    "max_suggestions": 5
  }
}
```

## Server Management

### Starting the Server

```bash
# Navigate to the project directory
cd /path/to/mcp-atlassian

# Start the server using the module
python3 -m src.mcp_atlassian.server
```

### Monitoring Logs

The server logs activity to the following locations:

```bash
# Main server logs
cat logs/mcp-atlassian.log

# Authentication audit logs
cat logs/auth-audit-*.log

# Analytics logs (if enabled)
cat logs/analytics-*.log
```

### Stopping the Server

The server can be stopped with Ctrl+C in the terminal where it's running, or by sending a SIGTERM signal:

```bash
# Find the PID
ps aux | grep "[p]ython.*mcp_atlassian.server"

# Stop the server
kill <PID>
```

### Restarting the Server

After making configuration changes, restart the server:

```bash
# Stop the current server (if running)
kill $(ps aux | grep "[p]ython.*mcp_atlassian.server" | awk '{print $2}')

# Start the server again
python3 -m src.mcp_atlassian.server
```

## Troubleshooting

### Common Issues

#### Auto-Approve Not Working

If you encounter issues with auto-approve not working:

1. Check both local and global MCP settings files
2. Ensure all tools are listed in the autoApprove array or use `["*"]` to approve all
3. Verify that the server is running
4. Check that the environment variables are correctly set

#### Connection Errors

If the server fails to connect to Atlassian services:

1. Verify API tokens and credentials
2. Check network connectivity
3. Ensure Atlassian URLs are correct
4. Inspect logs for detailed error messages

#### Permission Issues

If you see permission errors in the logs:

1. Ensure the account has the necessary permissions in Atlassian
2. Check that API tokens have the required scopes
3. Verify that file paths for logs and cache are writable

#### Module Import Errors

If you encounter import errors:

1. Verify all dependencies are installed
2. Check Python version compatibility
3. Ensure optional modules are properly handled in the code

## Security Considerations

### API Token Security

- Store API tokens in environment variables or secure credential stores
- Never commit tokens to version control
- Use the minimum required permissions for API tokens
- Rotate API tokens every 90 days

### Rate Limiting and Circuit Breakers

- Configure appropriate rate limits to prevent API abuse
- Implement circuit breakers to prevent cascading failures
- Monitor API usage to stay within Atlassian limits

### Audit Logging

- Enable comprehensive audit logging for security-sensitive operations
- Review logs regularly for suspicious activity
- Configure log rotation to manage disk space

### OAuth Configuration

For enterprise features using OAuth:

- Use a secure OAuth redirect URL
- Store client secrets securely
- Implement proper token refresh mechanisms

## Advanced Configuration

### Performance Tuning

For high-traffic environments:

```bash
# Increase cache size
CACHE_SIZE_MB=256

# Configure connection pooling
CONNECTION_POOL_SIZE=20

# Enable response caching
ENABLE_RESPONSE_CACHE=true
CACHE_TTL=300
```

### Custom Implementation Extensions

The server supports custom extensions:

1. Create a new module in the `src/mcp_atlassian/extensions/` directory
2. Implement the required interface
3. Register the extension in `src/mcp_atlassian/server.py`

## Maintenance

### Regular Updates

- Update dependencies regularly
- Monitor Atlassian API changes
- Apply security patches promptly
- Check logs for errors or warnings
- Keep environment variables and MCP settings in sync

### Monitoring Health

Set up monitoring for:

- Server process uptime
- Log file growth
- API call response times
- Rate limit usage
- Authentication failures

## Additional Resources

- [Full API Documentation](docs/API_REFERENCE.md)
- [User Guide](USER_GUIDE.md)
- [Roadmap](ROADMAP.md)
- [Changelog](CHANGELOG.md)
- [Security Policy](SECURITY.md)

---

## Support and Community

- Report issues on GitHub
- Join the community Discord server
- Check the wiki for common questions
- Contact commercial support for enterprise users

---

This setup guide provides everything needed to get the enhanced MCP-Atlassian server running. For more detailed information, please refer to the documentation in the `docs` directory.
