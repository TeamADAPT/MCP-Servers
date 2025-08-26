# MCP Atlassian Integration - User Guide

This guide provides instructions for using the MCP Atlassian Integration with Claude. The integration allows Claude to interact with your Atlassian Cloud products (Confluence and Jira) to perform various tasks.

## Overview

The MCP Atlassian Integration enables Claude to:

- Search and read Confluence pages
- Create and edit Confluence pages
- Attach files to Confluence pages
- Manage Confluence page versions
- View and search Jira issues
- Create Jira projects and issues
- Link Jira issues (including Stories to Epics)

## Using the Integration

Once the integration is set up by your administrator, you can ask Claude to perform various tasks related to Confluence and Jira. Here are some examples of what you can ask Claude to do:

### Confluence Tasks

1. **Search Confluence**
   - "Search Confluence for pages about project planning"
   - "Find Confluence pages in the ADOC space about API documentation"

2. **Get Page Content**
   - "Show me the content of the Confluence page with ID 12345"
   - "Get the details of the 'Project Overview' page in the PROJ space"

3. **Create Pages**
   - "Create a new Confluence page in the ADOC space titled 'API Documentation' with the following content..."
   - "Create a Confluence page from this markdown file"

4. **Attach Files**
   - "Attach this file to the Confluence page with ID 12345"
   - "Upload this image to the 'Project Overview' page"

5. **Manage Page Versions**
   - "Show me the version history of the Confluence page with ID 12345"
   - "Restore the Confluence page with ID 12345 to version 3"

### Jira Tasks

1. **View Issues**
   - "Show me the details of PROJ-123"
   - "Get information about the bug PROJ-456"

2. **Search Issues**
   - "Search for all open bugs in the PROJ project"
   - "Find all high-priority tasks assigned to John"

3. **Create Projects**
   - "Create a new Jira project with key DEMO and name 'Demonstration Project'"

4. **Create Issues**
   - "Create a new task in the PROJ project titled 'Update documentation'"
   - "Create a bug report in PROJ with high priority"
   - "Create a story in the PROJ project and link it to the Epic PROJ-123"

5. **Link Issues**
   - "Link PROJ-123 to PROJ-456 as 'blocks'"
   - "Create a 'relates to' link between PROJ-123 and PROJ-789"
   - "Show me all available issue link types"

## Working with Epics and Stories

The integration supports linking Stories to Epics, which is a common workflow in Agile project management:

1. **Creating a Story Linked to an Epic**
   - "Create a new Story in the PROJ project titled 'Implement login feature' and link it to the Epic PROJ-123"

2. **Viewing Epic Links**
   - "Show me all Stories linked to the Epic PROJ-123"
   - "Get details of the Epic PROJ-123 including linked issues"

3. **Creating Links Between Issues**
   - "Create a 'blocks' link from PROJ-123 to PROJ-456"
   - "Link the Story PROJ-789 to the Epic PROJ-123"

## Tips for Effective Use

1. **Be Specific with IDs and Keys**
   - When referring to Confluence pages or Jira issues, provide specific IDs or keys when possible
   - For Confluence: "Get the page with ID 12345"
   - For Jira: "Show me the issue PROJ-123"

2. **Use Proper Query Syntax**
   - For Confluence searches, use CQL (Confluence Query Language)
   - For Jira searches, use JQL (Jira Query Language)
   - Example: "Search Jira for issues with JQL: project = PROJ AND status = 'In Progress'"

3. **Provide Complete Information**
   - When creating new items, provide all necessary information
   - For Confluence pages: space key, title, and content
   - For Jira issues: project key, summary, and issue type

4. **Check Available Link Types**
   - Before creating links between issues, check the available link types
   - "Show me all available Jira issue link types"
   - Use the exact name of the link type when creating links

## Troubleshooting

If you encounter issues with the integration, try the following:

1. **Check Permissions**
   - Ensure the account used for the integration has appropriate permissions in Confluence and Jira

2. **Verify IDs and Keys**
   - Double-check that you're using the correct page IDs, issue keys, and project keys

3. **Review Syntax**
   - Ensure your CQL and JQL queries use the correct syntax

4. **Contact Administrator**
   - If issues persist, contact your administrator to check the integration configuration

## Examples

### Example 1: Creating a Confluence Page

**User**: "Create a new Confluence page in the ADOC space titled 'Project Guidelines' with the following content: # Project Guidelines\n\nThis document outlines the standard guidelines for all projects.\n\n## Naming Conventions\n\nAll projects should follow the standard naming convention..."

**Claude**: *Creates the page and provides a link to it*

### Example 2: Creating a Jira Story Linked to an Epic

**User**: "Create a new Story in the PROJ project titled 'Implement user authentication' with description 'Add user authentication using OAuth' and link it to the Epic PROJ-123"

**Claude**: *Creates the Story, links it to the Epic, and provides the issue key and link*

### Example 3: Searching Jira Issues

**User**: "Search Jira for all high-priority bugs in the PROJ project that are still open"

**Claude**: *Searches using JQL and returns a list of matching issues*

## Conclusion

The MCP Atlassian Integration provides powerful capabilities for working with Confluence and Jira through Claude. By using natural language requests, you can efficiently manage your Atlassian content and workflows without having to switch between different applications.

For administrator documentation and technical details, please refer to the [MCP Atlassian Integration README](https://github.com/pashpashpash/mcp-atlassian).
