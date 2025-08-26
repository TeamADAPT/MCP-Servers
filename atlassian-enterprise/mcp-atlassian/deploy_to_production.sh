#!/bin/bash
# Deployment script for Enhanced Jira Integration
# This script deploys changes from development to production

set -e

# Define paths
CURRENT_DIR="$(pwd)"
DEV_DIR="/data-nova/ax/DevOps/mcp/mcp-troubleshoot/Atlassian-connection/atlas-fix"
PROD_DIR="/data-nova/ax/DevOps/mcp/mcp-servers/cicd/mcp-atlassian"
BACKUP_DIR="${PROD_DIR}/backups/$(date +%Y%m%d-%H%M%S)"
VENV_DIR="${PROD_DIR}/venv-production"
LOG_FILE="${CURRENT_DIR}/deployment_$(date +%Y%m%d-%H%M%S).log"

# Start logging
echo "===== Deployment Started at $(date) =====" | tee -a "${LOG_FILE}"

# Function to log messages
log() {
    echo "$(date +"%Y-%m-%d %H:%M:%S") - $1" | tee -a "${LOG_FILE}"
}

# Check if we're in the development directory
if [ "${CURRENT_DIR}" != "${DEV_DIR}" ]; then
    log "ERROR: This script must be run from the development directory (${DEV_DIR})"
    exit 1
fi

# Check if production directory exists
if [ ! -d "${PROD_DIR}" ]; then
    log "ERROR: Production directory does not exist. Run production_setup.sh first."
    exit 1
fi

# Create backup
log "Creating backup of production directory..."
mkdir -p "${BACKUP_DIR}"
cp -r "${PROD_DIR}/src" "${BACKUP_DIR}/src" 2>/dev/null || log "No src directory to backup."
cp -r "${PROD_DIR}/docs" "${BACKUP_DIR}/docs" 2>/dev/null || log "No docs directory to backup."
cp "${PROD_DIR}/.env" "${BACKUP_DIR}/.env" 2>/dev/null || log "No .env file to backup."
log "Backup created at ${BACKUP_DIR}"

# Check for uncommitted changes
log "Checking for uncommitted changes in development repository..."
if ! git diff-index --quiet HEAD --; then
    log "WARNING: You have uncommitted changes in your development repository."
    read -p "Would you like to commit these changes before proceeding? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        log "Committing changes..."
        git add .
        git commit -m "Automatic commit before deployment $(date)"
    else
        log "Proceeding without committing changes. This is not recommended."
    fi
fi

# Push changes to repository
log "Pushing changes to repository..."
git push origin main || {
    log "ERROR: Failed to push changes to repository."
    exit 1
}

# Update production repository
log "Updating production repository..."
cd "${PROD_DIR}" || {
    log "ERROR: Failed to change to production directory."
    exit 1
}
git pull || {
    log "ERROR: Failed to pull latest changes."
    exit 1
}

# Set up virtual environment
log "Setting up virtual environment..."
if [ ! -d "${VENV_DIR}" ]; then
    log "Creating new virtual environment..."
    python -m venv "${VENV_DIR}" || {
        log "ERROR: Failed to create virtual environment."
        exit 1
    }
fi

# Install dependencies
log "Installing dependencies..."
source "${VENV_DIR}/bin/activate" || {
    log "ERROR: Failed to activate virtual environment."
    exit 1
}
pip install --upgrade pip || {
    log "ERROR: Failed to upgrade pip."
    exit 1
}
pip install idna==3.4 httpx requests pydantic atlassian-python-api jira || {
    log "ERROR: Failed to install dependencies."
    exit 1
}

# Copy necessary files from staging
log "Copying files from staging directory..."
mkdir -p "${PROD_DIR}/staging/src/mcp_atlassian"
mkdir -p "${PROD_DIR}/staging/docs"
mkdir -p "${PROD_DIR}/staging/tests"

# Copy source files
cp -r "${DEV_DIR}/staging/src/mcp_atlassian/"* "${PROD_DIR}/staging/src/mcp_atlassian/" || {
    log "WARNING: Failed to copy source files from staging."
}

# Copy documentation files
cp -r "${DEV_DIR}/staging/docs/"* "${PROD_DIR}/staging/docs/" 2>/dev/null || log "No documentation files to copy."

# Copy test files
cp -r "${DEV_DIR}/staging/tests/"* "${PROD_DIR}/staging/tests/" 2>/dev/null || log "No test files to copy."

# Copy deployment scripts
cp "${DEV_DIR}/clean_deployment_venv.sh" "${PROD_DIR}/clean_deployment_venv.sh" || {
    log "WARNING: Failed to copy deployment script."
}
chmod +x "${PROD_DIR}/clean_deployment_venv.sh"

# Copy diagnostic tools
cp "${DEV_DIR}/atlas_diagnostics.py" "${PROD_DIR}/atlas_diagnostics.py" || {
    log "WARNING: Failed to copy diagnostic tool."
}
cp "${DEV_DIR}/validate_mcp_atlassian.py" "${PROD_DIR}/validate_mcp_atlassian.py" 2>/dev/null || log "No validation script to copy."
cp "${DEV_DIR}/test_feature_flags_direct.py" "${PROD_DIR}/test_feature_flags_direct.py" || {
    log "WARNING: Failed to copy test script."
}
chmod +x "${PROD_DIR}/"*.py

# Run deployment script in production
log "Running deployment script in production..."
cd "${PROD_DIR}" || {
    log "ERROR: Failed to change to production directory."
    exit 1
}
./clean_deployment_venv.sh || {
    log "ERROR: Failed to run deployment script in production."
    exit 1
}

# Deactivate virtual environment
deactivate

# Complete deployment
log "Deployment complete."
log "Next steps:"
log "1. Run verify_production.sh to verify the deployment"
log "2. Test the Enhanced Jira Integration in production"

echo "===== Deployment Completed at $(date) =====" | tee -a "${LOG_FILE}"

# Return to development directory
cd "${CURRENT_DIR}"