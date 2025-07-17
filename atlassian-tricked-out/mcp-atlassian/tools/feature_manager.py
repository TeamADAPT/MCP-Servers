#!/usr/bin/env python3
"""
MCP Atlassian Feature Flag Manager

This script provides a command-line interface for managing feature flags
in the MCP Atlassian integration.

Usage:
  feature_manager.py list                  # List all feature flags and their status
  feature_manager.py enable FEATURE_NAME   # Enable a feature
  feature_manager.py disable FEATURE_NAME  # Disable a feature
  feature_manager.py save                  # Save current flag state to config file
  feature_manager.py reset                 # Reset all runtime overrides
  feature_manager.py diagnostics           # Run diagnostics

Enhanced Confluence Features:
  enhanced_confluence                      # Enable all enhanced Confluence features
  space_management                         # Space creation, permissions, and management
  template_management                      # Manage and use templates and blueprints
  content_management                       # Advanced content, properties, and export features
"""

import os
import sys
import argparse
import logging
from typing import List, Optional

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from src.mcp_atlassian.feature_flags import (
        get_all_flags, get_feature_groups, enable_feature, 
        disable_feature, reset_runtime_overrides, save_current_flags_to_config
    )
    from src.mcp_atlassian.diagnostics import run_diagnostics, format_diagnostics_report, save_diagnostics_report
except ImportError as e:
    print(f"Error: Could not import MCP Atlassian modules: {e}")
    print("Make sure you're running this script from the correct directory.")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("feature-manager")


def list_features() -> None:
    """List all feature flags and their current status."""
    all_flags = get_all_flags()
    feature_groups = get_feature_groups()
    
    print("MCP Atlassian Feature Flags")
    print("==========================")
    
    # Print by feature group
    for group_name, flags in feature_groups.items():
        print(f"\n{group_name.upper()} Features:")
        for flag in flags:
            status = "✓ ENABLED" if all_flags.get(flag, False) else "✗ disabled"
            print(f"  {flag:<25} {status}")
    
    # Print any flags not in groups
    ungrouped_flags = set(all_flags.keys()) - {flag for flags in feature_groups.values() for flag in flags}
    if ungrouped_flags:
        print("\nOTHER Features:")
        for flag in sorted(ungrouped_flags):
            status = "✓ ENABLED" if all_flags.get(flag, False) else "✗ disabled"
            print(f"  {flag:<25} {status}")
    
    print("\nEnvironment Variables:")
    for flag in all_flags:
        env_var = f"ENABLE_{flag.upper()}"
        value = os.getenv(env_var)
        if value:
            print(f"  {env_var}={value}")


def enable_feature_flag(feature_name: str) -> None:
    """Enable a feature flag.
    
    Args:
        feature_name: Name of the feature to enable
    """
    if enable_feature(feature_name):
        print(f"Feature '{feature_name}' enabled successfully")
    else:
        print(f"Failed to enable feature '{feature_name}'")
        sys.exit(1)


def disable_feature_flag(feature_name: str) -> None:
    """Disable a feature flag.
    
    Args:
        feature_name: Name of the feature to disable
    """
    if disable_feature(feature_name):
        print(f"Feature '{feature_name}' disabled successfully")
    else:
        print(f"Failed to disable feature '{feature_name}'")
        sys.exit(1)


def save_flags() -> None:
    """Save current feature flag state to config file."""
    if save_current_flags_to_config():
        print("Feature flags saved to config file successfully")
    else:
        print("Failed to save feature flags to config file")
        sys.exit(1)


def reset_flags() -> None:
    """Reset all runtime feature flag overrides."""
    reset_runtime_overrides()
    print("Runtime feature flag overrides have been reset")


def run_diagnostics_cmd() -> None:
    """Run diagnostics and display results."""
    print("Running diagnostics...")
    diagnostics = run_diagnostics()
    report = format_diagnostics_report(diagnostics)
    print("\nDiagnostics Report:")
    print(report)
    
    # Save report
    file_path = save_diagnostics_report(report)
    print(f"\nReport saved to: {file_path}")


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description="MCP Atlassian Feature Flag Manager")
    subparsers = parser.add_subparsers(dest="command", help="command to execute")
    
    # List command
    list_parser = subparsers.add_parser("list", help="List all feature flags and their status")
    
    # Enable command
    enable_parser = subparsers.add_parser("enable", help="Enable a feature")
    enable_parser.add_argument("feature_name", help="Name of the feature to enable")
    
    # Disable command
    disable_parser = subparsers.add_parser("disable", help="Disable a feature")
    disable_parser.add_argument("feature_name", help="Name of the feature to disable")
    
    # Save command
    save_parser = subparsers.add_parser("save", help="Save current flag state to config file")
    
    # Reset command
    reset_parser = subparsers.add_parser("reset", help="Reset all runtime overrides")
    
    # Diagnostics command
    diagnostics_parser = subparsers.add_parser("diagnostics", help="Run diagnostics")
    
    args = parser.parse_args()
    
    if args.command == "list":
        list_features()
    elif args.command == "enable":
        enable_feature_flag(args.feature_name)
    elif args.command == "disable":
        disable_feature_flag(args.feature_name)
    elif args.command == "save":
        save_flags()
    elif args.command == "reset":
        reset_flags()
    elif args.command == "diagnostics":
        run_diagnostics_cmd()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()