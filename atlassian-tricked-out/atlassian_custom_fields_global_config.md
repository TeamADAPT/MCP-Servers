# Extending Atlassian MCP Server: Global Custom Fields Configuration

## Background

Currently, the MCP-Atlassian server attempts to set custom fields (`customfield_10057` for "name" and `customfield_10058` for "Dept") when creating issues, but these fields fail in certain projects (e.g., ZSHOT) with an error:

```
"Field 'customfield_10057' cannot be set. It is not on the appropriate screen, or unknown."
```

This happens because custom fields in Jira are context-specific - they're only available to projects and issue types defined in their "contexts".

## Proposed Solution

Extend the MCP-Atlassian server to:

1. Create a global context for these custom fields (or modify their existing contexts)
2. Make them available to all projects and issue types
3. Add conditional handling for projects where fields are unavailable

## Implementation Details

### 1. Custom Field Context API Endpoints

Jira REST API v3 provides endpoints for managing custom field contexts:

- **Create custom field context**: `POST /rest/api/3/field/{fieldId}/context`
- **Get custom field contexts**: `GET /rest/api/3/field/{fieldId}/context`
- **Assign contexts to projects**: `PUT /rest/api/3/field/{fieldId}/context/{contextId}/project`

### 2. Creating a Global Context

To create a global context (applies to all projects and issue types):

```javascript
// Example request body
const globalContextBody = {
  "description": "Global context for name field",
  "name": "Global name field context",
  "projectIds": [],  // Empty array = apply to all projects
  "issueTypeIds": [] // Empty array = apply to all issue types
};

// API call
const response = await api.asUser().request({
  method: 'POST',
  url: `/rest/api/3/field/customfield_10057/context`,
  headers: { 'Content-Type': 'application/json' },
  body: globalContextBody
});
```

### 3. Required Permissions

- **Classic**: `manage:jira-configuration`
- **Granular**: `read:field:jira`, `write:field:jira`, `read:custom-field-contextual-configuration:jira`
- **Required scope**: `ADMIN`

This requires administrator-level privileges in the Jira instance.

## New MCP Tools to Implement

1. **get_custom_field_ids**: List all custom fields in the Jira instance
2. **get_custom_field_contexts**: Get contexts for a specific custom field
3. **create_global_custom_field_context**: Create a global context for a custom field
4. **assign_custom_field_to_all_projects**: Make a custom field available in all projects

## Code Implementation Plan

### 1. Add New Methods to JiraFetcher Class

```python
def get_custom_fields(self):
    """Get all custom fields from the Jira instance."""
    # Use REST API to retrieve all fields and filter for custom fields
    
def create_global_field_context(self, field_id, name, description):
    """Create a global context for a custom field."""
    # Use REST API to create a context with empty projectIds and issueTypeIds
    
def assign_field_to_projects(self, field_id, context_id, project_ids=None):
    """Assign a custom field to specific projects or all projects if None."""
    # Use REST API to assign the field to projects
```

### 2. Add Conditional Handling in create_issue Method

```python
def create_issue(self, project_key, summary, ..., name=None, dept=None):
    # Prepare fields
    fields = {...}
    
    # Only add custom fields if they are required AND available for this project
    try:
        # First try with custom fields
        if name is not None:
            fields["customfield_10057"] = [name]
        if dept is not None:
            fields["customfield_10058"] = [dept]
            
        # Make API call
        # ...
    except Exception as e:
        # If error indicates unavailable fields, retry without those fields
        if "Field 'customfield_10057' cannot be set" in str(e) or "Field 'customfield_10058' cannot be set" in str(e):
            # Log warning
            logger.warning(f"Custom fields not available for project {project_key}, retrying without them")
            
            # Remove custom fields
            if "customfield_10057" in fields:
                del fields["customfield_10057"]
            if "customfield_10058" in fields:
                del fields["customfield_10058"]
                
            # Retry API call
            # ...
        else:
            # If error is not related to custom fields, re-raise
            raise
```

## Future Extensions

In addition to these changes, we should consider other Atlassian tools to extend:

1. **Jira Service Management**: Add support for service desk operations
2. **Advanced Jira workflows**: Add support for custom workflows and transitions
3. **Atlassian Marketplace Apps**: Add support for popular apps via their APIs

## Implementation Timeframe

The proposed changes can be implemented in approximately 2-3 days:
- Day 1: Research and implement custom field context methods
- Day 2: Add conditional handling and test with different projects
- Day 3: Documentation and refinement
