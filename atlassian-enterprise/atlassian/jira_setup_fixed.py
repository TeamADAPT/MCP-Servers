#!/usr/bin/env python3

import os
import json
import requests
from requests.auth import HTTPBasicAuth
import sys
import time

# Load environment variables
JIRA_BASE_URL = "https://YOUR-CREDENTIALS@YOUR-DOMAIN/json",
    "Content-Type": "application/json"
}

def create_component(name, description):
    """Create a project component"""
    url = f"{JIRA_BASE_URL}/rest/api/3/component"
    
    data = {
        "name": name,
        "description": description,
        "project": PROJECT_KEY
    }
        
    response = requests.post(
        url,
        headers=headers,
        auth=auth,
        json=data
    )
    
    if response.status_code >= 200 and response.status_code < 300:
        print(f"Created component: {name}")
        return response.json()
    else:
        print(f"Failed to create component {name}: {response.status_code} - {response.text}")
        return None

def create_epic(summary, description, labels=None):
    """Create an epic in the project"""
    url = f"{JIRA_BASE_URL}/rest/api/3/issue"
    
    # Fix labels by replacing spaces with underscores
    fixed_labels = []
    if labels:
        fixed_labels = [label.replace(" ", "_") for label in labels]
    
    data = {
        "fields": {
            "project": {
                "key": PROJECT_KEY
            },
            "summary": summary,
            "description": {
                "type": "doc",
                "version": 1,
                "content": [
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": description
                            }
                        ]
                    }
                ]
            },
            "issuetype": {
                "name": "Epic"
            }
        }
    }
    
    if fixed_labels:
        data["fields"]["labels"] = fixed_labels
    
    response = requests.post(
        url,
        headers=headers,
        auth=auth,
        json=data
    )
    
    if response.status_code >= 200 and response.status_code < 300:
        print(f"Created epic: {summary}")
        return response.json()
    else:
        print(f"Failed to create epic {summary}: {response.status_code} - {response.text}")
        return None

def main():
    print("Setting up Jira Project Components and Epics for Echo Resonance...")
    
    # Load team components
    try:
        with open('team_components.json', 'r') as f:
            team_components = json.load(f)
    except Exception as e:
        print(f"Error loading team_components.json: {e}")
        team_components = []
    
    # Load project categories
    try:
        with open('project_categories.json', 'r') as f:
            project_categories = json.load(f)
    except Exception as e:
        print(f"Error loading project_categories.json: {e}")
        project_categories = []
    
    # Load epics
    try:
        with open('echo_resonance_import.json', 'r') as f:
            epics = json.load(f)
    except Exception as e:
        print(f"Error loading echo_resonance_import.json: {e}")
        epics = []
    
    # Create team components
    print("\n=== Creating Team Components ===")
    for component in team_components:
        create_component(
            component["name"], 
            component["description"]
        )
        # Small delay to avoid rate limiting
        time.sleep(0.5)
    
    # Create category components
    print("\n=== Creating Category Components ===")
    for category in project_categories:
        create_component(
            category["name"], 
            category["description"]
        )
        # Small delay to avoid rate limiting
        time.sleep(0.5)
    
    # Create epics
    print("\n=== Creating Epics ===")
    for epic in epics:
        create_epic(
            epic["summary"],
            epic["description"],
            epic.get("labels")
        )
        # Small delay to avoid rate limiting
        time.sleep(1)
    
    print("\nSetup complete!")

if __name__ == "__main__":
    main()
