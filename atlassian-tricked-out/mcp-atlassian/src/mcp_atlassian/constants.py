"""Constants used throughout the MCP Atlassian integration."""

# Tool categories
TOOL_CATEGORY_CONFLUENCE = "Confluence"
TOOL_CATEGORY_JIRA = "Jira"
TOOL_CATEGORY_JSM = "Jira Service Management"
TOOL_CATEGORY_BITBUCKET = "Bitbucket"
TOOL_CATEGORY_ENTERPRISE = "Enterprise Features"

# Feature groups
FEATURE_GROUP_CORE = "core"
FEATURE_GROUP_ENHANCED_JIRA = "enhanced_jira"
FEATURE_GROUP_ENHANCED_CONFLUENCE = "enhanced_confluence"
FEATURE_GROUP_JSM = "jsm"
FEATURE_GROUP_BITBUCKET = "bitbucket"
FEATURE_GROUP_ENTERPRISE = "enterprise"

# Default environment variable prefixes
ENV_PREFIX_CONFLUENCE = "CONFLUENCE"
ENV_PREFIX_JIRA = "JIRA"
ENV_PREFIX_JSM = "JSM"
ENV_PREFIX_BITBUCKET = "BITBUCKET"

# Feature flag environment variable prefix
ENV_PREFIX_FEATURE_FLAG = "ENABLE"

# Atlassian API endpoints
API_PATH_JIRA = "/rest/api/3"
API_PATH_CONFLUENCE = "/rest/api/latest"
API_PATH_JSM = "/rest/servicedeskapi"
API_PATH_BITBUCKET = "/rest/api/1.0"

# HTTP methods
HTTP_GET = "GET"
HTTP_POST = "POST"
HTTP_PUT = "PUT"
HTTP_DELETE = "DELETE"

# Status codes
STATUS_SUCCESS = "success"
STATUS_ERROR = "error"
STATUS_WARNING = "warning"

# Tool error messages
ERROR_MISSING_CREDENTIALS = "Missing required credentials for this service"
ERROR_SERVICE_UNAVAILABLE = "Service is not available or configured"
ERROR_INVALID_INPUT = "Invalid input parameters"
ERROR_NETWORK_ERROR = "Network error while connecting to service"
ERROR_API_ERROR = "API returned an error"
ERROR_PERMISSION_DENIED = "Permission denied for this operation"
ERROR_RESOURCE_NOT_FOUND = "Resource not found"
ERROR_INVALID_CONFIGURATION = "Invalid configuration"

# Default pagination values
DEFAULT_PAGINATION_LIMIT = 50
DEFAULT_PAGINATION_START = 0