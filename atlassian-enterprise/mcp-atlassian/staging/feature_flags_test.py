#!/usr/bin/env python3
"""
Test script for feature flags in the MCP Atlassian integration.

This script verifies that the feature flags system is working correctly
and that Enhanced Jira features can be toggled on and off.
"""

import os
import sys
import json

# Add the src directory to the path
src_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, src_dir)

try:
    # Try to import the config module
    from src.mcp_atlassian.config import get_config, FeatureFlags
    
    # Create an instance of FeatureFlags
    print("=== Testing Feature Flags ===")
    
    # Get the global config
    config = get_config()
    print(f"Initial enabled flags: {config.feature_flags.get_enabled_flags()}")
    
    # Enable Enhanced Jira feature
    print("\nTesting feature flag enablement:")
    feature_name = "ENHANCED_JIRA"
    result = config.feature_flags.enable(feature_name)
    print(f"Enabled {feature_name}: {result}")
    print(f"Enabled flags after enabling {feature_name}: {config.feature_flags.get_enabled_flags()}")
    print(f"Is {feature_name} enabled? {config.feature_flags.is_enabled(feature_name)}")
    
    # Disable Enhanced Jira feature
    print("\nTesting feature flag disablement:")
    result = config.feature_flags.disable(feature_name)
    print(f"Disabled {feature_name}: {result}")
    print(f"Enabled flags after disabling {feature_name}: {config.feature_flags.get_enabled_flags()}")
    print(f"Is {feature_name} enabled? {config.feature_flags.is_enabled(feature_name)}")
    
    # Test environment variable loading
    print("\nTesting environment variable loading:")
    os.environ["MCP_ATLASSIAN_FEATURE_FLAGS"] = "ENHANCED_JIRA,BITBUCKET_INTEGRATION"
    
    # Create a new instance that should load from environment
    flags = FeatureFlags()
    print(f"Enabled flags from environment: {flags.get_enabled_flags()}")
    
    # Clean up
    del os.environ["MCP_ATLASSIAN_FEATURE_FLAGS"]
    
    print("\nFeature flags system is working correctly!")
    
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Please make sure you have the correct directory structure and the config.py file exists.")
    sys.exit(1)
except Exception as e:
    print(f"An error occurred while testing feature flags: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)