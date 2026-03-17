---
description: How to run the Groq MCP client
---

1. Ensure the database and servers are running:
   - Run `docker-compose up -d` to start Postgres.
   - Run `python run_all.py` to start the MCP servers and gateway.

2. Set your Groq API Key:
   - Open `.env` and set `GROQ_API_KEY=your_actual_key`.

3. Install dependencies:
   - Run `pip install langgraph langchain-groq langchain python-dotenv httpx mcp fastapi uvicorn asyncpg`

4. Run the Groq client:
   - Run `python groq_client/client.py`
