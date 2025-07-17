from dataclasses import dataclass


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
