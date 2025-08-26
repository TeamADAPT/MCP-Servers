---
title: README
date: 2024-12-07
version: v100.0.0
status: migrated
---
# Atlassian Onboarding Guide for New Teams

## Overview
This guide provides step-by-step instructions for new teams to set up and integrate with our Atlassian tools. Follow these steps in order to ensure proper setup and access.

## Prerequisites
1. Team name registered with Project Management
2. Access to `/data-nova/ax/docs_central/`
3. Access to `/data/chase/secrets/`

## Quick Start Steps

### 1. Access Credentials
```bash
# View shared credentials
cat /data/chase/secrets/atlassian_credentials.md
```

### 2. Environment Setup
1. Create .env file:
```bash
# Copy template
cp /data-nova/ax/project_mgmt/.env.template .env

# Add credentials from /data/chase/secrets/atlassian_credentials.md
```

### 3. Verify Connection
```bash
# Run from /data-nova/ax/project_mgmt
cd /data-nova/ax/project_mgmt
./scripts/test_atlassian_connection.sh
```

## Required Team Setup

### 1. Confluence Space Setup
1. Create team space
2. Set up required pages:
   - Team Overview
   - Project Documentation
   - Technical Specifications
   - Meeting Notes
   - Team Processes

### 2. Jira Project Setup
1. Create team project
2. Configure:
   - Project workflows
   - Issue types
   - Team boards
   - Sprint settings

### 3. Team Tagging
Always prefix content with team name:
- Jira: `[TEAM-NAME] Issue Title`
- Confluence: `[TEAM-NAME] Page Title`

## Documentation Structure

### Required Team Documentation
1. Team Space Home
   ```markdown
   # [TEAM-NAME] Space
   ## Overview
   - Team purpose
   - Key responsibilities
   - Current projects
   
   ## Quick Links
   - Team backlog
   - Sprint board
   - Documentation
   ```

2. Project Documentation
   ```markdown
   # [TEAM-NAME] Projects
   ## Current Projects
   - Project A
     - Overview
     - Timeline
     - Dependencies
   ```

3. Technical Documentation
   ```markdown
   # [TEAM-NAME] Technical Documentation
   ## Architecture
   - System design
   - Integration points
   - Dependencies
   ```

## Integration Examples

### 1. Jira Integration
```python
# Example from /data-nova/ax/docs_central/atlassian/examples/jira_examples.py
from atlassian import Jira

jira = Jira(
    url=os.getenv('ATLASSIAN_URL'),
    username=os.getenv('ATLASSIAN_USERNAME'),
    password=os.getenv('ATLASSIAN_API_TOKEN')
)

# Create team-tagged issue
issue = jira.create_issue(fields={
    'project': {'key': 'TEAM'},
    'summary': f'[{TEAM_NAME}] Issue Title',
    'description': 'Description',
    'issuetype': {'name': 'Task'}
})
```

### 2. Confluence Integration
```python
# Example from /data-nova/ax/docs_central/atlassian/examples/confluence_examples.py
from atlassian import Confluence

confluence = Confluence(
    url=os.getenv('ATLASSIAN_URL'),
    username=os.getenv('ATLASSIAN_USERNAME'),
    password=os.getenv('ATLASSIAN_API_TOKEN')
)

# Create team-tagged page
page = confluence.create_page(
    space='TEAM',
    title=f'[{TEAM_NAME}] Page Title',
    body='<h1>Content</h1>'
)
```

## Best Practices

### 1. Documentation
- Keep documentation up to date
- Use consistent formatting
- Include code examples
- Link related items

### 2. Issue Management
- Tag all issues with team name
- Use appropriate issue types
- Link related issues
- Update status regularly

### 3. Team Communication
- Document meeting notes
- Update sprint boards
- Link discussions to issues
- Share knowledge base

## Support Resources
1. Documentation: `/data-nova/ax/docs_central/atlassian/`
2. Examples: `/data-nova/ax/docs_central/atlassian/examples/`
3. Troubleshooting: `/data-nova/ax/docs_central/atlassian/troubleshooting.md`

## Getting Help
1. Check troubleshooting guide
2. Review example code
3. Contact Project Management:
   - Create question file: `YYYY-MM-DD_HH-MM-SS_TZ_[YOUR-TEAM]_TO_ProjectMgmt_QUESTION.md`
   - Ping @ProjectMgmt in #project-support

## Next Steps
1. Complete setup
2. Create required documentation
3. Configure team workflows
4. Start using tools

## Version History
| Date | Editor | Changes |
|------|--------|---------|
| 2024-12-06 23:30:00 MST | Project Management Team | Initial onboarding guide |
