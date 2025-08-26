#!/usr/bin/env python3

import os
from atlassian import Confluence
from datetime import datetime

# Initialize client with shared credentials
confluence = Confluence(
    url=os.getenv('ATLASSIAN_URL'),
    username=os.getenv('ATLASSIAN_USERNAME'),
    password=os.getenv('ATLASSIAN_API_TOKEN')
)

def create_page(space_key, team_name, title, body_content):
    """Create a Confluence page with team tag."""
    full_title = f'[{team_name}] {title}'
    return confluence.create_page(
        space=space_key,
        title=full_title,
        body=body_content
    )

def update_page(page_id, team_name, title, new_content):
    """Update an existing page with team tag."""
    full_title = f'[{team_name}] {title}'
    return confluence.update_page(
        page_id=page_id,
        title=full_title,
        body=new_content
    )

def add_page_comment(page_id, team_name, comment_text):
    """Add a comment to a page with team tag."""
    return confluence.add_comment(
        page_id,
        f'[{team_name}] {comment_text}'
    )

def create_team_documentation(space_key, team_name, project_name):
    """Create a structured team documentation space."""
    # Create main project page
    main_page = create_page(
        space_key=space_key,
        team_name=team_name,
        title=f'{project_name} Documentation',
        body_content=f'''
        <h1>{team_name} - {project_name} Documentation</h1>
        <p>Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S %Z')}</p>
        <ac:structured-macro ac:name="toc"/>
        '''
    )

    # Create child pages
    sections = [
        ('Overview', '<h2>Project Overview</h2><p>Project description and goals</p>'),
        ('Architecture', '<h2>System Architecture</h2><p>Technical architecture details</p>'),
        ('Setup Guide', '<h2>Setup Instructions</h2><p>How to set up the project</p>'),
        ('API Documentation', '<h2>API Reference</h2><p>API endpoints and usage</p>'),
        ('Team Processes', '<h2>Team Workflows</h2><p>Development and deployment processes</p>')
    ]

    for section_title, section_content in sections:
        confluence.create_page(
            space=space_key,
            title=f'[{team_name}] {project_name} - {section_title}',
            body=section_content,
            parent_id=main_page['id']
        )

    return main_page

def search_team_content(team_name):
    """Search for all content tagged with team name."""
    cql = f'title ~ "[{team_name}]"'
    return confluence.cql(cql)

def create_sprint_report(space_key, team_name, sprint_number, sprint_data):
    """Create a sprint report page."""
    title = f'Sprint {sprint_number} Report'
    content = f'''
    <h1>{team_name} - Sprint {sprint_number} Report</h1>
    <p>Report generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S %Z')}</p>
    
    <h2>Sprint Overview</h2>
    <table>
        <tr><th>Start Date</th><td>{sprint_data['start_date']}</td></tr>
        <tr><th>End Date</th><td>{sprint_data['end_date']}</td></tr>
        <tr><th>Story Points</th><td>{sprint_data['story_points']}</td></tr>
        <tr><th>Completion</th><td>{sprint_data['completion_percentage']}%</td></tr>
    </table>

    <h2>Achievements</h2>
    <ul>
    {''.join(f'<li>{item}</li>' for item in sprint_data['achievements'])}
    </ul>

    <h2>Challenges</h2>
    <ul>
    {''.join(f'<li>{item}</li>' for item in sprint_data['challenges'])}
    </ul>

    <h2>Next Sprint Goals</h2>
    <ul>
    {''.join(f'<li>{item}</li>' for item in sprint_data['next_sprint_goals'])}
    </ul>
    '''
    
    return create_page(space_key, team_name, title, content)

# Example usage:
if __name__ == "__main__":
    # Replace with your team name
    TEAM = "DEVOPS"
    SPACE = "TEAM"
    
    # Create team documentation structure
    main_page = create_team_documentation(
        space_key=SPACE,
        team_name=TEAM,
        project_name="Infrastructure Automation"
    )
    print(f"Created documentation structure: {main_page['id']}")
    
    # Create a sprint report
    sprint_data = {
        'start_date': '2024-12-01',
        'end_date': '2024-12-14',
        'story_points': 34,
        'completion_percentage': 92,
        'achievements': [
            'Automated deployment pipeline',
            'Implemented monitoring system',
            'Updated security protocols'
        ],
        'challenges': [
            'Integration testing delays',
            'Third-party API issues'
        ],
        'next_sprint_goals': [
            'Implement automated testing',
            'Enhance monitoring dashboards'
        ]
    }
    
    sprint_report = create_sprint_report(
        space_key=SPACE,
        team_name=TEAM,
        sprint_number=1,
        sprint_data=sprint_data
    )
    print(f"Created sprint report: {sprint_report['id']}")
    
    # Search team content
    team_content = search_team_content(TEAM)
    print(f"Found {len(team_content['results'])} pages for team {TEAM}")
