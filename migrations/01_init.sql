CREATE TABLE mcp_servers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    endpoint VARCHAR(255) NOT NULL,
    port INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Seed initial servers
INSERT INTO mcp_servers (name, endpoint, port) VALUES 
('database_server', 'http://127.0.0.1', 8001),
('github_server', 'http://127.0.0.1', 8002);
