# Extending MCP-Atlassian: Confluence and Jira Service Management

## Current Status

The MCP-Atlassian server currently provides basic tools for:
- Confluence page management 
- Jira issue tracking
- Custom fields management (with implementation plan for global settings)

## 1. Enhanced Confluence Integration

### Current Capabilities
- `confluence_search` - Search content using CQL
- `confluence_get_page` - Get page content by ID
- `confluence_get_comments` - Get comments for a page
- `confluence_create_page` - Create a new page with markdown
- `confluence_attach_file` - Attach a file to a page
- `confluence_get_page_history` - Get version history
- `confluence_update_page` - Update existing page
- `confluence_move_page` - Move a page
- `confluence_get_page_tree` - Get hierarchical page structure

### Proposed Extensions

#### 1.1 Spaces Management
```python
def create_space(self, key, name, description=None):
    """Create a new Confluence space"""
    
def archive_space(self, key):
    """Archive a Confluence space"""
    
def restore_space(self, key):
    """Restore an archived Confluence space"""
```

#### 1.2 Templates and Blueprints
```python
def get_templates(self):
    """Get available Confluence templates"""
    
def create_page_from_template(self, space_key, title, template_id, template_parameters=None):
    """Create a page from template with parameters"""
```

#### 1.3 Advanced Content Management
```python
def get_content_properties(self, content_id):
    """Get custom properties for content"""
    
def set_content_property(self, content_id, property_key, property_value):
    """Set a custom property for content"""
    
def get_content_restrictions(self, content_id):
    """Get view/edit restrictions for content"""
    
def set_content_restrictions(self, content_id, restrictions):
    """Set view/edit restrictions for content"""
```

#### 1.4 Macros Support
```python
def get_available_macros(self):
    """Get a list of available macros"""
    
def add_macro_to_page(self, page_id, macro_type, macro_parameters):
    """Add a macro to a page"""
    
def update_page_macro(self, page_id, macro_id, macro_parameters):
    """Update an existing macro on a page"""
```

#### 1.5 Labels and Metadata
```python
def add_label(self, content_id, label):
    """Add a label to content"""
    
def remove_label(self, content_id, label):
    """Remove a label from content"""
    
def get_content_by_label(self, label, content_type=None, space_key=None):
    """Find content with specific label"""
```

## 2. Jira Service Management Integration

Jira Service Management (JSM) extends Jira with service desk capabilities. The API is available at `/rest/servicedeskapi/`.

### Proposed New Tools

#### 2.1 Service Desk Access
```python
def get_service_desks(self):
    """Get all service desks available to the user"""
    
def get_service_desk(self, service_desk_id):
    """Get details about a specific service desk"""
```

#### 2.2 Request Types
```python
def get_request_types(self, service_desk_id):
    """Get available request types for a service desk"""
    
def get_request_type_fields(self, service_desk_id, request_type_id):
    """Get fields for a request type"""
```

#### 2.3 Customer Requests
```python
def create_customer_request(self, service_desk_id, request_type_id, 
                          summary, description, 
                          request_field_values=None,
                          attachments=None):
    """Create a customer request (service desk ticket)"""
    
def get_customer_requests(self, service_desk_id=None, 
                        request_type_id=None, 
                        status=None, 
                        expand=None):
    """Get customer requests with optional filtering"""
    
def get_customer_request(self, issue_id_or_key):
    """Get details about a specific customer request"""
```

#### 2.4 Request Participants
```python
def get_request_participants(self, issue_id_or_key):
    """Get participants for a customer request"""
    
def add_request_participant(self, issue_id_or_key, account_id):
    """Add a participant to a customer request"""
    
def remove_request_participant(self, issue_id_or_key, account_id):
    """Remove a participant from a customer request"""
```

#### 2.5 SLA Management
```python
def get_request_sla(self, issue_id_or_key):
    """Get SLA information for a request"""
```

#### 2.6 Queues
```python
def get_queues(self, service_desk_id):
    """Get queues for a service desk"""
    
def get_queue_issues(self, service_desk_id, queue_id):
    """Get issues in a queue"""
```

#### 2.7 Organizations
```python
def get_organizations(self, service_desk_id=None):
    """Get organizations"""
    
def add_organization(self, service_desk_id, organization_id):
    """Add an organization to a service desk"""
```

## Implementation Strategy

### 1. Code Structure

Add new classes:
- `ConfluenceAdvanced` - For advanced Confluence operations
- `JiraServiceManager` - For JSM-specific operations

Update server.py to expose new tools.

### 2. Authentication and Scopes

JSM requires additional scopes:
- Classic: `manage:servicedesk-customer`
- Granular: `read:servicedesk-request`, `write:servicedesk-request`

### 3. Environmental Variables

Add new environment variables for JSM-specific configuration:
```
JSM_BASE_URL=https://your-domain.atlassian.net
JSM_API_TOKEN=YOUR-API-TOKEN-HERE
```

### 4. Error Handling

Implement dedicated error handling for JSM-specific errors:
```python
def _handle_jsm_error(self, response):
    """Handle JSM-specific error responses"""
    if response.status_code == 404:
        raise ValueError("Service desk resource not found")
    elif response.status_code == 403:
        raise ValueError("Permission denied - check JSM scopes")
    # ...
```

## API Endpoints Reference

### Confluence

- `/rest/api/3/content` - Create/get content
- `/rest/api/3/space` - Manage spaces
- `/rest/api/3/template` - Work with templates
- `/rest/api/3/contentproperty` - Content properties

### Jira Service Management

- `/rest/servicedeskapi/servicedesk` - Service desk info
- `/rest/servicedeskapi/request` - Customer requests
- `/rest/servicedeskapi/request/{issueIdOrKey}/participant` - Request participants
- `/rest/servicedeskapi/request/{issueIdOrKey}/sla` - SLA information
- `/rest/servicedeskapi/servicedesk/{serviceDeskId}/queue` - Queues
- `/rest/servicedeskapi/organization` - Organizations

## Timeline and Resources

| Phase | Duration | Resources |
|-------|----------|-----------|
| Research & Design | 1 week | 1 developer |
| Confluence Extensions | 2 weeks | 1 developer |
| JSM Integration | 3 weeks | 1 developer |
| Testing & Documentation | 2 weeks | 1 developer + 1 QA |

Total estimated time: 8 weeks (can be reduced with parallel implementation)
