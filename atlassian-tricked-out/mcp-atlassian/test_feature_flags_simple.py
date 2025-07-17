#!/usr/bin/env python3
"""
Simple standalone test for the feature flags system
"""

import os
import sys

# Add the MCP Atlassian package to the Python path
sys.path.insert(0, '/data-nova/ax/DevOps/mcp/mcp-troubleshoot/Atlassian-connection/mcp-atlassian/src')

# Test by importing the feature_flags module
try:
    from mcp_atlassian import feature_flags
    print("✅ Successfully imported feature_flags module!")
    
    # List all flags
    print("\nAll available flags:")
    for flag in feature_flags.ALL_FLAGS:
        print(f"  - {flag}")
    
    # Set an environment variable
    os.environ["MCP_ATLASSIAN_FEATURE_FLAGS"] = "ENHANCED_JIRA,BITBUCKET_INTEGRATION"
    
    # Reset the flags
    feature_flags.reset_runtime_overrides()
    
    # Get enabled flags
    print("\nEnabled flags after setting environment variable:")
    for flag in feature_flags.get_enabled_flags():
        print(f"  - {flag}")
    
    # Enable a flag at runtime
    feature_flags.enable_feature("ENHANCED_CONFLUENCE")
    
    # Get enabled flags again
    print("\nEnabled flags after runtime enable:")
    for flag in feature_flags.get_enabled_flags():
        print(f"  - {flag}")
    
    # Test is_enabled
    for flag in feature_flags.ALL_FLAGS:
        print(f"  {flag}: {feature_flags.is_enabled(flag)}")
    
    print("\n✅ Feature flags system is working correctly!")
    sys.exit(0)
except ImportError as e:
    print(f"❌ Error importing feature_flags module: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error testing feature_flags module: {e}")
    sys.exit(1)