from mcp.server.fastmcp import FastMCP
import asyncpg
import os

# Create a FastMCP server
mcp = FastMCP("Database Server", host="127.0.0.1", port=8001)

@mcp.tool()
async def query_db(sql: str) -> str:
    """Execute a SQL query against the database"""
    # In a real app, connect to actual DB. For now, mock or use DB_URL
    print(f"========== databse service called yes.........")
    return f"Executed query: {sql}. Result: [Mocked Result]"

if __name__ == "__main__":
    # Use the 'run' method with streamable-http transport
    mcp.run(transport="streamable-http") 
