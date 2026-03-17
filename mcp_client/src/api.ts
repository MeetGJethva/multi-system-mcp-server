import axios from 'axios';

const GATEWAY_URL = 'http://localhost:8000';

export interface MCPServer {
  id: number;
  name: string;
  endpoint: string;
  port: number;
}

export interface MCPTool {
  name: string;
  description: string;
  inputSchema: any;
}

export const api = {
  getServers: async () => {
    const response = await axios.get(`${GATEWAY_URL}/servers`);
    return response.data as MCPServer[];
  },
  getTools: async (serverName: string) => {
    const response = await axios.get(`${GATEWAY_URL}/servers/${serverName}/tools`);
    return response.data as MCPTool[];
  },
  callTool: async (serverName: string, toolName: string, arguments_obj: any) => {
    const response = await axios.post(`${GATEWAY_URL}/servers/${serverName}/tools/${toolName}`, {
      arguments: arguments_obj
    });
    return response.data;
  }
};
