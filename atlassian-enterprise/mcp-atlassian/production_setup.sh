#!/bin/bash
# Initial setup script for restructuring repositories and directories
# This script handles the repository restructuring for consistent workflow

set -e

# Define paths
CURRENT_DIR="$(pwd)"
DEV_DIR="/data-nova/ax/DevOps/mcp/mcp-troubleshoot/Atlassian-connection/atlas-fix"
PROD_DIR="/data-nova/ax/DevOps/mcp/mcp-servers/cicd/mcp-atlassian"
ARCHIVE_DIR="/data-nova/ax/DevOps/mcp/mcp-servers/cicd/mcp-atlassian-archive-$(date +%Y%m%d)"
REPO_URL="https://github.com/TeamADAPT/atlas-fix.git"
LOG_FILE="${CURRENT_DIR}/production_setup.log"

# Start logging
echo "===== Production Setup Started at $(date) =====" | tee -a "${LOG_FILE}"

# Function to log messages
log() {
    echo "$(date +"%Y-%m-%d %H:%M:%S") - $1" | tee -a "${LOG_FILE}"
}

# Verify that we're in the development directory
if [ "${CURRENT_DIR}" != "${DEV_DIR}" ]; then
    log "ERROR: This script must be run from the development directory (${DEV_DIR})"
    exit 1
fi

# Check for uncommitted changes
log "Checking for uncommitted changes in development repository..."
if ! git diff-index --quiet HEAD --; then
    log "WARNING: You have uncommitted changes in your development repository."
    read -p "Would you like to commit these changes before proceeding? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        log "Committing changes..."
        git add .
        git commit -m "Automatic commit before production setup $(date)"
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

# Archive current production directory
log "Archiving current production directory to ${ARCHIVE_DIR}..."
if [ -d "${PROD_DIR}" ]; then
    sudo mv "${PROD_DIR}" "${ARCHIVE_DIR}" || {
        log "ERROR: Failed to archive current production directory."
        exit 1
    }
    log "Current production directory archived successfully."
else
    log "Production directory does not exist, skipping archiving."
fi

# Create new production directory and clone repository
log "Creating new production directory and cloning repository..."
sudo mkdir -p "${PROD_DIR}" || {
    log "ERROR: Failed to create new production directory."
    exit 1
}
sudo chown $(whoami):$(whoami) "${PROD_DIR}" || {
    log "ERROR: Failed to change ownership of production directory."
    exit 1
}
cd "${PROD_DIR}" || {
    log "ERROR: Failed to change to production directory."
    exit 1
}
git clone "${REPO_URL}" . || {
    log "ERROR: Failed to clone repository."
    exit 1
}

# Copy necessary files from archive if needed
if [ -d "${ARCHIVE_DIR}" ]; then
    log "Copying necessary files from archive..."
    
    # Copy .env file
    if [ -f "${ARCHIVE_DIR}/.env" ]; then
        cp "${ARCHIVE_DIR}/.env" "${PROD_DIR}/.env" || {
            log "WARNING: Failed to copy .env file."
        }
    fi
    
    # Copy any other necessary files
    # cp "${ARCHIVE_DIR}/other_file" "${PROD_DIR}/other_file"
    
    log "Necessary files copied from archive."
fi

# Set up proper permissions
log "Setting up proper permissions..."
chmod +x "${PROD_DIR}/*.sh" 2>/dev/null || log "No shell scripts to make executable."

# Create directories if needed
log "Creating necessary directories..."
mkdir -p "${PROD_DIR}/logs"
mkdir -p "${PROD_DIR}/backups"

# Complete setup
log "Production directory setup complete."
log "Next steps:"
log "1. Run deploy_to_production.sh to deploy the Enhanced Jira Integration"
log "2. Run verify_production.sh to verify the deployment"

echo "===== Production Setup Completed at $(date) =====" | tee -a "${LOG_FILE}"

# Return to development directory
cd "${CURRENT_DIR}"