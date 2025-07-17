#!/usr/bin/env python
import os
import sys
from dotenv import load_dotenv
from atlassian import Confluence, Jira

# Load environment variables
load_dotenv(dotenv_path=".env")

# Print environment variables
print(f"CONFLUENCE_URL: {os.getenv('CONFLUENCE_URL')}")
print(f"CONFLUENCE_USERNAME: {os.getenv('CONFLUENCE_USERNAME')}")
print(f"CONFLUENCE_API_TOKEN: {'*' * 10 if os.getenv('CONFLUENCE_API_TOKEN') else None}")
print(f"JIRA_URL: {os.getenv('JIRA_URL')}")
print(f"JIRA_USERNAME: {os.getenv('JIRA_USERNAME')}")
print(f"JIRA_API_TOKEN: {'*' * 10 if os.getenv('JIRA_API_TOKEN') else None}")

# Test Confluence
try:
    print("Testing Confluence connection...")
    confluence = Confluence(
        url=os.getenv("CONFLUENCE_URL"),
        username=os.getenv("CONFLUENCE_USERNAME"),
        password=os.getenv("CONFLUENCE_API_TOKEN"),
        cloud=True
    )
    spaces = confluence.get_all_spaces(start=0, limit=5)
    print(f"Successfully connected to Confluence! Found {len(spaces['results'])} spaces.")
    for space in spaces['results']:
        print(f"Space: {space['name']} ({space['key']})")
except Exception as e:
    print(f"Error connecting to Confluence: {e}")

# Test Jira
try:
    print("\nTesting Jira connection...")
    jira = Jira(
        url=os.getenv("JIRA_URL"),
        username=os.getenv("JIRA_USERNAME"),
        password=os.getenv("JIRA_API_TOKEN"),
        cloud=True
    )
    projects = jira.projects()
    print(f"Successfully connected to Jira! Found {len(projects)} projects.")
    for project in projects[:5]:
        print(f"Project: {project['name']} ({project['key']})")
except Exception as e:
    print(f"Error connecting to Jira: {e}")