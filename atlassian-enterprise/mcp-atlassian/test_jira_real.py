#!/usr/bin/env python3
"""
Real-world test for Enhanced Jira Integration
Creates a test issue in the ATLAS project
"""

import os
import sys
import importlib.util
import json
from datetime import datetime

# Add the current directory to the path
sys.path.insert(0, "/data-nova/ax/DevOps/mcp/mcp-troubleshoot/Atlassian-connection/mcp-atlassian/src")

# Enable Enhanced Jira feature
os.environ["MCP_ATLASSIAN_ENABLE_ENHANCED_JIRA"] = "true"

def load_credentials():
    """Load Atlassian credentials from environment or file"""
    # Check environment variables first
    username = os.environ.get("ATLASSIAN_USERNAME")
    api_token = os.environ.get("ATLASSIAN_API_TOKEN")
    url = os.environ.get("ATLASSIAN_URL")
    
    # If not in environment, try to load from credentials file
    if not (username and api_token and url):
        try:
            creds_file = os.path.expanduser("~/.atlassian_credentials.json")
            if os.path.exists(creds_file):
                with open(creds_file, "r") as f:
                    creds = json.load(f)
                username = creds.get("username")
                api_token = creds.get("api_token")
                url = creds.get("url")
        except Exception as e:
            print(f"Error loading credentials file: {e}")
    
    return username, api_token, url

def test_feature_flags():
    """Test that feature flags are working correctly"""
    try:
        from mcp_atlassian.feature_flags import is_enabled, get_enabled_flags
        
        print("\n=== Feature Flags Test ===")
        flags = get_enabled_flags()
        print(f"Enabled flags: {flags}")
        print(f"ENHANCED_JIRA enabled: {is_enabled('ENHANCED_JIRA')}")
        
        if "ENHANCED_JIRA" not in flags:
            print("ERROR: ENHANCED_JIRA flag not enabled. Please check environment variables.")
            return False
        
        return True
    except Exception as e:
        print(f"ERROR testing feature flags: {e}")
        return False

def test_enhanced_jira():
    """Test the Enhanced Jira Integration by creating a real issue"""
    try:
        from mcp_atlassian.enhanced_jira import EnhancedJiraManager
        
        # Load credentials
        username, api_token, url = load_credentials()
        
        if not (username and api_token and url):
            print("ERROR: Atlassian credentials not found. Please set environment variables or create credentials file.")
            return False
        
        print("\n=== Enhanced Jira Test ===")
        print(f"Connecting to Jira at {url}")
        
        # Create manager
        manager = EnhancedJiraManager(
            url=url,
            username=username,
            api_token=api_token
        )
        
        # Create unique issue summary
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        issue_summary = f"Test Issue - Enhanced Jira Integration - {timestamp}"
        
        # Create issue with custom fields
        print(f"Creating issue: {issue_summary}")
        issue = manager.create_issue(
            project_key="ATLAS",
            summary=issue_summary,
            description="This is a test issue created by the Enhanced Jira Integration. This verifies that the implementation is working correctly with custom fields support.",
            issue_type="Task",
            custom_fields={
                "Department": "Engineering",
                "Team": "Platform"
            }
        )
        
        # Print issue details
        print(f"Issue created successfully: {issue.key}")
        print(f"Issue URL: {url}/browse/{issue.key}")
        
        return True
    except Exception as e:
        print(f"ERROR testing Enhanced Jira: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("=== Enhanced Jira Integration Real-World Test ===")
    
    # Test feature flags
    if not test_feature_flags():
        print("\nFeature flags test failed. Aborting further tests.")
        return 1
    
    # Test Enhanced Jira
    if not test_enhanced_jira():
        print("\nEnhanced Jira test failed.")
        return 1
    
    print("\nAll tests passed successfully!")
    return 0

if __name__ == "__main__":
    sys.exit(main())