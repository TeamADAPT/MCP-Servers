import asyncio
from dataclasses import dataclass
from urllib.parse import urlparse

import click
import httpx
import mcp.types as types
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions
from mcp.shared.exceptions import McpError
import mcp.server.stdio

SENTRY_API_BASE = "https://YOUR-CREDENTIALS@YOUR-DOMAIN//", "https://YOUR-CREDENTIALS@YOUR-DOMAIN/last occurred
                - Review error counts and status""",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "issue_id_or_url": {
                            "type": "string",
                            "description": "Sentry issue ID or URL to analyze"
                        }
                    },
                    "required": ["issue_id_or_url"]
                }
            )
        ]

    @server.call_tool()
    async def handle_call_tool(
        name: str, arguments: dict | None
    ) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
        if name != "get_sentry_issue":
            raise ValueError(f"Unknown tool: {name}")

        if not arguments or "issue_id_or_url" not in arguments:
            raise ValueError("Missing issue_id_or_url argument")

        issue_data = await handle_sentry_issue(http_client, auth_token, arguments["issue_id_or_url"])
        return issue_data.to_tool_result()

    return server

@click.command()
@click.option(
    "--auth-token",
    envvar="SENTRY_TOKEN",
    required=True,
    help="Sentry authentication token",
)
def main(auth_token: str):
    async def _run():
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            server = await serve(auth_token)
            await server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="sentry",
                    server_version="0.4.1",
                    capabilities=server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={},
                    ),
                ),
            )

    asyncio.run(_run())
