import asyncio

from . import server
from .confluence import ConfluenceFetcher
from .jira import JiraFetcher

# Additional modules will be enabled in future versions
# from .bitbucket import BitbucketManager
# from .bitbucket_integration import BitbucketIntegrationManager
# from .bitbucket_pipeline import BitbucketPipelineManager

__version__ = "0.2.1"


def main():
    """Main entry point for the package."""
    asyncio.run(server.main())


__all__ = [
    "main",
    "server",
    "__version__",
    "ConfluenceFetcher",
    "JiraFetcher"
    # "BitbucketManager",
    # "BitbucketIntegrationManager",
    # "BitbucketPipelineManager"
]
