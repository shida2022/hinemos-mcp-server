#!/usr/bin/env python3
"""Repository API usage examples.

This is a template file for repository operations.
Copy this file and update the configuration with your Hinemos server details.
"""

from hinemos_mcp import HinemosClient, RepositoryAPI

# Configuration template - update with your Hinemos server details
CONFIG = {
    "base_url": "http://your-hinemos-server:8080/HinemosWeb/api",
    "username": "your-username",
    "password": "your-password",
    "verify_ssl": False  # Set to True in production with valid SSL certificates
}

def main():
    """Main example function."""
    print("Repository API Examples")
    print("=" * 50)
    
    with HinemosClient(**CONFIG) as client:
        repo = RepositoryAPI(client)
        
        # Example 1: List all nodes
        print("\n1. Listing all nodes:")
        nodes = repo.list_nodes()
        print(f"Found {len(nodes)} nodes:")
        for node in nodes[:5]:  # Show first 5
            print(f"  - {node.facility_id}: {node.facility_name}")
        
        # Example 2: Get facility tree
        print("\n2. Getting facility tree:")
        tree = repo.get_facility_tree()
        print(f"Root facility: {tree.facility_name}")
        
        # Example 3: Create a new node (commented out for safety)
        print("\n3. Creating a new node (example):")
        print("# Uncomment and modify the following to create a node:")
        print("# new_node = repo.create_node(")
        print("#     facility_id='EXAMPLE_NODE',")
        print("#     facility_name='Example Node',")
        print("#     ip_address='192.168.1.100',")
        print("#     description='Example node for testing',")
        print("#     platform_family='LINUX'")
        print("# )")
        
        # Example 4: Search for specific node (update facility_id)
        print("\n4. Getting specific node details:")
        if nodes:
            first_node = nodes[0]
            node_detail = repo.get_node(first_node.facility_id)
            print(f"Node details for {node_detail.facility_id}:")
            print(f"  Name: {node_detail.facility_name}")
            print(f"  Description: {node_detail.description}")
            if hasattr(node_detail, 'ip_address_v4'):
                print(f"  IP: {node_detail.ip_address_v4}")
        
        # Example 5: Get agent status
        print("\n5. Agent status:")
        try:
            agent_status = repo.get_agent_status()
            print(f"Found {len(agent_status['agents'])} agents")
            for agent in agent_status['agents'][:3]:  # Show first 3
                print(f"  - {agent['facility_id']}: last login {agent['last_login']}")
        except Exception as e:
            print(f"Could not get agent status: {e}")

if __name__ == "__main__":
    main()