# Time MCP Server

A Model Context Protocol server that provides time and timezone conversion capabilities. This server enables LLMs to get current time information and perform timezone conversions using IANA timezone names, with automatic system timezone detection.

### Available Tools

- `get_current_time` - Get current time in a specific timezone or system timezone.
  - Required arguments:
    - `timezone` (string): IANA timezone name (e.g., 'America/New_York', 'Europe/London')

- `convert_time` - Convert time between timezones.
  - Required arguments:
    - `source_timezone` (string): Source IANA timezone name
    - `time` (string): Time in 24-hour format (HH:MM)
    - `target_timezone` (string): Target IANA timezone name

## Installation

### Using uv (recommended)

When using [`uv`](https://YOUR-CREDENTIALS@YOUR-DOMAIN/inspector uvx mcp-server-time
```

Or if you've installed the package in a specific directory or are developing on it:

```bash
cd path/to/servers/src/time
npx @modelcontextprotocol/inspector uv run mcp-server-time
```

## Examples of Questions for Claude

1. "What time is it now?" (will use system timezone)
2. "What time is it in Tokyo?"
3. "When it's 4 PM in New York, what time is it in London?"
4. "Convert 9:30 AM Tokyo time to New York time"

## Build

Docker build:

```bash
cd src/time
docker build -t mcp/time .
```

## Contributing

We encourage contributions to help expand and improve mcp-server-time. Whether you want to add new time-related tools, enhance existing functionality, or improve documentation, your input is valuable.

For examples of other MCP servers and implementation patterns, see:
https://github.com/modelcontextprotocol/servers

Pull requests are welcome! Feel free to contribute new ideas, bug fixes, or enhancements to make mcp-server-time even more powerful and useful.

## License

mcp-server-time is licensed under the MIT License. This means you are free to use, modify, and distribute the software, subject to the terms and conditions of the MIT License. For more details, please see the LICENSE file in the project repository.
