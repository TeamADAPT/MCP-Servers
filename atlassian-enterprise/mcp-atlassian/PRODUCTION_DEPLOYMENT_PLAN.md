# Production Deployment Plan

## Overview

This document outlines the plan for deploying the Enhanced Jira Integration from the development environment to the production server. The goal is to establish a consistent workflow for future development and deployment operations.

## Current Environment

- **Development Environment**: `/data-nova/ax/DevOps/mcp/mcp-troubleshoot/Atlassian-connection/atlas-fix`
- **Production Environment**: `/data-nova/ax/DevOps/mcp/mcp-servers/cicd/mcp-atlassian`
- **GitHub Repository**: `https://github.com/TeamADAPT/atlas-fix.git`

## Deployment Strategy

### 1. Repository Setup

The current repository structure needs adjustment to ensure consistent development and deployment workflow:

1. **Archive Current Production**: Rename the current production directory to preserve it
2. **Create New Production Directory**: Using our enhanced implementation
3. **Repository Consistency**: Ensure both development and production point to the correct repositories

### 2. Deployment Procedure

We will use a virtual environment-based deployment approach to ensure all dependencies, especially idna.core, work correctly:

1. **Create Virtual Environment**: Set up a new virtual environment in production
2. **Install Dependencies**: Install all required dependencies, including idna==3.4
3. **Deploy Files**: Copy all necessary files from development to production
4. **Configuration**: Update configuration files for production
5. **Testing**: Run verification tests in production
6. **Documentation**: Update documentation in production

### 3. Automation

To facilitate future deployments, we will create automated scripts:

1. **Deployment Script**: To deploy from development to production
2. **Backup Script**: To create backups before deployment
3. **Verification Script**: To test the deployment

## Implementation Plan

### Phase 1: Repository Restructuring

1. Push all changes in the development environment to the GitHub repository
2. Archive the current production directory
3. Clone the repository to the new production directory
4. Update remote references if needed

### Phase 2: Production Deployment

1. Create a virtual environment in production
2. Install all dependencies
3. Configure the production environment
4. Deploy the Enhanced Jira Integration

### Phase 3: Verification and Documentation

1. Run verification tests in production
2. Update documentation to reflect the new deployment process
3. Create a maintenance guide for future updates

## Deployment Scripts

Three scripts will be created to automate the deployment process:

1. `production_setup.sh`: Initial setup script for restructuring
2. `deploy_to_production.sh`: Script for deploying changes
3. `verify_production.sh`: Script for verifying the deployment

## Maintenance Procedure

For future updates, the procedure will be:

1. Make changes in the development environment
2. Test in the development environment
3. Push changes to the GitHub repository
4. Run the deployment script to update production
5. Verify the deployment

## Rollback Plan

In case of deployment issues:

1. Restore from the automated backup
2. Roll back to the previous version in GitHub
3. Run the verification script to confirm restoration

## Conclusion

This deployment plan ensures a consistent workflow for developing and deploying changes to the MCP Atlassian server. By following this plan, we establish a solid foundation for future development and troubleshooting.