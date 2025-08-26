# Production Deployment Instructions

This document provides step-by-step instructions for deploying the Enhanced Jira Integration to the production server.

## Prerequisites

- Access to the development directory: `/data-nova/ax/DevOps/mcp/mcp-troubleshoot/Atlassian-connection/atlas-fix`
- Access to the production directory: `/data-nova/ax/DevOps/mcp/mcp-servers/cicd/mcp-atlassian`
- Sudo or appropriate permissions to modify the production directory

## Step 1: Preparing the Repository

1. Push all changes to the GitHub repository:
   ```bash
   cd /data-nova/ax/DevOps/mcp/mcp-troubleshoot/Atlassian-connection/atlas-fix
   git add .
   git commit -m "Prepare for production deployment"
   git push origin main
   ```

## Step 2: Archiving the Current Production Directory

1. Create an archive directory:
   ```bash
   ARCHIVE_DIR="/data-nova/ax/DevOps/mcp/mcp-servers/cicd/mcp-atlassian-archive-$(date +%Y%m%d)"
   sudo mv /data-nova/ax/DevOps/mcp/mcp-servers/cicd/mcp-atlassian ${ARCHIVE_DIR}
   ```

## Step 3: Setting Up the New Production Directory

1. Clone the repository to the new production directory:
   ```bash
   sudo mkdir -p /data-nova/ax/DevOps/mcp/mcp-servers/cicd/mcp-atlassian
   sudo chown $(whoami):$(whoami) /data-nova/ax/DevOps/mcp/mcp-servers/cicd/mcp-atlassian
   cd /data-nova/ax/DevOps/mcp/mcp-servers/cicd/mcp-atlassian
   git clone https://github.com/TeamADAPT/atlas-fix.git .
   ```

2. Create the necessary directories:
   ```bash
   mkdir -p logs backups
   ```

3. Copy the .env file from the archive:
   ```bash
   cp ${ARCHIVE_DIR}/.env .
   ```

## Step 4: Setting Up the Virtual Environment

1. Create a virtual environment:
   ```bash
   python -m venv venv-production
   source venv-production/bin/activate
   pip install --upgrade pip
   pip install idna==3.4 httpx requests pydantic atlassian-python-api jira
   ```

## Step 5: Deploying the Enhanced Jira Integration

1. Run the clean deployment script:
   ```bash
   cd /data-nova/ax/DevOps/mcp/mcp-servers/cicd/mcp-atlassian
   source venv-production/bin/activate
   chmod +x clean_deployment_venv.sh
   ./clean_deployment_venv.sh
   ```

## Step 6: Verification

1. Run the verification scripts:
   ```bash
   cd /data-nova/ax/DevOps/mcp/mcp-servers/cicd/mcp-atlassian
   source venv-production/bin/activate
   
   # Test idna.core
   python -c "import idna; print('idna version:', idna.__version__); from idna.core import encode; print('idna.core available')"
   
   # Test feature flags
   export MCP_ATLASSIAN_ENABLE_ENHANCED_JIRA="true"
   python test_feature_flags_direct.py
   
   # Run full diagnostics
   python atlas_diagnostics.py
   ```

## Step 7: Final Verification

1. Test accessing the Enhanced Jira Integration through the MCP:
   ```bash
   # Example command to test the MCP integration
   # This will depend on your specific MCP setup
   python -c "from mcp_atlassian.feature_flags import is_enabled, get_enabled_flags; print('Enhanced Jira enabled:', is_enabled('ENHANCED_JIRA')); print('Enabled flags:', get_enabled_flags())"
   ```

## Troubleshooting

If you encounter issues during deployment, try the following:

1. Check the logs in the `logs/` directory
2. Run the diagnostic tool:
   ```bash
   python atlas_diagnostics.py
   ```
3. Verify idna.core availability:
   ```bash
   python -c "import idna; print('idna version:', idna.__version__); from idna.core import encode; print('idna.core available')"
   ```
4. Check for error messages in the deployment logs
5. Restore from the archive if necessary:
   ```bash
   sudo rm -rf /data-nova/ax/DevOps/mcp/mcp-servers/cicd/mcp-atlassian
   sudo mv ${ARCHIVE_DIR} /data-nova/ax/DevOps/mcp/mcp-servers/cicd/mcp-atlassian
   ```

## Next Steps

After successful deployment:

1. Update the documentation
2. Communicate the deployment to the team
3. Monitor the system for any issues
4. Plan the next phase of development

By following these instructions, you'll have successfully deployed the Enhanced Jira Integration to the production server.