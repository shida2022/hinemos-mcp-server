#!/usr/bin/env python3
"""Debug script to check available tools."""

import asyncio
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.hinemos_mcp.server.server import HinemosMCPServer


async def debug_tools():
    """Debug available tools."""
    
    print("Debugging MCP Tools")
    print("=" * 40)
    
    # Create server instance
    server = HinemosMCPServer(
        base_url=os.environ.get("HINEMOS_BASE_URL", "http://localhost:8080/HinemosWeb/api"),
        username=os.environ.get("HINEMOS_USERNAME", "hinemos"),
        password=os.environ.get("HINEMOS_PASSWORD", "hinemos"),
        verify_ssl=False
    )
    
    print("Server created successfully")
    
    # Get tools directly from the list_tools handler
    try:
        # Access the handler function directly
        handlers = server.server._handlers
        list_tools_handler = None
        
        for handler_type, handlers_list in handlers.items():
            if handler_type.value == 'tools/list':
                list_tools_handler = handlers_list[0] if handlers_list else None
                break
        
        if list_tools_handler:
            print("Found list_tools handler")
            tools = await list_tools_handler()
            
            print(f"\nFound {len(tools)} tools:")
            for i, tool in enumerate(tools, 1):
                print(f"{i}. {tool.name}")
                print(f"   Description: {tool.description}")
                if 'scope' in tool.name.lower():
                    print(f"   *** SCOPE TOOL ***")
                print()
                
        else:
            print("No list_tools handler found")
            
    except Exception as e:
        print(f"Error getting tools: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(debug_tools())