import asyncio
from mcp.client import MCPClient

async def main():
    client = MCPClient('http://localhost:8000')
    tools = await client.list_tools()
    print(f'Available tools: {[tool.name for tool in tools]}')
    
    try:
        resources = await client.list_resources()
        print(f'Available resources: {resources}')
    except Exception as e:
        print(f'Error listing resources: {e}')

asyncio.run(main())
