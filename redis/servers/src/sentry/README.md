# mcp-server-sentry: A Sentry MCP server

## Overview

A Model Context Protocol server for retrieving and analyzing issues from Sentry.io. This server provides tools to inspect error reports, stacktraces, and other debugging information from your Sentry account.

### Tools

1. `get_sentry_issue`
   - Retrieve and analyze a Sentry issue by ID or URL
   - Input:
     - `issue_id_or_url` (string): Sentry issue ID or URL to analyze
   - Returns: Issue details including:
     - Title
     - Issue ID
     - Status
     - Level
     - First seen timestamp
     - Last seen timestamp
     - Event count
     - Full stacktrace

### Prompts

1. `sentry-issue`
   - Retrieve issue details from Sentry
   - Input:
     - `issue_id_or_url` (string): Sentry issue ID or URL
   - Returns: Formatted issue details as conversation context

## Installation

### Using uv (recommended)

When using [`uv`](https://YOUR-CREDENTIALS@YOUR-DOMAIN/inspector uvx mcp-server-sentry --auth-token YOUR_SENTRY_TOKEN
```

Or if you've installed the package in a specific directory or are developing on it:

```
cd path/to/servers/src/sentry
npx @modelcontextprotocol/inspector uv run mcp-server-sentry --auth-token YOUR_SENTRY_TOKEN
```

## License

This MCP server is licensed under the MIT License. This means you are free to use, modify, and distribute the software, subject to the terms and conditions of the MIT License. For more details, please see the LICENSE file in the project repository.
