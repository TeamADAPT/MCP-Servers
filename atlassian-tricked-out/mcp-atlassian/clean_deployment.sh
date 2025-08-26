#!/bin/bash
# Clean deployment script for Enhanced Jira Integration

set -e

# Source directory (where the new files are)
SRC_DIR="$(pwd)/staging"

# Target directory (original MCP Atlassian directory)
TARGET_DIR="/data-nova/ax/DevOps/mcp/mcp-troubleshoot/Atlassian-connection/mcp-atlassian"

# Backup directory
BACKUP_DIR="$(pwd)/backups/$(date +%Y%m%d-%H%M%S)"

echo "=== Clean Deployment of Enhanced Jira Integration ==="
echo "Source directory: $SRC_DIR"
echo "Target directory: $TARGET_DIR"
echo "Backup directory: $BACKUP_DIR"
echo

# Check directories
if [ ! -d "$SRC_DIR" ]; then
    echo "ERROR: Source directory not found: $SRC_DIR"
    exit 1
fi

if [ ! -d "$TARGET_DIR" ]; then
    echo "ERROR: Target directory not found: $TARGET_DIR"
    exit 1
fi

# Create backup directory
mkdir -p "$BACKUP_DIR/src/mcp_atlassian"
mkdir -p "$BACKUP_DIR/tests"
mkdir -p "$BACKUP_DIR/docs"

# Function to backup and copy a file
backup_and_copy() {
    local source="$1"
    local target="$2"
    local backup_dir="$3"
    
    # Extract the directory part of the target path
    local target_dir=$(dirname "$target")
    local backup_path="$backup_dir/$(basename "$target")"
    
    # Create target directory if it doesn't exist
    mkdir -p "$target_dir"
    
    # Backup existing file if it exists
    if [ -f "$target" ]; then
        echo "Backing up $target to $backup_path"
        cp "$target" "$backup_path"
    fi
    
    # Copy new file
    echo "Copying $source to $target"
    cp "$source" "$target"
}

# Backup and copy files
echo "Backing up and deploying files..."

# Config
if [ -f "$SRC_DIR/src/mcp_atlassian/config.py" ]; then
    backup_and_copy "$TARGET_DIR/src/mcp_atlassian/config.py" "$BACKUP_DIR/src/mcp_atlassian/config.py" "$BACKUP_DIR/src/mcp_atlassian"
    cp "$SRC_DIR/src/mcp_atlassian/config.py" "$TARGET_DIR/src/mcp_atlassian/config.py"
fi

# Feature flags adapter
echo "Creating feature_flags.py adapter..."
cat > "$TARGET_DIR/src/mcp_atlassian/feature_flags.py" << 'EOF'
"""
Feature flags adapter for MCP Atlassian integration.

This module provides compatibility with existing code that imports
feature flags functions directly.
"""

import logging
from typing import Dict, List, Set, Optional

from .config import get_config

logger = logging.getLogger("mcp-atlassian-feature-flags")

def is_enabled(flag_name: str) -> bool:
    """
    Check if a feature flag is enabled.
    
    Args:
        flag_name: The name of the feature flag
        
    Returns:
        bool: True if the flag is enabled, False otherwise
    """
    try:
        return get_config().feature_flags.is_enabled(flag_name)
    except Exception as e:
        logger.error(f"Error checking if feature flag '{flag_name}' is enabled: {e}")
        return False


def enable_feature(flag_name: str) -> bool:
    """
    Enable a feature flag at runtime.
    
    Args:
        flag_name: The name of the feature flag
        
    Returns:
        bool: True if the flag was enabled, False otherwise
    """
    try:
        return get_config().feature_flags.enable(flag_name)
    except Exception as e:
        logger.error(f"Error enabling feature flag '{flag_name}': {e}")
        return False


def disable_feature(flag_name: str) -> bool:
    """
    Disable a feature flag at runtime.
    
    Args:
        flag_name: The name of the feature flag
        
    Returns:
        bool: True if the flag was disabled, False otherwise
    """
    try:
        return get_config().feature_flags.disable(flag_name)
    except Exception as e:
        logger.error(f"Error disabling feature flag '{flag_name}': {e}")
        return False


def get_all_flags() -> Dict[str, bool]:
    """
    Get all feature flags and their status.
    
    Returns:
        Dict[str, bool]: Dictionary of feature flags and their status
    """
    try:
        config = get_config()
        result = {}
        
        for flag in config.feature_flags.ALL_FLAGS:
            result[flag] = config.feature_flags.is_enabled(flag)
            
        return result
    except Exception as e:
        logger.error(f"Error getting all feature flags: {e}")
        return {}


def reset_runtime_overrides():
    """Reset any runtime feature flag overrides."""
    try:
        config = get_config()
        # Recreate feature flags from environment
        config.feature_flags = config.feature_flags.__class__()
    except Exception as e:
        logger.error(f"Error resetting feature flag overrides: {e}")


def get_feature_groups() -> Dict[str, List[str]]:
    """
    Get feature groups.
    
    Returns:
        Dict[str, List[str]]: Dictionary of feature groups and their flags
    """
    return {
        "Jira": [
            "ENHANCED_JIRA",
        ],
        "Confluence": [
            "ENHANCED_CONFLUENCE",
        ],
        "Bitbucket": [
            "BITBUCKET_INTEGRATION",
        ],
        "JSM": [
            "JSM_INTEGRATION",
        ],
        "Analytics": [
            "ADVANCED_ANALYTICS",
        ],
    }
EOF

# Enhanced Jira files
if [ -f "$SRC_DIR/src/mcp_atlassian/enhanced_jira.py" ]; then
    backup_and_copy "$TARGET_DIR/src/mcp_atlassian/enhanced_jira.py" "$BACKUP_DIR/src/mcp_atlassian/enhanced_jira.py" "$BACKUP_DIR/src/mcp_atlassian"
    cp "$SRC_DIR/src/mcp_atlassian/enhanced_jira.py" "$TARGET_DIR/src/mcp_atlassian/enhanced_jira.py"
fi

if [ -f "$SRC_DIR/src/mcp_atlassian/server_enhanced_jira.py" ]; then
    backup_and_copy "$TARGET_DIR/src/mcp_atlassian/server_enhanced_jira.py" "$BACKUP_DIR/src/mcp_atlassian/server_enhanced_jira.py" "$BACKUP_DIR/src/mcp_atlassian"
    cp "$SRC_DIR/src/mcp_atlassian/server_enhanced_jira.py" "$TARGET_DIR/src/mcp_atlassian/server_enhanced_jira.py"
fi

# Tests
if [ -f "$SRC_DIR/tests/test_enhanced_jira.py" ]; then
    backup_and_copy "$TARGET_DIR/tests/test_enhanced_jira.py" "$BACKUP_DIR/tests/test_enhanced_jira.py" "$BACKUP_DIR/tests"
    cp "$SRC_DIR/tests/test_enhanced_jira.py" "$TARGET_DIR/tests/test_enhanced_jira.py"
fi

# Documentation
if [ -f "$SRC_DIR/docs/enhanced_jira_integration.md" ]; then
    backup_and_copy "$TARGET_DIR/docs/enhanced_jira_integration.md" "$BACKUP_DIR/docs/enhanced_jira_integration.md" "$BACKUP_DIR/docs"
    cp "$SRC_DIR/docs/enhanced_jira_integration.md" "$TARGET_DIR/docs/enhanced_jira_integration.md"
fi

# Update the changelog
if [ -f "$TARGET_DIR/CHANGELOG.md" ]; then
    cp "$TARGET_DIR/CHANGELOG.md" "$BACKUP_DIR/CHANGELOG.md"
    
    # Add new version entry to the beginning of the file
    cat > "$TARGET_DIR/CHANGELOG.md.new" << 'EOF'
# Changelog

## [0.3.0] - 2025-05-18

### Added
- Implemented Enhanced Jira Integration (Phase 3, Group 1):
  - Added comprehensive feature flags system for conditional enablement
  - Enhanced Jira functionality with custom field management
  - Added caching system for performance improvements
  - Implemented bulk operations for issues and links
  - Added project health analysis and reporting
  - Added improved error handling with retry logic
  - Created tests for enhanced Jira functionality
  - Added documentation in docs/enhanced_jira_integration.md

EOF
    
    # Append the original changelog
    cat "$TARGET_DIR/CHANGELOG.md" >> "$TARGET_DIR/CHANGELOG.md.new"
    mv "$TARGET_DIR/CHANGELOG.md.new" "$TARGET_DIR/CHANGELOG.md"
fi

echo "Deployment completed successfully!"
echo "All original files have been backed up to: $BACKUP_DIR"
echo
echo "To enable Enhanced Jira features, set the following environment variables:"
echo "export MCP_ATLASSIAN_FEATURE_FLAGS=\"ENHANCED_JIRA\""
echo "# or"
echo "export MCP_ATLASSIAN_ENABLE_ENHANCED_JIRA=\"true\""
echo
echo "For more information, see the documentation at:"
echo "$TARGET_DIR/docs/enhanced_jira_integration.md"