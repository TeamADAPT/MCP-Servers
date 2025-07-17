# MCP Atlassian Integration

This repository contains the implementation of the MCP Atlassian Integration, providing enhanced functionality for Jira, Confluence, and Bitbucket integration.

## Overview

The MCP Atlassian Integration provides a comprehensive set of tools for interacting with Atlassian products through the MCP framework. It includes enhanced functionality for:

- Jira: Issue management, custom fields, and more
- Confluence: Content management, space management, and more
- Bitbucket: Repository management, integration, and more
- JSM: Service management, queues, and more

## Feature Flags

Features can be enabled through feature flags, allowing for conditional enablement. To enable features, set the following environment variables:

```bash
# Enable specific features
export MCP_ATLASSIAN_ENABLE_ENHANCED_JIRA="true"
export MCP_ATLASSIAN_ENABLE_BITBUCKET_INTEGRATION="true"

# Or enable multiple features at once
export MCP_ATLASSIAN_FEATURE_FLAGS="ENHANCED_JIRA,BITBUCKET_INTEGRATION"
```

## Development Workflow

For information on the development workflow, see [DEVELOPMENT_WORKFLOW.md](./DEVELOPMENT_WORKFLOW.md).

## Deployment

For information on deploying to production, see [PRODUCTION_DEPLOYMENT_PLAN.md](./PRODUCTION_DEPLOYMENT_PLAN.md).

## Documentation

- [Development Workflow](./DEVELOPMENT_WORKFLOW.md): Information on the development workflow
- [Production Deployment Plan](./PRODUCTION_DEPLOYMENT_PLAN.md): Information on deploying to production
- [Deployment Report](./DEPLOYMENT_REPORT.md): Report on the deployment of the Enhanced Jira Integration
- [Final Validation Report](./FINAL_VALIDATION_REPORT.md): Report on the validation of the deployment
- [Fix Implementation Summary](./FIX_IMPLEMENTATION_SUMMARY.md): Summary of the fix implementation

## Scripts

- [production_setup.sh](./production_setup.sh): Initial setup script for restructuring
- [deploy_to_production.sh](./deploy_to_production.sh): Script for deploying changes
- [verify_production.sh](./verify_production.sh): Script for verifying the deployment
- [atlas_diagnostics.py](./atlas_diagnostics.py): Diagnostic tool for the MCP Atlassian Integration
- [test_feature_flags_direct.py](./test_feature_flags_direct.py): Test script for feature flags

## Dependencies

The MCP Atlassian Integration requires the following dependencies:

- idna==3.4
- httpx
- requests
- pydantic
- atlassian-python-api
- jira