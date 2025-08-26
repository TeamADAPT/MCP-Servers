# Atlassian Setup Instructions (Version 2)

## Document Information
- **Created**: 2024-12-07 13:00:00 MST
- **Status**: VERIFIED WORKING
- **Timeline**: Complete within 24 hours

## Prerequisites
1. Access `/data/chase/secrets/atlassian_credentials.md` for shared credentials
2. Python 3.x installed
3. Required packages: `pip install atlassian-python-api requests`

## Automated Setup (Recommended)

### 1. Environment Setup
```bash
# Copy template
cp /data-nova/ax/project_mgmt/.env.template .env

# Add credentials from /data/chase/secrets/atlassian_credentials.md to .env
ATLASSIAN_URL=https://YOUR-CREDENTIALS@YOUR-DOMAIN