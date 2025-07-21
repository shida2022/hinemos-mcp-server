#!/usr/bin/env python3
"""Hinemos MCP HTTP Server entry point."""

import asyncio
import os
import sys
from src.hinemos_mcp.server.http_fastmcp_server import HinemosHTTPFastMCPServer


def main():
    """Main entry point for Hinemos HTTP MCP Server."""
    # Get configuration from environment variables
    base_url = os.environ.get("HINEMOS_BASE_URL", "http://localhost:8080/HinemosWeb/api")
    username = os.environ.get("HINEMOS_USERNAME", "hinemos")
    password = os.environ.get("HINEMOS_PASSWORD", "hinemos")
    verify_ssl = os.environ.get("HINEMOS_VERIFY_SSL", "true").lower() == "true"
    
    # HTTP server configuration
    host = os.environ.get("MCP_HTTP_HOST", "127.0.0.1")
    port = int(os.environ.get("MCP_HTTP_PORT", "8000"))
    
    # Validate required configuration
    if not all([base_url, username, password]):
        print("Error: Missing required environment variables:", file=sys.stderr)
        print("Required: HINEMOS_BASE_URL, HINEMOS_USERNAME, HINEMOS_PASSWORD", file=sys.stderr)
        print("Optional: HINEMOS_VERIFY_SSL (default: true)", file=sys.stderr)
        print("Optional: MCP_HTTP_HOST (default: 127.0.0.1), MCP_HTTP_PORT (default: 8000)", file=sys.stderr)
        sys.exit(1)
    
    # Create and run server
    server = HinemosHTTPFastMCPServer(
        base_url=base_url,
        username=username,
        password=password,
        verify_ssl=verify_ssl
    )
    
    print(f"Starting Hinemos HTTP MCP Server...", file=sys.stderr)
    print(f"Hinemos URL: {base_url}", file=sys.stderr)
    print(f"Username: {username}", file=sys.stderr)
    print(f"SSL Verification: {verify_ssl}", file=sys.stderr)
    print(f"Server will run on: http://{host}:{port}", file=sys.stderr)
    print("", file=sys.stderr)
    print("Available endpoints:", file=sys.stderr)
    print(f"  Health Check: http://{host}:{port}/health", file=sys.stderr)
    print(f"  Tools List:   http://{host}:{port}/tools", file=sys.stderr)
    print(f"  Resources:    http://{host}:{port}/resources", file=sys.stderr)
    print("", file=sys.stderr)
    
    try:
        server.run(host=host, port=port)
    except KeyboardInterrupt:
        print("\\nServer stopped by user", file=sys.stderr)
    except Exception as e:
        print(f"Server error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()