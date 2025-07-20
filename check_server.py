#!/usr/bin/env python3
"""Check server implementation."""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.hinemos_mcp.server.server import HinemosMCPServer


def check_server():
    """Check server implementation."""
    
    print("Checking Server Implementation")
    print("=" * 40)
    
    # Create server instance
    server = HinemosMCPServer(
        base_url="http://localhost:8080/HinemosWeb/api",
        username="test",
        password="test",
        verify_ssl=False
    )
    
    print("✓ Server created successfully")
    print(f"✓ Server name: {server.server.name}")
    
    # Check the source code for tool definitions
    import inspect
    source = inspect.getsource(HinemosMCPServer._setup_handlers)
    
    # Count tool definitions
    scope_tools = [
        "hinemos_create_scope",
        "hinemos_assign_nodes_to_scope", 
        "hinemos_remove_nodes_from_scope"
    ]
    
    print(f"\nChecking for scope tools in source code:")
    for tool in scope_tools:
        if tool in source:
            print(f"✓ {tool} - Found in source")
        else:
            print(f"✗ {tool} - NOT found in source")
    
    # Check if the tools are properly defined in the list_tools function
    if "hinemos_create_scope" in source:
        print(f"\n✓ Scope tools are implemented in the server")
    else:
        print(f"\n✗ Scope tools are missing from the server")
    
    # Check call_tool handler
    if "elif name == \"hinemos_create_scope\":" in source:
        print(f"✓ Tool handlers are implemented")
    else:
        print(f"✗ Tool handlers are missing")
    
    return True


if __name__ == "__main__":
    check_server()