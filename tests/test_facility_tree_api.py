#!/usr/bin/env python3
"""Test the new facility tree API functionality."""

import os
import sys
import json

# Add the parent directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

from src.hinemos_mcp.client import HinemosClient
from src.hinemos_mcp.repository import RepositoryAPI


def test_facility_tree_api():
    """Test the facility tree API methods."""
    config = {
        "base_url": os.environ.get("HINEMOS_BASE_URL", "http://localhost:8080/HinemosWeb/api"),
        "username": os.environ.get("HINEMOS_USERNAME", "hinemos"),
        "password": os.environ.get("HINEMOS_PASSWORD", "hinemos"),
        "verify_ssl": False
    }
    
    print(f"Testing facility tree API with: {config['base_url']}")
    
    try:
        with HinemosClient(**config) as client:
            repo_api = RepositoryAPI(client)
            
            print("\n--- Testing get_facility_tree (full tree) ---")
            try:
                tree_data = repo_api.get_facility_tree()
                print("✓ Full facility tree retrieved successfully")
                print(f"Tree data type: {type(tree_data)}")
                if isinstance(tree_data, dict):
                    print(f"Root keys: {list(tree_data.keys())}")
                    if 'data' in tree_data:
                        data = tree_data['data']
                        print(f"Root facility: {data.get('facilityId', 'N/A')} - {data.get('facilityName', 'N/A')}")
                    if 'children' in tree_data:
                        children = tree_data['children']
                        print(f"Number of child facilities: {len(children) if children else 0}")
                        if children:
                            for i, child in enumerate(children[:3]):  # Show first 3 children
                                child_data = child.get('data', {})
                                print(f"  Child {i+1}: {child_data.get('facilityId', 'N/A')} - {child_data.get('facilityName', 'N/A')}")
                print()
            except Exception as e:
                print(f"✗ Full facility tree error: {str(e)}")
            
            print("\n--- Testing get_node_tree ---")
            try:
                node_tree = repo_api.get_node_tree()
                print("✓ Node tree retrieved successfully")
                print(f"Node tree type: {type(node_tree)}")
                if isinstance(node_tree, dict):
                    print(f"Node tree keys: {list(node_tree.keys())}")
                print()
            except Exception as e:
                print(f"✗ Node tree error: {str(e)}")
            
            # Test with a specific scope if we found any in the full tree
            print("\n--- Testing get_facility_tree with specific scope ---")
            try:
                # Try with a known scope
                test_scopes = ["AP_SERVER", "DB_SERVER", "REGISTERED"]
                for scope_id in test_scopes:
                    try:
                        scope_tree = repo_api.get_facility_tree(scope_id)
                        print(f"✓ Scope tree for '{scope_id}' retrieved successfully")
                        if isinstance(scope_tree, dict) and 'data' in scope_tree:
                            data = scope_tree['data']
                            print(f"  Scope: {data.get('facilityId', 'N/A')} - {data.get('facilityName', 'N/A')}")
                            children = scope_tree.get('children', [])
                            print(f"  Contains {len(children) if children else 0} child facilities")
                        break
                    except Exception as e:
                        print(f"  Scope '{scope_id}' not accessible: {str(e)}")
            except Exception as e:
                print(f"✗ Specific scope tree error: {str(e)}")
            
    except Exception as e:
        print(f"✗ Connection failed: {str(e)}")
        return False
    
    return True


if __name__ == "__main__":
    # Set environment variables
    os.environ["HINEMOS_BASE_URL"] = "http://localhost:8080/HinemosWeb/api"
    os.environ["HINEMOS_USERNAME"] = "hinemos"
    os.environ["HINEMOS_PASSWORD"] = "hinemos"
    
    success = test_facility_tree_api()
    sys.exit(0 if success else 1)