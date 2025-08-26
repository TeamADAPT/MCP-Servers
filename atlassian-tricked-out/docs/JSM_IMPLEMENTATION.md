# JSM Implementation for MCP-Atlassian Server

## Overview

This document provides an overview of the Jira Service Management (JSM) integration implemented for the MCP-Atlassian server. The implementation consists of a comprehensive set of features for working with JSM, including both core functionality and advanced features.

## Core Implementation

The core JSM implementation includes the following components:

1. **JiraServiceManager Class**: A base class that handles interaction with the JSM API, including authentication, request handling, and error management.

2. **API Request Handling**: Centralized API request handling with robust error management, providing meaningful error messages for different HTTP status codes.

3. **Service Desk Operations**: Methods for retrieving service desk information, including listing all service desks and getting details for specific service desks.

4. **Request Type Management**: APIs for working with request types, including retrieving available request types and their field configurations.

5. **Customer Request Management**: Full lifecycle management of customer requests, including creation, retrieval, and updating.

6. **Request Participants**: APIs to manage participants on customer requests, including adding, removing, and listing participants.

7. **SLA Operations**: Functionality to retrieve SLA information for requests, helping track compliance with service level agreements.

8. **Queue Management**: Basic queue management for service desks, including listing queues and retrieving issues from queues.

9. **Organization Management**: Methods to manage organization access to service desks, including adding and removing organizations.

## Advanced Features

In addition to the core functionality, the implementation includes these advanced features:

### 1. Knowledge Base Integration

The `JSMKnowledgeBase` class provides comprehensive integration with JSM knowledge bases:

- Knowledge base management: Create, retrieve, and manage knowledge bases
- Article management: CRUD operations for knowledge base articles
- Article search and suggestions: Search for articles across knowledge bases and get suggestions based on request content
- Request-article linking: Link and unlink articles to/from service desk requests

### 2. Advanced Queue Management

The `JSMQueueManager` class extends basic queue functionality with:

- Enhanced queue retrieval: Get queues with issue counts
- Custom queue creation: Create and manage custom queues with JQL filters
- Advanced issue filtering: Filter queue issues with custom sorting and field expansion
- Queue metrics: Generate performance metrics for queues, including average resolution time, created vs. resolved counts, and breakdowns by status and priority

### 3. Approvals Workflow Management

The `JSMApprovalManager` class provides advanced approval workflow capabilities:

- Enhanced approval operations: Get detailed approval information and add comments to approvals
- Multi-level approvals: Configure and manage approval levels with different approver groups
- Approval workflow creation: Create custom approval workflows for specific request types
- Approval metrics: Generate metrics on approval performance, including average approval time and approval status distribution

### 4. Custom Form Support

The `JSMFormManager` class provides comprehensive form management:

- Custom field creation: Create and configure custom fields for JSM forms
- Field options management: Configure options for select/multiselect fields
- Form configuration: Retrieve and update form configurations for request types
- Field order management: Customize the order of fields in request forms
- Field requirements: Configure field requirements and validation rules
- Form validation: Validate form data against requirements before submission

## Architecture

The implementation follows a modular design:

1. **Base Service**: `JiraServiceManager` provides the foundation for all JSM operations.

2. **Specialized Services**: Advanced features are implemented as separate service classes that can work independently or use the base service.

3. **Tool Registration**: All functionality is exposed through the MCP server as tools that can be invoked by clients.

4. **Conditional Loading**: Services are loaded conditionally based on the availability of credentials, ensuring the server can still function without JSM access.

## Error Handling

The implementation includes comprehensive error handling:

1. **API Error Handling**: Specific handling for different HTTP status codes, with appropriate error messages.

2. **Input Validation**: Validation of input parameters before making API calls.

3. **Logging**: Detailed logging of errors and operations for debugging.

4. **Graceful Degradation**: The system works even if only some services are available.

## Testing

The implementation includes mock-based tests that can run without actual credentials:

1. **Base Functionality Tests**: Tests for core JSM functionality.

2. **Advanced Feature Tests**: Tests for knowledge base, queue management, approvals, and forms.

3. **Mock API Responses**: Tests use mock API responses to validate functionality without making actual API calls.

## Challenges and Solutions

During implementation, several challenges were encountered and addressed:

1. **API Limitations**: Some advanced features required working around API limitations by combining multiple API calls.

2. **Authentication**: Handled different authentication requirements while maintaining backward compatibility.

3. **Custom Fields**: Implemented support for custom fields, including the required 'name' and 'dept' fields.

4. **Error Handling**: Created a robust error handling system that provides meaningful feedback to clients.

5. **Performance**: Optimized API calls to minimize request counts and improve performance.

## Usage Examples

### Creating a Customer Request

```python
# Initialize the JSM client
jsm_client = JiraServiceManager()

# Create a customer request
request = jsm_client.create_customer_request(
    service_desk_id="10",
    request_type_id="25",
    summary="Need access to system XYZ",
    description="I require access to the XYZ system for my new role",
    name="John Doe",
    dept="Engineering"
)
```

### Working with Knowledge Base Articles

```python
# Initialize the Knowledge Base client
kb_client = JSMKnowledgeBase(jsm_client=jsm_client)

# Create a new article
article = kb_client.create_article(
    knowledge_base_id="KB-123",
    title="How to Reset Your Password",
    body="<p>Follow these steps to reset your password...</p>",
    labels=["password", "security"]
)

# Link article to a request
kb_client.link_article_to_request(
    issue_id_or_key="SD-456",
    article_id=article["id"]
)
```

### Managing Approvals

```python
# Initialize the Approvals client
approvals_client = JSMApprovalManager(jsm_client=jsm_client)

# Answer an approval with a comment
result = approvals_client.answer_approval(
    issue_id_or_key="SD-789",
    approval_id="APV-123",
    decision="approve",
    comment="Approved after review of documentation"
)

# Get approval metrics
metrics = approvals_client.get_approval_metrics(
    service_desk_id="10",
    time_period="1m"  # Last month
)
```

## Conclusion

The JSM implementation provides a comprehensive solution for integrating with Jira Service Management from the MCP-Atlassian server. It includes both core functionality and advanced features, with robust error handling and test coverage.