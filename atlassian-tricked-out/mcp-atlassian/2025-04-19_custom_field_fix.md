# MCP-Atlassian Custom Fields Fix Documentation

**Date**: April 19, 2025
**Time**: 3:44 PM (America/Phoenix, UTC-7:00)

## Issue Summary

The Atlassian MCP server has hardcoded default values for two custom fields:
- `customfield_10057` ("name") - currently hardcoded as `["Stella"]`
- `customfield_10058` ("Dept") - currently hardcoded as `["DevOps-MCP"]`

These fields need to be modified to:
1. Remove the default values
2. Require users to provide values for each command
3. Throw an error message if the fields are not provided
4. Ensure values are not persistent between commands

## Identified Locations of Hardcoded Values

### 1. In `src/mcp_atlassian/jira.py`:

#### A. In the `create_issue` method (around line 440):
```python
# Add "Stella:" prefix to the summary
stella_summary = f"Stella: {summary}"

# Create issue data with custom fields
issue_data = {
    "fields": {
        "project": {
            "key": project_key
        },
        "summary": stella_summary,
        "issuetype": {
            "name": issue_type
        },
        "priority": {
            "name": priority
        },
        # Add custom fields with correct IDs (as arrays of strings)
        "customfield_10057": ["Stella"],  # Name field
        "customfield_10058": ["DevOps-MCP"]  # Dept field
    }
}
```

#### B. In the `create_epic` method (around line 677):
```python
# Add "Stella:" prefix to the summary
stella_summary = f"Stella: {summary}"

# Create Epic data with custom fields
epic_data = {
    "fields": {
        "project": {
            "key": project_key
        },
        "summary": stella_summary,
        "issuetype": {
            "name": "Epic"
        },
        "priority": {
            "name": priority
        },
        # Add custom fields with correct IDs
        "customfield_10057": ["Stella"],  # Name field
        "customfield_10058": ["DevOps-MCP"],  # Dept field
        "customfield_10011": epic_name  # Epic Name field
    }
}
```

### 2. In `src/mcp_atlassian/server.py`:
The tool schemas for `jira_create_issue` and `jira_create_epic` don't expose these fields as parameters, making it impossible for users to customize them.

## Required Changes

### 1. Modify `jira.py`:

#### A. Update `create_issue` method:
```python
def create_issue(self, project_key: str, summary: str, issue_type: str = "Task", 
                description: str = "", labels: List[str] = None, 
                priority: str = "Medium", parent_key: str = None, epic_link: str = None,
                name: str = None, dept: str = None) -> dict:
    """
    Create a new Jira issue or subtask.
    
    Args:
        # [existing parameters]
        name: (REQUIRED) The name value for the custom field
        dept: (REQUIRED) The department value for the custom field
        
    Returns:
        Dictionary containing the created issue details
    """
    try:
        # Ensure required parameters are provided
        if name is None:
            raise ValueError("'name' is a required parameter and must be provided")
        if dept is None:
            raise ValueError("'dept' is a required parameter and must be provided")
            
        # [existing code]
        
        # Create issue data with custom fields provided by user
        issue_data = {
            "fields": {
                "project": {
                    "key": project_key
                },
                "summary": summary,  # Remove Stella prefix
                "issuetype": {
                    "name": issue_type
                },
                "priority": {
                    "name": priority
                },
                # Add custom fields with values provided by user
                "customfield_10057": [name],  # Name field
                "customfield_10058": [dept]   # Dept field
            }
        }
        
        # [rest of function remains the same]
    }
```

#### B. Update `create_epic` method:
```python
def create_epic(self, project_key: str, summary: str, description: str = "", 
               priority: str = "Medium", epic_name: Optional[str] = None, 
               epic_color: Optional[str] = None, name: str = None, dept: str = None) -> dict:
    """
    Create a new Epic in Jira.
    
    Args:
        # [existing parameters]
        name: (REQUIRED) The name value for the custom field
        dept: (REQUIRED) The department value for the custom field
        
    Returns:
        Dictionary containing the created Epic details
    """
    try:
        # Ensure required parameters are provided
        if name is None:
            raise ValueError("'name' is a required parameter and must be provided")
        if dept is None:
            raise ValueError("'dept' is a required parameter and must be provided")
            
        # [existing code]
        
        # Create Epic data with custom fields provided by user
        epic_data = {
            "fields": {
                "project": {
                    "key": project_key
                },
                "summary": summary,  # Remove Stella prefix
                "issuetype": {
                    "name": "Epic"
                },
                "priority": {
                    "name": priority
                },
                # Add custom fields with values provided by user
                "customfield_10057": [name],  # Name field
                "customfield_10058": [dept],  # Dept field
                "customfield_10011": epic_name  # Epic Name field
            }
        }
        
        # [rest of function remains the same]
    }
```

### 2. Update Tool Schemas in `server.py`:

#### A. Update `jira_create_issue` tool schema:
```python
Tool(
    name="jira_create_issue",
    description="Create a new Jira issue or subtask",
    inputSchema={
        "type": "object",
        "properties": {
            # [existing properties]
            "name": {
                "type": "string",
                "description": "REQUIRED: Name value for the custom field"
            },
            "dept": {
                "type": "string",
                "description": "REQUIRED: Department value for the custom field"
            }
        },
        "required": ["project_key", "summary", "name", "dept"],
    },
)
```

#### B. Update `jira_create_epic` tool schema:
```python
Tool(
    name="jira_create_epic",
    description="Create a new Epic in Jira",
    inputSchema={
        "type": "object",
        "properties": {
            # [existing properties]
            "name": {
                "type": "string",
                "description": "REQUIRED: Name value for the custom field"
            },
            "dept": {
                "type": "string",
                "description": "REQUIRED: Department value for the custom field"
            }
        },
        "required": ["project_key", "summary", "name", "dept"],
    },
)
```

#### C. Update the `call_tool` method to pass these parameters to the respective methods:
```python
elif name == "jira_create_issue":
    # [existing code]
    name = arguments.get("name")
    dept = arguments.get("dept")
    
    result = jira_fetcher.create_issue(
        # [existing parameters]
        name=name,
        dept=dept
    )
    
elif name == "jira_create_epic":
    # [existing code]
    name = arguments.get("name")
    dept = arguments.get("dept")
    
    result = jira_fetcher.create_epic(
        # [existing parameters]
        name=name,
        dept=dept
    )
```

## Verification Steps

After implementing these changes, the following verification steps should be taken:

1. Try creating an issue with the name and dept parameters provided (should succeed)
2. Try creating an issue without providing these parameters (should fail with an appropriate error message)
3. Create multiple issues to verify values aren't persisted between commands (each issue should have the values specified for that command only)

## Reversion Plan

If the changes cause issues, they can be reverted by:

1. Reverting `jira.py` to restore the original method signatures and hardcoded values
2. Reverting `server.py` to restore the original tool schemas and `call_tool` method
3. Testing with the original functionality to ensure proper operation

## Change Log

### 1. src/mcp_atlassian/jira.py - 2025-04-19, 3:46:32 PM

Modified the `create_issue` method:
- Added `name` and `dept` parameters to the method signature
- Added validation to check if these parameters are provided
- Removed hardcoded values `["Stella"]` and `["DevOps-MCP"]`
- Removed the "Stella:" prefix from the summary field
- Updated the docstring to indicate that these parameters are required

Modified the `create_epic` method:
- Added `name` and `dept` parameters to the method signature
- Added validation to check if these parameters are provided
- Removed hardcoded values `["Stella"]` and `["DevOps-MCP"]`
- Removed the "Stella:" prefix from the summary field
- Updated the docstring to indicate that these parameters are required

### 2. src/mcp_atlassian/server.py - 2025-04-19, 3:48:32 PM

Modified `jira_create_issue` tool schema:
- Added `name` and `dept` properties to the inputSchema
- Added both fields to the "required" array
- Updated the property descriptions to indicate they are required

Modified `jira_create_epic` tool schema:
- Added `name` and `dept` properties to the inputSchema
- Added both fields to the "required" array
- Updated the property descriptions to indicate they are required

Updated `call_tool` method:
- Modified the `jira_create_issue` handler to extract and pass name and dept parameters
- Modified the `jira_create_epic` handler to extract and pass name and dept parameters

The changes ensure that:
1. The fields are no longer hardcoded
2. Users must provide values for each command
3. An error is thrown if the fields are not provided
4. Values are not persistent between commands
