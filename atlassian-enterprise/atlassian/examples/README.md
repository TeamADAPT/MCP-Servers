---
title: README
date: 2024-12-07
version: v100.0.0
status: migrated
---
# Atlassian API Examples

## Overview
This directory contains practical examples for interacting with Jira and Confluence using the shared team credentials. All examples include proper team tagging and follow best practices.

## Prerequisites
1. Access to shared credentials at `/data/chase/secrets/atlassian_credentials.md`
2. Python 3.x installed
3. Required packages:
```bash
pip install atlassian-python-api requests
```

## Files

### 1. jira_examples.py
Demonstrates common Jira operations:
- Creating issues with team tags
- Creating epics
- Adding comments
- Creating sprints
- Searching team-specific issues

Usage:
```bash
python3 jira_examples.py
```

### 2. confluence_examples.py
Demonstrates common Confluence operations:
- Creating pages with team tags
- Updating existing pages
- Adding comments
- Creating structured documentation
- Generating sprint reports
- Searching team content

Usage:
```bash
python3 confluence_examples.py
```

## Important Notes
1. Always use the shared credentials from `/data/chase/secrets/atlassian_credentials.md`
2. Tag all content with your team name
3. Follow error handling practices shown in examples
4. Test in your team's designated space first

## Common Patterns

### Team Tagging
All examples use consistent team tagging:
```python
f'[{team_name}] {title}'  # For titles
f'[{team_name}] {comment_text}'  # For comments
```

### Error Handling
```python
try:
    # API operations
    result = jira.create_issue(...)
except Exception as e:
    print(f"Error: {str(e)}")
    # Handle error appropriately
```

### Authentication
```python
from atlassian import Jira, Confluence

# Use shared credentials
client = Jira(
    url=os.getenv('ATLASSIAN_URL'),
    username=os.getenv('ATLASSIAN_USERNAME'),
    password=os.getenv('ATLASSIAN_API_TOKEN')
)
```

## Testing Your Setup
1. Update your .env file with shared credentials
2. Run test script:
```bash
python3 scripts/test_atlassian_connection.sh
```
3. Try the example scripts

## Need Help?
- Check `/data-nova/ax/docs_central/atlassian/troubleshooting.md`
- Ping @ProjectMgmt in #project-support
- Create a question file: `YYYY-MM-DD_HH-MM-SS_TZ_[YOUR-TEAM]_TO_ProjectMgmt_QUESTION.md`
