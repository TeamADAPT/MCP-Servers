# Enhanced Jira Integration

This document describes the enhanced Jira integration features in the MCP Atlassian connector.

## Overview

The Enhanced Jira Integration provides advanced functionality for working with Jira, extending the basic Jira integration with features such as:

- Custom field management
- Improved error handling with retry logic
- Caching for performance improvements
- Bulk operations
- Project health analysis
- Advanced search capabilities
- Sprint reporting

## Configuration

### Feature Flags

Enhanced Jira features are controlled via feature flags. To enable Enhanced Jira functionality, set one of the following:

- Add `ENHANCED_JIRA` to the comma-separated `MCP_ATLASSIAN_FEATURE_FLAGS` environment variable
- Set the `MCP_ATLASSIAN_ENABLE_ENHANCED_JIRA` environment variable to "true", "1", or "yes"

Example:
```bash
# Enable via feature flags list
export MCP_ATLASSIAN_FEATURE_FLAGS="ENHANCED_JIRA,BITBUCKET_INTEGRATION"

# Or enable specifically
export MCP_ATLASSIAN_ENABLE_ENHANCED_JIRA="true"
```

### Required Environment Variables

The Enhanced Jira integration requires the same environment variables as the basic Jira integration:

```bash
export JIRA_URL="https://YOUR-CREDENTIALS@YOUR-DOMAIN