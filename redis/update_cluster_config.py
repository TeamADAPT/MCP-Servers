#!/usr/bin/env python3

import json
import sys
import os

def update_config():
    # Paths
    cline_settings_path = "/home/x/.config/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json"
    cluster_config_path = "redis-cluster-mcp-config.json"
    
    try:
        # Read current Cline settings
        with open(cline_settings_path, "r") as f:
            cline_settings = json.load(f)
        
        # Read cluster Redis MCP config    
        with open(cluster_config_path, "r") as f:
            cluster_config = json.load(f)
        
        # Update redis-cluster configuration in Cline settings
        for server_name, config in cluster_config["mcpServers"].items():
            cline_settings["mcpServers"][server_name] = config
        
        # Write updated settings back to file
        with open(cline_settings_path, "w") as f:
            json.dump(cline_settings, f, indent=2)
            
        print(f"Successfully added {list(cluster_config['mcpServers'].keys())} to Cline settings")
        return True
    except Exception as e:
        print(f"Error updating configuration: {e}")
        return False

if __name__ == "__main__":
    update_config()
