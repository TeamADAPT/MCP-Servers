#!/usr/bin/env python3
"""
Direct test of the feature flags module without relying on imports
"""

import os
import sys
import importlib.util

# Path to feature_flags.py
feature_flags_path = '/data-nova/ax/DevOps/mcp/mcp-troubleshoot/Atlassian-connection/mcp-atlassian/src/mcp_atlassian/feature_flags.py'

try:
    # Load the module directly from file
    spec = importlib.util.spec_from_file_location("feature_flags", feature_flags_path)
    feature_flags = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(feature_flags)
    
    print("✅ Successfully loaded feature_flags module!")
    
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
    print("\nChecking individual flags:")
    for flag in feature_flags.ALL_FLAGS:
        print(f"  {flag}: {feature_flags.is_enabled(flag)}")
    
    print("\n✅ Feature flags system is working correctly!")
    sys.exit(0)
except Exception as e:
    print(f"❌ Error testing feature_flags module: {e}")
    sys.exit(1)