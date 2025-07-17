from dataclasses import dataclass, field
import os
from typing import Dict, List, Any, Optional, Set


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
        """Check if a feature flag is enabled.
        
        Args:
            flag: Feature flag name
            
        Returns:
            True if the flag is enabled, False otherwise
        """
        return flag in self._enabled_flags
    
    def enable(self, flag: str) -> bool:
        """Enable a feature flag at runtime.
        
        Args:
            flag: Feature flag name
            
        Returns:
            True if the flag was enabled, False if it was invalid
        """
        if flag in self.ALL_FLAGS:
            self._enabled_flags.add(flag)
            return True
        return False
    
    def disable(self, flag: str) -> bool:
        """Disable a feature flag at runtime.
        
        Args:
            flag: Feature flag name
            
        Returns:
            True if the flag was disabled, False if it was invalid or not enabled
        """
        if flag in self._enabled_flags:
            self._enabled_flags.remove(flag)
            return True
        return False
    
    def get_enabled_flags(self) -> List[str]:
        """Get a list of all enabled feature flags.
        
        Returns:
            List of enabled feature flag names
        """
        return list(self._enabled_flags)


@dataclass
class MCPConfig:
    """Main MCP Atlassian configuration."""
    
    confluence: Optional["ConfluenceConfig"] = None
    jira: Optional["JiraConfig"] = None
    bitbucket: Optional["BitbucketConfig"] = None
    feature_flags: FeatureFlags = field(default_factory=FeatureFlags)


@dataclass
class ConfluenceConfig:
    """Confluence API configuration."""

    url: str  # Base URL for Confluence
    username: str  # Email or username
    api_token: str  # API token used as password

    @property
    def is_cloud(self) -> bool:
        """Check if this is a cloud instance."""
        return "atlassian.net" in self.url


@dataclass
class JiraConfig:
    """Jira API configuration."""

    url: str  # Base URL for Jira
    username: str  # Email or username
    api_token: str  # API token used as password

    @property
    def is_cloud(self) -> bool:
        """Check if this is a cloud instance."""
        return "atlassian.net" in self.url


@dataclass
class BitbucketConfig:
    """Bitbucket API configuration."""

    url: str  # Base URL for Bitbucket API
    workspace: str  # Bitbucket workspace
    username: str  # Email or username
    app_password: str  # App password for authentication

    @property
    def is_cloud(self) -> bool:
        """Check if this is a cloud instance."""
        return "api.bitbucket.org" in self.url


# Global configuration instance
_config: Optional[MCPConfig] = None


def get_config() -> MCPConfig:
    """Get or create the global configuration instance.
    
    Returns:
        MCPConfig instance
    """
    global _config
    
    if _config is None:
        _config = MCPConfig(
            feature_flags=FeatureFlags()
        )
        
        # Load configurations from environment if available
        if all([os.environ.get(var) for var in ["CONFLUENCE_URL", "CONFLUENCE_USERNAME", "CONFLUENCE_API_TOKEN"]]):
            _config.confluence = ConfluenceConfig(
                url=os.environ["CONFLUENCE_URL"],
                username=os.environ["CONFLUENCE_USERNAME"],
                api_token=os.environ["CONFLUENCE_API_TOKEN"]
            )
            
        if all([os.environ.get(var) for var in ["JIRA_URL", "JIRA_USERNAME", "JIRA_API_TOKEN"]]):
            _config.jira = JiraConfig(
                url=os.environ["JIRA_URL"],
                username=os.environ["JIRA_USERNAME"],
                api_token=os.environ["JIRA_API_TOKEN"]
            )
            
        if all([os.environ.get(var) for var in ["BITBUCKET_URL", "BITBUCKET_WORKSPACE", "BITBUCKET_USERNAME", "BITBUCKET_APP_PASSWORD"]]):
            _config.bitbucket = BitbucketConfig(
                url=os.environ["BITBUCKET_URL"],
                workspace=os.environ["BITBUCKET_WORKSPACE"],
                username=os.environ["BITBUCKET_USERNAME"],
                app_password=os.environ["BITBUCKET_APP_PASSWORD"]
            )
    
    return _config
