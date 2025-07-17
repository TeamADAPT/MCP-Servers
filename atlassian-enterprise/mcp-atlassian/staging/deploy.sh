#!/bin/bash
# Deploy the Enhanced Jira Integration for MCP Atlassian

# Set error handling
set -e

# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Default target directory
DEFAULT_TARGET_DIR="/data-nova/ax/DevOps/mcp/mcp-atlassian"

# Parse command line arguments
TARGET_DIR=${1:-$DEFAULT_TARGET_DIR}

echo "=== MCP Atlassian Enhanced Jira Integration Deployment ==="
echo "Source directory: $SCRIPT_DIR"
echo "Target directory: $TARGET_DIR"
echo

# Check if target directory exists
if [ ! -d "$TARGET_DIR" ]; then
    echo "ERROR: Target directory '$TARGET_DIR' does not exist."
    echo "Please provide a valid target directory or create it first."
    exit 1
fi

# Check if target is a valid MCP Atlassian installation
if [ ! -d "$TARGET_DIR/src/mcp_atlassian" ]; then
    echo "ERROR: Target directory does not appear to be a valid MCP Atlassian installation."
    echo "The directory '$TARGET_DIR/src/mcp_atlassian' does not exist."
    exit 1
fi

# Confirm deployment
echo "This will deploy the Enhanced Jira Integration to the target directory."
echo "Any existing files will be backed up with a .bak extension."

# Check if the script is running in non-interactive mode
if [ -t 1 ]; then
    # Terminal is interactive
    read -p "Continue with deployment? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Deployment cancelled."
        exit 1
    fi
else
    # Non-interactive mode (e.g., running from Claude)
    echo "Running in non-interactive mode, continuing with deployment..."
fi

# Create backup of files
echo "Creating backups of existing files..."
if [ -f "$TARGET_DIR/src/mcp_atlassian/config.py" ]; then
    cp "$TARGET_DIR/src/mcp_atlassian/config.py" "$TARGET_DIR/src/mcp_atlassian/config.py.bak"
fi
if [ -f "$TARGET_DIR/src/mcp_atlassian/enhanced_jira.py" ]; then
    cp "$TARGET_DIR/src/mcp_atlassian/enhanced_jira.py" "$TARGET_DIR/src/mcp_atlassian/enhanced_jira.py.bak"
fi
if [ -f "$TARGET_DIR/src/mcp_atlassian/server_enhanced_jira.py" ]; then
    cp "$TARGET_DIR/src/mcp_atlassian/server_enhanced_jira.py" "$TARGET_DIR/src/mcp_atlassian/server_enhanced_jira.py.bak"
fi

# Create directories if needed
mkdir -p "$TARGET_DIR/tests"
mkdir -p "$TARGET_DIR/docs"

# Copy source files
echo "Copying source files..."
cp "$SCRIPT_DIR/src/mcp_atlassian/config.py" "$TARGET_DIR/src/mcp_atlassian/"
cp "$SCRIPT_DIR/src/mcp_atlassian/enhanced_jira.py" "$TARGET_DIR/src/mcp_atlassian/"
cp "$SCRIPT_DIR/src/mcp_atlassian/server_enhanced_jira.py" "$TARGET_DIR/src/mcp_atlassian/"

# Copy test files
echo "Copying test files..."
cp "$SCRIPT_DIR/tests/test_enhanced_jira.py" "$TARGET_DIR/tests/"

# Copy documentation
echo "Copying documentation..."
cp "$SCRIPT_DIR/docs/enhanced_jira_integration.md" "$TARGET_DIR/docs/"

echo "Deployment completed successfully!"
echo
echo "To enable Enhanced Jira features, set the following environment variables:"
echo "export MCP_ATLASSIAN_FEATURE_FLAGS=\"ENHANCED_JIRA\""
echo "# or"
echo "export MCP_ATLASSIAN_ENABLE_ENHANCED_JIRA=\"true\""
echo
echo "Remember to restart the MCP Atlassian service after setting environment variables."
echo
echo "For more information, see the documentation at:"
echo "$TARGET_DIR/docs/enhanced_jira_integration.md"