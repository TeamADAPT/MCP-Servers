# Custom Fields Fix Documentation

## Overview

This document details the fix for the custom fields issue in the Jira integration. Previously, two Jira custom fields were hardcoded with default values:

- `customfield_10057` ("name") - hardcoded as ["Stella"]
- `customfield_10058` ("Dept") - hardcoded as ["DevOps-MCP"]

The fix has been implemented to:
1. Remove the hardcoded default values
2. Require users to provide values for each command
3. Throw error messages if fields are not provided
4. Ensure values are not persistent between commands

## Implementation Details

### Files Modified

- `src/mcp_atlassian/jira.py`: Modified to require and use the provided name and dept parameters
- `src/mcp_atlassian/server.py`: Updated schema definitions to require name and dept parameters

### Changes Made

#### In `jira.py`

The `create_issue` and `create_epic` methods were updated to:

1. Include parameter validation:
```python
# Ensure required parameters are provided
if name is None:
    raise ValueError("'name' is a required parameter and must be provided")
if dept is None:
    raise ValueError("'dept' is a required parameter and must be provided")
```

2. Use the provided values instead of hardcoded defaults:
```python
# Add custom fields with values provided by user
"customfield_10057": [name],  # Name field
"customfield_10058": [dept]   # Dept field
```

#### In `server.py`

The tool schemas for `jira_create_issue` and `jira_create_epic` were updated to include name and dept as required parameters:

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

Both parameters were added to the `required` array to ensure they are mandatory.

## Testing

A comprehensive test script (`test_custom_fields.py`) was created to verify the fix. It includes tests for:

1. Verifying that name is required for create_issue and create_epic
2. Verifying that dept is required for create_issue and create_epic
3. Verifying that the methods accept and use the provided values correctly

All tests pass, confirming that the custom fields fix has been properly implemented.

## Usage Examples

### Creating a Jira Issue

```python
result = jira_fetcher.create_issue(
    project_key="ADAPT",
    summary="Test Issue",
    name="Custom-Name-Value",  # Required
    dept="Custom-Dept-Value"   # Required
)
```

### Creating a Jira Epic

```python
result = jira_fetcher.create_epic(
    project_key="ADAPT",
    summary="Test Epic",
    epic_name="Epic Name",
    name="Custom-Name-Value",  # Required
    dept="Custom-Dept-Value"   # Required
)
```

## Error Handling

When the required parameters are not provided, appropriate error messages are thrown:

- For missing name: `'name' is a required parameter and must be provided`
- For missing dept: `'dept' is a required parameter and must be provided`

## Integration with MCP Server

The server tool schemas have been updated to ensure the parameters are validated at the API level before being passed to the methods. This ensures:

1. Consistency in API validation and method validation
2. Clear error messages for users
3. Proper documentation of the required parameters

## Additional Notes

- The fix ensures that values must be provided for each command, preventing persistence between commands
- The parameter validation happens in both server.py (schema validation) and jira.py (method validation)
- The test suite verifies both negative cases (missing parameters) and positive cases (providing parameters)
EOF < /dev/null
