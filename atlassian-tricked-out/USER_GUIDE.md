# MCP Atlassian Integration - Comprehensive User Guide

This guide provides detailed instructions for using the enhanced MCP Atlassian Integration with Claude. The integration enables seamless interaction with your Atlassian Cloud products including Jira, Confluence, Jira Service Management (JSM), and Bitbucket, along with enterprise-grade features.

## Overview

The enhanced MCP Atlassian Integration provides Claude with comprehensive capabilities:

### Jira Capabilities
- View, search, and filter Jira issues with advanced JQL support
- Create and update issues of all types (Epics, Stories, Tasks, Bugs, etc.)
- Manage issue relationships and links
- Handle issue transitions and workflow
- Create and manage projects with custom fields
- Track Epics and their linked Stories
- Add comments and attachments

### Confluence Capabilities
- Search and read pages with advanced CQL support
- Create, edit, and update pages with rich formatting
- Create pages from file templates
- Manage page versions and history
- Organize pages within spaces
- Attach files and manage attachments
- Navigate page hierarchies

### Jira Service Management (JSM) Capabilities
- Manage service desks and request types
- Create and track customer requests
- Handle approvals and SLAs
- Integrate with knowledge bases
- Manage queues and organizations

### Bitbucket Capabilities
- Repository management and exploration
- Branch creation and management
- Pull request workflows
- Code review processes
- Pipeline management and CI/CD
- Security and permissions management

### Enterprise Features
- Advanced analytics and reporting
- AI-powered classification and suggestions
- Cross-product integration
- Enhanced security features
- Marketplace app integration

## Using the Integration

Once the integration is set up by your administrator, you can ask Claude to perform various tasks across the Atlassian ecosystem. Here are some examples of what you can ask Claude to do:

### Confluence Tasks

1. **Search Confluence**
   - "Search Confluence for pages about project planning"
   - "Find Confluence pages in the ADOC space about API documentation"
   - "Search Confluence using CQL: space = ADOC AND text ~ 'database schema'"

2. **Get Page Content**
   - "Show me the content of the Confluence page with ID 12345"
   - "Get the details of the 'Project Overview' page in the PROJ space"
   - "Show me all comments on the Confluence page with ID 12345"

3. **Create and Update Pages**
   - "Create a new Confluence page in the ADOC space titled 'API Documentation' with the following content..."
   - "Create a Confluence page from this markdown file"
   - "Update the 'Project Overview' page in the PROJ space with this new content"
   - "Move the page 'Team Charter' to the 'Policies' space"

4. **Manage Page Organization**
   - "Show me the page tree for the ADOC space"
   - "Create a new page as a child of the 'Project Overview' page"
   - "Move the 'Meeting Notes' page under the 'Team Documents' parent page"

5. **Attach Files**
   - "Attach this file to the Confluence page with ID 12345"
   - "Upload this image to the 'Project Overview' page"
   - "Add a comment to the attachment on page ID 12345"

6. **Manage Page Versions**
   - "Show me the version history of the Confluence page with ID 12345"
   - "Restore the Confluence page with ID 12345 to version 3"
   - "Compare versions 2 and 3 of the Confluence page with ID 12345"

7. **Enhanced Templates and Spaces**
   - "Create a new project space using the Engineering template"
   - "Apply the Meeting Notes template to this page"
   - "Create a documentation space with standard content structure"

### Jira Tasks

1. **View and Search Issues**
   - "Show me the details of PROJ-123"
   - "Get information about the bug PROJ-456"
   - "Search for all open bugs in the PROJ project"
   - "Find all high-priority tasks assigned to John"
   - "Search issues with JQL: project = PROJ AND priority = High AND status != Done"

2. **Create and Manage Projects**
   - "Create a new Jira project with key DEMO and name 'Demonstration Project'"
   - "Set up a Kanban board for the DEMO project"
   - "Configure a workflow for the DEMO project"
   - "Set up custom fields for the DEMO project"

3. **Create and Update Issues**
   - "Create a new task in the PROJ project titled 'Update documentation'"
   - "Create a bug report in PROJ with high priority"
   - "Update the description of PROJ-123"
   - "Change the status of PROJ-123 to 'In Progress'"
   - "Set the priority of PROJ-123 to 'Highest'"

4. **Work with Epics and Stories**
   - "Create a new Epic in the PROJ project titled 'User Authentication Improvements'"
   - "Create a story in the PROJ project and link it to the Epic PROJ-123"
   - "Show me all stories linked to the Epic PROJ-123"
   - "Update the progress of Epic PROJ-123 based on its stories"

5. **Issue Links and Relationships**
   - "Link PROJ-123 to PROJ-456 as 'blocks'"
   - "Create a 'relates to' link between PROJ-123 and PROJ-789"
   - "Show me all available issue link types"
   - "Find all issues that block PROJ-123"

6. **Comments and Attachments**
   - "Add a comment to PROJ-123"
   - "Attach this file to issue PROJ-123"
   - "Show me all attachments for PROJ-123"
   - "Get the comments on PROJ-123"

7. **Custom Fields Management**
   - "Set up global custom fields for Name and Department"
   - "Update the Name and Department fields for PROJ-123"
   - "Show me all custom fields available in this Jira instance"

### Jira Service Management (JSM) Tasks

1. **Service Desk Management**
   - "Show me all service desks available"
   - "Get details about the IT Help service desk"
   - "Create a new service desk for HR requests"

2. **Request Types**
   - "Show me all request types for the IT Help service desk"
   - "Create a new request type for 'Database Access'"
   - "Update the fields required for the 'Software Installation' request type"

3. **Customer Requests**
   - "Create a new request for database access"
   - "Show me all open requests in the IT Help service desk"
   - "Update the status of request IT-123"
   - "Add a comment to request IT-123"
   - "Assign request IT-123 to John"

4. **SLA Management**
   - "Show me the SLAs for the IT Help service desk"
   - "Check the SLA status for request IT-123"
   - "Create a new SLA for high-priority requests"

5. **Knowledge Base**
   - "Create a knowledge base article for resetting passwords"
   - "Link knowledge base article KB-123 to request type 'Password Reset'"
   - "Show me all knowledge base articles for the IT Help service desk"

6. **Queue Management**
   - "Show me all queues for the IT Help service desk"
   - "Create a new queue for security-related requests"
   - "Show me all requests in the 'Urgent' queue"

### Bitbucket Tasks

1. **Repository Management**
   - "Show me all repositories in our workspace"
   - "Create a new repository named 'api-service'"
   - "Get details about the 'frontend' repository"
   - "Delete the 'test-repo' repository"

2. **Branch Management**
   - "List all branches in the 'api-service' repository"
   - "Create a new branch 'feature/login' from main in the 'api-service' repository"
   - "Get details about the 'feature/login' branch"
   - "Delete the 'old-feature' branch"

3. **Pull Requests**
   - "List all open pull requests in the 'api-service' repository"
   - "Create a new pull request from 'feature/login' to 'main'"
   - "Get details about pull request #123"
   - "Merge pull request #123"
   - "Decline pull request #456"

4. **Code Review**
   - "Show me all comments on pull request #123"
   - "Add a comment to pull request #123"
   - "Approve pull request #123"
   - "Request changes on pull request #123"

5. **CI/CD Pipelines**
   - "Show me the pipeline configuration for the 'api-service' repository"
   - "List all recent pipeline runs for the 'api-service' repository"
   - "Run a pipeline on the 'feature/login' branch"
   - "Show me the log for pipeline run #123"

6. **Repository Settings**
   - "Configure branch restrictions for the 'main' branch"
   - "Set up a webhook for the 'api-service' repository"
   - "Show me all users with access to the 'api-service' repository"
   - "Grant write access to user 'jane' for the 'api-service' repository"

### Enterprise Features

1. **Advanced Analytics**
   - "Generate a usage report for our Jira instance"
   - "Show me activity metrics for the PROJ project"
   - "Generate a report of Confluence page views by team"
   - "Show me performance metrics for our service desk"

2. **AI Capabilities**
   - "Classify PROJ-123 into the appropriate category"
   - "Suggest related issues for PROJ-123"
   - "Generate a summary of the last sprint's activity"
   - "Analyze sentiment in service desk request comments"
   - "Recommend knowledge base articles for request IT-123"

3. **Enhanced Security**
   - "Configure rate limiting for our Jira API access"
   - "Set up circuit breakers for the Confluence integration"
   - "Generate a security audit report for API usage"
   - "Show me all authentication events from the last week"

4. **Marketplace Integration**
   - "Search for time tracking apps compatible with our Jira instance"
   - "Install the 'Advanced Roadmaps' app for Jira"
   - "Show me all installed Marketplace apps"
   - "Get details about the 'ScriptRunner' app configuration"

## Advanced Workflows

The enhanced integration supports sophisticated workflows across multiple Atlassian products:

### Cross-Product Integration

1. **Jira and Confluence Integration**
   - "Create a Confluence page for PROJ-123 using the issue details"
   - "Link Confluence page 12345 to Jira issue PROJ-123"
   - "Show all Confluence pages linked to PROJ-123"
   - "Create Jira issues based on requirements in Confluence page 12345"

2. **Jira and Bitbucket Integration**
   - "Create a branch in 'api-service' for Jira issue PROJ-123"
   - "Link pull request #123 to Jira issue PROJ-456"
   - "Show all commits related to PROJ-123"
   - "Create a Jira issue from pull request #123"

3. **JSM and Confluence Integration**
   - "Create a knowledge base article for service desk request IT-123"
   - "Link knowledge base article to the 'Password Reset' request type"
   - "Show all knowledge base articles for the IT Help service desk"

4. **Complete DevOps Cycle**
   - "Create a Jira Epic for the 'Authentication System Redesign'"
   - "Break down the Epic into Stories and Tasks"
   - "Create branches in Bitbucket for each Story"
   - "Create pull requests when the work is done"
   - "Link pull requests to Jira issues"
   - "Run CI/CD pipelines on the branches"
   - "Document the implementation in Confluence"
   - "Create service desk request types for user support"

### Enterprise Analytics and AI

1. **Advanced Reporting**
   - "Generate a cross-product usage report for the Engineering team"
   - "Create a dashboard showing Jira issues, code commits, and documentation updates"
   - "Produce performance analytics for service desk responsiveness"

2. **AI-Enhanced Workflows**
   - "Analyze all issues in the PROJ project and suggest classification categories"
   - "Generate summaries of all documentation in the ADOC space"
   - "Provide sentiment analysis of customer service desk requests"
   - "Recommend knowledge base articles based on service desk request content"

## Tips for Effective Use

1. **Be Specific with IDs and Keys**
   - When referring to resources, provide specific IDs or keys when possible
   - For Confluence: "Get the page with ID 12345"
   - For Jira: "Show me the issue PROJ-123"
   - For Bitbucket: "Show pull request #123 in the 'api-service' repository"
   - For JSM: "Get details for service desk request IT-123"

2. **Use Proper Query Syntax**
   - For Confluence searches, use CQL (Confluence Query Language)
   - For Jira searches, use JQL (Jira Query Language)
   - For Bitbucket, use specific repository and branch identifiers
   - Examples:
     - "Search Jira with JQL: project = PROJ AND priority = High AND status != Done"
     - "Search Confluence with CQL: space = ADOC AND type = page AND text ~ 'database'"

3. **Provide Complete Information**
   - When creating resources, provide all necessary information
   - For Confluence pages: space key, title, content, and optional parent
   - For Jira issues: project key, summary, issue type, and required custom fields
   - For Bitbucket: repository, branch names, and commit details
   - For JSM: service desk ID, request type, and description

4. **Leverage Cross-Product Features**
   - Take advantage of integrations between Atlassian products
   - Link resources across products for better traceability
   - Use templates and automations to standardize workflows
   - Implement end-to-end processes spanning multiple products

5. **Utilize Advanced Features**
   - Implement custom fields across projects
   - Set up templates for standardization
   - Configure advanced security features
   - Integrate with Marketplace apps

## Troubleshooting

If you encounter issues with the integration, try the following:

1. **Check Permissions and Credentials**
   - Ensure the MCP server has appropriate API credentials for all Atlassian services
   - Verify that the API tokens have the necessary permissions
   - Check that environment variables are correctly configured

2. **Verify Resource Identifiers**
   - Double-check that you're using the correct page IDs, issue keys, repository names, etc.
   - Ensure spaces, projects, and repositories actually exist

3. **Review Query Syntax**
   - Ensure your CQL, JQL, and other queries use the correct syntax
   - Check for proper formatting of query parameters
   - Verify field names and operators

4. **Check Logs and Diagnostics**
   - Review the MCP server logs for error messages
   - Enable DEBUG logging for more detailed information
   - Check any error responses from the Atlassian APIs

5. **Service Availability**
   - Verify that all Atlassian services are available and responsive
   - Check for any API rate limiting issues
   - Ensure network connectivity to Atlassian Cloud services

6. **Contact Administrator**
   - If issues persist, contact your MCP administrator to check the integration configuration
   - Check for updates to the MCP-Atlassian server

## Extended Examples

### Example 1: Complete Epic Management Workflow

**User**: "Create a new Epic in the PROJ project called 'User Authentication Redesign' with description 'Implement new OAuth2-based authentication system'. Then create three Stories linked to this Epic: 'Implement OAuth2 provider integration', 'Create new login UI', and 'Update API endpoints to use new auth system'."

**Claude**: *Creates the Epic and linked Stories, providing keys and links to each. Then suggests creating a Confluence space for documentation and potential Bitbucket branches for implementation.*

### Example 2: Cross-Product Documentation

**User**: "Find all open bugs in the authentication system, then create a Confluence page in the TEAM space that summarizes these issues and links to each one."

**Claude**: *Searches Jira for authentication bugs, creates a structured Confluence page summarizing the issues with direct links to each Jira issue, and provides a link to the new page.*

### Example 3: Complex JSM Request Workflow

**User**: "Create a new request type in the IT service desk for 'Database Access', then create a knowledge base article explaining the approval process, and link the article to the request type."

**Claude**: *Creates the request type with appropriate fields, creates a knowledge base article with process documentation, links them together, and provides confirmation with links to both resources.*

### Example 4: Bitbucket Pipeline Configuration

**User**: "Set up a CI/CD pipeline in the 'api-service' repository that runs tests, builds a container, and deploys to staging when changes are pushed to the 'develop' branch."

**Claude**: *Configures the pipeline with appropriate stages, creates the pipeline configuration file, commits it to the repository, and provides a summary of the pipeline setup.*

### Example 5: Advanced Analytics Report

**User**: "Generate a report showing the status of all issues in the current sprint, including their related pull requests and build statuses."

**Claude**: *Creates a comprehensive report pulling data from Jira for issue status, Bitbucket for pull requests and build information, and presents it in a structured format.*

## Conclusion

The enhanced MCP Atlassian Integration provides comprehensive capabilities for working with the entire Atlassian ecosystem through Claude. By using natural language requests, you can efficiently manage your Atlassian content and workflows across Jira, Confluence, JSM, and Bitbucket with enterprise-grade features.

For advanced configuration options, administrator documentation, and technical details, please refer to:
- [SETUP.md](docs/SETUP.md) - Setup instructions
- [ROADMAP.md](ROADMAP.md) - Upcoming features
- [API_REFERENCE.md](docs/API_REFERENCE.md) - Detailed API documentation
