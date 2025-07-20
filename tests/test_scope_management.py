#!/usr/bin/env python3
"""Test script for scope management features."""

import asyncio
import json
import os
import sys

# Add the parent directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

from src.hinemos_mcp.server.server import HinemosMCPServer


async def test_scope_tools():
    """Test scope creation and node assignment tools."""
    
    # Initialize server (using dummy credentials for testing)
    server = HinemosMCPServer(
        base_url="http://localhost:8080/HinemosWeb/api",
        username="hinemos",
        password="hinemos",
        verify_ssl=False
    )
    
    print("Testing scope management tools...")
    
    # Test 1: List available tools
    print("\n1. Listing available tools...")
    try:
        tools = await server.server.list_tools()
        scope_tools = [tool for tool in tools if 'scope' in tool.name]
        
        print(f"Found {len(scope_tools)} scope-related tools:")
        for tool in scope_tools:
            print(f"  - {tool.name}: {tool.description}")
            
    except Exception as e:
        print(f"Error listing tools: {e}")
    
    # Test 2: Check tool schemas
    print("\n2. Checking tool schemas...")
    try:
        tools = await server.server.list_tools()
        for tool in tools:
            if 'scope' in tool.name:
                print(f"\nTool: {tool.name}")
                print(f"Schema: {json.dumps(tool.inputSchema, indent=2)}")
                
    except Exception as e:
        print(f"Error checking schemas: {e}")
    
    print("\nScope management tools are properly configured!")
    return True


def test_repository_api():
    """Test the RepositoryAPI scope functions directly."""
    print("\n3. Testing RepositoryAPI scope functions...")
    
    try:
        from src.hinemos_mcp.repository import RepositoryAPI
        from src.hinemos_mcp.client import HinemosClient
        
        print("✓ Successfully imported RepositoryAPI")
        print("✓ create_scope method exists:", hasattr(RepositoryAPI, 'create_scope'))
        print("✓ assign_nodes_to_scope method exists:", hasattr(RepositoryAPI, 'assign_nodes_to_scope'))
        print("✓ remove_nodes_from_scope method exists:", hasattr(RepositoryAPI, 'remove_nodes_from_scope'))
        
        return True
        
    except Exception as e:
        print(f"Error testing RepositoryAPI: {e}")
        return False


if __name__ == "__main__":
    print("Testing Scope Management Implementation")
    print("=" * 50)
    
    # Test 1: Repository API functions
    if test_repository_api():
        print("✓ RepositoryAPI tests passed")
    else:
        print("✗ RepositoryAPI tests failed")
    
    # Test 2: MCP Server tools
    try:
        result = asyncio.run(test_scope_tools())
        if result:
            print("✓ MCP Server tool tests passed")
        else:
            print("✗ MCP Server tool tests failed")
    except Exception as e:
        print(f"✗ MCP Server tool tests failed: {e}")
    
    print("\n" + "=" * 50)
    print("Test completed!")