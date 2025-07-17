"""
Configuration for MCP Atlassian Integration.
"""

import os
import logging
from typing import Dict, List, Set, Optional

logger = logging.getLogger("mcp-atlassian-config")

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
        """
        Check if a feature flag is enabled.
        
        Args:
            flag_name: The name of the feature flag
            
        Returns:
            bool: True if the flag is enabled, False otherwise
        """
        # Check runtime overrides first
        if flag_name in self._runtime_overrides:
            return self._runtime_overrides[flag_name]
        
        # Then check environment-based flags
        return flag_name in self._enabled_flags
    
    def enable(self, flag_name: str) -> bool:
        """
        Enable a feature flag at runtime.
        
        Args:
            flag_name: The name of the feature flag
            
        Returns:
            bool: True if the flag was enabled, False otherwise
        """
        if flag_name not in self.ALL_FLAGS:
            logger.warning(f"Attempted to enable unknown feature flag: {flag_name}")
            return False
        
        self._runtime_overrides[flag_name] = True
        return True
    
    def disable(self, flag_name: str) -> bool:
        """
        Disable a feature flag at runtime.
        
        Args:
            flag_name: The name of the feature flag
            
        Returns:
            bool: True if the flag was disabled, False otherwise
        """
        if flag_name not in self.ALL_FLAGS:
            logger.warning(f"Attempted to disable unknown feature flag: {flag_name}")
            return False
        
        self._runtime_overrides[flag_name] = False
        return True
    
    def get_enabled_flags(self) -> List[str]:
        """
        Get list of all enabled flags.
        
        Returns:
            List[str]: List of enabled flag names
        """
        result = []
        
        for flag in self.ALL_FLAGS:
            if self.is_enabled(flag):
                result.append(flag)
                
        return result

class JiraConfig:
    """Configuration for Jira."""
    
    def __init__(self, url=None, username=None, api_token=None):
        """
        Initialize Jira configuration.
        
        Args:
            url: Jira URL
            username: Jira username
            api_token: Jira API token
        """
        self.url = url or os.environ.get("JIRA_URL", "")
        self.username = username or os.environ.get("JIRA_USERNAME", "")
        self.api_token = api_token or os.environ.get("JIRA_API_TOKEN", "")
        
        # Validate configuration
        if not self.url:
            logger.warning("Jira URL is not configured")
        if not self.username:
            logger.warning("Jira username is not configured")
        if not self.api_token:
            logger.warning("Jira API token is not configured")

class ConfluenceConfig:
    """Configuration for Confluence."""
    
    def __init__(self, url=None, username=None, api_token=None):
        """
        Initialize Confluence configuration.
        
        Args:
            url: Confluence URL
            username: Confluence username
            api_token: Confluence API token
        """
        self.url = url or os.environ.get("CONFLUENCE_URL", "")
        self.username = username or os.environ.get("CONFLUENCE_USERNAME", "")
        self.api_token = api_token or os.environ.get("CONFLUENCE_API_TOKEN", "")
        
        # Use Jira credentials if not specified
        if not self.url:
            self.url = os.environ.get("JIRA_URL", "").replace("/jira", "")
        if not self.username:
            self.username = os.environ.get("JIRA_USERNAME", "")
        if not self.api_token:
            self.api_token = os.environ.get("JIRA_API_TOKEN", "")
        
        # Validate configuration
        if not self.url:
            logger.warning("Confluence URL is not configured")
        if not self.username:
            logger.warning("Confluence username is not configured")
        if not self.api_token:
            logger.warning("Confluence API token is not configured")

class BitbucketConfig:
    """Configuration for Bitbucket."""
    
    def __init__(self, url=None, username=None, api_token=None):
        """
        Initialize Bitbucket configuration.
        
        Args:
            url: Bitbucket URL
            username: Bitbucket username
            api_token: Bitbucket API token
        """
        self.url = url or os.environ.get("BITBUCKET_URL", "")
        self.username = username or os.environ.get("BITBUCKET_USERNAME", "")
        self.api_token = api_token or os.environ.get("BITBUCKET_API_TOKEN", "")
        
        # Use Jira credentials if not specified
        if not self.url:
            self.url = os.environ.get("JIRA_URL", "").replace("/jira", "/bitbucket")
        if not self.username:
            self.username = os.environ.get("JIRA_USERNAME", "")
        if not self.api_token:
            self.api_token = os.environ.get("JIRA_API_TOKEN", "")
        
        # Validate configuration
        if not self.url:
            logger.warning("Bitbucket URL is not configured")
        if not self.username:
            logger.warning("Bitbucket username is not configured")
        if not self.api_token:
            logger.warning("Bitbucket API token is not configured")

class MCPConfig:
    """
    MCP Configuration for Atlassian services.
    
    This class centralizes all configuration for the MCP Atlassian Integration.
    """
    
    _instance = None
    
    def __init__(self):
        """Initialize MCP config."""
        self.feature_flags = FeatureFlags()
        self.jira = JiraConfig()
        self.confluence = ConfluenceConfig()
        self.bitbucket = BitbucketConfig()

def get_config() -> MCPConfig:
    """
    Get the global config instance.
    
    Returns:
        MCPConfig: The global config instance
    """
    if MCPConfig._instance is None:
        MCPConfig._instance = MCPConfig()
    
    return MCPConfig._instance
EOFX < /dev/null
