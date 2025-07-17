# MCP-Atlassian Test Suite

This directory contains tests for the MCP-Atlassian integration.

## Overview

The test suite covers the core functionality of the MCP-Atlassian integration, with a focus on:

1. API interactions with Jira and Confluence
2. Custom fields handling and validation
3. Error recovery mechanisms
4. Configuration management

## Test Files

- **test_mock.py**: Mock tests that don't require actual Jira/Confluence credentials. These tests validate the custom fields functionality using mocks instead of actual API calls, making them suitable for running in environments without credentials.

## Running Tests

To run the mock tests (which don't require credentials):

```bash
cd /data-nova/ax/DevOps/mcp/mcp-servers/cicd/mcp-atlassian
python -m tests.test_mock
```

## Custom Fields Testing

The mock tests specifically validate the behavior related to the 2025-04-19 custom fields fix, including:

1. Validation that `name` and `dept` fields are required
2. Handling of unavailable custom fields in various projects
3. Automatic field availability detection and recovery
4. Cache mechanisms for tracking field availability
5. API calls for setting fields as global

## Test Design Principles

1. **Independence**: Tests should not depend on the state of other tests
2. **Mocking**: External dependencies are mocked to ensure tests can run without actual credentials
3. **Comprehensive Coverage**: Tests should cover both happy paths and error cases
4. **Readability**: Test names and documentation should clearly explain what is being tested

## Adding New Tests

When adding new tests:

1. Follow the existing pattern for mock setup and tear down
2. Use descriptive method names that explain what is being tested
3. Add print statements for manual verification when running tests directly
4. For API interaction tests, always mock the API responses