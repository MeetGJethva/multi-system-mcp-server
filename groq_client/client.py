import os
import asyncio
import httpx
from dotenv import load_dotenv
from typing import List, Dict, Any, Type
from pydantic import BaseModel, Field, create_model
from langchain_groq import ChatGroq
from langchain_core.tools import StructuredTool
from langgraph.prebuilt import create_react_agent
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()

# Configuration
GATEWAY_URL = os.getenv("GATEWAY_URL", "http://localhost:8000")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MODEL = "llama-3.3-70b-versatile"  # More reliable for multi-tool calls than 8b

async def get_mcp_tools() -> List[StructuredTool]:
    """Fetch tools from the gateway and convert them to LangChain StructuredTools"""
    async with httpx.AsyncClient() as http_client:
        try:
            # 1. Get list of servers
            response = await http_client.get(f"{GATEWAY_URL}/servers")
            servers = response.json()
            
            langchain_tools = []
            
            for server in servers:
                server_name = server['name']
                tools_response = await http_client.get(f"{GATEWAY_URL}/servers/{server_name}/tools")
                mcp_tools = tools_response.json()
                
                for tool in mcp_tools:
                    tool_name = tool['name']
                    description = tool.get('description', f"Call {tool_name} on {server_name}")
                    input_schema = tool.get('inputSchema', {"type": "object", "properties": {}})
                    
                    # Create a dynamic function for this tool
                    def create_tool_func(s_name, t_name):
                        async def func(**kwargs):
                            async with httpx.AsyncClient() as client:
                                url = f"{GATEWAY_URL}/servers/{s_name}/tools/{t_name}"
                                resp = await client.post(url, json={"arguments": kwargs})
                                return resp.json()
                        return func

                    # Map JSON Schema types to Python types for Pydantic
                    type_map = {
                        "string": str,
                        "integer": int,
                        "number": float,
                        "boolean": bool,
                        "array": list,
                        "object": dict
                    }

                    # Build fields for the Pydantic model
                    fields = {}
                    properties = input_schema.get("properties", {})
                    required = input_schema.get("required", [])
                    
                    for prop_name, prop_info in properties.items():
                        prop_type = type_map.get(prop_info.get("type", "string"), Any)
                        prop_desc = prop_info.get("description", "")
                        
                        if prop_name in required:
                            fields[prop_name] = (prop_type, Field(..., description=prop_desc))
                        else:
                            fields[prop_name] = (prop_type, Field(None, description=prop_desc))

                    # Create the model with a cleaner name
                    args_model = create_model(f"{tool_name}_input", **fields)
                    
                    # Define handlers
                    async_handler = create_tool_func(server_name, tool_name)
                    
                    def sync_handler(**kwargs):
                        raise NotImplementedError("This tool is async-only")

                    langchain_tools.append(
                        StructuredTool.from_function(
                            func=sync_handler,
                            name=tool_name,
                            description=description,
                            coroutine=async_handler,
                            args_schema=args_model
                        )
                    )
            
            return langchain_tools
        except Exception as e:
            print(f"Error fetching tools: {e}")
            return []

async def main():
    if not GROQ_API_KEY:
        print("Please set GROQ_API_KEY in your .env file")
        return

    # 1. Initialize LLM
    llm = ChatGroq(
        temperature=0,
        model_name=MODEL,
        groq_api_key=GROQ_API_KEY
    )

    # 2. Setup tools
    print("Fetching tools from MCP Gateway...")
    tools = await get_mcp_tools()
    
    if not tools:
        print("No tools found. Please ensure the gateway and servers are running.")
        return

    print(f"Found {len(tools)} tools: {[t.name for t in tools]}")

    # 3. Create Agent (using LangGraph's modern ReAct agent)
    print("Initializing LangGraph agent...")
    
    # System message can be passed directly as state_modifier
    system_message = (
        "You are a helpful assistant with access to various external tools via MCP. "
        "When you need to fetch information, use the specific tool available. "
        "For GitHub repository details, use the 'get_repo_info' tool. "
        "For database queries, follow these steps in order: "
        "1. Call 'get_all_tables' (no arguments) to list all tables. "
        "2. Call 'get_table_schema' with the table_name argument to get columns for a specific table. "
        "3. Call 'execute_query' with the sql argument to run your query. "
        "Never pass arguments to 'get_all_tables' — it takes no parameters."
    )
    
    app = create_react_agent(llm, tools, prompt=system_message)

    # 4. Run interaction — maintain conversation history across turns
    conversation_history = []

    while True:
        user_input = input("\nUser: ")
        if user_input.strip().lower() in ("exit", "quit", "q"):
            print("Goodbye!")
            break

        conversation_history.append(("user", user_input))

        inputs = {"messages": conversation_history}
        final_event = None
        async for event in app.astream(inputs, stream_mode="values"):
            final_event = event

        if final_event is None:
            print("Assistant: (no response)")
            continue

        final_message = final_event["messages"][-1]
        print(f"\nAssistant: {final_message.content}")

        # Append the assistant's reply to keep history
        conversation_history.append(("assistant", final_message.content))

if __name__ == "__main__":
    asyncio.run(main())
