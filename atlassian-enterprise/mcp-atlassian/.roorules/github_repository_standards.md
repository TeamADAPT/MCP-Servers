# GitHub Repository Standards

## Overview

This document outlines the standards for creating and managing GitHub repositories within the organization. These standards ensure consistency, security, and best practices across all repositories.

## Repository Creation Standards

When creating new GitHub repositories, the following standards must be followed:

1. **Branch Naming**:
   - Always use `main` as the default branch name
   - Do not use `master` as a branch name

2. **Repository Visibility**:
   - All repositories should be created as `private` by default
   - Public repositories require explicit approval from the security team

3. **Authentication**:
   - Always use the GitHub CLI (`gh`) for repository operations
   - Do not attempt to re-authenticate as we maintain persistent authentication

## Implementation Guidelines

### Using GitHub CLI

When creating a new repository, use the following command structure:

```bash
gh repo create [ORG]/[REPO-NAME] --private --description "[DESCRIPTION]" --source=. --push
```

Example:

```bash
gh repo create TeamADAPT/turbo-mode --private --description "TURBO MODE framework for continuous execution" --source=. --push
```

### Branch Setup

When initializing a new Git repository, always specify the main branch:

```bash
git init -b main
```

### Repository Settings

After creation, ensure the following settings are configured:

1. Branch protection rules for the main branch
2. Required reviews for pull requests
3. Status checks required before merging
4. Appropriate team access permissions

## Compliance

All repositories must comply with these standards. Non-compliant repositories will be flagged during security audits and may be subject to remediation.

## Contact

For questions or assistance with GitHub repository standards, please contact the MemCommsOps team.
