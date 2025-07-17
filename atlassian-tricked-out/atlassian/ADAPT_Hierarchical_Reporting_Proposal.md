# ADAPT Hierarchical Reporting & Board Structure Proposal

**Date:** April 29, 2025  
**Prepared by:** CommsOps Atlassian Team

## Executive Summary

This proposal outlines a comprehensive approach to standardize executive reporting and implement a hierarchical Jira board structure across all ADAPT teams. The goal is to provide appropriate visibility at each leadership tier while maintaining alignment across the organization.

## 1. Mandatory Executive Summaries

### Proposed Implementation

1. **Standardized Template**
   - Create a standardized executive summary template based on the Echo Resonance example
   - Include sections for: accomplishments, current status, todo items, team collaboration, critical path
   - Make available through Confluence template library

2. **Reporting Schedule**
   - **Tier 1 (Executive)**: Weekly summaries due every Friday by 4PM
   - **Tier 2 (Directors)**: Bi-weekly summaries due every Monday and Thursday by 2PM
   - **Tier 3 (Team Leads)**: Daily standup summaries (lightweight format)

3. **Automation**
   - Create a Python script to generate executive summary template with proper dating
   - Implement Jira automation rule to remind team leads of upcoming summary due dates
   - Set up a bot to post reminders in team Slack channels

4. **Integration**
   - Link executive summaries to Jira epics via Confluence
   - Generate team-specific sections by querying Jira data
   - Roll up team summaries into department summaries automatically

5. **Rollout Plan**
   - Week 1: Pilot with 3 teams (Echo Resonance already implemented)
   - Week 2: Expand to all ADAPT teams
   - Week 3: Full organization implementation

### Implementation Requirements

- Script to generate executive summary templates
- Jira automation rules for reminders
- Confluence space for storing and organizing summaries
- Training materials for team leads and directors

## 2. Hierarchical Jira Board Structure

### Proposed Architecture

```
TIER 1: EXECUTIVE BOARDS
├── All Projects Master Board (High-level metrics only)
│   └── Program-Level KPI Dashboard
│       └── Resource Allocation View
└── Strategic Initiatives Board (Epic-level only)
    └── Critical Path & Dependencies View
        └── Risk Register View

TIER 2: DIRECTOR BOARDS
├── Department Overview Board
│   ├── Team Performance Dashboard
│   └── Resource Utilization View
├── Cross-Team Dependency Board
│   └── Team Coordination View 
└── Department Roadmap Board
    └── Milestone Tracking View

TIER 3: TEAM LEAD BOARDS
├── Team Sprint Board
│   ├── Kanban View
│   └── Scrum Board View
├── Team Backlog Board
│   └── Prioritization View
└── Team Metrics Board
    └── Velocity & Burndown Views
```

### Board Creation & Maintenance

1. **Standardized Board Creation**
   - Create Jira board templates for each tier
   - Develop Python script to automate board creation with appropriate JQL filters
   - Define standard gadgets and layout for each board type

2. **Automated Roll-Up Reporting**
   - Configure automatic issue roll-up from team-level to director-level
   - Implement weighted scoring for accurate progress reporting
   - Define KPIs appropriate for each leadership tier

3. **Access Control**
   - Implement role-based access control for boards
   - Create shared project roles for cross-team visibility
   - Set up guest access for stakeholders

4. **Implementation Timeline**
   - Month 1: Define and document board structures
   - Month 2: Implement Tier 1 and 2 boards
   - Month 3: Implement Tier 3 boards and integration

## 3. Technical Implementation Details

### Executive Summary Automation

```python
#!/usr/bin/env python3
"""
Executive Summary Generator
Creates standardized executive summary templates for team reporting
"""

import os
import datetime
import argparse
import requests
from jinja2 import Template

# Template location
TEMPLATE_DIR = "/data-nova/ax/InfraOps/CommsOps/atlassian/templates"
TEMPLATE_NAME = "executive_summary_template.md"

def generate_summary(team_name, output_dir="."):
    """Generate executive summary from template"""
    
    # Get current date
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    
    # Load template
    template_path = os.path.join(TEMPLATE_DIR, TEMPLATE_NAME)
    with open(template_path, 'r') as f:
        template_content = f.read()
    
    # Create template object
    template = Template(template_content)
    
    # Get Jira data for team
    jira_data = get_jira_team_data(team_name)
    
    # Render template with data
    summary_content = template.render(
        team_name=team_name,
        date=today,
        jira_data=jira_data
    )
    
    # Write to file
    output_file = f"{team_name}_Executive_Summary_{today}.md"
    output_path = os.path.join(output_dir, output_file)
    
    with open(output_path, 'w') as f:
        f.write(summary_content)
    
    print(f"Executive summary created: {output_path}")
    return output_path

def get_jira_team_data(team_name):
    """Get relevant Jira data for team"""
    # This would query the Jira API to get relevant data
    # Simplified version for proposal
    return {
        "completed_tasks": 24,
        "in_progress": 18,
        "blockers": 3,
        "upcoming_milestones": ["API Integration", "Dashboard Deployment"],
        "team_velocity": 42,
        "key_risks": ["Resource availability", "External dependency"]
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate team executive summary')
    parser.add_argument('team', help='Team name')
    parser.add_argument('--output', '-o', default='.', help='Output directory')
    
    args = parser.parse_args()
    generate_summary(args.team, args.output)
```

### Hierarchical Board Creation

```python
#!/usr/bin/env python3
"""
Hierarchical Board Generator
Creates standardized Jira board hierarchy for a project
"""

import os
import json
import requests
from requests.auth import HTTPBasicAuth

# Jira Connection Details
JIRA_BASE_URL = "https://levelup2x.atlassian.net"
JIRA_EMAIL = os.getenv("ATLASSIAN_EMAIL")
JIRA_API_TOKEN = os.getenv("ATLASSIAN_API_TOKEN")

# Authentication
auth = HTTPBasicAuth(JIRA_EMAIL, JIRA_API_TOKEN)
headers = {
    "Accept": "application/json",
    "Content-Type": "application/json"
}

def create_board_hierarchy(project_key, project_name):
    """Create complete board hierarchy for a project"""
    
    results = {
        "tier1": [],
        "tier2": [],
        "tier3": []
    }
    
    # Create Tier 1: Executive Boards
    results["tier1"].append(create_board(
        f"{project_name} Executive Overview",
        "com.pyxis.greenhopper.jira:next-gen-board",
        f"project = {project_key} ORDER BY Rank ASC",
        ["priority", "status"],
        "executive"
    ))
    
    # Create Tier 2: Director Boards
    results["tier2"].append(create_board(
        f"{project_name} Department Overview",
        "com.pyxis.greenhopper.jira:next-gen-board",
        f"project = {project_key} ORDER BY Rank ASC",
        ["component", "status"],
        "director"
    ))
    
    results["tier2"].append(create_board(
        f"{project_name} Cross-Team Dependencies",
        "com.pyxis.greenhopper.jira:next-gen-board",
        f'project = {project_key} AND "Team Dependencies" is not EMPTY ORDER BY Rank ASC',
        ["issuelink", "status"],
        "director"
    ))
    
    # Create Tier 3: Team Boards
    # Get components (teams)
    components = get_project_components(project_key)
    
    for component in components:
        results["tier3"].append(create_board(
            f"{component} Team Board",
            "com.pyxis.greenhopper.jira:next-gen-board",
            f'project = {project_key} AND component = "{component}" ORDER BY Rank ASC',
            ["assignee", "status"],
            "team"
        ))
    
    return results

def create_board(name, type, filter_query, quick_filters, board_level):
    """Create a single board with configuration"""
    
    url = f"{JIRA_BASE_URL}/rest/agile/1.0/board"
    
    payload = {
        "name": name,
        "type": type,
        "filterId": create_filter(name, filter_query),
        "location": {
            "projectKeyOrId": "ADAPT"
        },
        "config": {
            "ranking": {
                "rankCustomFieldId": 10019
            }
        }
    }
    
    try:
        response = requests.post(
            url,
            headers=headers,
            auth=auth,
            data=json.dumps(payload)
        )
        
        if response.status_code == 201:
            print(f"Created board: {name}")
            board = response.json()
            
            # Add quick filters
            for filter_name in quick_filters:
                add_quick_filter(board["id"], filter_name)
            
            return board
        else:
            print(f"Failed to create board: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Error creating board: {str(e)}")
        return None

def create_filter(name, jql):
    """Create a filter for the board"""
    url = f"{JIRA_BASE_URL}/rest/api/3/filter"
    
    payload = {
        "name": f"Filter for {name}",
        "jql": jql,
        "sharePermissions": [
            {
                "type": "global"
            }
        ]
    }
    
    try:
        response = requests.post(
            url,
            headers=headers,
            auth=auth,
            data=json.dumps(payload)
        )
        
        if response.status_code == 201:
            print(f"Created filter for: {name}")
            return response.json()["id"]
        else:
            print(f"Failed to create filter: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Error creating filter: {str(e)}")
        return None

def add_quick_filter(board_id, filter_name):
    """Add quick filter to board"""
    # Implementation would depend on Jira version and API
    print(f"Added quick filter: {filter_name} to board {board_id}")
    return True

def get_project_components(project_key):
    """Get all components for a project"""
    url = f"{JIRA_BASE_URL}/rest/api/3/project/{project_key}/components"
    
    try:
        response = requests.get(
            url,
            headers=headers,
            auth=auth
        )
        
        if response.status_code == 200:
            components = response.json()
            return [comp["name"] for comp in components]
        else:
            print(f"Failed to get components: {response.status_code} - {response.text}")
            return []
    except Exception as e:
        print(f"Error getting components: {str(e)}")
        return []

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Create hierarchical board structure')
    parser.add_argument('project_key', help='Project key')
    parser.add_argument('project_name', help='Project name')
    
    args = parser.parse_args()
    result = create_board_hierarchy(args.project_key, args.project_name)
    
    print(f"\nCreated {len(result['tier1'])} executive boards")
    print(f"Created {len(result['tier2'])} director boards")
    print(f"Created {len(result['tier3'])} team boards")
```

## 4. Training & Adoption Plan

To ensure successful adoption across the organization:

1. **Documentation**
   - Create step-by-step guides for each leadership tier
   - Provide examples of well-crafted executive summaries
   - Document board filtering and customization options

2. **Training Sessions**
   - Conduct tier-specific training sessions:
     - Executive overview (1 hour)
     - Director deep-dive (2 hours)
     - Team lead workshops (4 hours)
   - Provide hands-on exercises for each role

3. **Support Resources**
   - Designate Atlassian champions in each department
   - Establish office hours for questions and troubleshooting
   - Create FAQ document based on common questions

4. **Measuring Success**
   - Track adoption rate across teams
   - Measure time savings for status reporting
   - Survey leadership on usefulness of hierarchical views

## 5. MCP Services Integration

The hierarchical reporting structure can leverage the existing MCP Atlassian server for data integration:

1. **Data Collection**: Use the MCP Atlassian server to gather data from Jira and Confluence
2. **Report Generation**: Generate executive summaries using MCP tools
3. **Notification System**: Implement reminders through MCP Redis server
4. **Data Visualization**: Use MCP to generate metrics for dashboards

## Implementation Recommendation

The recommended approach is to implement this solution in three phases:

1. **Phase 1 (Weeks 1-2): Executive Summary Standardization**
   - Deploy the executive summary template
   - Create automation scripts for generation
   - Pilot with Echo Resonance and 2 other teams

2. **Phase 2 (Weeks 3-6): Hierarchical Board Creation**
   - Implement Tier 1 executive boards
   - Create Tier 2 director boards
   - Set up initial reporting automation

3. **Phase 3 (Weeks 7-10): Full Rollout**
   - Set up all team-level boards
   - Complete integration between tiers
   - Conduct training for all leadership levels

## Required Resources

- Atlassian administrator (2 days/week)
- Python developer (5 days)
- Technical writer (3 days)
- Training coordinator (2 days)
