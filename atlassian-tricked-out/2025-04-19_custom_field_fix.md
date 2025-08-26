# MCP-Atlassian Custom Fields Fix Implementation Plan

## Problem Statement

The MCP-Atlassian server attempts to set custom fields (`customfield_10057` for "name" and `customfield_10058` for "Dept") when creating issues, but these fields fail in certain projects (e.g., ZSHOT) with errors:

```
"Field 'customfield_10057' cannot be set. It is not on the appropriate screen, or unknown."
```

Additionally, we want to:
1. Make these fields required and remove any default values
2. Make sure they error if not provided
3. Make sure the values are not persisted between commands
4. Remove any prefix additions to the issue title

## Analysis of Current Implementation

Based on code examination:

1. The custom fields are already marked as required in the `jira.py` file with appropriate validation:
   ```python
   if name is None:
       raise ValueError("'name' is a required parameter and must be provided")
   if dept is None:
       raise ValueError("'dept' is a required parameter and must be provided")
   ```

2. The tool schemas in `server.py` correctly specify these as required parameters:
   ```python
   "name": {
       "type": "string",
       "description": "REQUIRED: The name value for the custom field"
   },
   "dept": {
       "type": "string",
       "description": "REQUIRED: The department value for the custom field"
   }
   ```

3. The issue with persistent values and title prefixes is not immediately visible in the code, suggesting it might be:
   - In another layer not visible in these files 
   - In the Jira instance configuration
   - In how the MCP tools are being called

4. There are no mechanisms to handle cases where custom fields aren't available in certain projects

## Solution Components

### 1. API Enhancements

Implement these methods in the `JiraFetcher` class:

```python
def get_custom_fields(self):
    """Get all custom fields from the Jira instance."""
    # Use REST API to retrieve custom fields and their contexts
    
def create_global_field_context(self, field_id, name, description):
    """Create a global context for a custom field."""
    # Use the API to create a context with empty projectIds and issueTypeIds
    
def assign_field_to_projects(self, field_id, context_id, project_ids=None):
    """Assign a custom field to specific projects or all projects if None."""
    # Use the API to assign the field to projects
    
def get_field_contexts(self, field_id):
    """Get the contexts for a specific field."""
    # Use the API to get contexts for a field
```

### 2. Error Handling Improvements

1. Add a try/except block to handle cases where custom fields aren't available:

```python
def create_issue(self, project_key, summary, ..., name=None, dept=None):
    # Prepare fields
    fields = {...}
    
    # Try first with custom fields
    try:
        if name is not None:
            fields["customfield_10057"] = [name]
        if dept is not None:
            fields["customfield_10058"] = [dept]
            
        # Make API call
        # ...
    except Exception as e:
        # If error indicates unavailable fields, retry without them
        if "Field 'customfield_10057' cannot be set" in str(e) or "Field 'customfield_10058' cannot be set" in str(e):
            logger.warning(f"Custom fields not available for project {project_key}")
            
            # Remove custom fields and retry
            if "customfield_10057" in fields:
                del fields["customfield_10057"]
            if "customfield_10058" in fields:
                del fields["customfield_10058"]
                
            # Retry API call
            # ...
```

### 3. Remove Title Prefix

Confirm that we're not appending anything to the summary:

```python
# In create_issue function
issue_data = {
    "fields": {
        "project": {
            "key": project_key
        },
        "summary": summary,  # Ensure no prefix is added here
        # ...
    }
}
```

## Implementation Steps

1. Add new methods to `JiraFetcher` class for custom field management
2. Modify create_issue and create_epic to handle unavailable custom fields
3. Test modifications with various projects, especially ZSHOT
4. Document the changes and update relevant API schemas

## Administrative Tasks

1. Run a Jira API call to identify all custom fields:
   ```
   GET /rest/api/3/field
   ```

2. Create global contexts for our custom fields:
   ```
   POST /rest/api/3/field/customfield_10057/context
   {
     "name": "Global name field context",
     "description": "Context for name field that applies to all projects",
     "projectIds": [],
     "issueTypeIds": []
   }
   ```

3. Assign these fields to all relevant projects or make them global

## Testing Plan

1. Test creating issues in MCP project (where fields work)
2. Test creating issues in ZSHOT project (where fields previously failed)
3. Verify that omitting name or dept fields results in appropriate errors
4. Verify that values are not persisted between commands
5. Check that issue titles don't have unexpected prefixes

## Rollback Plan

In case of issues, restore the original code from the repository. The changes are contained to:
- `src/mcp_atlassian/jira.py`
- `src/mcp_atlassian/server.py` (possibly)
