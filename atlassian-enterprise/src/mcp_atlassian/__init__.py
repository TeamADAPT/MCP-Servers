import asyncio

from . import server
from .confluence import ConfluenceFetcher
from .jira import JiraFetcher

# We'll comment out the imports that may be causing issues
# but keep them here for future reference
# from .space_management import ConfluenceSpaceManager
# from .template_management import ConfluenceTemplateManager
# from .content_management import ConfluenceContentManager
# from .auth import auth_manager, AuthenticationManager
# from .analytics import analytics_manager, AnalyticsManager
# from .ai_capabilities import ai_capabilities_manager, AICapabilitiesManager
# from .marketplace_integration import app_integration_manager, AppIntegrationManager

__version__ = "0.3.0"


def main():
    """Main entry point for the package."""
    asyncio.run(server.main())


__all__ = [
    "main",
    "server",
    "__version__",
    "ConfluenceFetcher",
    "JiraFetcher"
    # "ConfluenceSpaceManager",
    # "ConfluenceTemplateManager",
    # "ConfluenceContentManager",
    # "JiraManager",
    # "auth_manager",
    # "AuthenticationManager",
    # "analytics_manager",
    # "AnalyticsManager",
    # "ai_capabilities_manager",
    # "AICapabilitiesManager",
    # "app_integration_manager",
    # "AppIntegrationManager"
]
