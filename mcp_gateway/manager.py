import asyncio
import httpx
import asyncpg
from typing import Dict, List, Any
from mcp import ClientSession, StdioServerParameters
from mcp.client.sse import sse_client
from pydantic import BaseModel

class MCPServerConfig(BaseModel):
    id: int
    name: str
    endpoint: str
    port: int

class ServerManager:
    def __init__(self, db_url: str):
        self.db_url = db_url
        self.sessions: Dict[str, ClientSession] = {}
        self._lock = asyncio.Lock()

    async def get_servers_from_db(self) -> List[MCPServerConfig]:
        conn = await asyncpg.connect(self.db_url)
        try:
            rows = await conn.fetch("SELECT id, name, endpoint, port FROM mcp_servers")
            return [MCPServerConfig(**dict(row)) for row in rows]
        except Exception as e:
            print(f"Error fetching servers: {e}")
            return []
        finally:
            await conn.close()

    async def connect_to_server(self, config: MCPServerConfig):
        url = f"{config.endpoint}:{config.port}/sse"
        async with sse_client(url) as streams:
            async with ClientSession(streams[0], streams[1]) as session:
                await session.initialize()
                self.sessions[config.name] = session
                # Keep session alive in a background task or just store for now?
                # Actually, for a gateway, we might want to connect on demand or maintain long-lived ones.
                # Given the "super scalable" requirement, long-lived connections for each server might be better.
                # But SSE client context manager closes it. We need a way to keep it open.
                pass

    async def list_tools(self, server_name: str) -> List[Any]:
        if server_name not in self.sessions:
            # Try to reconnect if needed
            pass
        session = self.sessions.get(server_name)
        if session:
            result = await session.list_tools()
            return result.tools
        return []

    async def call_tool(self, server_name: str, tool_name: str, arguments: Dict[str, Any]) -> Any:
        session = self.sessions.get(server_name)
        if session:
            return await session.call_tool(tool_name, arguments)
        return None
