# MCP-Atlassian: Comprehensive Atlassian Cloud Integration

A powerful Model Context Protocol (MCP) server providing comprehensive integration with the Atlassian ecosystem, including Jira, Confluence, Jira Service Management (JSM), and Bitbucket.

## Features

### Core Integration
- 🔄 **Unified API**: Seamless integration with all Atlassian products
- 🔒 **Enterprise Authentication**: OAuth 2.0 support with token management
- 📊 **Comprehensive Logging**: Detailed audit trails and error tracking
- ⚡ **Performance Optimized**: Efficient API usage with caching and batching

### Jira Integration
- 🎫 **Issue Management**: Complete issue lifecycle management
- 📝 **Custom Fields**: Global custom field management
- 🔍 **Advanced Search**: Powerful JQL-based search capabilities
- 🏃‍♀️ **Workflow Control**: Transition and status management

### Confluence Integration
- 📄 **Content Management**: Comprehensive page and content operations
- 🏢 **Space Management**: Advanced space creation and configuration
- 📚 **Templates & Blueprints**: Template-based content creation
- 🧩 **Macro Support**: Advanced formatting with macro embedding

### Jira Service Management (JSM)
- 🛎️ **Service Desk**: Complete service desk management
- 🙋 **Request Handling**: Customer request operations
- ⏱️ **SLA Tracking**: Service level agreement monitoring
- ✅ **Approvals**: Multi-step approval workflows

### Bitbucket Integration
- 📁 **Repository Management**: Complete repository operations
- 🔀 **Pull Requests**: Full pull request lifecycle
- 🔄 **CI/CD Pipelines**: Build and deployment management
- 🛡️ **Code Security**: Branch protection and permissions

### Enterprise Features
- 📊 **Advanced Analytics**: Cross-product insights and reporting
- 🤖 **AI Capabilities**: Smart classification and content suggestions
- 🔌 **App Marketplace Integration**: Third-party app support
- 🛡️ **Enhanced Security**: Rate limiting and circuit breakers

## Installation

### Prerequisites
- Python 3.10+
- Atlassian Cloud account with API access
- API tokens for each Atlassian service you want to use

### Installation Steps

```bash
# Clone the repository
git clone https://YOUR-CREDENTIALS@YOUR-DOMAIN//your-domain.atlassian.net
CONFLUENCE_USERNAME=your-email@example.com
CONFLUENCE_API_TOKEN=YOUR-API-TOKEN-HERE
```

### JSM Configuration
```
# JSM Configuration 
# (can use Jira credentials if not specified)
JSM_URL=https://YOUR-CREDENTIALS@YOUR-DOMAIN//api.bitbucket.org/2.0
BITBUCKET_USERNAME=your-username
BITBUCKET_APP_PASSWORD=your-app-password
```

### Enterprise Features Configuration
```
# Enterprise Features
ENABLE_ANALYTICS=true
ENABLE_AI_CAPABILITIES=true
ENABLE_MARKETPLACE_INTEGRATION=true
```

## Usage Examples

### Jira Issue Creation

```python
from mcp.client import MCPClient

client = MCPClient("http://localhost:8080")
response = client.call_tool("jira_create_issue", {
    "project_key": "PROJ",
    "summary": "Fix login issue",
    "description": "Users are experiencing login failures",
    "issue_type": "Bug",
    "priority": "High",
    "name": "Jane Smith",
    "dept": "Engineering"
})

print(f"Created issue: {response['key']}")
```

### Confluence Page Creation

```python
from mcp.client import MCPClient

client = MCPClient("http://localhost:8080")
response = client.call_tool("confluence_create_page", {
    "space_key": "TEAM",
    "title": "Project Planning",
    "content": "# Project Planning\n\nThis page contains project planning information.",
    "parent_id": "123456"
})

print(f"Created page: {response['page_id']}")
```

### JSM Service Request Creation

```python
from mcp.client import MCPClient

client = MCPClient("http://localhost:8080")
response = client.call_tool("jsm_create_customer_request", {
    "service_desk_id": "10",
    "request_type_id": "25",
    "summary": "Need access to database",
    "description": "I require access to the production database for troubleshooting.",
    "name": "John Doe",
    "dept": "Support"
})

print(f"Created request: {response['issueKey']}")
```

### Bitbucket Pull Request Creation

```python
from mcp.client import MCPClient

client = MCPClient("http://localhost:8080")
response = client.call_tool("bitbucket_create_pull_request", {
    "repository": "project/repo",
    "source_branch": "feature/new-feature",
    "destination_branch": "main",
    "title": "Add new feature",
    "description": "This PR adds the new feature with tests"
})

print(f"Created PR: {response['id']}")
```

## Available Tools

See the [Tools Documentation](docs/TOOLS.md) for a complete list of available tools and their parameters.

## Architecture

MCP-Atlassian follows a modular architecture:

- **Core Server**: Handles MCP protocol communication
- **Service Managers**: Dedicated classes for each Atlassian service
- **Tool Registration**: Exposes functionality through standardized tools
- **Authentication**: Handles secure authentication with all services

## Documentation

- [Setup Guide](docs/SETUP.md): Detailed installation and setup instructions
- [Tools Documentation](docs/TOOLS.md): Complete list of available tools
- [API Reference](docs/API_REFERENCE.md): Detailed API documentation
- [Usage Guides](docs/guides/): Detailed guides for each component
- [Administration](docs/admin/): Guides for administrators
- [Development](docs/development/): Guide for developers extending the server

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.