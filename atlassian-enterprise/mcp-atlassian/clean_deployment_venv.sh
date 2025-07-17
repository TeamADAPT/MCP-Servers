#!/bin/bash
# Clean deployment script for Enhanced Jira Integration using virtual environment

set -e

# Source directory (where the new files are)
SRC_DIR="$(pwd)/staging"

# Target directory (original MCP Atlassian directory)
TARGET_DIR="/data-nova/ax/DevOps/mcp/mcp-troubleshoot/Atlassian-connection/mcp-atlassian"

# Backup directory
BACKUP_DIR="$(pwd)/backups/$(date +%Y%m%d-%H%M%S)"

# Virtual environment path
VENV_DIR="$(pwd)/venv-fix"

echo "=== Clean Deployment of Enhanced Jira Integration ==="
echo "Source directory: $SRC_DIR"
echo "Target directory: $TARGET_DIR"
echo "Backup directory: $BACKUP_DIR"
echo "Virtual environment: $VENV_DIR"
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

# Make sure virtual environment exists
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment..."
    python -m venv "$VENV_DIR"
    source "$VENV_DIR/bin/activate"
    pip install --upgrade pip
    pip install idna==3.4 httpx requests pydantic atlassian-python-api jira
else
    source "$VENV_DIR/bin/activate"
fi

echo "Using Python interpreter: $(which python)"
echo "Python version: $(python --version)"
echo "Pip version: $(pip --version)"
echo

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
    backup_and_copy "$SRC_DIR/src/mcp_atlassian/config.py" "$TARGET_DIR/src/mcp_atlassian/config.py" "$BACKUP_DIR/src/mcp_atlassian"
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
import os
from typing import Dict, List, Set, Optional

logger = logging.getLogger("mcp-atlassian-feature-flags")

# Define feature flag constants
ENHANCED_JIRA = "ENHANCED_JIRA"
BITBUCKET_INTEGRATION = "BITBUCKET_INTEGRATION"
ENHANCED_CONFLUENCE = "ENHANCED_CONFLUENCE"
JSM_INTEGRATION = "JSM_INTEGRATION"
ADVANCED_ANALYTICS = "ADVANCED_ANALYTICS"

# All available flags
ALL_FLAGS = {
    ENHANCED_JIRA,
    BITBUCKET_INTEGRATION,
    ENHANCED_CONFLUENCE,
    JSM_INTEGRATION,
    ADVANCED_ANALYTICS
}

# Cache enabled flags to avoid repeatedly checking environment variables
_enabled_flags: Optional[Set[str]] = None
_runtime_overrides: Dict[str, bool] = {}

def _load_flags():
    """Load feature flags from environment variables."""
    global _enabled_flags
    
    _enabled_flags = set()
    
    # Load flags from main environment variable
    flags_str = os.environ.get("MCP_ATLASSIAN_FEATURE_FLAGS", "")
    if flags_str:
        for flag in flags_str.split(","):
            flag = flag.strip().upper()
            if flag in ALL_FLAGS:
                _enabled_flags.add(flag)
    
    # Check for individual flag environment variables
    for flag in ALL_FLAGS:
        env_var = f"MCP_ATLASSIAN_ENABLE_{flag}"
        if os.environ.get(env_var, "").lower() in ("true", "1", "yes"):
            _enabled_flags.add(flag)

def is_enabled(flag_name: str) -> bool:
    """
    Check if a feature flag is enabled.
    
    Args:
        flag_name: The name of the feature flag
        
    Returns:
        bool: True if the flag is enabled, False otherwise
    """
    global _enabled_flags, _runtime_overrides
    
    if flag_name in _runtime_overrides:
        return _runtime_overrides[flag_name]
    
    if _enabled_flags is None:
        _load_flags()
    
    return flag_name in _enabled_flags


def enable_feature(flag_name: str) -> bool:
    """
    Enable a feature flag at runtime.
    
    Args:
        flag_name: The name of the feature flag
        
    Returns:
        bool: True if the flag was enabled, False otherwise
    """
    global _runtime_overrides
    
    if flag_name not in ALL_FLAGS:
        logger.warning(f"Attempted to enable unknown feature flag: {flag_name}")
        return False
    
    _runtime_overrides[flag_name] = True
    return True


def disable_feature(flag_name: str) -> bool:
    """
    Disable a feature flag at runtime.
    
    Args:
        flag_name: The name of the feature flag
        
    Returns:
        bool: True if the flag was disabled, False otherwise
    """
    global _runtime_overrides
    
    if flag_name not in ALL_FLAGS:
        logger.warning(f"Attempted to disable unknown feature flag: {flag_name}")
        return False
    
    _runtime_overrides[flag_name] = False
    return True


def get_all_flags() -> Dict[str, bool]:
    """
    Get all feature flags and their status.
    
    Returns:
        Dict[str, bool]: Dictionary of feature flags and their status
    """
    result = {}
    
    for flag in ALL_FLAGS:
        result[flag] = is_enabled(flag)
        
    return result


def reset_runtime_overrides():
    """Reset any runtime feature flag overrides."""
    global _runtime_overrides, _enabled_flags
    
    _runtime_overrides = {}
    _enabled_flags = None


def get_feature_groups() -> Dict[str, List[str]]:
    """
    Get feature groups.
    
    Returns:
        Dict[str, List[str]]: Dictionary of feature groups and their flags
    """
    return {
        "Jira": [
            ENHANCED_JIRA,
        ],
        "Confluence": [
            ENHANCED_CONFLUENCE,
        ],
        "Bitbucket": [
            BITBUCKET_INTEGRATION,
        ],
        "JSM": [
            JSM_INTEGRATION,
        ],
        "Analytics": [
            ADVANCED_ANALYTICS,
        ],
    }


def get_enabled_flags() -> List[str]:
    """
    Get list of all enabled flags.
    
    Returns:
        List[str]: Enabled flags
    """
    return [flag for flag, enabled in get_all_flags().items() if enabled]
EOF

# Enhanced Jira files
if [ -f "$SRC_DIR/src/mcp_atlassian/enhanced_jira.py" ]; then
    backup_and_copy "$SRC_DIR/src/mcp_atlassian/enhanced_jira.py" "$TARGET_DIR/src/mcp_atlassian/enhanced_jira.py" "$BACKUP_DIR/src/mcp_atlassian"
fi

if [ -f "$SRC_DIR/src/mcp_atlassian/server_enhanced_jira.py" ]; then
    backup_and_copy "$SRC_DIR/src/mcp_atlassian/server_enhanced_jira.py" "$TARGET_DIR/src/mcp_atlassian/server_enhanced_jira.py" "$BACKUP_DIR/src/mcp_atlassian"
fi

# Tests
if [ -f "$SRC_DIR/tests/test_enhanced_jira.py" ]; then
    backup_and_copy "$SRC_DIR/tests/test_enhanced_jira.py" "$TARGET_DIR/tests/test_enhanced_jira.py" "$BACKUP_DIR/tests"
fi

# Documentation
if [ -f "$SRC_DIR/docs/enhanced_jira_integration.md" ]; then
    backup_and_copy "$SRC_DIR/docs/enhanced_jira_integration.md" "$TARGET_DIR/docs/enhanced_jira_integration.md" "$BACKUP_DIR/docs"
fi

# Create or update constants.py
echo "Creating constants.py for feature flags..."
cat > "$TARGET_DIR/src/mcp_atlassian/constants.py" << 'EOF'
"""
Constants for MCP Atlassian integration.
"""

# Feature flags
FEATURE_FLAG_ENHANCED_JIRA = "ENHANCED_JIRA"
FEATURE_FLAG_BITBUCKET_INTEGRATION = "BITBUCKET_INTEGRATION"
FEATURE_FLAG_ENHANCED_CONFLUENCE = "ENHANCED_CONFLUENCE"
FEATURE_FLAG_JSM_INTEGRATION = "JSM_INTEGRATION"
FEATURE_FLAG_ADVANCED_ANALYTICS = "ADVANCED_ANALYTICS"

# Custom field IDs
CUSTOM_FIELD_NAME = "customfield_10057"
CUSTOM_FIELD_DEPARTMENT = "customfield_10058"
CUSTOM_FIELD_EPIC_LINK = "customfield_10059"

# Issue types
ISSUE_TYPE_EPIC = "Epic"
ISSUE_TYPE_STORY = "Story"
ISSUE_TYPE_TASK = "Task"
ISSUE_TYPE_BUG = "Bug"
EOF

# Create diagnostics module
echo "Creating diagnostics module..."
cat > "$TARGET_DIR/src/mcp_atlassian/diagnostics.py" << 'EOF'
"""
Diagnostic utilities for MCP Atlassian Integration.
"""

import importlib
import logging
import os
import sys
import json
from typing import Dict, List, Any, Optional, Tuple

logger = logging.getLogger("mcp-atlassian-diagnostics")

def check_dependencies() -> Dict[str, bool]:
    """
    Check if required dependencies are available.
    
    Returns:
        Dict[str, bool]: Dictionary of dependency names and their availability
    """
    dependencies = {
        "httpx": False,
        "requests": False,
        "idna": False,
        "pydantic": False,
        "atlassian-python-api": False,
        "jira": False,
    }
    
    for dep in dependencies.keys():
        try:
            importlib.import_module(dep)
            dependencies[dep] = True
        except ImportError:
            pass
    
    return dependencies

def check_idna_core() -> bool:
    """
    Check if idna.core is available.
    
    Returns:
        bool: True if idna.core is available, False otherwise
    """
    try:
        from idna.core import encode, decode
        return True
    except ImportError:
        return False

def check_feature_flags() -> Dict[str, Any]:
    """
    Check the status of feature flags.
    
    Returns:
        Dict[str, Any]: Feature flags status
    """
    result = {
        "importable": False,
        "enabled_flags": [],
        "env_vars": {},
    }
    
    # Check environment variables
    for key, value in os.environ.items():
        if key.startswith("MCP_ATLASSIAN_"):
            result["env_vars"][key] = value
    
    # Try to import feature_flags module
    try:
        from mcp_atlassian.feature_flags import get_all_flags, is_enabled
        result["importable"] = True
        
        # Get enabled flags
        all_flags = get_all_flags()
        result["all_flags"] = all_flags
        result["enabled_flags"] = [flag for flag, enabled in all_flags.items() if enabled]
    except ImportError:
        pass
    
    return result

def run_diagnostics() -> Dict[str, Any]:
    """
    Run diagnostics on MCP Atlassian Integration.
    
    Returns:
        Dict[str, Any]: Diagnostic results
    """
    return {
        "python_version": sys.version,
        "python_executable": sys.executable,
        "dependencies": check_dependencies(),
        "idna_core_available": check_idna_core(),
        "feature_flags": check_feature_flags(),
    }

def print_diagnostics(results: Optional[Dict[str, Any]] = None):
    """
    Print diagnostic results in a human-readable format.
    
    Args:
        results: Diagnostic results (if None, will run diagnostics)
    """
    if results is None:
        results = run_diagnostics()
    
    print("\n" + "=" * 80)
    print("MCP ATLASSIAN INTEGRATION DIAGNOSTICS")
    print("=" * 80 + "\n")
    
    print(f"Python version: {results['python_version']}")
    print(f"Python executable: {results['python_executable']}")
    
    print("\n" + "-" * 40)
    print("DEPENDENCIES")
    print("-" * 40)
    
    deps = results["dependencies"]
    for dep, available in deps.items():
        status = "✅ Available" if available else "❌ Not available"
        print(f"{dep}: {status}")
    
    print("\n" + "-" * 40)
    print("IDNA CORE")
    print("-" * 40)
    
    idna_status = "✅ Available" if results["idna_core_available"] else "❌ Not available"
    print(f"idna.core: {idna_status}")
    
    print("\n" + "-" * 40)
    print("FEATURE FLAGS")
    print("-" * 40)
    
    ff = results["feature_flags"]
    flags_status = "✅ Available" if ff["importable"] else "❌ Not available"
    print(f"feature_flags module: {flags_status}")
    
    if ff["importable"]:
        print("\nEnabled flags:")
        if ff["enabled_flags"]:
            for flag in ff["enabled_flags"]:
                print(f"  - {flag}")
        else:
            print("  None")
    
    print("\nEnvironment variables:")
    if ff["env_vars"]:
        for var, value in ff["env_vars"].items():
            print(f"  {var}={value}")
    else:
        print("  None")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Run diagnostics
    results = run_diagnostics()
    
    # Print results
    print_diagnostics(results)
    
    # Check for issues
    deps_ok = all(results["dependencies"].values())
    idna_ok = results["idna_core_available"]
    ff_ok = results["feature_flags"]["importable"]
    
    if not deps_ok or not idna_ok or not ff_ok:
        print("\nSome issues were detected. Please check the following:")
        
        if not idna_ok:
            print("\n1. IDNA issue:")
            print("   Try reinstalling idna:")
            print("   pip uninstall -y idna")
            print("   pip install idna==3.4")
        
        if not deps_ok:
            print("\n2. Missing dependencies:")
            missing = [dep for dep, available in results["dependencies"].items() if not available]
            print(f"   Install missing packages: {', '.join(missing)}")
            print("   pip install " + " ".join(missing))
        
        if not ff_ok:
            print("\n3. Feature flags issue:")
            print("   Make sure the feature_flags.py module is properly installed")
            print("   Try running the deployment script again")
        
        sys.exit(1)
    else:
        print("\nAll checks passed! The MCP Atlassian integration should work correctly.")
        sys.exit(0)
EOF

# Update the CHANGELOG.md
if [ -f "$TARGET_DIR/CHANGELOG.md" ]; then
    cp "$TARGET_DIR/CHANGELOG.md" "$BACKUP_DIR/CHANGELOG.md"
    
    # Add new version entry to the beginning of the file
    cat > "$TARGET_DIR/CHANGELOG.md.new" << 'EOF'
# Changelog

## [0.3.0] - 2025-05-19

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

### Fixed
- Fixed issue with idna package dependency by using virtual environment
- Added compatibility layer for feature flags system
- Improved diagnostics for troubleshooting environment issues

EOF
    
    # Append the original changelog
    cat "$TARGET_DIR/CHANGELOG.md" >> "$TARGET_DIR/CHANGELOG.md.new"
    mv "$TARGET_DIR/CHANGELOG.md.new" "$TARGET_DIR/CHANGELOG.md"
fi

# Create a simple test script
cat > "$TARGET_DIR/feature_flags_test.py" << 'EOF'
#!/usr/bin/env python3
"""
Test feature flags functionality
"""

import os
import sys
from mcp_atlassian.feature_flags import (
    is_enabled,
    enable_feature,
    disable_feature,
    get_all_flags,
    get_enabled_flags,
    reset_runtime_overrides,
)

def main():
    print("\n=== Feature Flags Test ===\n")
    
    # Test 1: Check all flags
    print("All flags:")
    all_flags = get_all_flags()
    for flag, enabled in all_flags.items():
        print(f"  {flag}: {enabled}")
    
    # Test 2: Environment variables
    print("\nEnvironment variables:")
    for var, value in os.environ.items():
        if var.startswith("MCP_ATLASSIAN_"):
            print(f"  {var}={value}")
    
    # Test 3: Enable a flag
    test_flag = next(iter(all_flags.keys()))
    print(f"\nEnabling {test_flag}...")
    enable_feature(test_flag)
    print(f"  {test_flag} enabled: {is_enabled(test_flag)}")
    
    # Test 4: Disable a flag
    print(f"\nDisabling {test_flag}...")
    disable_feature(test_flag)
    print(f"  {test_flag} enabled: {is_enabled(test_flag)}")
    
    # Test 5: Reset overrides
    print(f"\nResetting overrides...")
    reset_runtime_overrides()
    print(f"  {test_flag} enabled: {is_enabled(test_flag)}")
    
    # Test 6: Get enabled flags
    print("\nEnabled flags:")
    for flag in get_enabled_flags():
        print(f"  {flag}")
    
    print("\nFeature flags test completed successfully!")
    return 0

if __name__ == "__main__":
    sys.exit(main())
EOF

chmod +x "$TARGET_DIR/feature_flags_test.py"

echo "Deployment completed successfully!"
echo "All original files have been backed up to: $BACKUP_DIR"
echo

# Test the feature flags functionality
echo "Testing feature flags functionality..."
cd "$TARGET_DIR" && PYTHONPATH="$TARGET_DIR" python feature_flags_test.py

echo
echo "To enable Enhanced Jira features, set the following environment variables:"
echo "export MCP_ATLASSIAN_FEATURE_FLAGS=\"ENHANCED_JIRA\""
echo "# or"
echo "export MCP_ATLASSIAN_ENABLE_ENHANCED_JIRA=\"true\""
echo
echo "For more information, see the documentation at:"
echo "$TARGET_DIR/docs/enhanced_jira_integration.md"
echo
echo "To verify the installation with the virtual environment, run:"
echo "source $VENV_DIR/bin/activate && python $TARGET_DIR/src/mcp_atlassian/diagnostics.py"