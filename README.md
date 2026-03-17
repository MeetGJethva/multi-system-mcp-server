# Multi-System MCP Server Project

This project implements a scalable MCP gateway that manages multiple MCP servers dynamically using a PostgreSQL database for configuration.

## Features
- **MCP Gateway**: FastAPI-based gateway that routes requests to multiple MCP servers.
- **Dynamic Discovery**: Servers are configured in the database and discovered at runtime.
- **Tool Autodiscovery**: Add tools to any server, and they become immediately available through the gateway.
- **Browser Client**: A modern React-based UI to interact with all servers and tools.
- **Groq Integration**: AI-powered tool suggestions and results summarization.

## Project Structure
- `mcp_gateway/`: The main gateway service (Port 8000).
- `mcp_servers/`:
  - `db_server/`: Database MCP server (Port 8001).
  - `github_server/`: GitHub MCP server (Port 8002).
- `mcp_client/`: React browser client.
- `migrations/`: Database initialization scripts.

## Getting Started

### Prerequisites
- Docker & Docker Compose
- `uv` (Python package manager)
- Node.js & npm

### Running the Project

1. **Start the Database**:
   ```bash
   docker-compose up -d
   ```

2. **Run MCP Servers**:
   In separate terminals:
   ```bash
   cd mcp_servers/db_server && uv run main.py
   cd mcp_servers/github_server && uv run main.py
   ```

3. **Run the Gateway**:
   ```bash
   cd mcp_gateway && uv run main.py
   ```

4. **Run the Client**:
   ```bash
   cd mcp_client && npm install && npm run dev
   ```

## Configuration
The `mcp_servers` table in PostgreSQL defines which servers the gateway connects to. You can add more rows to this table to include new MCP servers.

## Autodiscovery
The gateway dynamically fetches tools from the servers listed in the database. Since servers use **FastMCP** with **Streamable HTTP** transport, the gateway can query them without needing a restart when new tools are added. This ensures a highly dynamic and scalable environment.
