---
title: troubleshooting
date: 2024-12-07
version: v100.0.0
status: migrated
---
# Atlassian Troubleshooting Guide

## Common Issues and Solutions

### 1. Authentication Issues

#### 403 Forbidden Error
```
{"errorMessages":["The client does not have permission"],"errors":{}}
```
**Solution:**
1. Verify you're using the shared credentials from `/data/chase/secrets/atlassian_credentials.md`
2. Check that the API token is copied exactly, including all characters
3. Ensure no extra whitespace in the token

#### 401 Unauthorized Error
```
{"errorMessages":["Client must be authenticated"],"errors":{}}
```
**Solution:**
1. Verify ATLASSIAN_USERNAME matches the shared email exactly
2. Check API token format starts with "ATATT"
3. For browser access, use the shared password from credentials file

### 2. Connection Issues

#### Cannot Connect to Server
```
Connection refused or Network is unreachable
```
**Solution:**
1. Verify ATLASSIAN_URL is exactly `https://YOUR-CREDENTIALS@YOUR-DOMAIN/private window

### Quick Verification

Run the test script to verify your setup:
```bash
python3 scripts/test_atlassian_connection.sh
```

### Still Having Issues?

1. Check your .env file matches credentials exactly
2. Run test script with debug logging:
```bash
LOG_LEVEL=DEBUG python3 scripts/test_atlassian_connection.sh
```
3. Contact Support:
   - Ping @ProjectMgmt in #project-support
   - Create question file: `YYYY-MM-DD_HH-MM-SS_TZ_[YOUR-TEAM]_TO_ProjectMgmt_QUESTION.md`
   - Include full error message and steps to reproduce

### Logging Best Practices

1. Always include your team name in logs
2. Log full error responses
3. Include timestamps
4. Don't log credentials or tokens
