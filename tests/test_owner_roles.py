#!/usr/bin/env python3
"""Test different owner role IDs for facility tree."""

import os
import sys
import json

# Add the parent directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

from src.hinemos_mcp.client import HinemosClient
from src.hinemos_mcp.repository import RepositoryAPI


def test_owner_roles():
    """Test different owner role IDs."""
    config = {
        "base_url": "http://localhost:8080/HinemosWeb/api",
        "username": "hinemos",
        "password": "hinemos",
        "verify_ssl": False
    }
    
    # Test different owner role IDs
    role_ids_to_test = [
        "__ALL__",
        "ALL_USERS", 
        "ADMINISTRATORS",
        "ADMIN",
        "HINEMOS",
        "hinemos",
        None  # No parameter
    ]
    
    try:
        with HinemosClient(**config) as client:
            repo_api = RepositoryAPI(client)
            
            for role_id in role_ids_to_test:
                print(f"\n=== Testing owner role: {role_id} ===")
                try:
                    if role_id is None:
                        # Test without owner_role_id parameter
                        tree_data = repo_api.get_facility_tree()
                    else:
                        tree_data = repo_api.get_facility_tree(owner_role_id=role_id)
                    
                    if isinstance(tree_data, dict):
                        data = tree_data.get('data', {})
                        children = tree_data.get('children', [])
                        children_total = tree_data.get('childrenTotal', 0)
                        
                        print(f"✓ Success with role '{role_id}'")
                        print(f"  Root: {data.get('facilityId', 'N/A')} - {data.get('facilityName', 'N/A')}")
                        print(f"  Children count: {len(children)}")
                        print(f"  Children total: {children_total}")
                        
                        if children:
                            print("  First few children:")
                            for i, child in enumerate(children[:5]):
                                child_data = child.get('data', {})
                                print(f"    {i+1}. {child_data.get('facilityId', 'N/A')} - {child_data.get('facilityName', 'N/A')}")
                        
                        # If we found children, this is the correct role
                        if children:
                            print(f"*** FOUND WORKING ROLE: {role_id} ***")
                            return role_id
                            
                except Exception as e:
                    print(f"✗ Failed with role '{role_id}': {str(e)}")
            
            print("\n=== Testing REGISTERED scope specifically ===")
            for role_id in ["ALL_USERS", "ADMINISTRATORS", "__ALL__"]:
                try:
                    tree_data = repo_api.get_facility_tree("REGISTERED", role_id)
                    if isinstance(tree_data, dict):
                        data = tree_data.get('data')
                        children = tree_data.get('children', [])
                        
                        if data and children:
                            print(f"✓ REGISTERED scope works with role '{role_id}'")
                            print(f"  Scope: {data.get('facilityId', 'N/A')} - {data.get('facilityName', 'N/A')}")
                            print(f"  Contains {len(children)} facilities")
                            return role_id
                        else:
                            print(f"  REGISTERED scope empty with role '{role_id}'")
                except Exception as e:
                    print(f"✗ REGISTERED failed with role '{role_id}': {str(e)}")
    
    except Exception as e:
        print(f"Connection failed: {str(e)}")
        return None
    
    return None


if __name__ == "__main__":
    working_role = test_owner_roles()
    if working_role:
        print(f"\n*** RECOMMENDED OWNER ROLE ID: {working_role} ***")
    else:
        print("\n*** NO WORKING OWNER ROLE FOUND ***")