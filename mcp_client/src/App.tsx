import React, { useState, useEffect } from 'react';
import { api, MCPServer, MCPTool } from './api';
import { Layout, Server, Tool, Play, CheckCircle, AlertCircle } from 'lucide-react';
import './App.css';

function App() {
  const [servers, setServers] = useState<MCPServer[]>([]);
  const [selectedServer, setSelectedServer] = useState<MCPServer | null>(null);
  const [tools, setTools] = useState<MCPTool[]>([]);
  const [results, setResults] = useState<Record<string, any>>({});
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadServers();
  }, []);

  const loadServers = async () => {
    try {
      const data = await api.getServers();
      setServers(data);
    } catch (err) {
      console.error('Failed to load servers', err);
    }
  };

  const selectServer = async (server: MCPServer) => {
    setSelectedServer(server);
    setLoading(true);
    try {
      const data = await api.getTools(server.name);
      setTools(data);
    } catch (err) {
      console.error('Failed to load tools', err);
      setTools([]);
    } finally {
      setLoading(false);
    }
  };

  const runTool = async (tool: MCPTool) => {
    if (!selectedServer) return;
    setLoading(true);
    try {
      // For simplicity, we use empty arguments or mock them
      // In a real app, you'd show a form based on tool.inputSchema
      const result = await api.callTool(selectedServer.name, tool.name, {});
      setResults((prev: Record<string, any>) => ({ ...prev, [tool.name]: result }));
    } catch (err) {
      setResults((prev: Record<string, any>) => ({ ...prev, [tool.name]: { error: String(err) } }));
    } finally {
      setLoading(false);
    }
  };

  const [groqKey, setGroqKey] = useState(localStorage.getItem('groq_key') || '');

  useEffect(() => {
    localStorage.setItem('groq_key', groqKey);
  }, [groqKey]);

  return (
    <div className="app">
      <div className="sidebar">
        <h2 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Layout size={24} color="#6366f1" />
          MCP Hub
        </h2>
        
        <div style={{ marginTop: '1.5rem', marginBottom: '1.5rem' }}>
          <label style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Groq API Key</label>
          <input 
            type="password" 
            className="input" 
            value={groqKey} 
            onChange={(e: React.ChangeEvent<HTMLInputElement>) => setGroqKey(e.target.value)}
            placeholder="gsk_..."
            style={{ width: '100%', marginTop: '0.5rem', background: 'rgba(255,255,255,0.05)', border: '1px solid var(--border)', borderRadius: '6px', padding: '0.5rem', color: 'white' }}
          />
        </div>

        <div style={{ marginTop: '1rem' }}>
          <h4 style={{ color: 'var(--text-muted)', fontSize: '0.75rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
            Connected Servers
          </h4>
          {servers.map((s: MCPServer) => (
            <div 
              key={s.id} 
              className={`server-item ${selectedServer?.id === s.id ? 'active' : ''}`}
              onClick={() => selectServer(s)}
            >
              <Server size={18} />
              <span>{s.name}</span>
            </div>
          ))}
        </div>
      </div>

      <div className="main-content">
        {!selectedServer ? (
          <div style={{ textAlign: 'center', marginTop: '10rem', color: 'var(--text-muted)' }}>
            <Server size={64} style={{ marginBottom: '1rem', opacity: 0.5 }} />
            <h3>Select a server to get started</h3>
          </div>
        ) : (
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
              <h1>{selectedServer.name}</h1>
              <span style={{ fontSize: '0.875rem', color: 'var(--text-muted)' }}>
                {selectedServer.endpoint}:{selectedServer.port}
              </span>
            </div>

            {loading && <div>Loading tools...</div>}

            <div className="tools-grid">
              {tools.map(tool => (
                <div key={tool.name} className="card tool-card">
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                    <div>
                      <h3 style={{ margin: 0 }}>{tool.name}</h3>
                      <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginTop: '0.5rem' }}>
                        {tool.description}
                      </p>
                    </div>
                    <button className="btn" onClick={() => runTool(tool)} disabled={loading}>
                      <Play size={14} style={{ marginRight: '0.4rem' }} />
                      Run
                    </button>
                  </div>

                  {results[tool.name] && (
                    <div style={{ marginTop: '1.5rem' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem', fontSize: '0.875rem' }}>
                        {results[tool.name].error ? <AlertCircle size={14} color="#ef4444" /> : <CheckCircle size={14} color="#10b981" />}
                        <span>Result:</span>
                      </div>
                      <pre>{JSON.stringify(results[tool.name], null, 2)}</pre>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
