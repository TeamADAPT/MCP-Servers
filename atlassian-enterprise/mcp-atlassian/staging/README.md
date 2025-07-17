# MCP Atlassian Enhanced Jira Integration

This directory contains the Enhanced Jira Integration deployment files.

## Files

- **src/mcp_atlassian/config.py**: Configuration for Atlassian integration with feature flags support
- **src/mcp_atlassian/enhanced_jira.py**: Enhanced Jira manager implementation
- **src/mcp_atlassian/server_enhanced_jira.py**: Server integration for enhanced Jira tools
- **tests/test_enhanced_jira.py**: Tests for enhanced Jira functionality
- **docs/enhanced_jira_integration.md**: Documentation for enhanced Jira integration

## Deployment

Run the deployment script to deploy these files:

```bash
cd /data-nova/ax/DevOps/mcp/mcp-troubleshoot/Atlassian-connection/atlas-fix
./clean_deployment_venv.sh
```

This will deploy the Enhanced Jira Integration with backups of the original files.

## Feature Flags

The Enhanced Jira Integration uses a feature flags system to enable or disable features. To enable the Enhanced Jira features, set the following environment variable:

```bash
export MCP_ATLASSIAN_FEATURE_FLAGS="ENHANCED_JIRA"
```

Or, for individual feature flags:

```bash
export MCP_ATLASSIAN_ENABLE_ENHANCED_JIRA="true"
```
EOF < /dev/null
