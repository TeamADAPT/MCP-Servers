# MCP Atlassian Integration Fix Instructions

## Issue

The MCP Atlassian integration is encountering an issue with the `idna` package, which is preventing proper functionality. The specific error is:

```
ModuleNotFoundError: No module named 'idna.core'
```

## Solution

This issue can be resolved by reinstalling the `idna` package with a compatible version. Follow these steps:

1. Reinstall the `idna` package:
   ```bash
   pip uninstall -y idna
   pip install idna==3.4
   ```

2. If that doesn't resolve the issue, create a new virtual environment:
   ```bash
   python -m venv /data-nova/ax/DevOps/mcp/mcp-troubleshoot/Atlassian-connection/atlas-fix/venv
   source /data-nova/ax/DevOps/mcp/mcp-troubleshoot/Atlassian-connection/atlas-fix/venv/bin/activate
   pip install httpx requests idna==3.4 pydantic atlassian-python-api jira
   ```

3. Run the validation script to check if the issue is resolved:
   ```bash
   python /data-nova/ax/DevOps/mcp/mcp-troubleshoot/Atlassian-connection/atlas-fix/validate_mcp_atlassian.py
   ```

## Enhanced Jira Integration

The Enhanced Jira Integration has been successfully deployed to:
```
/data-nova/ax/DevOps/mcp/mcp-troubleshoot/Atlassian-connection/mcp-atlassian
```

To enable the Enhanced Jira features, set the following environment variable:
```bash
export MCP_ATLASSIAN_FEATURE_FLAGS="ENHANCED_JIRA"
```

Or:
```bash
export MCP_ATLASSIAN_ENABLE_ENHANCED_JIRA="true"
```

## Backups

Backups of the original files are stored in:
```
/data-nova/ax/DevOps/mcp/mcp-troubleshoot/Atlassian-connection/atlas-fix/backups
```

If you encounter any issues, you can restore from these backups.

## Testing

You can test the feature flags functionality with:
```bash
python /data-nova/ax/DevOps/mcp/mcp-troubleshoot/Atlassian-connection/atlas-fix/feature_flags_test.py
```

## Documentation

For more information about the Enhanced Jira Integration, see:
```
/data-nova/ax/DevOps/mcp/mcp-troubleshoot/Atlassian-connection/mcp-atlassian/docs/enhanced_jira_integration.md
```

## Fix Script

A comprehensive fix script is available at:
```bash
python /data-nova/ax/DevOps/mcp/mcp-troubleshoot/Atlassian-connection/atlas-fix/fix_atlassian_connection.py
```

Run with:
```bash
python /data-nova/ax/DevOps/mcp/mcp-troubleshoot/Atlassian-connection/atlas-fix/fix_atlassian_connection.py --help
```
