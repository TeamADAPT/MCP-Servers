#!/usr/bin/env python3
"""
Create Stella's DevOps-MCP Command Board for Echo Resonance

This script creates a Jira board specifically for Stella's DevOps-MCP team for the Echo Resonance project.
It addresses the permission issues with the previous script.

Usage:
  python3 create_stella_board.py
"""

import os
import json
import requests
from requests.auth import HTTPBasicAuth

# Atlassian credentials from environment variables
JIRA_BASE_URL = "https://YOUR-CREDENTIALS@YOUR-DOMAIN/json",
    "Content-Type": "application/json"
}

def get_all_er_boards():
    """Check for existing boards for the Echo Resonance project"""
    url = f"{JIRA_BASE_URL}/rest/agile/1.0/board"
    
    params = {
        "projectKeyOrId": "ER"
    }
    
    response = requests.get(
        url,
        params=params,
        headers=headers,
        auth=auth
    )
    
    if response.status_code == 200:
        boards_data = response.json()
        boards = boards_data.get("values", [])
        
        if boards:
            print("\n📋 Existing Echo Resonance Boards:")
            for board in boards:
                board_id = board.get("id")
                board_name = board.get("name")
                board_type = board.get("type", "").capitalize()
                print(f" - {board_name} ({board_type}) - ID: {board_id}")
                print(f"   URL: {JIRA_BASE_URL}/jira/software/projects/ER/boards/{board_id}")
            return boards
        else:
            print("No existing boards found for Echo Resonance project.")
            return []
    else:
        print(f"❌ Failed to get boards: {response.status_code} - {response.text}")
        return []

def get_mcp_issues_for_er():
    """Find issues in the ER project related to DevOps-MCP team"""
    url = f"{JIRA_BASE_URL}/rest/api/3/search"
    
    params = {
        "jql": 'project = "ER" AND text ~ "DevOps-MCP"',
        "maxResults": 100
    }
    
    response = requests.get(
        url,
        params=params,
        headers=headers,
        auth=auth
    )
    
    if response.status_code == 200:
        search_data = response.json()
        issues = search_data.get("issues", [])
        
        if issues:
            print(f"\n✅ Found {len(issues)} DevOps-MCP issues in the ER project.")
            return issues
        else:
            print("No DevOps-MCP issues found in the ER project.")
            return []
    else:
        print(f"❌ Failed to search for issues: {response.status_code} - {response.text}")
        return []

def check_for_component(component_name="DevOps-MCP"):
    """Check if the DevOps-MCP component exists in the ER project"""
    url = f"{JIRA_BASE_URL}/rest/api/3/project/ER/components"
    
    response = requests.get(
        url,
        headers=headers,
        auth=auth
    )
    
    if response.status_code == 200:
        components = response.json()
        for component in components:
            if component.get("name") == component_name:
                print(f"✅ Found {component_name} component in the ER project.")
                return component.get("id")
        
        print(f"❌ Component {component_name} not found in the ER project.")
        return None
    else:
        print(f"❌ Failed to get components: {response.status_code} - {response.text}")
        return None

def create_board_filter(name, jql):
    """Create a filter for the board with proper permissions"""
    url = f"{JIRA_BASE_URL}/rest/api/3/filter"
    
    # Fix permission issue by not using global sharing
    payload = {
        "name": name,
        "description": f"Filter for {name}",
        "jql": jql,
        # No sharePermissions means it's private to the creator
    }
    
    response = requests.post(
        url,
        data=json.dumps(payload),
        headers=headers,
        auth=auth
    )
    
    if response.status_code in [200, 201]:
        filter_data = response.json()
        filter_id = filter_data.get("id")
        print(f"✅ Successfully created filter '{name}' with ID: {filter_id}")
        return filter_id
    else:
        print(f"❌ Failed to create filter: {response.status_code} - {response.text}")
        return None

def create_stella_board():
    """Create a specialized board for Stella's DevOps-MCP team"""
    # First check if DevOps-MCP component exists
    component_id = check_for_component("DevOps-MCP")
    
    # Set the JQL based on component existence
    if component_id:
        jql = f'project = ER AND component = "DevOps-MCP" ORDER BY Rank ASC'
    else:
        # Fallback JQL if component doesn't exist
        jql = 'project = ER AND text ~ "DevOps-MCP" ORDER BY Rank ASC'
    
    # Create filter for the board
    filter_id = create_board_filter("Stella DevOps-MCP Team Filter", jql)
    
    if not filter_id:
        print("❌ Cannot create board without a filter.")
        return None
    
    # Board creation endpoint
    url = f"{JIRA_BASE_URL}/rest/agile/1.0/board"
    
    # Get ER project ID
    er_project_id = get_project_id("ER")
    if not er_project_id:
        print("❌ Could not find ER project ID.")
        return None
    
    # Board configuration
    payload = {
        "name": "Stella's DevOps-MCP Command Board",
        "type": "kanban",
        "filterId": filter_id,
        "location": {
            "projectId": er_project_id
        }
    }
    
    response = requests.post(
        url,
        data=json.dumps(payload),
        headers=headers,
        auth=auth
    )
    
    if response.status_code in [200, 201]:
        board_data = response.json()
        board_id = board_data.get("id")
        print(f"✅ Successfully created Stella's DevOps-MCP Command Board with ID: {board_id}")
        print(f"🔗 Board URL: {JIRA_BASE_URL}/jira/software/projects/ER/boards/{board_id}")
        return board_id
    else:
        print(f"❌ Failed to create Stella's board: {response.status_code} - {response.text}")
        return None

def get_project_id(project_key):
    """Get the project ID for a given project key"""
    url = f"{JIRA_BASE_URL}/rest/api/3/project/{project_key}"
    
    response = requests.get(
        url,
        headers=headers,
        auth=auth
    )
    
    if response.status_code == 200:
        project_data = response.json()
        return project_data.get("id")
    else:
        print(f"❌ Failed to get project ID: {response.status_code} - {response.text}")
        return None

def main():
    """Main function to create Stella's DevOps-MCP Command Board"""
    print("🚀 Starting Stella's DevOps-MCP Command Board Creation")
    print("=====================================================")
    
    # Check for existing boards
    existing_boards = get_all_er_boards()
    stella_board_exists = False
    
    # Check if Stella's board already exists
    for board in existing_boards:
        if "Stella" in board.get("name") or "DevOps-MCP" in board.get("name"):
            stella_board_exists = True
            print(f"\n✅ Stella's board already exists: {board.get('name')}")
            break
    
    if stella_board_exists:
        proceed = input("\nStella's board already exists. Create another one? (y/n): ")
        if proceed.lower() != 'y':
            print("Exiting without creating a new board.")
            return
    
    # Check if there are any DevOps-MCP issues in ER
    mcp_issues = get_mcp_issues_for_er()
    
    # Create Stella's board
    print("\n📋 Creating Stella's DevOps-MCP Command Board...")
    board_id = create_stella_board()
    
    if board_id:
        print("\n🎉 Stella's Board Creation Successful!")
        print("=====================================================")
        print(f"Board URL: {JIRA_BASE_URL}/jira/software/projects/ER/boards/{board_id}")
        
        # Create a reference to this board in the project documentation
        print("\nNext Steps:")
        print("1. Add this board to echo_resonance_dashboards.md")
        print("2. Link to this board from project_summary.md")
        print("3. Notify Stella about her dedicated command board")
    else:
        print("\n❌ Failed to create Stella's board.")
        print("Try using the Jira UI directly to create the board.")

if __name__ == "__main__":
    main()
