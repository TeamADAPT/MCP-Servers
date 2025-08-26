---
title: getting_started
date: 2024-12-07
version: v100.0.0
status: migrated
---
# Getting Started with Atlassian Tools

## Initial Setup

1. Access the shared credentials file:
```bash
cat /data/chase/secrets/atlassian_credentials.md
```

2. Create or update your .env file with the shared credentials
3. Tag all your entries with your team name (e.g., "[DEVOPS] Feature Implementation")

## Common Operations

### Creating a Jira Issue
```python
from atlassian import Jira

# Initialize client with shared credentials
jira = Jira(
    url=os.getenv('ATLASSIAN_URL'),
    username=os.getenv('ATLASSIAN_USERNAME'),
    password=os.getenv('ATLASSIAN_API_TOKEN')
)

# Create an issue
issue = jira.create_issue(
    fields={
        'project': {'key': 'DEVOPS'},  # Replace with your project
        'summary': '[YOURTEAM] Issue Title',
        'description': 'Issue description',
        'issuetype': {'name': 'Task'}
    }
)
```

### Creating a Confluence Page
```python
from atlassian import Confluence

# Initialize client with shared credentials
confluence = Confluence(
    url=os.getenv('ATLASSIAN_URL'),
    username=os.getenv('ATLASSIAN_USERNAME'),
    password=os.getenv('ATLASSIAN_API_TOKEN')
)

# Create a page
page = confluence.create_page(
    space='TEAM',
    title='[YOURTEAM] Page Title',
    body='<p>Page content</p>'
)
```

### Browser Access (if needed)
1. Use the shared email from credentials file
2. Use the shared password from credentials file
3. Always tag content with your team name

## Best Practices

1. **Tagging**
   - Always prefix titles with your team name in brackets
   - Example: "[DEVOPS] Feature Implementation"

2. **API Usage**
   - Use the shared credentials
   - Include error handling
   - Follow rate limiting guidelines

3. **Content Organization**
   - Use consistent naming conventions
   - Keep documentation up to date
   - Link related items across Jira and Confluence

## Testing Your Setup

Run the connection test:
```bash
python3 scripts/test_atlassian_connection.sh
```

## Need Help?

1. Check `/data-nova/ax/docs_central/atlassian/troubleshooting.md`
2. Ping @ProjectMgmt in #project-support
3. Create a question file following the naming convention:
   `YYYY-MM-DD_HH-MM-SS_TZ_[YOUR-TEAM]_TO_ProjectMgmt_QUESTION.md`
