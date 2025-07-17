#!/usr/bin/env python3

import json
import sys
import os

def merge_configs():
    # Path to Cline MCP settings file
    cline_settings_path = "/home/x/.config/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json"
    
    # Path to Redis MCP config
    redis_config_path = "redis-mcp-config.json"
    
    try:
        # Load Cline MCP settings
        with open(cline_settings_path, "r") as f:
            cline_settings = json.load(f)
    except Exception as e:
        print(f"Error reading Cline MCP settings: {e}")
        return False
    
    try:
        # Load Redis MCP config
        with open(redis_config_path, "r") as f:
            redis_config = json.load(f)
    except Exception as e:
        print(f"Error reading Redis MCP config: {e}")
        return False
    
    # Initialize mcpServers if not present
    if "mcpServers" not in cline_settings:
        cline_settings["mcpServers"] = {}
    
    # Add/update Redis MCP server config
    cline_settings["mcpServers"]["redis-mcp"] = redis_config["mcpServers"]["redis-mcp"]
    
    try:
        # Write updated config back to Cline MCP settings file
        with open(cline_settings_path, "w") as f:
            json.dump(cline_settings, f, indent=2)
        print("Successfully merged redis-mcp configuration into Cline MCP settings")
        return True
    except Exception as e:
        print(f"Error writing to Cline MCP settings file: {e}")
        return False

if __name__ == "__main__":
    success = merge_configs()
    sys.exit(0 if success else 1)
