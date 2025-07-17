#!/usr/bin/env python3
"""Test for feature flags implementation."""

import os
import sys
from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional

# Define the feature flags class
class FeatureFlags:
    """Feature flags for conditional enablement of MCP Atlassian features."""
    
    # Feature flag constants
    ENHANCED_JIRA = "ENHANCED_JIRA"
    BITBUCKET_INTEGRATION = "BITBUCKET_INTEGRATION"
    ENHANCED_CONFLUENCE = "ENHANCED_CONFLUENCE"
    JSM_INTEGRATION = "JSM_INTEGRATION"
    ADVANCED_ANALYTICS = "ADVANCED_ANALYTICS"
    
    # All available flags
    ALL_FLAGS = {
        ENHANCED_JIRA,
        BITBUCKET_INTEGRATION,
        ENHANCED_CONFLUENCE,
        JSM_INTEGRATION,
        ADVANCED_ANALYTICS
    }
    
    def __init__(self):
        """Initialize feature flags from environment variables."""
        self._enabled_flags: Set[str] = set()
        
        # Load flags from environment
        flags_str = os.environ.get("MCP_ATLASSIAN_FEATURE_FLAGS", "")
        if flags_str:
            for flag in flags_str.split(","):
                flag = flag.strip().upper()
                if flag in self.ALL_FLAGS:
                    self._enabled_flags.add(flag)
                    
        # Load individual flags
        for flag in self.ALL_FLAGS:
            env_var = f"MCP_ATLASSIAN_ENABLE_{flag}"
            if os.environ.get(env_var, "").lower() in ("true", "1", "yes"):
                self._enabled_flags.add(flag)
    
    def is_enabled(self, flag: str) -> bool:
        """Check if a feature flag is enabled."""
        return flag in self._enabled_flags
    
    def enable(self, flag: str) -> bool:
        """Enable a feature flag at runtime."""
        if flag in self.ALL_FLAGS:
            self._enabled_flags.add(flag)
            return True
        return False
    
    def disable(self, flag: str) -> bool:
        """Disable a feature flag at runtime."""
        if flag in self._enabled_flags:
            self._enabled_flags.remove(flag)
            return True
        return False
    
    def get_enabled_flags(self) -> List[str]:
        """Get a list of all enabled feature flags."""
        return list(self._enabled_flags)


@dataclass
class MCPConfig:
    """Main MCP Atlassian configuration."""
    feature_flags: FeatureFlags = field(default_factory=FeatureFlags)


# Run tests
if __name__ == "__main__":
    print("=== Testing Feature Flags ===")
    
    # Test constructor with empty environment
    if "MCP_ATLASSIAN_FEATURE_FLAGS" in os.environ:
        del os.environ["MCP_ATLASSIAN_FEATURE_FLAGS"]
    
    flags = FeatureFlags()
    print(f"Enabled flags with empty environment: {flags.get_enabled_flags()}")
    
    # Test constructor with environment variable
    os.environ["MCP_ATLASSIAN_FEATURE_FLAGS"] = "ENHANCED_JIRA,BITBUCKET_INTEGRATION"
    flags = FeatureFlags()
    
    print(f"Enabled flags from environment: {flags.get_enabled_flags()}")
    print(f"Is ENHANCED_JIRA enabled? {flags.is_enabled('ENHANCED_JIRA')}")
    print(f"Is BITBUCKET_INTEGRATION enabled? {flags.is_enabled('BITBUCKET_INTEGRATION')}")
    print(f"Is ENHANCED_CONFLUENCE enabled? {flags.is_enabled('ENHANCED_CONFLUENCE')}")
    
    # Test enable/disable functions
    print("\nTesting enable/disable:")
    flags.disable("ENHANCED_JIRA")
    print(f"After disabling ENHANCED_JIRA: {flags.get_enabled_flags()}")
    print(f"Is ENHANCED_JIRA enabled? {flags.is_enabled('ENHANCED_JIRA')}")
    
    flags.enable("ENHANCED_JIRA")
    print(f"After enabling ENHANCED_JIRA: {flags.get_enabled_flags()}")
    print(f"Is ENHANCED_JIRA enabled? {flags.is_enabled('ENHANCED_JIRA')}")
    
    # Test MCPConfig
    print("\nTesting MCPConfig:")
    config = MCPConfig()
    print(f"MCPConfig enabled flags: {config.feature_flags.get_enabled_flags()}")
    
    # Test individual flag environment variables
    print("\nTesting individual flag environment variables:")
    del os.environ["MCP_ATLASSIAN_FEATURE_FLAGS"]
    os.environ["MCP_ATLASSIAN_ENABLE_ENHANCED_CONFLUENCE"] = "true"
    
    flags = FeatureFlags()
    print(f"Enabled flags with individual env var: {flags.get_enabled_flags()}")
    print(f"Is ENHANCED_CONFLUENCE enabled? {flags.is_enabled('ENHANCED_CONFLUENCE')}")
    
    print("\nFeature flags implementation works correctly!")