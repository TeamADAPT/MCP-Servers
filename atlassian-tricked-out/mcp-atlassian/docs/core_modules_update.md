# Core Modules Update

This document describes the updates made to the core modules in the MCP Atlassian integration as part of Phase 2 of the implementation plan.

## Overview

As part of the Phase 2 (Core Module Integration), the following changes have been made to the core modules:

1. Added `BitbucketConfig` class to `config.py`
2. Updated `__init__.py` with new version and import statements
3. Created stub files for Bitbucket integration
4. Added analytics.py module with basic functionality

## Detailed Changes

### 1. Config Module Updates (`config.py`)

The `config.py` file has been updated to include the `BitbucketConfig` class:

```python
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
```

This enables proper configuration for Bitbucket integration, similar to the existing JiraConfig and ConfluenceConfig classes.

### 2. Init Module Updates (`__init__.py`)

The `__init__.py` file has been updated with:

1. Version bump to 0.2.1
2. Added imports for ConfluenceFetcher and JiraFetcher
3. Added commented imports for future Bitbucket modules

```python
import asyncio

from . import server
from .confluence import ConfluenceFetcher
from .jira import JiraFetcher

# Additional modules will be enabled in future versions
# from .bitbucket import BitbucketManager
# from .bitbucket_integration import BitbucketIntegrationManager
# from .bitbucket_pipeline import BitbucketPipelineManager

__version__ = "0.2.1"
```

### 3. Bitbucket Integration Stubs

Three stub files have been created for Bitbucket integration:

1. **bitbucket.py**: Contains `BitbucketManager` class for basic Bitbucket operations like repository management
2. **bitbucket_integration.py**: Contains `BitbucketIntegrationManager` class for repository integrations, permissions, and analytics
3. **bitbucket_pipeline.py**: Contains `BitbucketPipelineManager` class for Bitbucket Pipelines operations

These files include skeleton methods and common utility functions like:
- `_make_api_request` for REST API communication
- `_paginate_results` for handling paginated API responses
- Core methods for basic functionality

### 4. Analytics Module (`analytics.py`)

A new module called `analytics.py` has been added with basic functionality:

1. `AnalyticsManager` class with stub methods for:
   - `get_project_metrics`: Basic metrics for Jira projects
   - `analyze_time_tracking`: Time tracking analysis
   - `detect_issue_patterns`: Issue pattern detection
   - `generate_trend_report`: Trend analysis over time
   - `generate_custom_report`: Custom report generation

## Environment Variables

The following environment variables can be used for Bitbucket configuration:

- `BITBUCKET_URL`: Bitbucket API URL (default: "https://api.bitbucket.org/2.0")
- `BITBUCKET_WORKSPACE`: Bitbucket workspace
- `BITBUCKET_USERNAME`: Bitbucket username
- `BITBUCKET_APP_PASSWORD`: Bitbucket app password

## Feature Flags

Bitbucket and Analytics features are controlled by feature flags:

```bash
# Enable Bitbucket features
export ENABLE_BITBUCKET=true
export ENABLE_BITBUCKET_INTEGRATION=true
export ENABLE_BITBUCKET_PIPELINE=true

# Enable analytics features
export ENABLE_ANALYTICS=true
```

## Next Steps

1. Expand Bitbucket integration with additional methods and error handling
2. Implement full analytics functionality with data visualization
3. Add comprehensive test suite for Bitbucket and analytics modules
4. Integrate with feature flag system for conditional enabling of features