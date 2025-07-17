# Enhanced Jira Integration

## Overview

The Enhanced Jira Integration provides advanced features for working with Jira, including:

- Comprehensive custom field management
- Caching system for performance improvements
- Bulk operations for issues and links
- Project health analysis and reporting
- Improved error handling with retry logic

## Feature Flags

Enhanced Jira Integration is controlled by feature flags, allowing for conditional enablement. By default, 
the feature is disabled until explicitly enabled through environment variables.

### Enabling Enhanced Jira

To enable the Enhanced Jira feature, set one of the following environment variables:

```bash
# Option 1: Set the specific feature flag
export MCP_ATLASSIAN_ENABLE_ENHANCED_JIRA="true"

# Option 2: Enable multiple features at once
export MCP_ATLASSIAN_FEATURE_FLAGS="ENHANCED_JIRA,BITBUCKET_INTEGRATION"
```

### Feature Flag Management

The feature flags system provides runtime control over features:

```python
from mcp_atlassian.feature_flags import is_enabled, enable_feature, disable_feature

# Check if a feature is enabled
if is_enabled("ENHANCED_JIRA"):
    # Use enhanced Jira features
    
# Enable a feature at runtime
enable_feature("ENHANCED_JIRA")

# Disable a feature at runtime
disable_feature("ENHANCED_JIRA")
```

## Custom Field Management

Enhanced Jira Manager handles custom fields for issues and epics:

```python
from mcp_atlassian.enhanced_jira import EnhancedJiraManager

# Initialize the manager
manager = EnhancedJiraManager(url="https://your-jira-instance.com", 
                              username="your-username", 
                              api_token="your-token")

# Create issue with custom fields
issue = manager.create_issue(
    project_key="PROJ",
    summary="Task with custom fields",
    description="This is a task with custom fields",
    issue_type="Task",
    custom_fields={
        "Department": "Engineering",
        "Team": "Platform",
        "Priority Score": 80
    }
)
```

## Tools

The Enhanced Jira integration provides the following tools through the MCP interface:

- `jira_enhanced_create_issue`: Create an issue with custom fields
- `jira_enhanced_create_epic`: Create an epic with custom fields
- `jira_enhanced_update_issue`: Update an issue with custom fields
- `jira_enhanced_get_issue`: Get an issue with all fields
- `jira_enhanced_search_issues`: Search for issues with advanced filtering
- `jira_enhanced_link_issues`: Create links between issues
- `jira_enhanced_get_project_health`: Get project health metrics
- `jira_enhanced_bulk_create_issues`: Create multiple issues in one operation
- `jira_enhanced_bulk_update_issues`: Update multiple issues in one operation

## Troubleshooting

If you encounter any issues with the Enhanced Jira Integration, run the diagnostics script:

```bash
python -m mcp_atlassian.diagnostics
```

This will check for common issues and provide recommendations for resolving them.

## Dependencies

The Enhanced Jira Integration requires the following dependencies:

- `httpx`: For HTTP requests
- `requests`: For HTTP requests
- `idna>=3.4`: For internationalized domain names
- `pydantic`: For data validation
- `atlassian-python-api`: For Atlassian API integration
- `jira`: For Jira API integration
EOF < /dev/null
