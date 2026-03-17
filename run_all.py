import subprocess
import time
import os
import sys

def run_command(command, name):
    print(f"Starting {name}...")
    return subprocess.Popen(command, shell=True)

def main():
    # 1. Start Database Server
    db_server = run_command("python mcp_servers/db_server/main.py", "Database Server")
    
    # 2. Start GitHub Server
    github_server = run_command("python mcp_servers/github_server/main.py", "GitHub Server")
    
    # Give servers time to start
    time.sleep(2)
    
    # 3. Start Gateway
    gateway = run_command("python mcp_gateway/main.py", "MCP Gateway")
    
    print("\nAll systems starting up. Press Ctrl+C to stop all.")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping all services...")
        db_server.terminate()
        github_server.terminate()
        gateway.terminate()
        print("Done.")

if __name__ == "__main__":
    main()
