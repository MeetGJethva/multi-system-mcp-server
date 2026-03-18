from mcp.server.fastmcp import FastMCP
import asyncpg
import os
import json

# Create a FastMCP server
mcp = FastMCP("Database Server", host="127.0.0.1", port=8001)

# Database connection URL from environment variable
DB_URL = os.getenv("DATABASE_URL", "postgresql://mcp_user:mcp_password@localhost:5432/test_db")


async def get_connection():
    """Create and return a database connection."""
    return await asyncpg.connect(DB_URL)


@mcp.tool()
async def get_all_tables() -> str:
    """
    Get a list of all tables in the database.
    Returns a JSON list of table names from the public schema.
    """
    print("Fetching all tables...")
    conn = None
    try:
        conn = await get_connection()
        rows = await conn.fetch(
            """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
              AND table_type = 'BASE TABLE'
            ORDER BY table_name;
            """
        )
        tables = [row["table_name"] for row in rows]
        result = json.dumps({"tables": tables, "count": len(tables)}, indent=2)
        print(tables)
        return result
    except Exception as e:
        result = json.dumps({"error": str(e)})
        print(str(e))
        return result
    finally:
        if conn:
            await conn.close()


@mcp.tool()
async def get_table_schema(table_name: str) -> str:
    """
    Get the schema (columns, data types, nullable, default values) of a specific table.
    
    Args:
        table_name: The name of the table to get the schema for.
    
    Returns a JSON object with column details for the given table.
    """
    print(f"Fetching schema for table: {table_name}")
    conn = None
    try:
        conn = await get_connection()
        rows = await conn.fetch(
            """
            SELECT
                column_name,
                data_type,
                character_maximum_length,
                is_nullable,
                column_default
            FROM information_schema.columns
            WHERE table_schema = 'public'
              AND table_name = $1
            ORDER BY ordinal_position;
            """,
            table_name,
        )
        if not rows:
            return json.dumps({"error": f"Table '{table_name}' not found or has no columns."})

        columns = [
            {
                "column_name": row["column_name"],
                "data_type": row["data_type"],
                "max_length": row["character_maximum_length"],
                "is_nullable": row["is_nullable"],
                "default": row["column_default"],
            }
            for row in rows
        ]
        result = json.dumps({"table": table_name, "columns": columns}, indent=2)
        print(columns)
        return result
    except Exception as e:
        result = json.dumps({"error": str(e)})
        print(str(e))
        return result
    finally:
        if conn:
            await conn.close()


@mcp.tool()
async def get_all_tables_schema() -> str:
    """
    Get the schema of ALL tables in the database at once.
    Returns a JSON object mapping each table name to its column definitions.
    """
    print("Fetching schema for all tables...")
    conn = None
    try:
        conn = await get_connection()
        rows = await conn.fetch(
            """
            SELECT
                table_name,
                column_name,
                data_type,
                character_maximum_length,
                is_nullable,
                column_default
            FROM information_schema.columns
            WHERE table_schema = 'public'
            ORDER BY table_name, ordinal_position;
            """
        )
        schema: dict = {}
        for row in rows:
            tbl = row["table_name"]
            if tbl not in schema:
                schema[tbl] = []
            schema[tbl].append(
                {
                    "column_name": row["column_name"],
                    "data_type": row["data_type"],
                    "max_length": row["character_maximum_length"],
                    "is_nullable": row["is_nullable"],
                    "default": row["column_default"],
                }
            )
        result = json.dumps({"schema": schema, "table_count": len(schema)}, indent=2)
        print(schema)
        return result
    except Exception as e:
        result = json.dumps({"error": str(e)})
        print(str(e))
        return result
    finally:
        if conn:
            await conn.close()


@mcp.tool()
async def execute_query(sql: str) -> str:
    """
    Execute a SQL query against the database and return the results.
    
    - For SELECT queries: returns matching rows as a JSON list.
    - For INSERT / UPDATE / DELETE: returns the number of affected rows.
    - Use with caution — only safe, read-oriented queries are recommended for an AI agent.
    
    Args:
        sql: The SQL query string to execute.
    
    Returns a JSON object with the query results or status.
    """
    print(f"Executing query: {sql}")
    conn = None
    try:
        conn = await get_connection()
        sql_stripped = sql.strip().upper()

        if sql_stripped.startswith("SELECT") or sql_stripped.startswith("WITH"):
            rows = await conn.fetch(sql)
            results = [dict(row) for row in rows]
            result = json.dumps(
                {"rows": results, "row_count": len(results)},
                indent=2,
                default=str,  # handle non-serializable types like datetime
            )
            print(results)
            return result
        else:
            status = await conn.execute(sql)
            result = json.dumps({"status": status})
            print(status)
            return result
    except Exception as e:
        result = json.dumps({"error": str(e)})
        print(str(e))
        return result
    finally:
        if conn:
            await conn.close()


if __name__ == "__main__":
    # Use the 'run' method with streamable-http transport
    mcp.run(transport="streamable-http")
