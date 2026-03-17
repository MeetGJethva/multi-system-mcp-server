import asyncio
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
try:
    from manager import ServerManager, MCPServerConfig
except ImportError:
    from .manager import ServerManager, MCPServerConfig
from typing import List, Dict, Any
import os

app = FastAPI(title="MCP Gateway")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_URL = os.getenv("DATABASE_URL", "postgresql://mcp_user:mcp_password@localhost:5432/mcp_db")
manager = ServerManager(DB_URL)

@app.on_event("startup")
async def startup_event():
    # Initial discovery
    # In a real app, we might want to maintain persistent sessions.
    # For now, let's just ensure we can query the DB.
    pass

@app.get("/servers")
async def list_servers():
    return await manager.get_servers_from_db()

@app.get("/servers/{server_name}/tools")
async def list_tools(server_name: str):
    # For simplicity, we connect/disconnect or use a long-lived session
    # Let's try to get config first
    servers = await manager.get_servers_from_db()
    config = next((s for s in servers if s.name == server_name), None)
    if not config:
        raise HTTPException(status_code=404, detail="Server not found")
    
    # Connect and get tools
    url = f"{config.endpoint}:{config.port}/mcp" 
    from mcp.client.streamable_http import streamable_http_client
    from mcp import ClientSession
    
    try:
        async with streamable_http_client(url) as (read, write, _):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.list_tools()
                return result.tools
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/servers/{server_name}/tools/{tool_name}")
async def call_tool(server_name: str, tool_name: str, request: Dict[str, Any]):
    servers = await manager.get_servers_from_db()
    config = next((s for s in servers if s.name == server_name), None)
    if not config:
        raise HTTPException(status_code=404, detail="Server not found")
    
    url = f"{config.endpoint}:{config.port}/mcp"
    from mcp.client.streamable_http import streamable_http_client
    from mcp import ClientSession
    
    try:
        async with streamable_http_client(url) as (read, write, _):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool(tool_name, request.get("arguments", {}))
                return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
