# Atlassian MCP Custom Fields Usage Guide

## Overview

The Atlassian MCP server requires two custom fields for Jira issue creation:

1. **Name** (`customfield_10057`): User's name
2. **Dept** (`customfield_10058`): User's department

These fields are required for all issue creation and Epic creation operations to maintain consistent metadata across your Jira instance.

## Handling Custom Fields

### Required Fields

When creating Jira issues or Epics, both Name and Dept fields are required:

```python
# Example: Creating a Jira issue
result = jira_fetcher.create_issue(
    project_key="PROJ",
    summary="Task summary",
    name="John Doe",     # Required
    dept="Engineering"   # Required
)
```

### Global Custom Fields

The Atlassian MCP server now includes tools to make these custom fields available in all projects across your Jira instance.

#### Making Custom Fields Available Globally

Use the `jira_set_custom_fields_global` tool to ensure these fields are available in all projects:

```bash
# Example tool call
jira_set_custom_fields_global
```

This tool will:
1. Create global contexts for both custom fields (if they don't already exist)
2. Make them available to all projects and issue types
3. Return the operation results

#### Automatic Error Handling

If a project doesn't have these custom fields available, the system will:

1. Attempt to create the issue with the custom fields
2. If it fails due to unavailable fields, retry without them
3. Update an internal cache to avoid future errors with the same project
4. Return information about which fields were used

Example response:
```json
{
  "key": "PROJ-123",
  "summary": "Task summary",
  "type": "Task",
  "url": "https://your-domain.atlassian.net/browse/PROJ-123",
  "project": "PROJ",
  "custom_fields_used": {
    "name": true,
    "dept": false
  }
}
```

### Viewing Custom Fields

To view all custom fields in your Jira instance, use the `jira_get_custom_fields` tool:

```bash
# Example tool call
jira_get_custom_fields
```

This will return:
- Details about the Name field
- Details about the Dept field
- A list of all custom fields in your Jira instance

## Technical Details

### How the System Works

1. The system maintains a cache of which projects have which custom fields available
2. On first use, it assumes all custom fields are available
3. If an error occurs, it updates the cache for that project
4. Subsequent operations use this information to avoid errors

### Field IDs

The internal field IDs are defined as constants in the `JiraFetcher` class:

```python
# Define custom field IDs as constants
NAME_FIELD_ID = "customfield_10057"
DEPT_FIELD_ID = "customfield_10058"
```

### Adding Support to Existing Projects

If you have existing projects without these custom fields:

1. Use the `jira_set_custom_fields_global` tool to make them available globally
2. If you have existing screens that need these fields, add them through the Jira admin interface

## Best Practices

1. **Always Provide Values**: Always provide Name and Dept values when creating issues
2. **Run Global Setup**: Run the `jira_set_custom_fields_global` tool when setting up for a new Jira instance
3. **Check Usage Results**: Review the `custom_fields_used` information in responses to ensure fields are being used correctly

## Troubleshooting

If you encounter issues with custom fields:

1. Verify field IDs match your Jira configuration
2. Run `jira_get_custom_fields` to check if your fields exist
3. Run `jira_set_custom_fields_global` to ensure they're globally available
4. Check if your project screens include these fields in their configuration