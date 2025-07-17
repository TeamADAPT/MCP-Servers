# Active Context

## Current Task (2025-04-19)

### MCP-Atlassian Custom Fields Modification

**Task Summary**: Modifying the MCP-Atlassian server implementation to remove hardcoded default values for custom fields "name" (customfield_10057) and "Dept" (customfield_10058), making them required parameters that must be explicitly set for each command.

**Current Status**: Analysis completed. Documented the current implementation and required changes in `2025-04-19_custom_field_fix.md`.

**Key Files**:
- `src/mcp_atlassian/jira.py` - Contains the hardcoded field values in `create_issue` and `create_epic` methods
- `src/mcp_atlassian/server.py` - Needs schema updates to expose these fields as required parameters

**Requirements**:
1. Remove hardcoded default values
2. Make both fields required parameters
3. Validate fields are provided and throw appropriate errors if missing
4. Ensure values are not persistent between commands (must be set for each use)

**Next Steps**:
1. Update `jira.py` to add the new parameters and remove hardcoded values
2. Update `server.py` to expose these fields in the tool schemas
3. Implement validation in both files to ensure the parameters are provided
4. Test the changes with both valid and invalid inputs
5. Update changelog with implementation details
