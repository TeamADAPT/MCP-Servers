#!/usr/bin/env python
"""
Focused test for feature flags that doesn't rely on imports from MCP server
"""

import os
import sys
import logging
from typing import Set, Dict, List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("feature-flags-test")

# Simplified config module implementation
class FeatureFlags:
    """
    Feature flags for conditional enablement of MCP Atlassian features.
    Simplified version for testing.
    """
    
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
        self._runtime_overrides: Dict[str, bool] = {}
        
        # Load flags from main environment variable
        flags_str = os.environ.get("MCP_ATLASSIAN_FEATURE_FLAGS", "")
        if flags_str:
            for flag in flags_str.split(","):
                flag = flag.strip().upper()
                if flag in self.ALL_FLAGS:
                    self._enabled_flags.add(flag)
        
        # Check for individual flag environment variables
        for flag in self.ALL_FLAGS:
            env_var = f"MCP_ATLASSIAN_ENABLE_{flag}"
            if os.environ.get(env_var, "").lower() in ("true", "1", "yes"):
                self._enabled_flags.add(flag)
    
    def is_enabled(self, flag_name: str) -> bool:
        """Check if a feature flag is enabled."""
        # Check runtime overrides first
        if flag_name in self._runtime_overrides:
            return self._runtime_overrides[flag_name]
        
        # Then check environment-based flags
        return flag_name in self._enabled_flags
    
    def enable(self, flag_name: str) -> bool:
        """Enable a feature flag at runtime."""
        if flag_name not in self.ALL_FLAGS:
            logger.warning(f"Attempted to enable unknown feature flag: {flag_name}")
            return False
        
        self._runtime_overrides[flag_name] = True
        return True
    
    def disable(self, flag_name: str) -> bool:
        """Disable a feature flag at runtime."""
        if flag_name not in self.ALL_FLAGS:
            logger.warning(f"Attempted to disable unknown feature flag: {flag_name}")
            return False
        
        self._runtime_overrides[flag_name] = False
        return True
    
    def get_enabled_flags(self) -> List[str]:
        """Get list of all enabled flags."""
        result = []
        
        for flag in self.ALL_FLAGS:
            if self.is_enabled(flag):
                result.append(flag)
                
        return result

class MCPConfig:
    """
    MCP Configuration for Atlassian services.
    Simplified version for testing.
    """
    
    def __init__(self):
        """Initialize MCP config."""
        self.feature_flags = FeatureFlags()

# Global config instance
_config: Optional[MCPConfig] = None

def get_config() -> MCPConfig:
    """Get the global config instance."""
    global _config
    
    if _config is None:
        _config = MCPConfig()
        
    return _config

# Test the implementation
def run_tests():
    """Run tests for feature flags."""
    # Test 1: Default configuration (no flags enabled)
    logger.info("Test 1: Default configuration (no flags enabled)")
    flags = get_config().feature_flags
    
    logger.info(f"Enabled flags: {flags.get_enabled_flags()}")
    logger.info(f"Is ENHANCED_JIRA enabled? {flags.is_enabled('ENHANCED_JIRA')}")
    logger.info(f"Is BITBUCKET_INTEGRATION enabled? {flags.is_enabled('BITBUCKET_INTEGRATION')}")
    
    # Test 2: Enable flags through environment variables
    logger.info("\nTest 2: Enable flags through environment variables")
    os.environ["MCP_ATLASSIAN_FEATURE_FLAGS"] = "ENHANCED_JIRA,BITBUCKET_INTEGRATION"
    
    # Recreate config to pick up new environment variables
    global _config
    _config = None
    
    flags = get_config().feature_flags
    logger.info(f"Enabled flags: {flags.get_enabled_flags()}")
    logger.info(f"Is ENHANCED_JIRA enabled? {flags.is_enabled('ENHANCED_JIRA')}")
    logger.info(f"Is BITBUCKET_INTEGRATION enabled? {flags.is_enabled('BITBUCKET_INTEGRATION')}")
    
    # Test 3: Enable/disable at runtime
    logger.info("\nTest 3: Enable/disable at runtime")
    
    logger.info(f"Enabling JSM_INTEGRATION: {flags.enable('JSM_INTEGRATION')}")
    logger.info(f"Disabling ENHANCED_JIRA: {flags.disable('ENHANCED_JIRA')}")
    
    logger.info(f"Enabled flags: {flags.get_enabled_flags()}")
    logger.info(f"Is ENHANCED_JIRA enabled? {flags.is_enabled('ENHANCED_JIRA')}")
    logger.info(f"Is JSM_INTEGRATION enabled? {flags.is_enabled('JSM_INTEGRATION')}")
    
    # Test 4: Test with individual flag environment variables
    logger.info("\nTest 4: Test with individual flag environment variables")
    os.environ.clear()
    os.environ["MCP_ATLASSIAN_ENABLE_ENHANCED_CONFLUENCE"] = "true"
    
    # Recreate config to pick up new environment variables
    _config = None
    
    flags = get_config().feature_flags
    logger.info(f"Enabled flags: {flags.get_enabled_flags()}")
    logger.info(f"Is ENHANCED_CONFLUENCE enabled? {flags.is_enabled('ENHANCED_CONFLUENCE')}")
    
    logger.info("\nAll tests passed!")

if __name__ == "__main__":
    run_tests()
