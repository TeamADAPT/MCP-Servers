#!/usr/bin/env python3

import json
import sys
import os

def update_config():
    # Paths
    cline_settings_path = "/home/x/.config/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json"
    fixed_config_path = "redis-mcp-config-fixed.json"
    
    try:
        # Read current Cline settings
        with open(cline_settings_path, "r") as f:
            cline_settings = json.load(f)
        
        # Read fixed Redis MCP config    
        with open(fixed_config_path, "r") as f:
            fixed_config = json.load(f)
        
        # Update redis-mcp configuration in Cline settings
        cline_settings["mcpServers"]["redis-mcp"] = fixed_config["mcpServers"]["redis-mcp"]
        
        # Write updated settings back to file
        with open(cline_settings_path, "w") as f:
            json.dump(cline_settings, f, indent=2)
            
        print("Successfully updated redis-mcp configuration in Cline settings")
        return True
    except Exception as e:
        print(f"Error updating configuration: {e}")
        return False

if __name__ == "__main__":
    update_config()
