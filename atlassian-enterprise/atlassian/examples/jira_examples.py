#!/usr/bin/env python3

import os
from atlassian import Jira
from datetime import datetime

# Initialize client with shared credentials
jira = Jira(
    url=os.getenv('ATLASSIAN_URL'),
    username=os.getenv('ATLASSIAN_USERNAME'),
    password=os.getenv('ATLASSIAN_API_TOKEN')
)

def create_issue(project_key, team_name, summary, description, issue_type='Task'):
    """Create a Jira issue with team tag."""
    return jira.create_issue(fields={
        'project': {'key': project_key},
        'summary': f'[{team_name}] {summary}',
        'description': description,
        'issuetype': {'name': issue_type}
    })

def create_epic(project_key, team_name, epic_name, epic_summary, epic_description):
    """Create an epic with team tag."""
    return jira.create_issue(fields={
        'project': {'key': project_key},
        'summary': f'[{team_name}] {epic_name}',
        'description': epic_description,
        'issuetype': {'name': 'Epic'},
        'customfield_10011': epic_summary  # Epic Name field
    })

def add_comment(issue_key, team_name, comment_text):
    """Add a comment with team tag."""
    return jira.add_comment(
        issue_key,
        f'[{team_name}] {comment_text}'
    )

def create_sprint(board_id, team_name, sprint_name):
    """Create a sprint with team tag."""
    return jira.create_sprint(
        f'[{team_name}] {sprint_name}',
        board_id,
        startDate=datetime.now().isoformat()
    )

def search_team_issues(team_name):
    """Search for all issues tagged with team name."""
    jql = f'summary ~ "[{team_name}]" ORDER BY created DESC'
    return jira.jql(jql)

# Example usage:
if __name__ == "__main__":
    # Replace with your team name
    TEAM = "DEVOPS"
    PROJECT = "ADAPT"
    
    # Create an issue
    issue = create_issue(
        project_key=PROJECT,
        team_name=TEAM,
        summary="Implement New Feature",
        description="Detailed description of the feature"
    )
    print(f"Created issue: {issue['key']}")
    
    # Create an epic
    epic = create_epic(
        project_key=PROJECT,
        team_name=TEAM,
        epic_name="Q1 Objectives",
        epic_summary="Q1 Development Goals",
        epic_description="Detailed description of Q1 objectives"
    )
    print(f"Created epic: {epic['key']}")
    
    # Add a comment
    comment = add_comment(
        issue_key=issue['key'],
        team_name=TEAM,
        comment_text="Initial implementation complete"
    )
    print(f"Added comment to {issue['key']}")
    
    # Search team issues
    team_issues = search_team_issues(TEAM)
    print(f"Found {len(team_issues['issues'])} issues for team {TEAM}")
