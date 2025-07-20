#!/usr/bin/env python3
"""Test Hinemos REST API connection and basic operations."""

import os
import sys

# Add the parent directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

from src.hinemos_mcp.client import HinemosClient
from src.hinemos_mcp.repository import RepositoryAPI


def test_connection():
    """Test basic Hinemos connection."""
    config = {
        "base_url": os.environ.get("HINEMOS_BASE_URL", "http://localhost:8080/HinemosWeb/api"),
        "username": os.environ.get("HINEMOS_USERNAME", "hinemos"),
        "password": os.environ.get("HINEMOS_PASSWORD", "hinemos"),
        "verify_ssl": False
    }
    
    print(f"Testing connection to: {config['base_url']}")
    print(f"Username: {config['username']}")
    
    try:
        with HinemosClient(**config) as client:
            print("✓ Client connection successful")
            
            # Test repository API
            repo_api = RepositoryAPI(client)
            
            # List all scopes first (should include root scope)
            print("\n--- Testing list_scopes ---")
            scopes = repo_api.list_scopes()
            print(f"Found {len(scopes)} scopes:")
            for scope in scopes[:10]:  # Show first 10
                print(f"  - {scope.facility_id}: {scope.facility_name}")
            
            # List all nodes
            print("\n--- Testing list_nodes ---")
            nodes = repo_api.list_nodes()
            print(f"Found {len(nodes)} nodes:")
            for node in nodes[:10]:  # Show first 10
                print(f"  - {node.facility_id}: {node.facility_name}")
                if hasattr(node, 'ip_address'):
                    print(f"    IP: {node.ip_address}")
            
            # Try to get a specific node that should exist
            if nodes:
                print(f"\n--- Testing get_node with first available node ---")
                first_node = nodes[0]
                print(f"Trying to get node: {first_node.facility_id}")
                node_detail = repo_api.get_node(first_node.facility_id)
                print(f"✓ Successfully retrieved node: {node_detail.facility_name}")
            
            # Test with ROOT facility ID specifically
            print(f"\n--- Testing get_node with ROOT ---")
            try:
                root_node = repo_api.get_node("ROOT")
                print(f"✓ ROOT node found: {root_node.facility_name}")
            except Exception as e:
                print(f"✗ ROOT node error: {str(e)}")
                
                # Check if ROOT exists in scopes
                root_scopes = [s for s in scopes if s.facility_id == "ROOT"]
                if root_scopes:
                    print(f"  But ROOT exists as scope: {root_scopes[0].facility_name}")
                else:
                    print("  ROOT not found in scopes either")
            
    except Exception as e:
        print(f"✗ Connection failed: {str(e)}")
        return False
    
    return True


if __name__ == "__main__":
    # Set environment variables
    os.environ["HINEMOS_BASE_URL"] = "http://localhost:8080/HinemosWeb/api"
    os.environ["HINEMOS_USERNAME"] = "hinemos"
    os.environ["HINEMOS_PASSWORD"] = "hinemos"
    
    success = test_connection()
    sys.exit(0 if success else 1)