#!/usr/bin/env python3
"""Debug script to check scope visibility in facility tree."""

import os
import sys

# Add the parent directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

from src.hinemos_mcp.client import HinemosClient
from src.hinemos_mcp.repository import RepositoryAPI


def debug_scope_visibility():
    """Debug scope visibility with different owner role settings."""
    
    print("Debugging Scope Visibility")
    print("=" * 50)
    
    config = {
        "base_url": "http://localhost:8080/HinemosWeb/api",
        "username": "hinemos",
        "password": "hinemos",
        "verify_ssl": False
    }
    
    try:
        with HinemosClient(**config) as client:
            repo_api = RepositoryAPI(client)
            
            print("1. Testing facility tree with different owner role IDs...")
            
            # Test with different owner role IDs
            owner_roles = ["ALL_USERS", "ADMINISTRATORS", ""]
            
            for role in owner_roles:
                print(f"\n--- Testing with ownerRoleId: '{role}' ---")
                try:
                    tree_data = repo_api.get_facility_tree(owner_role_id=role)
                    
                    # Count facilities in tree
                    def count_facilities(node, depth=0):
                        count = 1
                        indent = "  " * depth
                        facility_type = node.get('facilityType', 'UNKNOWN')
                        owner_role = node.get('ownerRoleId', 'N/A')
                        print(f"{indent}- {node.get('facilityName', 'N/A')} (ID: {node.get('facilityId', 'N/A')}, Type: {facility_type}, Owner: {owner_role})")
                        
                        if 'children' in node:
                            for child in node['children']:
                                count += count_facilities(child, depth + 1)
                        return count
                    
                    if isinstance(tree_data, dict):
                        total = count_facilities(tree_data)
                        print(f"Total facilities found: {total}")
                    else:
                        print(f"Unexpected tree structure: {type(tree_data)}")
                        
                except Exception as e:
                    print(f"Error with ownerRoleId '{role}': {e}")
            
            print("\n2. Checking all facilities...")
            try:
                all_facilities = repo_api.get_all_facilities()
                print(f"\nTotal facilities in system: {len(all_facilities)}")
                
                # Look for recently created scopes
                print("\nRecent scopes (non-built-in):")
                for facility in all_facilities:
                    if (hasattr(facility, 'facility_type') and 
                        facility.facility_type and 
                        'SCOPE' in str(facility.facility_type) and
                        not getattr(facility, 'built_in_flg', False)):
                        print(f"  - {facility.facility_name} (ID: {facility.facility_id}, Owner: {getattr(facility, 'owner_role_id', 'N/A')})")
                        
            except Exception as e:
                print(f"Error getting all facilities: {e}")
                
    except Exception as e:
        print(f"Connection error: {e}")


if __name__ == "__main__":
    debug_scope_visibility()