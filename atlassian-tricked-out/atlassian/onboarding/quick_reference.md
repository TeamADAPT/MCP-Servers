---
title: quick_reference
date: 2024-12-07
version: v100.0.0
status: migrated
---
# Atlassian Quick Reference Guide

## Common Operations

### Jira

#### Creating Issues
```python
# Using API
issue = jira.create_issue(fields={
    'project': {'key': 'TEAM'},
    'summary': f'[{TEAM_NAME}] Issue Title',
    'description': 'Description',
    'issuetype': {'name': 'Task'}
})

# Browser URL
https://levelup2x.atlassian.net/jira/software/projects/[PROJECT-KEY]/issues/create
```

#### Searching Issues
```python
# JQL Examples
f'project = "{PROJECT_KEY}" AND summary ~ "[{TEAM_NAME}]"'  # Team issues
f'project = "{PROJECT_KEY}" AND created >= -7d'  # Last 7 days
f'project = "{PROJECT_KEY}" AND status = "In Progress"'  # Active issues
```

#### Sprint Management
```python
# Create Sprint
sprint = jira.create_sprint(
    name=f'[{TEAM_NAME}] Sprint {number}',
    board_id=board_id
)

# Start Sprint
jira.start_sprint(sprint_id)
```

### Confluence

#### Page Creation
```python
# Using API
page = confluence.create_page(
    space='TEAM',
    title=f'[{TEAM_NAME}] Page Title',
    body='<h1>Content</h1>'
)

# Browser URL
https://levelup2x.atlassian.net/wiki/spaces/[SPACE-KEY]/pages/create
```

#### Content Search
```python
# CQL Examples
f'title ~ "[{TEAM_NAME}]"'  # Team pages
f'space = "{SPACE_KEY}" AND created >= "2024/12/01"'  # Recent pages
f'type = page AND label = "technical"'  # Technical docs
```

## Common URLs

### Jira
- Board: `/jira/software/projects/[PROJECT-KEY]/boards/[BOARD-ID]`
- Backlog: `/jira/software/projects/[PROJECT-KEY]/backlogs/[BACKLOG-ID]`
- Issues: `/jira/software/projects/[PROJECT-KEY]/issues`
- Create Issue: `/jira/software/projects/[PROJECT-KEY]/issues/create`
- Dashboards: `/jira/dashboards`

### Confluence
- Space Home: `/wiki/spaces/[SPACE-KEY]`
- Create Page: `/wiki/spaces/[SPACE-KEY]/pages/create`
- Space Settings: `/wiki/spaces/[SPACE-KEY]/space-settings`
- Search: `/wiki/search`

## Required Prefixes

### Issue Titles
```
[TEAM-NAME] Feature: Description
[TEAM-NAME] Bug: Description
[TEAM-NAME] Task: Description
```

### Page Titles
```
[TEAM-NAME] Technical Documentation
[TEAM-NAME] Meeting Notes YYYY-MM-DD
[TEAM-NAME] Sprint Review Sprint-N
```

## Common Templates

### Issue Description
```markdown
## Overview
[Brief description]

## Requirements
- Requirement 1
- Requirement 2

## Acceptance Criteria
- [ ] Criteria 1
- [ ] Criteria 2

## Dependencies
- Dependency 1
- Dependency 2
```

### Meeting Notes
```markdown
# [TEAM-NAME] Meeting Notes YYYY-MM-DD

## Attendees
- [Name] - [Role]

## Agenda
1. Topic 1
2. Topic 2

## Discussion
### Topic 1
- Point 1
- Point 2

### Topic 2
- Point 1
- Point 2

## Action Items
- [ ] Action 1 - [Owner] - [Due Date]
- [ ] Action 2 - [Owner] - [Due Date]
```

## Quick Commands

### Test Connection
```bash
cd /data-nova/ax/project_mgmt
./scripts/test_atlassian_connection.sh
```

### View Credentials
```bash
cat /data/chase/secrets/atlassian_credentials.md
```

### Update Environment
```bash
cp /data-nova/ax/project_mgmt/.env.template .env
# Edit .env with credentials
```

## Support Resources
- Documentation: `/data-nova/ax/docs_central/atlassian/`
- Examples: `/data-nova/ax/docs_central/atlassian/examples/`
- Troubleshooting: `/data-nova/ax/docs_central/atlassian/troubleshooting.md`
- Onboarding: `/data-nova/ax/docs_central/atlassian/onboarding/`

## Version History
| Date | Editor | Changes |
|------|--------|---------|
| 2024-12-06 23:35:00 MST | Project Management Team | Initial quick reference guide |
