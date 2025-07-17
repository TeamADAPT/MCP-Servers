# Development Workflow

This document outlines the workflow for developing, testing, and deploying changes to the MCP Atlassian server.

## Repository Structure

- **Development Repository**: `/data-nova/ax/DevOps/mcp/mcp-troubleshoot/Atlassian-connection/atlas-fix`
- **Production Repository**: `/data-nova/ax/DevOps/mcp/mcp-servers/cicd/mcp-atlassian`
- **GitHub Repository**: `https://github.com/TeamADAPT/atlas-fix.git`

## Development Workflow

### 1. Initial Setup

If you're starting a new development cycle, follow these steps:

1. Ensure your development repository is up to date:
   ```bash
   cd /data-nova/ax/DevOps/mcp/mcp-troubleshoot/Atlassian-connection/atlas-fix
   git pull origin main
   ```

2. Create or activate a virtual environment:
   ```bash
   # Create if it doesn't exist
   python -m venv venv-fix

   # Activate
   source venv-fix/bin/activate

   # Install dependencies
   pip install --upgrade pip
   pip install idna==3.4 httpx requests pydantic atlassian-python-api jira
   ```

### 2. Development Process

When developing new features or fixing issues, follow these steps:

1. Create a feature/fix branch:
   ```bash
   git checkout -b feature/NAME_OF_FEATURE
   ```

2. Make necessary changes to the codebase

3. Test your changes using the provided test scripts:
   ```bash
   # Run the diagnostic tool
   python atlas_diagnostics.py

   # Test feature flags
   python test_feature_flags_direct.py

   # Run additional tests as needed
   ```

4. Commit your changes:
   ```bash
   git add .
   git commit -m "Descriptive commit message"
   ```

5. Push your changes to the repository:
   ```bash
   git push origin feature/NAME_OF_FEATURE
   ```

6. Create a Pull Request and get it reviewed

7. Once approved, merge into the main branch:
   ```bash
   git checkout main
   git merge feature/NAME_OF_FEATURE
   git push origin main
   ```

### 3. Deployment Process

To deploy changes to production, follow these steps:

1. Ensure all changes are committed and pushed to the repository

2. Run the deployment scripts:
   ```bash
   # If this is the first deployment
   ./production_setup.sh

   # For subsequent deployments
   ./deploy_to_production.sh
   ```

3. Verify the deployment:
   ```bash
   ./verify_production.sh
   ```

## Feature Flags

The MCP Atlassian server uses feature flags to conditionally enable features. To enable features, set the following environment variables:

```bash
# Enable specific features
export MCP_ATLASSIAN_ENABLE_ENHANCED_JIRA="true"
export MCP_ATLASSIAN_ENABLE_BITBUCKET_INTEGRATION="true"

# Or enable multiple features at once
export MCP_ATLASSIAN_FEATURE_FLAGS="ENHANCED_JIRA,BITBUCKET_INTEGRATION"
```

## Directory Structure

The development repository should maintain the following directory structure:

```
atlas-fix/
├── staging/                     # Staged files for deployment
│   ├── src/                     # Source files
│   │   └── mcp_atlassian/       # MCP Atlassian modules
│   ├── docs/                    # Documentation
│   └── tests/                   # Test files
├── backups/                     # Backup files
├── venv-fix/                    # Virtual environment
├── scripts/                     # Utility scripts
├── *.py                         # Diagnostic and test scripts
├── *.sh                         # Deployment scripts
└── *.md                         # Documentation files
```

## Troubleshooting

If you encounter issues during development or deployment, try the following:

1. Check the log files in the `logs/` directory
2. Run the diagnostic tool:
   ```bash
   python atlas_diagnostics.py
   ```
3. Verify idna.core availability:
   ```bash
   python -c "import idna; print(idna.__version__); from idna.core import encode; print('idna.core available')"
   ```
4. Check for error messages in the deployment logs

## Maintenance

Regular maintenance tasks include:

1. Updating dependencies in both development and production environments
2. Cleaning up old backups
3. Running diagnostic tools to ensure the system is functioning correctly
4. Updating documentation as needed

By following this workflow, you'll ensure a consistent and reliable development and deployment process for the MCP Atlassian server.