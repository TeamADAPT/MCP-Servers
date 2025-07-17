# MCP-Atlassian Strategic Implementation Plan

## Overview

This comprehensive plan outlines the strategic approach to enhancing the MCP-Atlassian server with three major capability improvements:

1. **Global Custom Fields Management** - Making custom fields available across all Jira projects
2. **Enhanced Confluence Integration** - Advanced features for content management
3. **Jira Service Management Integration** - Service desk capabilities

## Current State Analysis

The MCP-Atlassian server currently provides:
- Basic Jira project and issue management
- Basic Confluence page operations
- Custom fields that work in some projects (MCP) but fail in others (ZSHOT) with errors

## Implementation Priorities

### 1. Global Custom Fields Fix (MCP-21)

**Status**: Research complete, ready for implementation
**Timeline**: 1 week

#### Implementation Steps:

1. **API Enhancements** (2 days)
   - Add new methods to `JiraFetcher` class:
     - `get_custom_fields()` - List all custom fields
     - `get_field_contexts(field_id)` - Get contexts for a field
     - `create_global_field_context(field_id, name, description)` - Create global context
     - `assign_field_to_projects(field_id, context_id, project_ids)` - Assign to projects

2. **Error Handling** (1 day)
   - Modify `create_issue` and `create_epic` methods to:
     - Try first with custom fields
     - Gracefully handle "Field cannot be set" errors
     - Retry without custom fields if they're not available

3. **Setup API Tools** (1 day)
   - Create MCP tool wrappers for new methods:
     - `jira_get_custom_fields` - Get all custom fields
     - `jira_create_global_field_context` - Create a global context
     - `jira_assign_field_to_projects` - Assign field to projects

4. **Testing** (1 day)
   - Test creating issues in MCP project (where fields work)
   - Test creating issues in ZSHOT project (where fields previously failed)
   - Verify validation when fields are omitted
   - Verify no persistent values between commands

#### Acceptance Criteria:
- Custom fields "name" and "Dept" available in all projects
- Validation errors when fields are not provided
- No field values persisted between commands
- No unexpected title prefixes

### 2. Enhanced Confluence Integration (MCP-22)

**Status**: Design complete, ready for implementation
**Timeline**: 2-3 weeks

#### Implementation Steps:

1. **Spaces Management** (3 days)
   - Create methods for managing spaces:
     - Create space
     - Archive/restore space
     - Get space details/permissions

2. **Templates and Blueprints** (3 days)
   - Implement template functionality:
     - Get available templates
     - Create pages from templates with parameters
     - Manage custom templates

3. **Advanced Content Management** (3 days)
   - Add content property management:
     - Get/set content properties
     - Manage content restrictions
     - Handle advanced content operations

4. **Macros Support** (3 days)
   - Implement macro functionality:
     - Get available macros
     - Add/update macros on pages
     - Remove macros from pages

5. **Labels and Metadata** (2 days)
   - Add label management:
     - Add/remove labels
     - Find content by label
     - Manage content metadata

#### Acceptance Criteria:
- All new tools available through MCP server
- Documentation for each tool
- Example usage for each capability
- Tests for each functionality

### 3. Jira Service Management Integration (MCP-23)

**Status**: Design complete, ready for implementation
**Timeline**: 3-4 weeks

#### Implementation Steps:

1. **Service Desk & Request Types** (5 days)
   - Implement service desk operations:
     - Get service desks
     - Get request types
     - Get field requirements

2. **Customer Requests Management** (5 days)
   - Create customer request operations:
     - Create customer requests
     - Search and get requests
     - Update requests

3. **Request Participants & SLA** (3 days)
   - Implement participant management:
     - Get/add/remove participants
     - Get SLA information

4. **Queues and Organizations** (3 days)
   - Add queue management:
     - Get queues
     - Get issues in queues
     - Manage organizations

5. **Integration & Authentication** (5 days)
   - Connect with Jira Service Management API
   - Handle authentication and permissions
   - Implement error handling for JSM-specific errors

#### Acceptance Criteria:
- All JSM tools available through MCP server
- Successful creation and management of service desk tickets
- Documentation for each tool
- Tests for each functionality

## Technical Implementation

### New Class Structure

1. **JiraAdvanced** (extends JiraFetcher)
   - Handles advanced Jira operations including custom fields

2. **ConfluenceAdvanced** (extends ConfluenceFetcher)
   - Handles advanced Confluence operations

3. **JiraServiceManager** (new class)
   - Dedicated to JSM operations
   - Uses the `/rest/servicedeskapi/` endpoints

### Authentication Updates

Additional API token permissions may be required:
- For Jira: `jira:field:read`, `jira:field:write`
- For JSM: `manage:servicedesk-customer`

### Environment Variable Updates

Add support for JSM-specific variables:
```
JSM_URL=https://your-domain.atlassian.net
JSM_USERNAME=your-username
JSM_API_TOKEN=YOUR-API-TOKEN-HERE
```

## Dependencies and Risks

### Dependencies:
- Access to Jira instance with admin permissions
- Access to Confluence with appropriate permissions
- Access to Jira Service Management with appropriate licenses

### Risks:
- **Custom Fields**: Field IDs may differ between Jira instances
- **Confluence Macros**: Macro support varies by Confluence version
- **JSM Availability**: Requires JSM license

## Timeline

| Phase | Start | Duration | End |
|-------|-------|----------|-----|
| Global Custom Fields Fix | April 22, 2025 | 1 week | April 29, 2025 |
| Enhanced Confluence Integration | April 29, 2025 | 3 weeks | May 20, 2025 |
| JSM Integration | May 20, 2025 | 4 weeks | June 17, 2025 |

## Resources Required

- 1 Full-time Python Developer
- Access to Atlassian test environment
- Documentation resources

## Future Enhancements

After completing these core enhancements, consider:

1. **Bitbucket Integration**
   - Repository management
   - Pull request operations
   - Code review automation

2. **Trello Integration**
   - Board and card management
   - Checklist operations
   - Automation capabilities

3. **Statuspage Integration**
   - Status updates
   - Incident management
   - Maintenance scheduling

## Conclusion

This strategic plan provides a comprehensive approach to extending the MCP-Atlassian server with advanced capabilities. By implementing these enhancements, the server will provide a more robust and feature-complete integration with the Atlassian ecosystem, enabling AI assistants to perform a wider range of tasks.
