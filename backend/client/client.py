import os
import sys
from contextlib import asynccontextmanager
from mcp.client.stdio import stdio_client, StdioServerParameters
from mcp.client.session import ClientSession

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SERVER_SCRIPT = os.path.join(BASE_DIR, "backend", "server", "server.py")

@asynccontextmanager
async def mcp_client():
    """
    Context manager to spin up the MCP server via stdio and connect a client session.
    Yields the initialized ClientSession.
    """
    # Use the current python executable to run the MCP server script
    server_params = StdioServerParameters(
        command=sys.executable,
        args=[SERVER_SCRIPT],
        env=os.environ.copy()
    )
    
    async with stdio_client(server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            yield session
