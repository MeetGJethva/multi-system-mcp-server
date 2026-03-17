from mcp.server.fastmcp import FastMCP
import httpx
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create a FastMCP server
mcp = FastMCP("GitHub Server", host="127.0.0.1", port=8002)

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

@mcp.tool()
async def get_repo_info(owner: str, repo: str) -> str:
    """Get real-time information about a GitHub repository including stars, forks, and description."""
    print(f"GitHub service called for: {owner}/{repo}")
    
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "MCP-GitHub-Server"
    }
    
    if GITHUB_TOKEN and GITHUB_TOKEN != "your_github_token_here":
        headers["Authorization"] = f"token {GITHUB_TOKEN}"

    async with httpx.AsyncClient() as client:
        url = f"https://api.github.com/repos/{owner}/{repo}"
        try:
            response = await client.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                info = f"""
                    "Repository: {data['full_name']}\n"
                    "Description: {data.get('description', 'No description')}\n"
                    "Stars: {data['stargazers_count']}\n"
                    "Forks: {data['forks_count']}\n"
                    "Open Issues: {data['open_issues_count']}\n"
                    "Language: {data.get('language', 'N/A')}\n"
                    "URL: {data['html_url']}"
                """
                print(info)
                return info
            elif response.status_code == 404:
                return f"Error: Repository '{owner}/{repo}' not found."
            else:
                return f"Error: GitHub API returned status {response.status_code}. {response.text}"
        except Exception as e:
            return f"Error: Failed to connect to GitHub API: {str(e)}"

if __name__ == "__main__":
    mcp.run(transport="streamable-http")
