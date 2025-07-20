#!/usr/bin/env python3
"""Final test of facility tree functionality showing node-scope relationships."""

import os
import sys
import json

# Add the parent directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

from src.hinemos_mcp.client import HinemosClient
from src.hinemos_mcp.repository import RepositoryAPI


def test_final_facility_tree():
    """Final comprehensive test of facility tree."""
    config = {
        "base_url": "http://localhost:8080/HinemosWeb/api",
        "username": "hinemos",
        "password": "hinemos",
        "verify_ssl": False
    }
    
    try:
        with HinemosClient(**config) as client:
            repo_api = RepositoryAPI(client)
            
            print("=== COMPLETE FACILITY TREE STRUCTURE ===")
            tree_data = repo_api.get_facility_tree()
            
            def print_facility_tree(item, level=0):
                """Recursively print facility tree structure."""
                indent = "  " * level
                data = item.get('data', {})
                facility_id = data.get('facilityId', 'N/A')
                facility_name = data.get('facilityName', 'N/A')
                facility_type = data.get('facilityType', 'UNKNOWN')
                
                print(f"{indent}{facility_id} - {facility_name} [{facility_type}]")
                
                children = item.get('children', [])
                for child in children:
                    print_facility_tree(child, level + 1)
            
            print_facility_tree(tree_data)
            
            print("\n=== REGISTERED NODES SCOPE DETAILS ===")
            try:
                registered_tree = repo_api.get_facility_tree("REGISTERED")
                print("REGISTERED scope structure:")
                print_facility_tree(registered_tree)
            except Exception as e:
                print(f"Could not get REGISTERED scope: {str(e)}")
            
            print("\n=== NODE-SCOPE RELATIONSHIP SUMMARY ===")
            children = tree_data.get('children', [])
            for scope in children:
                scope_data = scope.get('data', {})
                scope_id = scope_data.get('facilityId', 'N/A')
                scope_name = scope_data.get('facilityName', 'N/A')
                scope_children = scope.get('children', [])
                
                print(f"\nScope: {scope_id} ({scope_name})")
                if scope_children:
                    print(f"  Contains {len(scope_children)} facilities:")
                    for child in scope_children:
                        child_data = child.get('data', {})
                        child_id = child_data.get('facilityId', 'N/A')
                        child_name = child_data.get('facilityName', 'N/A')
                        child_type = child_data.get('facilityType', 'UNKNOWN')
                        print(f"    - {child_id} ({child_name}) [{child_type}]")
                else:
                    print(f"  No direct child facilities")
            
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_final_facility_tree()