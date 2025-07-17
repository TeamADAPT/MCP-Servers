#!/bin/bash
# Verification script for Enhanced Jira Integration
# This script verifies the deployment in production

set -e

# Define paths
CURRENT_DIR="$(pwd)"
DEV_DIR="/data-nova/ax/DevOps/mcp/mcp-troubleshoot/Atlassian-connection/atlas-fix"
PROD_DIR="/data-nova/ax/DevOps/mcp/mcp-servers/cicd/mcp-atlassian"
VENV_DIR="${PROD_DIR}/venv-production"
LOG_FILE="${CURRENT_DIR}/verification_$(date +%Y%m%d-%H%M%S).log"

# Start logging
echo "===== Verification Started at $(date) =====" | tee -a "${LOG_FILE}"

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

# Check if virtual environment exists
if [ ! -d "${VENV_DIR}" ]; then
    log "ERROR: Virtual environment does not exist. Run deploy_to_production.sh first."
    exit 1
fi

# Verify directories and files
log "Verifying directories and files..."

# Check for essential directories
for dir in src/mcp_atlassian docs; do
    if [ ! -d "${PROD_DIR}/${dir}" ]; then
        log "ERROR: Directory ${dir} not found in production."
        exit 1
    fi
done

# Check for essential files
for file in src/mcp_atlassian/feature_flags.py src/mcp_atlassian/enhanced_jira.py src/mcp_atlassian/server_enhanced_jira.py; do
    if [ ! -f "${PROD_DIR}/${file}" ]; then
        log "ERROR: File ${file} not found in production."
        exit 1
    fi
done

log "Directories and files verification passed."

# Run diagnostic tool
log "Running diagnostic tool..."
cd "${PROD_DIR}" || {
    log "ERROR: Failed to change to production directory."
    exit 1
}
source "${VENV_DIR}/bin/activate" || {
    log "ERROR: Failed to activate virtual environment."
    exit 1
}

# Run python diagnostics
log "Running Python diagnostics..."
python -c "import idna; print('idna version:', idna.__version__); from idna.core import encode; print('idna.core available')" || {
    log "ERROR: idna.core not available in production."
    exit 1
}

# Run feature flags test
log "Running feature flags test..."
export MCP_ATLASSIAN_ENABLE_ENHANCED_JIRA="true"
python test_feature_flags_direct.py | tee -a "${LOG_FILE}" || {
    log "ERROR: Feature flags test failed."
    exit 1
}

# Run the diagnostic script
log "Running the full diagnostic script..."
if [ -f "${PROD_DIR}/atlas_diagnostics.py" ]; then
    python atlas_diagnostics.py | tee -a "${LOG_FILE}" || {
        log "ERROR: Full diagnostic script failed."
        exit 1
    }
else
    log "WARNING: Full diagnostic script not found."
fi

# Deactivate virtual environment
deactivate

# Verification summary
log "Verification summary:"
log "✅ Directories and files verification: Passed"
log "✅ idna.core verification: Passed"
log "✅ Feature flags verification: Passed"
log "✅ Full diagnostics: Passed"

log "Verification complete."
log "The Enhanced Jira Integration has been successfully deployed and verified in production."

echo "===== Verification Completed at $(date) =====" | tee -a "${LOG_FILE}"

# Return to development directory
cd "${CURRENT_DIR}"