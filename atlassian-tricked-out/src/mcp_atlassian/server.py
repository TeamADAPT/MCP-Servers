import json
import logging
import os
from collections.abc import Sequence
from typing import Any

from mcp.server import Server
from mcp.types import Resource, TextContent, Tool
from pydantic import AnyUrl

from .confluence import ConfluenceFetcher
from .jira import JiraFetcher

# We'll try to import the enhanced modules, but handle it if they're not available
try:
    from .server_jira_service_management import get_jsm_tools, handle_jsm_tool_call, get_jsm_available
    JSM_AVAILABLE = True
except ImportError:
    JSM_AVAILABLE = False
    logger = logging.getLogger("mcp-atlassian")
    logger.warning("JSM module not available, JSM features will be disabled")
    # Define dummy functions
    def get_jsm_tools(): return []
    def handle_jsm_tool_call(name, arguments): return []
    def get_jsm_available(): return False
    
# Try to import enhanced Confluence module
try:
    from .server_enhanced_confluence import get_enhanced_confluence_tools, handle_enhanced_confluence_tool_call
    from .confluence_space import SpaceManager
    from .confluence_template import TemplateManager
    from .confluence_content import ContentManager
    ENHANCED_CONFLUENCE_AVAILABLE = True
except ImportError:
    ENHANCED_CONFLUENCE_AVAILABLE = False
    logger = logging.getLogger("mcp-atlassian")
    logger.warning("Enhanced Confluence module not available, enhanced Confluence features will be disabled")
    # Define dummy functions
    def get_enhanced_confluence_tools(): return []
    def handle_enhanced_confluence_tool_call(name, arguments, space_manager=None, template_manager=None, content_manager=None): return {}

# Try to import enterprise modules
try:
    from .server_enterprise import get_enterprise_tools, handle_enterprise_tool_call
    ENTERPRISE_AVAILABLE = True
except ImportError:
    ENTERPRISE_AVAILABLE = False
    logger = logging.getLogger("mcp-atlassian")
    logger.warning("Enterprise module not available, enterprise features will be disabled")
    # Define dummy functions
    def get_enterprise_tools(): return []
    def handle_enterprise_tool_call(name, arguments): return {}

# Try to import Bitbucket modules
try:
    from .bitbucket import BitbucketManager
    from .bitbucket_pipeline import BitbucketPipelineManager
    from .bitbucket_integration import BitbucketIntegrationManager
    BITBUCKET_AVAILABLE = True
except ImportError:
    BITBUCKET_AVAILABLE = False
    logger = logging.getLogger("mcp-atlassian")
    logger.warning("Bitbucket module not available, Bitbucket features will be disabled")

# Configure logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger("mcp-atlassian")
logging.getLogger("mcp.server.lowlevel.server").setLevel(logging.WARNING)


def get_available_services():
    """Determine which services are available based on environment variables."""
    confluence_vars = all(
        [os.getenv("CONFLUENCE_URL"), os.getenv("CONFLUENCE_USERNAME"), os.getenv("CONFLUENCE_API_TOKEN")]
    )

    jira_vars = all([os.getenv("JIRA_URL"), os.getenv("JIRA_USERNAME"), os.getenv("JIRA_API_TOKEN")])
    
    bitbucket_vars = all([
        os.getenv("BITBUCKET_URL"), 
        os.getenv("BITBUCKET_USERNAME"), 
        os.getenv("BITBUCKET_APP_PASSWORD")
    ]) and BITBUCKET_AVAILABLE
    
    jsm_vars = get_jsm_available() if JSM_AVAILABLE else False
    
    enhanced_confluence_vars = ENHANCED_CONFLUENCE_AVAILABLE and confluence_vars
    
    enterprise_vars = ENTERPRISE_AVAILABLE

    return {
        "confluence": confluence_vars, 
        "jira": jira_vars,
        "bitbucket": bitbucket_vars,
        "jsm": jsm_vars,
        "enhanced_confluence": enhanced_confluence_vars,
        "enterprise": enterprise_vars
    }


# Initialize services based on available credentials
services = get_available_services()
confluence_fetcher = ConfluenceFetcher() if services["confluence"] else None
jira_fetcher = JiraFetcher() if services["jira"] else None

# Initialize Bitbucket services if available
bitbucket_manager = None
bitbucket_pipeline_manager = None
bitbucket_integration_manager = None
if services["bitbucket"]:
    try:
        bitbucket_manager = BitbucketManager()
        bitbucket_pipeline_manager = BitbucketPipelineManager()
        bitbucket_integration_manager = BitbucketIntegrationManager()
    except Exception as e:
        logger.error(f"Error initializing Bitbucket services: {str(e)}")
        services["bitbucket"] = False

# Initialize enhanced Confluence services if available
space_manager = None
template_manager = None
content_manager = None
if services["enhanced_confluence"]:
    try:
        space_manager = SpaceManager()
        template_manager = TemplateManager()
        content_manager = ContentManager()
    except Exception as e:
        logger.error(f"Error initializing enhanced Confluence services: {str(e)}")
        services["enhanced_confluence"] = False

app = Server("mcp-atlassian")


@app.list_resources()
async def list_resources() -> list[Resource]:
    """List available Confluence spaces and Jira projects as resources."""
    resources = []

    # Add Confluence spaces
    if confluence_fetcher:
        spaces_response = confluence_fetcher.get_spaces()
        if isinstance(spaces_response, dict) and "results" in spaces_response:
            spaces = spaces_response["results"]
            resources.extend(
                [
                    Resource(
                        uri=AnyUrl(f"confluence://{space['key']}"),
                        name=f"Confluence Space: {space['name']}",
                        mimeType="text/plain",
                        description=space.get("description", {}).get("plain", {}).get("value", ""),
                    )
                    for space in spaces
                ]
            )

    # Add Jira projects
    if jira_fetcher:
        try:
            projects = jira_fetcher.jira.projects()
            resources.extend(
                [
                    Resource(
                        uri=AnyUrl(f"jira://{project['key']}"),
                        name=f"Jira Project: {project['name']}",
                        mimeType="text/plain",
                        description=project.get("description", ""),
                    )
                    for project in projects
                ]
            )
        except Exception as e:
            logger.error(f"Error fetching Jira projects: {str(e)}")
            
    return resources


@app.read_resource()
async def read_resource(uri: AnyUrl) -> str:
    """Read content from Confluence, Jira or Bitbucket."""
    uri_str = str(uri)

    # Handle Confluence resources
    if uri_str.startswith("confluence://"):
        if not services["confluence"]:
            raise ValueError("Confluence is not configured. Please provide Confluence credentials.")
        parts = uri_str.replace("confluence://", "").split("/")

        # Handle space listing
        if len(parts) == 1:
            space_key = parts[0]
            documents = confluence_fetcher.get_space_pages(space_key)
            content = []
            for doc in documents:
                content.append(f"# {doc.metadata['title']}\n\n{doc.page_content}\n---")
            return "\n\n".join(content)

        # Handle specific page
        elif len(parts) >= 3 and parts[1] == "pages":
            space_key = parts[0]
            title = parts[2]
            doc = confluence_fetcher.get_page_by_title(space_key, title)

            if not doc:
                raise ValueError(f"Page not found: {title}")

            return doc.page_content

    # Handle Jira resources
    elif uri_str.startswith("jira://"):
        if not services["jira"]:
            raise ValueError("Jira is not configured. Please provide Jira credentials.")
        parts = uri_str.replace("jira://", "").split("/")

        # Handle project listing
        if len(parts) == 1:
            project_key = parts[0]
            issues = jira_fetcher.get_project_issues(project_key)
            content = []
            for issue in issues:
                content.append(f"# {issue.metadata['key']}: {issue.metadata['title']}\n\n{issue.page_content}\n---")
            return "\n\n".join(content)

        # Handle specific issue
        elif len(parts) >= 3 and parts[1] == "issues":
            issue_key = parts[2]
            issue = jira_fetcher.get_issue(issue_key)
            return issue.page_content
            
    # Handle Bitbucket resources
    elif uri_str.startswith("bitbucket://"):
        if not services["bitbucket"]:
            raise ValueError("Bitbucket is not configured. Please provide Bitbucket credentials.")
        
        parts = uri_str.replace("bitbucket://", "").split("/")
        
        # Handle repository listing
        if len(parts) == 1:
            repo_slug = parts[0]
            
            # Get repo info
            repo_info = bitbucket_manager.get_repository(repo_slug)
            
            # Get branches
            branches = bitbucket_manager.list_branches(repo_slug)
            branch_list = "\n".join([
                f"- {branch['name']}" for branch in branches[:5]
            ])
            if len(branches) > 5:
                branch_list += f"\n- ... {len(branches) - 5} more branches"
                
            # Get open PRs
            prs = bitbucket_manager.list_pull_requests(repo_slug, state="OPEN")
            pr_list = "\n".join([
                f"- {pr['title']} (#{pr['id']})" for pr in prs[:5]
            ])
            if not pr_list:
                pr_list = "No open pull requests"
            elif len(prs) > 5:
                pr_list += f"\n- ... {len(prs) - 5} more pull requests"
                
            # Get latest commits
            commits = bitbucket_manager.list_commits(repo_slug)
            commit_list = "\n".join([
                f"- {commit['hash'][:7]} - {commit.get('message', '').split(chr(10))[0][:80]}" 
                for commit in commits[:5]
            ])
            if len(commits) > 5:
                commit_list += f"\n- ... more commits"
                
            content = f"""# Repository: {repo_info['name']}

{repo_info.get('description', '')}

## Repository Information
- Owner: {repo_info.get('workspace', {}).get('name', 'Unknown')}
- Created: {repo_info.get('created_on', 'Unknown')}
- Updated: {repo_info.get('updated_on', 'Unknown')}
- Size: {repo_info.get('size', 0)} bytes
- Is Private: {repo_info.get('is_private', False)}
- Main Branch: {repo_info.get('mainbranch', {}).get('name', 'master')}

## Branches
{branch_list}

## Open Pull Requests
{pr_list}

## Recent Commits
{commit_list}
"""
            return content
            
        # Handle specific branch
        elif len(parts) >= 3 and parts[1] == "branches":
            repo_slug = parts[0]
            branch_name = parts[2]
            
            # Get branch info
            branch = bitbucket_manager.get_branch(repo_slug, branch_name)
            
            # Get commits for this branch
            commits = bitbucket_manager.list_commits(repo_slug, branch=branch_name)
            commit_list = "\n".join([
                f"- {commit['hash'][:7]} - {commit.get('message', '').split(chr(10))[0]}" 
                for commit in commits[:10]
            ])
            
            content = f"""# Branch: {branch['name']}

## Branch Information
- Repository: {repo_slug}
- Target: {branch.get('target', {}).get('hash', 'Unknown')[:10]}
- Created by: {branch.get('target', {}).get('author', {}).get('raw', 'Unknown')}

## Recent Commits
{commit_list}
"""
            return content
            
        # Handle specific pull request
        elif len(parts) >= 3 and parts[1] == "pullrequests":
            repo_slug = parts[0]
            pr_id = int(parts[2])
            
            # Get PR info
            pr = bitbucket_manager.get_pull_request(repo_slug, pr_id)
            
            # Get PR comments
            comments = bitbucket_manager.list_pull_request_comments(repo_slug, pr_id)
            comment_list = "\n".join([
                f"- {comment.get('user', {}).get('display_name', 'Unknown')}: {comment.get('content', {}).get('raw', '')[:100]}" 
                for comment in comments[:5]
            ])
            if len(comments) > 5:
                comment_list += f"\n- ... {len(comments) - 5} more comments"
                
            content = f"""# Pull Request: {pr['title']}

## Pull Request Information
- ID: {pr['id']}
- Author: {pr.get('author', {}).get('display_name', 'Unknown')}
- State: {pr.get('state', 'Unknown')}
- Created: {pr.get('created_on', 'Unknown')}
- Updated: {pr.get('updated_on', 'Unknown')}
- Source: {pr.get('source', {}).get('branch', {}).get('name', 'Unknown')}
- Destination: {pr.get('destination', {}).get('branch', {}).get('name', 'Unknown')}

## Description
{pr.get('description', 'No description provided')}

## Recent Comments
{comment_list}
"""
            return content

    # Invalid resource URI
    raise ValueError(f"Invalid resource URI: {uri}")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available Confluence, Jira, JSM, Bitbucket, and enhanced Confluence tools."""
    tools = []
    
    # Add JSM tools if available
    if services.get("jsm", False):
        try:
            jsm_tools = get_jsm_tools()
            tools.extend(jsm_tools)
            logger.info(f"Added {len(jsm_tools)} JSM tools")
        except Exception as e:
            logger.error(f"Error adding JSM tools: {str(e)}")
        
    # Add enhanced Confluence tools if available
    if services.get("enhanced_confluence", False):
        try:
            enhanced_confluence_tools = get_enhanced_confluence_tools()
            tools.extend(enhanced_confluence_tools)
            logger.info(f"Added {len(enhanced_confluence_tools)} enhanced Confluence tools")
        except Exception as e:
            logger.error(f"Error adding enhanced Confluence tools: {str(e)}")
        
    # Add enterprise tools
    if services.get("enterprise", False):
        try:
            enterprise_tools = get_enterprise_tools()
            tools.extend(enterprise_tools)
            logger.info(f"Added {len(enterprise_tools)} enterprise tools")
        except Exception as e:
            logger.error(f"Error adding enterprise tools: {str(e)}")

    # Add Bitbucket tools if available
    if services.get("bitbucket", False) and bitbucket_manager and bitbucket_pipeline_manager and bitbucket_integration_manager:
        # Core Bitbucket repository management tools
        tools.extend([
            Tool(
                name="bitbucket_list_repositories",
                description="List all repositories in the workspace",
                inputSchema={
                    "type": "object",
                    "properties": {},
                    "required": [],
                },
            ),
            Tool(
                name="bitbucket_get_repository",
                description="Get details of a specific repository",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "repo_slug": {"type": "string", "description": "The repository slug"}
                    },
                    "required": ["repo_slug"],
                },
            ),
            Tool(
                name="bitbucket_create_repository",
                description="Create a new repository in the workspace",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "repo_slug": {"type": "string", "description": "The repository slug (URL-friendly name)"},
                        "repo_name": {"type": "string", "description": "The display name for the repository"},
                        "description": {"type": "string", "description": "Optional repository description", "default": ""},
                        "is_private": {"type": "boolean", "description": "Whether the repository is private", "default": True},
                        "fork_policy": {"type": "string", "description": "Fork policy", "default": "no_forks", "enum": ["no_forks", "no_public_forks", "allow_forks"]},
                        "has_wiki": {"type": "boolean", "description": "Whether to enable the wiki", "default": False},
                        "has_issues": {"type": "boolean", "description": "Whether to enable issue tracking", "default": False}
                    },
                    "required": ["repo_slug", "repo_name"],
                },
            ),
            Tool(
                name="bitbucket_update_repository",
                description="Update an existing repository",
                inputSchema={
                    "type": "object", 
                    "properties": {
                        "repo_slug": {"type": "string", "description": "The repository slug"},
                        "repo_name": {"type": "string", "description": "Optional new display name for the repository"},
                        "description": {"type": "string", "description": "Optional new repository description"},
                        "is_private": {"type": "boolean", "description": "Optional new privacy setting"},
                        "fork_policy": {"type": "string", "description": "Optional new fork policy", "enum": ["no_forks", "no_public_forks", "allow_forks"]},
                        "has_wiki": {"type": "boolean", "description": "Optional new wiki setting"},
                        "has_issues": {"type": "boolean", "description": "Optional new issue tracking setting"}
                    },
                    "required": ["repo_slug"],
                },
            ),
            Tool(
                name="bitbucket_delete_repository",
                description="Delete a repository",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "repo_slug": {"type": "string", "description": "The repository slug"}
                    },
                    "required": ["repo_slug"],
                },
            ),
            
            # Branch management tools
            Tool(
                name="bitbucket_list_branches",
                description="List all branches in a repository",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "repo_slug": {"type": "string", "description": "The repository slug"}
                    },
                    "required": ["repo_slug"],
                },
            ),
            Tool(
                name="bitbucket_get_branch",
                description="Get details of a specific branch",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "repo_slug": {"type": "string", "description": "The repository slug"},
                        "branch_name": {"type": "string", "description": "The branch name"}
                    },
                    "required": ["repo_slug", "branch_name"],
                },
            ),
            Tool(
                name="bitbucket_create_branch",
                description="Create a new branch in a repository",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "repo_slug": {"type": "string", "description": "The repository slug"},
                        "branch_name": {"type": "string", "description": "The name for the new branch"},
                        "target_hash": {"type": "string", "description": "The commit hash to branch from"}
                    },
                    "required": ["repo_slug", "branch_name", "target_hash"],
                },
            ),
            Tool(
                name="bitbucket_delete_branch",
                description="Delete a branch",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "repo_slug": {"type": "string", "description": "The repository slug"},
                        "branch_name": {"type": "string", "description": "The branch name"}
                    },
                    "required": ["repo_slug", "branch_name"],
                },
            ),
            
            # Commit management tools
            Tool(
                name="bitbucket_list_commits",
                description="List commits in a repository",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "repo_slug": {"type": "string", "description": "The repository slug"},
                        "branch": {"type": "string", "description": "Optional branch name to filter commits"}
                    },
                    "required": ["repo_slug"],
                },
            ),
            Tool(
                name="bitbucket_get_commit",
                description="Get details of a specific commit",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "repo_slug": {"type": "string", "description": "The repository slug"},
                        "commit_hash": {"type": "string", "description": "The commit hash"}
                    },
                    "required": ["repo_slug", "commit_hash"],
                },
            ),
            Tool(
                name="bitbucket_get_commit_diff",
                description="Get the diff for a specific commit",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "repo_slug": {"type": "string", "description": "The repository slug"},
                        "commit_hash": {"type": "string", "description": "The commit hash"}
                    },
                    "required": ["repo_slug", "commit_hash"],
                },
            ),
            
            # Pull request management tools
            Tool(
                name="bitbucket_list_pull_requests",
                description="List pull requests in a repository",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "repo_slug": {"type": "string", "description": "The repository slug"},
                        "state": {"type": "string", "description": "Filter by state", "default": "OPEN", "enum": ["OPEN", "MERGED", "DECLINED", "SUPERSEDED"]}
                    },
                    "required": ["repo_slug"],
                },
            ),
            Tool(
                name="bitbucket_get_pull_request",
                description="Get details of a specific pull request",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "repo_slug": {"type": "string", "description": "The repository slug"},
                        "pull_request_id": {"type": "number", "description": "The pull request ID"}
                    },
                    "required": ["repo_slug", "pull_request_id"],
                },
            ),
            Tool(
                name="bitbucket_create_pull_request",
                description="Create a new pull request",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "repo_slug": {"type": "string", "description": "The repository slug"},
                        "title": {"type": "string", "description": "The pull request title"},
                        "source_branch": {"type": "string", "description": "The source branch name"},
                        "destination_branch": {"type": "string", "description": "The destination branch name"},
                        "description": {"type": "string", "description": "Optional pull request description", "default": ""},
                        "close_source_branch": {"type": "boolean", "description": "Whether to close the source branch after merging", "default": False},
                        "reviewers": {"type": "array", "items": {"type": "string"}, "description": "Optional list of reviewer account IDs"}
                    },
                    "required": ["repo_slug", "title", "source_branch", "destination_branch"],
                },
            ),
            Tool(
                name="bitbucket_update_pull_request",
                description="Update an existing pull request",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "repo_slug": {"type": "string", "description": "The repository slug"},
                        "pull_request_id": {"type": "number", "description": "The pull request ID"},
                        "title": {"type": "string", "description": "Optional new title"},
                        "description": {"type": "string", "description": "Optional new description"},
                        "destination_branch": {"type": "string", "description": "Optional new destination branch"},
                        "reviewers": {"type": "array", "items": {"type": "string"}, "description": "Optional new list of reviewer account IDs"}
                    },
                    "required": ["repo_slug", "pull_request_id"],
                },
            ),
            Tool(
                name="bitbucket_merge_pull_request",
                description="Merge a pull request",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "repo_slug": {"type": "string", "description": "The repository slug"},
                        "pull_request_id": {"type": "number", "description": "The pull request ID"},
                        "merge_strategy": {"type": "string", "description": "The merge strategy", "default": "merge_commit", "enum": ["merge_commit", "squash", "fast_forward"]},
                        "message": {"type": "string", "description": "Optional custom merge commit message"},
                        "close_source_branch": {"type": "boolean", "description": "Whether to close the source branch after merging"}
                    },
                    "required": ["repo_slug", "pull_request_id"],
                },
            ),
            Tool(
                name="bitbucket_decline_pull_request",
                description="Decline a pull request",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "repo_slug": {"type": "string", "description": "The repository slug"},
                        "pull_request_id": {"type": "number", "description": "The pull request ID"},
                        "reason": {"type": "string", "description": "Optional reason for declining"}
                    },
                    "required": ["repo_slug", "pull_request_id"],
                },
            ),
            
            # Pull request comments and reviews
            Tool(
                name="bitbucket_list_pull_request_comments",
                description="List comments on a pull request",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "repo_slug": {"type": "string", "description": "The repository slug"},
                        "pull_request_id": {"type": "number", "description": "The pull request ID"}
                    },
                    "required": ["repo_slug", "pull_request_id"],
                },
            ),
            Tool(
                name="bitbucket_add_pull_request_comment",
                description="Add a comment to a pull request",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "repo_slug": {"type": "string", "description": "The repository slug"},
                        "pull_request_id": {"type": "number", "description": "The pull request ID"},
                        "content": {"type": "string", "description": "The comment content (supports Markdown)"},
                        "parent_id": {"type": "number", "description": "Optional parent comment ID (for replies)"}
                    },
                    "required": ["repo_slug", "pull_request_id", "content"],
                },
            ),
            Tool(
                name="bitbucket_approve_pull_request",
                description="Approve a pull request",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "repo_slug": {"type": "string", "description": "The repository slug"},
                        "pull_request_id": {"type": "number", "description": "The pull request ID"}
                    },
                    "required": ["repo_slug", "pull_request_id"],
                },
            ),
            Tool(
                name="bitbucket_unapprove_pull_request",
                description="Remove approval from a pull request",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "repo_slug": {"type": "string", "description": "The repository slug"},
                        "pull_request_id": {"type": "number", "description": "The pull request ID"}
                    },
                    "required": ["repo_slug", "pull_request_id"],
                },
            ),
            Tool(
                name="bitbucket_request_changes",
                description="Request changes on a pull request",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "repo_slug": {"type": "string", "description": "The repository slug"},
                        "pull_request_id": {"type": "number", "description": "The pull request ID"},
                        "content": {"type": "string", "description": "The review content"}
                    },
                    "required": ["repo_slug", "pull_request_id", "content"],
                },
            ),
        ])
        
        # Pipeline management tools
        tools.extend([
            Tool(
                name="bitbucket_get_pipeline_config",
                description="Get the Bitbucket Pipelines configuration for a repository",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "repo_slug": {"type": "string", "description": "The repository slug"}
                    },
                    "required": ["repo_slug"],
                },
            ),
            Tool(
                name="bitbucket_enable_pipelines",
                description="Enable Bitbucket Pipelines for a repository",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "repo_slug": {"type": "string", "description": "The repository slug"}
                    },
                    "required": ["repo_slug"],
                },
            ),
            Tool(
                name="bitbucket_disable_pipelines",
                description="Disable Bitbucket Pipelines for a repository",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "repo_slug": {"type": "string", "description": "The repository slug"}
                    },
                    "required": ["repo_slug"],
                },
            ),
            Tool(
                name="bitbucket_list_pipelines",
                description="List pipeline executions for a repository",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "repo_slug": {"type": "string", "description": "The repository slug"},
                        "sort_by": {"type": "string", "description": "Field to sort by (prefix with - for descending order)", "default": "-created_on"}
                    },
                    "required": ["repo_slug"],
                },
            ),
            Tool(
                name="bitbucket_get_pipeline",
                description="Get details of a specific pipeline execution",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "repo_slug": {"type": "string", "description": "The repository slug"},
                        "pipeline_uuid": {"type": "string", "description": "The pipeline execution UUID"}
                    },
                    "required": ["repo_slug", "pipeline_uuid"],
                },
            ),
            Tool(
                name="bitbucket_stop_pipeline",
                description="Stop a running pipeline execution",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "repo_slug": {"type": "string", "description": "The repository slug"},
                        "pipeline_uuid": {"type": "string", "description": "The pipeline execution UUID"}
                    },
                    "required": ["repo_slug", "pipeline_uuid"],
                },
            ),
            Tool(
                name="bitbucket_get_pipeline_steps",
                description="Get the steps of a pipeline execution",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "repo_slug": {"type": "string", "description": "The repository slug"},
                        "pipeline_uuid": {"type": "string", "description": "The pipeline execution UUID"}
                    },
                    "required": ["repo_slug", "pipeline_uuid"],
                },
            ),
            Tool(
                name="bitbucket_get_step_log",
                description="Get the log for a specific pipeline step",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "repo_slug": {"type": "string", "description": "The repository slug"},
                        "pipeline_uuid": {"type": "string", "description": "The pipeline execution UUID"},
                        "step_uuid": {"type": "string", "description": "The step UUID"}
                    },
                    "required": ["repo_slug", "pipeline_uuid", "step_uuid"],
                },
            ),
            Tool(
                name="bitbucket_run_pipeline",
                description="Run a pipeline on a specific branch",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "repo_slug": {"type": "string", "description": "The repository slug"},
                        "branch": {"type": "string", "description": "The branch to run the pipeline on"},
                        "pipeline": {"type": "string", "description": "Optional specific pipeline target name"},
                        "variables": {"type": "array", "items": {"type": "object"}, "description": "Optional list of pipeline variables"}
                    },
                    "required": ["repo_slug", "branch"],
                },
            ),
            
            # Pipeline variables
            Tool(
                name="bitbucket_list_variables",
                description="List pipeline variables for a repository",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "repo_slug": {"type": "string", "description": "The repository slug"}
                    },
                    "required": ["repo_slug"],
                },
            ),
            Tool(
                name="bitbucket_create_variable",
                description="Create a new pipeline variable",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "repo_slug": {"type": "string", "description": "The repository slug"},
                        "key": {"type": "string", "description": "The variable key"},
                        "value": {"type": "string", "description": "The variable value"},
                        "secured": {"type": "boolean", "description": "Whether the variable is secured (masked in logs)", "default": False}
                    },
                    "required": ["repo_slug", "key", "value"],
                },
            ),
            Tool(
                name="bitbucket_update_variable",
                description="Update an existing pipeline variable",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "repo_slug": {"type": "string", "description": "The repository slug"},
                        "variable_uuid": {"type": "string", "description": "The variable UUID"},
                        "key": {"type": "string", "description": "Optional new key"},
                        "value": {"type": "string", "description": "Optional new value"},
                        "secured": {"type": "boolean", "description": "Optional new secured status"}
                    },
                    "required": ["repo_slug", "variable_uuid"],
                },
            ),
            Tool(
                name="bitbucket_delete_variable",
                description="Delete a pipeline variable",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "repo_slug": {"type": "string", "description": "The repository slug"},
                        "variable_uuid": {"type": "string", "description": "The variable UUID"}
                    },
                    "required": ["repo_slug", "variable_uuid"],
                },
            ),
            
            # Deployment Management
            Tool(
                name="bitbucket_list_environments",
                description="List deployment environments for a repository",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "repo_slug": {"type": "string", "description": "The repository slug"}
                    },
                    "required": ["repo_slug"],
                },
            ),
            Tool(
                name="bitbucket_create_environment",
                description="Create a new deployment environment",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "repo_slug": {"type": "string", "description": "The repository slug"},
                        "name": {"type": "string", "description": "The environment name"},
                        "environment_type": {"type": "string", "description": "The environment type", "default": "Test", "enum": ["Test", "Staging", "Production"]},
                        "environment_lock": {"type": "boolean", "description": "Whether the environment is locked for deployments", "default": False}
                    },
                    "required": ["repo_slug", "name"],
                },
            ),
            Tool(
                name="bitbucket_update_environment",
                description="Update an existing deployment environment",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "repo_slug": {"type": "string", "description": "The repository slug"},
                        "environment_uuid": {"type": "string", "description": "The environment UUID"},
                        "name": {"type": "string", "description": "Optional new name"},
                        "environment_type": {"type": "string", "description": "Optional new environment type", "enum": ["Test", "Staging", "Production"]},
                        "environment_lock": {"type": "boolean", "description": "Optional new lock status"}
                    },
                    "required": ["repo_slug", "environment_uuid"],
                },
            ),
            Tool(
                name="bitbucket_delete_environment",
                description="Delete a deployment environment",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "repo_slug": {"type": "string", "description": "The repository slug"},
                        "environment_uuid": {"type": "string", "description": "The environment UUID"}
                    },
                    "required": ["repo_slug", "environment_uuid"],
                },
            ),
            Tool(
                name="bitbucket_list_deployments",
                description="List deployments for a repository",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "repo_slug": {"type": "string", "description": "The repository slug"},
                        "environment_uuid": {"type": "string", "description": "Optional environment UUID to filter deployments"}
                    },
                    "required": ["repo_slug"],
                },
            ),
        ])
        
        # Repository integrations
        tools.extend([
            # Webhook management
            Tool(
                name="bitbucket_list_webhooks",
                description="List webhooks for a repository",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "repo_slug": {"type": "string", "description": "The repository slug"}
                    },
                    "required": ["repo_slug"],
                },
            ),
            Tool(
                name="bitbucket_create_webhook",
                description="Create a new webhook",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "repo_slug": {"type": "string", "description": "The repository slug"},
                        "url": {"type": "string", "description": "The URL to send webhook events to"},
                        "description": {"type": "string", "description": "Optional webhook description", "default": ""},
                        "events": {"type": "array", "items": {"type": "string"}, "description": "Optional list of events to trigger the webhook"},
                        "active": {"type": "boolean", "description": "Whether the webhook is active", "default": True}
                    },
                    "required": ["repo_slug", "url"],
                },
            ),
            Tool(
                name="bitbucket_update_webhook",
                description="Update an existing webhook",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "repo_slug": {"type": "string", "description": "The repository slug"},
                        "webhook_uuid": {"type": "string", "description": "The webhook UUID"},
                        "url": {"type": "string", "description": "Optional new URL"},
                        "description": {"type": "string", "description": "Optional new description"},
                        "events": {"type": "array", "items": {"type": "string"}, "description": "Optional new list of events"},
                        "active": {"type": "boolean", "description": "Optional new active status"}
                    },
                    "required": ["repo_slug", "webhook_uuid"],
                },
            ),
            Tool(
                name="bitbucket_delete_webhook",
                description="Delete a webhook",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "repo_slug": {"type": "string", "description": "The repository slug"},
                        "webhook_uuid": {"type": "string", "description": "The webhook UUID"}
                    },
                    "required": ["repo_slug", "webhook_uuid"],
                },
            ),
            
            # Repository permissions management
            Tool(
                name="bitbucket_get_repository_permissions",
                description="Get permissions for a repository",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "repo_slug": {"type": "string", "description": "The repository slug"}
                    },
                    "required": ["repo_slug"],
                },
            ),
            Tool(
                name="bitbucket_grant_user_permission",
                description="Grant permission to a user for a repository",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "repo_slug": {"type": "string", "description": "The repository slug"},
                        "user_uuid": {"type": "string", "description": "The user UUID"},
                        "permission": {"type": "string", "description": "The permission to grant", "enum": ["admin", "write", "read"]}
                    },
                    "required": ["repo_slug", "user_uuid", "permission"],
                },
            ),
            Tool(
                name="bitbucket_revoke_user_permission",
                description="Revoke permission from a user for a repository",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "repo_slug": {"type": "string", "description": "The repository slug"},
                        "user_uuid": {"type": "string", "description": "The user UUID"}
                    },
                    "required": ["repo_slug", "user_uuid"],
                },
            ),
            
            # Branch restrictions (protection rules)
            Tool(
                name="bitbucket_list_branch_restrictions",
                description="List branch restrictions for a repository",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "repo_slug": {"type": "string", "description": "The repository slug"}
                    },
                    "required": ["repo_slug"],
                },
            ),
            Tool(
                name="bitbucket_create_branch_restriction",
                description="Create a new branch restriction",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "repo_slug": {"type": "string", "description": "The repository slug"},
                        "kind": {"type": "string", "description": "The restriction kind (push, delete, force, require_approvals_to_merge, etc.)"},
                        "pattern": {"type": "string", "description": "The branch pattern to restrict"},
                        "users": {"type": "array", "items": {"type": "string"}, "description": "Optional list of user UUIDs to exempt from the restriction"},
                        "groups": {"type": "array", "items": {"type": "string"}, "description": "Optional list of group UUIDs to exempt from the restriction"},
                        "value": {"type": "number", "description": "Optional additional value for the restriction (e.g., number of approvals)"}
                    },
                    "required": ["repo_slug", "kind", "pattern"],
                },
            ),
            Tool(
                name="bitbucket_delete_branch_restriction",
                description="Delete a branch restriction",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "repo_slug": {"type": "string", "description": "The repository slug"},
                        "restriction_id": {"type": "number", "description": "The branch restriction ID"}
                    },
                    "required": ["repo_slug", "restriction_id"],
                },
            ),
            
            # Repository insights and reports
            Tool(
                name="bitbucket_get_repository_commits_stats",
                description="Get commit statistics for a repository",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "repo_slug": {"type": "string", "description": "The repository slug"},
                        "include": {"type": "string", "description": "Optional branch or tag to include"}
                    },
                    "required": ["repo_slug"],
                },
            ),
            Tool(
                name="bitbucket_get_repository_activity",
                description="Get activity statistics for a repository",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "repo_slug": {"type": "string", "description": "The repository slug"}
                    },
                    "required": ["repo_slug"],
                },
            ),
            Tool(
                name="bitbucket_get_repository_contributors",
                description="Get contributor statistics for a repository",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "repo_slug": {"type": "string", "description": "The repository slug"}
                    },
                    "required": ["repo_slug"],
                },
            ),
        ])

    if confluence_fetcher:
        tools.extend(
            [
                Tool(
                    name="confluence_search",
                    description="Search Confluence content using CQL",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "CQL query string (e.g. 'type=page AND space=DEV')",
                            },
                            "limit": {
                                "type": "number",
                                "description": "Maximum number of results (1-50)",
                                "default": 10,
                                "minimum": 1,
                                "maximum": 50,
                            },
                        },
                        "required": ["query"],
                    },
                ),
                Tool(
                    name="confluence_get_page",
                    description="Get content of a specific Confluence page by ID",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "page_id": {"type": "string", "description": "Confluence page ID"},
                            "include_metadata": {
                                "type": "boolean",
                                "description": "Whether to include page metadata",
                                "default": True,
                            },
                        },
                        "required": ["page_id"],
                    },
                ),
                Tool(
                    name="confluence_get_comments",
                    description="Get comments for a specific Confluence page",
                    inputSchema={
                        "type": "object",
                        "properties": {"page_id": {"type": "string", "description": "Confluence page ID"}},
                        "required": ["page_id"],
                    },
                ),
                Tool(
                    name="confluence_create_page",
                    description="Create a new Confluence page with markdown content",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "space_key": {"type": "string", "description": "The space key where the page will be created"},
                            "title": {"type": "string", "description": "The title of the page"},
                            "content": {"type": "string", "description": "The content of the page in markdown format"},
                            "parent_id": {"type": "string", "description": "Optional parent page ID for hierarchical organization"},
                            "content_type": {
                                "type": "string", 
                                "description": "The type of content",
                                "default": "markdown",
                                "enum": ["markdown", "storage"]
                            }
                        },
                        "required": ["space_key", "title", "content"],
                    },
                ),
                Tool(
                    name="confluence_create_page_from_file",
                    description="Create a new Confluence page from a markdown file",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "space_key": {"type": "string", "description": "The space key where the page will be created"},
                            "title": {"type": "string", "description": "The title of the page"},
                            "file_path": {"type": "string", "description": "Path to the markdown file"},
                            "parent_id": {"type": "string", "description": "Optional parent page ID for hierarchical organization"}
                        },
                        "required": ["space_key", "title", "file_path"],
                    },
                ),
                Tool(
                    name="confluence_attach_file",
                    description="Attach a file to a Confluence page",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "page_id": {"type": "string", "description": "The ID of the page to attach the file to"},
                            "file_path": {"type": "string", "description": "Path to the file to attach"},
                            "comment": {"type": "string", "description": "Optional comment for the attachment"}
                        },
                        "required": ["page_id", "file_path"],
                    },
                ),
                Tool(
                    name="confluence_get_page_history",
                    description="Get the version history of a Confluence page",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "page_id": {"type": "string", "description": "The ID of the page to get the history for"},
                            "limit": {"type": "number", "description": "Maximum number of versions to return", "default": 10}
                        },
                        "required": ["page_id"],
                    },
                ),
                Tool(
                    name="confluence_restore_page_version",
                    description="Restore a Confluence page to a previous version",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "page_id": {"type": "string", "description": "The ID of the page to restore"},
                            "version_number": {"type": "number", "description": "The version number to restore to"}
                        },
                        "required": ["page_id", "version_number"],
                    },
                ),
                Tool(
                    name="confluence_update_page",
                    description="Update an existing Confluence page",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "page_id": {"type": "string", "description": "The ID of the page to update"},
                            "title": {"type": "string", "description": "Optional new title for the page"},
                            "content": {"type": "string", "description": "Optional new content for the page"},
                            "content_type": {
                                "type": "string", 
                                "description": "The type of content",
                                "default": "markdown",
                                "enum": ["markdown", "storage"]
                            },
                            "message": {"type": "string", "description": "Optional message for the update"}
                        },
                        "required": ["page_id"],
                    },
                ),
                Tool(
                    name="confluence_move_page",
                    description="Move a Confluence page to a different parent or space",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "page_id": {"type": "string", "description": "The ID of the page to move"},
                            "target_parent_id": {"type": "string", "description": "Optional ID of the new parent page"},
                            "target_space_key": {"type": "string", "description": "Optional key of the new space"},
                            "position": {"type": "number", "description": "Optional position among siblings (0-based index)"}
                        },
                        "required": ["page_id"],
                    },
                ),
                Tool(
                    name="confluence_get_page_tree",
                    description="Get a hierarchical tree of pages in a space",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "space_key": {"type": "string", "description": "The space key"},
                            "root_page_id": {"type": "string", "description": "Optional ID of the root page (if not provided, gets the space root)"},
                            "depth": {"type": "number", "description": "Maximum depth of the tree (1-5)", "default": 3, "minimum": 1, "maximum": 5},
                            "expand": {"type": "string", "description": "Optional fields to expand"}
                        },
                        "required": ["space_key"],
                    },
                ),
            ]
        )

    if jira_fetcher:
        tools.extend(
            [
                Tool(
                    name="jira_get_issue",
                    description="Get details of a specific Jira issue",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "issue_key": {"type": "string", "description": "Jira issue key (e.g., 'PROJ-123')"},
                            "expand": {"type": "string", "description": "Optional fields to expand", "default": None},
                        },
                        "required": ["issue_key"],
                    },
                ),
                Tool(
                    name="jira_search",
                    description="Search Jira issues using JQL",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "jql": {"type": "string", "description": "JQL query string"},
                            "fields": {
                                "type": "string",
                                "description": "Comma-separated fields to return",
                                "default": "*all",
                            },
                            "limit": {
                                "type": "number",
                                "description": "Maximum number of results (1-50)",
                                "default": 10,
                                "minimum": 1,
                                "maximum": 50,
                            },
                        },
                        "required": ["jql"],
                    },
                ),
                Tool(
                    name="jira_get_project_issues",
                    description="Get all issues for a specific Jira project",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "project_key": {"type": "string", "description": "The project key"},
                            "limit": {
                                "type": "number",
                                "description": "Maximum number of results (1-50)",
                                "default": 10,
                                "minimum": 1,
                                "maximum": 50,
                            },
                        },
                        "required": ["project_key"],
                    },
                ),
                Tool(
                    name="jira_create_project",
                    description="Create a new Jira project",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "key": {"type": "string", "description": "The project key (must be uppercase, e.g., 'MOXY')"},
                            "name": {"type": "string", "description": "The project name"},
                            "project_type": {
                                "type": "string",
                                "description": "The project type",
                                "default": "software",
                                "enum": ["software", "business", "service_desk"],
                            },
                            "template": {
                                "type": "string",
                                "description": "The project template",
                                "default": "com.pyxis.greenhopper.jira:basic-software-development-template",
                            },
                        },
                        "required": ["key", "name"],
                    },
                ),
                Tool(
                    name="jira_create_issue",
                    description="Create a new Jira issue or subtask",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "project_key": {"type": "string", "description": "The project key (e.g., 'MOXY')"},
                            "summary": {"type": "string", "description": "The issue summary/title"},
                            "issue_type": {
                                "type": "string",
                                "description": "The issue type",
                                "default": "Task",
                                "enum": ["Task", "Bug", "Story", "Subtask"],
                            },
                            "description": {
                                "type": "string",
                                "description": "The issue description",
                                "default": "",
                            },
                            "labels": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "List of labels to apply to the issue",
                            },
                            "priority": {
                                "type": "string",
                                "description": "The issue priority",
                                "default": "Medium",
                                "enum": ["Highest", "High", "Medium", "Low", "Lowest"],
                            },
                            "parent_key": {
                                "type": "string",
                                "description": "The parent issue key (for subtasks)",
                            },
                            "epic_link": {
                                "type": "string",
                                "description": "The Epic issue key to link this issue to (for Stories)",
                            },
                            "name": {
                                "type": "string",
                                "description": "REQUIRED: The name value for the custom field",
                            },
                            "dept": {
                                "type": "string",
                                "description": "REQUIRED: The department value for the custom field",
                            },
                        },
                        "required": ["project_key", "summary", "name", "dept"],
                    },
                ),
                Tool(
                    name="jira_get_issue_link_types",
                    description="Get all available issue link types",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                        "required": [],
                    },
                ),
                Tool(
                    name="jira_create_issue_link",
                    description="Create a link between two Jira issues",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "link_type": {
                                "type": "string",
                                "description": "The type of link (e.g., 'Relates', 'Blocks', 'is blocked by')",
                                "default": "Relates"
                            },
                            "outward_issue": {
                                "type": "string",
                                "description": "The issue key that is the source of the link"
                            },
                            "inward_issue": {
                                "type": "string",
                                "description": "The issue key that is the target of the link"
                            }
                        },
                        "required": ["outward_issue", "inward_issue"],
                    },
                ),
                Tool(
                    name="jira_update_issue",
                    description="Update an existing Jira issue",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "issue_key": {
                                "type": "string",
                                "description": "The issue key to update (e.g., 'PROJ-123')"
                            },
                            "summary": {
                                "type": "string",
                                "description": "Optional new summary/title"
                            },
                            "description": {
                                "type": "string",
                                "description": "Optional new description"
                            },
                            "issue_type": {
                                "type": "string",
                                "description": "Optional new issue type"
                            },
                            "priority": {
                                "type": "string",
                                "description": "Optional new priority",
                                "enum": ["Highest", "High", "Medium", "Low", "Lowest"]
                            },
                            "fields": {
                                "type": "object",
                                "description": "Optional dictionary of additional fields to update"
                            },
                            "name": {
                                "type": "string",
                                "description": "Optional name value for the custom field"
                            },
                            "dept": {
                                "type": "string",
                                "description": "Optional department value for the custom field"
                            }
                        },
                        "required": ["issue_key"],
                    },
                ),
                Tool(
                    name="jira_transition_issue",
                    description="Transition an issue to a different status",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "issue_key": {
                                "type": "string",
                                "description": "The issue key to transition (e.g., 'PROJ-123')"
                            },
                            "transition_name": {
                                "type": "string",
                                "description": "The name of the transition to perform (e.g., 'In Progress', 'Done')"
                            }
                        },
                        "required": ["issue_key", "transition_name"],
                    },
                ),
                Tool(
                    name="jira_add_comment",
                    description="Add a comment to an issue",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "issue_key": {
                                "type": "string",
                                "description": "The issue key to comment on (e.g., 'PROJ-123')"
                            },
                            "comment": {
                                "type": "string",
                                "description": "The comment text"
                            }
                        },
                        "required": ["issue_key", "comment"],
                    },
                ),
                Tool(
                    name="jira_create_epic",
                    description="Create a new Epic in Jira",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "project_key": {
                                "type": "string",
                                "description": "The project key (e.g., 'MOXY')"
                            },
                            "summary": {
                                "type": "string",
                                "description": "The Epic summary/title"
                            },
                            "description": {
                                "type": "string",
                                "description": "The Epic description",
                                "default": ""
                            },
                            "priority": {
                                "type": "string",
                                "description": "The Epic priority",
                                "default": "Medium",
                                "enum": ["Highest", "High", "Medium", "Low", "Lowest"]
                            },
                            "epic_name": {
                                "type": "string",
                                "description": "Optional short name for the Epic (displayed on the Epic card)"
                            },
                            "epic_color": {
                                "type": "string",
                                "description": "Optional color for the Epic (e.g., 'ghx-label-1', 'ghx-label-2', etc.)"
                            },
                            "name": {
                                "type": "string",
                                "description": "REQUIRED: The name value for the custom field"
                            },
                            "dept": {
                                "type": "string",
                                "description": "REQUIRED: The department value for the custom field"
                            }
                        },
                        "required": ["project_key", "summary", "name", "dept"],
                    },
                ),
                Tool(
                    name="jira_get_epic_issues",
                    description="Get all issues linked to an Epic in a structured format",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "epic_key": {
                                "type": "string",
                                "description": "The Epic issue key (e.g., 'PROJ-123')"
                            },
                            "include_subtasks": {
                                "type": "boolean",
                                "description": "Whether to include subtasks of issues linked to the Epic",
                                "default": True
                            }
                        },
                        "required": ["epic_key"],
                    },
                ),
                Tool(
                    name="jira_update_epic_progress",
                    description="Update Epic progress tracking based on linked issues",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "epic_key": {
                                "type": "string",
                                "description": "The Epic issue key (e.g., 'PROJ-123')"
                            }
                        },
                        "required": ["epic_key"],
                    },
                ),
                Tool(
                    name="jira_get_issue_attachments",
                    description="Get all attachments for an issue",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "issue_key": {
                                "type": "string",
                                "description": "The issue key (e.g., 'PROJ-123')"
                            }
                        },
                        "required": ["issue_key"],
                    },
                ),
                Tool(
                    name="jira_attach_file_to_issue",
                    description="Attach a file to a Jira issue",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "issue_key": {
                                "type": "string",
                                "description": "The issue key (e.g., 'PROJ-123')"
                            },
                            "file_path": {
                                "type": "string",
                                "description": "Path to the file to attach"
                            },
                            "comment": {
                                "type": "string",
                                "description": "Optional comment for the attachment"
                            }
                        },
                        "required": ["issue_key", "file_path"],
                    },
                ),
                Tool(
                    name="jira_get_issue_transitions",
                    description="Get available transitions for an issue",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "issue_key": {
                                "type": "string",
                                "description": "The issue key (e.g., 'PROJ-123')"
                            }
                        },
                        "required": ["issue_key"],
                    },
                ),
                # New tool for managing custom fields globally
                Tool(
                    name="jira_set_custom_fields_global",
                    description="Configure Name and Dept custom fields to be available in all projects",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                        "required": [],
                    },
                ),
                # New tool for getting a list of all custom fields
                Tool(
                    name="jira_get_custom_fields",
                    description="Get a list of all custom fields in the Jira instance",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                        "required": [],
                    },
                ),
            ]
        )

    return tools


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> Sequence[TextContent]:
    """Handle tool calls for Confluence, enhanced Confluence, Jira, Bitbucket, and JSM operations."""
    try:
        # Handle JSM tools
        if name.startswith("jsm_"):
            if not services.get("jsm", False):
                raise ValueError("JSM is not configured. Please provide JSM credentials.")
            result = handle_jsm_tool_call(name, arguments)
            if isinstance(result, list) and all(isinstance(item, TextContent) for item in result):
                return result
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
        # Handle enhanced Confluence tools
        if (name.startswith("confluence_space_") or 
            name.startswith("confluence_templates_") or 
            name.startswith("confluence_content_")):
            if not services.get("enhanced_confluence", False):
                raise ValueError("Enhanced Confluence features are not configured properly.")
            result = handle_enhanced_confluence_tool_call(name, arguments, space_manager, template_manager, content_manager)
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
        # Handle enterprise tools
        if any(name.startswith(prefix) for prefix in ["atlassian_", "analytics_", "ai_", "app_"]):
            if not services.get("enterprise", False):
                raise ValueError("Enterprise features are not configured properly.")
            result = handle_enterprise_tool_call(name, arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
        # Handle Bitbucket core management tools
        if name.startswith("bitbucket_") and services.get("bitbucket", False):
            result = None
            
            # Repository management tools
            if name == "bitbucket_list_repositories":
                result = bitbucket_manager.list_repositories()
            elif name == "bitbucket_get_repository":
                result = bitbucket_manager.get_repository(arguments["repo_slug"])
            elif name == "bitbucket_create_repository":
                result = bitbucket_manager.create_repository(
                    repo_slug=arguments["repo_slug"],
                    repo_name=arguments["repo_name"],
                    description=arguments.get("description", ""),
                    is_private=arguments.get("is_private", True),
                    fork_policy=arguments.get("fork_policy", "no_forks"),
                    has_wiki=arguments.get("has_wiki", False),
                    has_issues=arguments.get("has_issues", False)
                )
            elif name == "bitbucket_update_repository":
                result = bitbucket_manager.update_repository(
                    repo_slug=arguments["repo_slug"],
                    repo_name=arguments.get("repo_name"),
                    description=arguments.get("description"),
                    is_private=arguments.get("is_private"),
                    fork_policy=arguments.get("fork_policy"),
                    has_wiki=arguments.get("has_wiki"),
                    has_issues=arguments.get("has_issues")
                )
            elif name == "bitbucket_delete_repository":
                result = bitbucket_manager.delete_repository(arguments["repo_slug"])
                
            # Branch management tools
            elif name == "bitbucket_list_branches":
                result = bitbucket_manager.list_branches(arguments["repo_slug"])
            elif name == "bitbucket_get_branch":
                result = bitbucket_manager.get_branch(arguments["repo_slug"], arguments["branch_name"])
            elif name == "bitbucket_create_branch":
                result = bitbucket_manager.create_branch(
                    repo_slug=arguments["repo_slug"],
                    branch_name=arguments["branch_name"],
                    target_hash=arguments["target_hash"]
                )
            elif name == "bitbucket_delete_branch":
                result = bitbucket_manager.delete_branch(arguments["repo_slug"], arguments["branch_name"])
                
            # Commit management tools
            elif name == "bitbucket_list_commits":
                result = bitbucket_manager.list_commits(arguments["repo_slug"], branch=arguments.get("branch"))
            elif name == "bitbucket_get_commit":
                result = bitbucket_manager.get_commit(arguments["repo_slug"], arguments["commit_hash"])
            elif name == "bitbucket_get_commit_diff":
                diff = bitbucket_manager.get_commit_diff(arguments["repo_slug"], arguments["commit_hash"])
                result = {"diff": diff}
                
            # Pull request management tools
            elif name == "bitbucket_list_pull_requests":
                result = bitbucket_manager.list_pull_requests(arguments["repo_slug"], state=arguments.get("state", "OPEN"))
            elif name == "bitbucket_get_pull_request":
                result = bitbucket_manager.get_pull_request(arguments["repo_slug"], arguments["pull_request_id"])
            elif name == "bitbucket_create_pull_request":
                result = bitbucket_manager.create_pull_request(
                    repo_slug=arguments["repo_slug"],
                    title=arguments["title"],
                    source_branch=arguments["source_branch"],
                    destination_branch=arguments["destination_branch"],
                    description=arguments.get("description", ""),
                    close_source_branch=arguments.get("close_source_branch", False),
                    reviewers=arguments.get("reviewers")
                )
            elif name == "bitbucket_update_pull_request":
                result = bitbucket_manager.update_pull_request(
                    repo_slug=arguments["repo_slug"],
                    pull_request_id=arguments["pull_request_id"],
                    title=arguments.get("title"),
                    description=arguments.get("description"),
                    destination_branch=arguments.get("destination_branch"),
                    reviewers=arguments.get("reviewers")
                )
            elif name == "bitbucket_merge_pull_request":
                result = bitbucket_manager.merge_pull_request(
                    repo_slug=arguments["repo_slug"],
                    pull_request_id=arguments["pull_request_id"],
                    merge_strategy=arguments.get("merge_strategy", "merge_commit"),
                    message=arguments.get("message"),
                    close_source_branch=arguments.get("close_source_branch")
                )
            elif name == "bitbucket_decline_pull_request":
                result = bitbucket_manager.decline_pull_request(
                    repo_slug=arguments["repo_slug"],
                    pull_request_id=arguments["pull_request_id"],
                    reason=arguments.get("reason")
                )
                
            # Pull request comments and reviews
            elif name == "bitbucket_list_pull_request_comments":
                result = bitbucket_manager.list_pull_request_comments(arguments["repo_slug"], arguments["pull_request_id"])
            elif name == "bitbucket_add_pull_request_comment":
                result = bitbucket_manager.add_pull_request_comment(
                    repo_slug=arguments["repo_slug"],
                    pull_request_id=arguments["pull_request_id"],
                    content=arguments["content"],
                    parent_id=arguments.get("parent_id")
                )
            elif name == "bitbucket_approve_pull_request":
                result = bitbucket_manager.approve_pull_request(arguments["repo_slug"], arguments["pull_request_id"])
            elif name == "bitbucket_unapprove_pull_request":
                result = bitbucket_manager.unapprove_pull_request(arguments["repo_slug"], arguments["pull_request_id"])
            elif name == "bitbucket_request_changes":
                result = bitbucket_manager.request_changes(
                    repo_slug=arguments["repo_slug"],
                    pull_request_id=arguments["pull_request_id"],
                    content=arguments["content"]
                )
                
            # Pipeline management tools
            elif name == "bitbucket_get_pipeline_config":
                result = bitbucket_pipeline_manager.get_pipeline_config(arguments["repo_slug"])
            elif name == "bitbucket_enable_pipelines":
                result = bitbucket_pipeline_manager.enable_pipelines(arguments["repo_slug"])
            elif name == "bitbucket_disable_pipelines":
                result = bitbucket_pipeline_manager.disable_pipelines(arguments["repo_slug"])
            elif name == "bitbucket_list_pipelines":
                result = bitbucket_pipeline_manager.list_pipelines(
                    repo_slug=arguments["repo_slug"],
                    sort_by=arguments.get("sort_by", "-created_on")
                )
            elif name == "bitbucket_get_pipeline":
                result = bitbucket_pipeline_manager.get_pipeline(arguments["repo_slug"], arguments["pipeline_uuid"])
            elif name == "bitbucket_stop_pipeline":
                result = bitbucket_pipeline_manager.stop_pipeline(arguments["repo_slug"], arguments["pipeline_uuid"])
            elif name == "bitbucket_get_pipeline_steps":
                result = bitbucket_pipeline_manager.get_pipeline_steps(arguments["repo_slug"], arguments["pipeline_uuid"])
            elif name == "bitbucket_get_step_log":
                log = bitbucket_pipeline_manager.get_step_log(
                    repo_slug=arguments["repo_slug"],
                    pipeline_uuid=arguments["pipeline_uuid"],
                    step_uuid=arguments["step_uuid"]
                )
                result = {"log": log}
            elif name == "bitbucket_run_pipeline":
                result = bitbucket_pipeline_manager.run_pipeline(
                    repo_slug=arguments["repo_slug"],
                    branch=arguments["branch"],
                    pipeline=arguments.get("pipeline"),
                    variables=arguments.get("variables")
                )
                
            # Pipeline variables
            elif name == "bitbucket_list_variables":
                result = bitbucket_pipeline_manager.list_variables(arguments["repo_slug"])
            elif name == "bitbucket_create_variable":
                result = bitbucket_pipeline_manager.create_variable(
                    repo_slug=arguments["repo_slug"],
                    key=arguments["key"],
                    value=arguments["value"],
                    secured=arguments.get("secured", False)
                )
            elif name == "bitbucket_update_variable":
                result = bitbucket_pipeline_manager.update_variable(
                    repo_slug=arguments["repo_slug"],
                    variable_uuid=arguments["variable_uuid"],
                    key=arguments.get("key"),
                    value=arguments.get("value"),
                    secured=arguments.get("secured")
                )
            elif name == "bitbucket_delete_variable":
                result = bitbucket_pipeline_manager.delete_variable(arguments["repo_slug"], arguments["variable_uuid"])
                
            # Deployment Management
            elif name == "bitbucket_list_environments":
                result = bitbucket_pipeline_manager.list_environments(arguments["repo_slug"])
            elif name == "bitbucket_create_environment":
                result = bitbucket_pipeline_manager.create_environment(
                    repo_slug=arguments["repo_slug"],
                    name=arguments["name"],
                    environment_type=arguments.get("environment_type", "Test"),
                    environment_lock=arguments.get("environment_lock", False)
                )
            elif name == "bitbucket_update_environment":
                result = bitbucket_pipeline_manager.update_environment(
                    repo_slug=arguments["repo_slug"],
                    environment_uuid=arguments["environment_uuid"],
                    name=arguments.get("name"),
                    environment_type=arguments.get("environment_type"),
                    environment_lock=arguments.get("environment_lock")
                )
            elif name == "bitbucket_delete_environment":
                result = bitbucket_pipeline_manager.delete_environment(arguments["repo_slug"], arguments["environment_uuid"])
            elif name == "bitbucket_list_deployments":
                result = bitbucket_pipeline_manager.list_deployments(
                    repo_slug=arguments["repo_slug"],
                    environment_uuid=arguments.get("environment_uuid")
                )
                
            # Webhook management
            elif name == "bitbucket_list_webhooks":
                result = bitbucket_integration_manager.list_webhooks(arguments["repo_slug"])
            elif name == "bitbucket_create_webhook":
                result = bitbucket_integration_manager.create_webhook(
                    repo_slug=arguments["repo_slug"],
                    url=arguments["url"],
                    description=arguments.get("description", ""),
                    events=arguments.get("events"),
                    active=arguments.get("active", True)
                )
            elif name == "bitbucket_update_webhook":
                result = bitbucket_integration_manager.update_webhook(
                    repo_slug=arguments["repo_slug"],
                    webhook_uuid=arguments["webhook_uuid"],
                    url=arguments.get("url"),
                    description=arguments.get("description"),
                    events=arguments.get("events"),
                    active=arguments.get("active")
                )
            elif name == "bitbucket_delete_webhook":
                result = bitbucket_integration_manager.delete_webhook(arguments["repo_slug"], arguments["webhook_uuid"])
                
            # Repository permissions management
            elif name == "bitbucket_get_repository_permissions":
                result = bitbucket_integration_manager.get_repository_permissions(arguments["repo_slug"])
            elif name == "bitbucket_grant_user_permission":
                result = bitbucket_integration_manager.grant_user_permission(
                    repo_slug=arguments["repo_slug"],
                    user_uuid=arguments["user_uuid"],
                    permission=arguments["permission"]
                )
            elif name == "bitbucket_revoke_user_permission":
                result = bitbucket_integration_manager.revoke_user_permission(arguments["repo_slug"], arguments["user_uuid"])
                
            # Branch restrictions (protection rules)
            elif name == "bitbucket_list_branch_restrictions":
                result = bitbucket_integration_manager.list_branch_restrictions(arguments["repo_slug"])
            elif name == "bitbucket_create_branch_restriction":
                result = bitbucket_integration_manager.create_branch_restriction(
                    repo_slug=arguments["repo_slug"],
                    kind=arguments["kind"],
                    pattern=arguments["pattern"],
                    users=arguments.get("users"),
                    groups=arguments.get("groups"),
                    value=arguments.get("value")
                )
            elif name == "bitbucket_delete_branch_restriction":
                result = bitbucket_integration_manager.delete_branch_restriction(arguments["repo_slug"], arguments["restriction_id"])
                
            # Repository insights and reports
            elif name == "bitbucket_get_repository_commits_stats":
                result = bitbucket_integration_manager.get_repository_commits_stats(
                    repo_slug=arguments["repo_slug"],
                    include=arguments.get("include")
                )
            elif name == "bitbucket_get_repository_activity":
                result = bitbucket_integration_manager.get_repository_activity(arguments["repo_slug"])
            elif name == "bitbucket_get_repository_contributors":
                result = bitbucket_integration_manager.get_repository_contributors(arguments["repo_slug"])
                
            if result is not None:
                return [TextContent(type="text", text=json.dumps(result, indent=2))]
            else:
                raise ValueError(f"Unknown Bitbucket tool: {name}")
                
            
        if name == "confluence_search":
            limit = min(int(arguments.get("limit", 10)), 50)
            documents = confluence_fetcher.search(arguments["query"], limit)
            search_results = [
                {
                    "page_id": doc.metadata["page_id"],
                    "title": doc.metadata["title"],
                    "space": doc.metadata["space"],
                    "url": doc.metadata["url"],
                    "last_modified": doc.metadata["last_modified"],
                    "type": doc.metadata["type"],
                    "excerpt": doc.page_content,
                }
                for doc in documents
            ]

            return [TextContent(type="text", text=json.dumps(search_results, indent=2))]

        elif name == "confluence_get_page":
            doc = confluence_fetcher.get_page_content(arguments["page_id"])
            include_metadata = arguments.get("include_metadata", True)

            if include_metadata:
                result = {"content": doc.page_content, "metadata": doc.metadata}
            else:
                result = {"content": doc.page_content}

            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "confluence_get_comments":
            comments = confluence_fetcher.get_page_comments(arguments["page_id"])
            formatted_comments = [
                {
                    "author": comment.metadata["author_name"],
                    "created": comment.metadata["last_modified"],
                    "content": comment.page_content,
                }
                for comment in comments
            ]

            return [TextContent(type="text", text=json.dumps(formatted_comments, indent=2))]
            
        elif name == "confluence_create_page":
            space_key = arguments["space_key"]
            title = arguments["title"]
            content = arguments["content"]
            parent_id = arguments.get("parent_id")
            content_type = arguments.get("content_type", "markdown")
            
            result = confluence_fetcher.create_page(
                space_key=space_key,
                title=title,
                content=content,
                parent_id=parent_id,
                content_type=content_type
            )
            
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
        elif name == "confluence_create_page_from_file":
            space_key = arguments["space_key"]
            title = arguments["title"]
            file_path = arguments["file_path"]
            parent_id = arguments.get("parent_id")
            
            result = confluence_fetcher.create_page_from_file(
                space_key=space_key,
                title=title,
                file_path=file_path,
                parent_id=parent_id
            )
            
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
        elif name == "confluence_attach_file":
            page_id = arguments["page_id"]
            file_path = arguments["file_path"]
            comment = arguments.get("comment")
            
            result = confluence_fetcher.attach_file(
                page_id=page_id,
                file_path=file_path,
                comment=comment
            )
            
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
        elif name == "confluence_get_page_history":
            page_id = arguments["page_id"]
            limit = min(int(arguments.get("limit", 10)), 50)
            
            result = confluence_fetcher.get_page_history(
                page_id=page_id,
                limit=limit
            )
            
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
        elif name == "confluence_restore_page_version":
            page_id = arguments["page_id"]
            version_number = int(arguments["version_number"])
            
            result = confluence_fetcher.restore_page_version(
                page_id=page_id,
                version_number=version_number
            )
            
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "jira_get_issue":
            doc = jira_fetcher.get_issue(arguments["issue_key"], expand=arguments.get("expand"))
            result = {"content": doc.page_content, "metadata": doc.metadata}
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "jira_search":
            limit = min(int(arguments.get("limit", 10)), 50)
            documents = jira_fetcher.search_issues(
                arguments["jql"], fields=arguments.get("fields", "*all"), limit=limit
            )
            search_results = [
                {
                    "key": doc.metadata["key"],
                    "title": doc.metadata["title"],
                    "type": doc.metadata["type"],
                    "status": doc.metadata["status"],
                    "created_date": doc.metadata["created_date"],
                    "priority": doc.metadata["priority"],
                    "link": doc.metadata["link"],
                    "excerpt": doc.page_content[:500] + "..." if len(doc.page_content) > 500 else doc.page_content,
                }
                for doc in documents
            ]
            return [TextContent(type="text", text=json.dumps(search_results, indent=2))]

        elif name == "jira_get_project_issues":
            limit = min(int(arguments.get("limit", 10)), 50)
            documents = jira_fetcher.get_project_issues(arguments["project_key"], limit=limit)
            project_issues = [
                {
                    "key": doc.metadata["key"],
                    "title": doc.metadata["title"],
                    "type": doc.metadata["type"],
                    "status": doc.metadata["status"],
                    "created_date": doc.metadata["created_date"],
                    "link": doc.metadata["link"],
                }
                for doc in documents
            ]
            return [TextContent(type="text", text=json.dumps(project_issues, indent=2))]
            
        elif name == "jira_create_project":
            key = arguments["key"]
            name = arguments["name"]
            project_type = arguments.get("project_type", "software")
            template = arguments.get("template", "com.pyxis.greenhopper.jira:basic-software-development-template")
            
            response = jira_fetcher.create_project(key, name, project_type, template)
            
            result = {
                "success": True,
                "message": f"Project {key} created successfully",
                "project": {
                    "key": key,
                    "name": name,
                    "project_type": project_type,
                    "template": template,
                    "url": f"{jira_fetcher.config.url.rstrip('/')}/projects/{key}"
                }
            }
            
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
        elif name == "jira_create_issue":
            project_key = arguments["project_key"]
            summary = arguments["summary"]
            issue_type = arguments.get("issue_type", "Task")
            description = arguments.get("description", "")
            labels = arguments.get("labels", [])
            priority = arguments.get("priority", "Medium")
            parent_key = arguments.get("parent_key")
            name = arguments["name"]
            dept = arguments["dept"]
            
            epic_link = arguments.get("epic_link")
            
            result = jira_fetcher.create_issue(
                project_key=project_key,
                summary=summary,
                issue_type=issue_type,
                description=description,
                labels=labels,
                priority=priority,
                parent_key=parent_key,
                epic_link=epic_link,
                name=name,
                dept=dept
            )
            
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
        elif name == "jira_get_issue_link_types":
            link_types = jira_fetcher.get_issue_link_types()
            
            result = {
                "link_types": link_types
            }
            
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
        elif name == "jira_create_issue_link":
            link_type = arguments.get("link_type", "Relates")
            outward_issue = arguments["outward_issue"]
            inward_issue = arguments["inward_issue"]
            
            jira_fetcher.create_issue_link(
                link_type=link_type,
                outward_issue=outward_issue,
                inward_issue=inward_issue
            )
            
            result = {
                "success": True,
                "message": f"Created link between {outward_issue} and {inward_issue}",
                "link_type": link_type,
                "outward_issue": outward_issue,
                "inward_issue": inward_issue
            }
            
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
        elif name == "jira_update_issue":
            issue_key = arguments["issue_key"]
            summary = arguments.get("summary")
            description = arguments.get("description")
            issue_type = arguments.get("issue_type")
            priority = arguments.get("priority")
            name = arguments.get("name")
            dept = arguments.get("dept")
            
            # Add custom fields to update if provided
            fields = arguments.get("fields", {})
            if name is not None:
                fields[jira_fetcher.NAME_FIELD_ID] = [name]
            if dept is not None:
                fields[jira_fetcher.DEPT_FIELD_ID] = [dept]
            
            result = jira_fetcher.update_issue(
                issue_key=issue_key,
                summary=summary,
                description=description,
                issue_type=issue_type,
                priority=priority,
                fields=fields
            )
            
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
        elif name == "jira_transition_issue":
            issue_key = arguments["issue_key"]
            transition_name = arguments["transition_name"]
            
            result = jira_fetcher.transition_issue(
                issue_key=issue_key,
                transition_name=transition_name
            )
            
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
        elif name == "jira_add_comment":
            issue_key = arguments["issue_key"]
            comment = arguments["comment"]
            
            result = jira_fetcher.add_comment(
                issue_key=issue_key,
                comment=comment
            )
            
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
        elif name == "jira_create_epic":
            project_key = arguments["project_key"]
            summary = arguments["summary"]
            description = arguments.get("description", "")
            priority = arguments.get("priority", "Medium")
            epic_name = arguments.get("epic_name")
            epic_color = arguments.get("epic_color")
            name = arguments["name"]
            dept = arguments["dept"]
            
            result = jira_fetcher.create_epic(
                project_key=project_key,
                summary=summary,
                description=description,
                priority=priority,
                epic_name=epic_name,
                epic_color=epic_color,
                name=name,
                dept=dept
            )
            
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
        elif name == "jira_get_epic_issues":
            epic_key = arguments["epic_key"]
            include_subtasks = arguments.get("include_subtasks", True)
            
            result = jira_fetcher.get_epic_issues(
                epic_key=epic_key,
                include_subtasks=include_subtasks
            )
            
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
        elif name == "jira_update_epic_progress":
            epic_key = arguments["epic_key"]
            
            result = jira_fetcher.update_epic_progress(
                epic_key=epic_key
            )
            
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
        elif name == "jira_get_issue_attachments":
            issue_key = arguments["issue_key"]
            
            result = jira_fetcher.get_issue_attachments(
                issue_key=issue_key
            )
            
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
        elif name == "jira_attach_file_to_issue":
            issue_key = arguments["issue_key"]
            file_path = arguments["file_path"]
            comment = arguments.get("comment")
            
            result = jira_fetcher.attach_file_to_issue(
                issue_key=issue_key,
                file_path=file_path,
                comment=comment
            )
            
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
        elif name == "jira_get_issue_transitions":
            issue_key = arguments["issue_key"]
            
            result = jira_fetcher.get_issue_transitions(
                issue_key=issue_key
            )
            
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
        elif name == "confluence_update_page":
            page_id = arguments["page_id"]
            title = arguments.get("title")
            content = arguments.get("content")
            content_type = arguments.get("content_type", "markdown")
            message = arguments.get("message")
            
            result = confluence_fetcher.update_page(
                page_id=page_id,
                title=title,
                content=content,
                content_type=content_type,
                message=message
            )
            
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
        elif name == "confluence_move_page":
            page_id = arguments["page_id"]
            target_parent_id = arguments.get("target_parent_id")
            target_space_key = arguments.get("target_space_key")
            position = arguments.get("position")
            
            result = confluence_fetcher.move_page(
                page_id=page_id,
                target_parent_id=target_parent_id,
                target_space_key=target_space_key,
                position=position
            )
            
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
        elif name == "confluence_get_page_tree":
            space_key = arguments["space_key"]
            root_page_id = arguments.get("root_page_id")
            depth = arguments.get("depth", 3)
            expand = arguments.get("expand")
            
            result = confluence_fetcher.get_page_tree(
                space_key=space_key,
                root_page_id=root_page_id,
                depth=depth,
                expand=expand
            )
            
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
        # New tools for custom field management
        elif name == "jira_set_custom_fields_global":
            result = jira_fetcher.set_custom_fields_as_global()
            
            # Format a friendly response
            message = "Successfully configured Name and Dept custom fields to be available globally in all projects."
            result["message"] = message
            
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
        elif name == "jira_get_custom_fields":
            custom_fields = jira_fetcher.get_custom_fields()
            
            # Format a more friendly response focusing on the Name and Dept fields
            name_field = next((field for field in custom_fields if field.get("id") == jira_fetcher.NAME_FIELD_ID), None)
            dept_field = next((field for field in custom_fields if field.get("id") == jira_fetcher.DEPT_FIELD_ID), None)
            
            result = {
                "name_field": name_field,
                "dept_field": dept_field,
                "all_custom_fields": custom_fields
            }
            
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        raise ValueError(f"Unknown tool: {name}")

    except Exception as e:
        logger.error(f"Tool execution error: {str(e)}")
        raise RuntimeError(f"Tool execution failed: {str(e)}")


async def main():
    # Import here to avoid issues with event loops
    from mcp.server.stdio import stdio_server

    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())