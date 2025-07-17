import logging
import os
from typing import Dict, List, Optional, Union, Any, Tuple
import json
import time
from datetime import datetime

import requests
from dotenv import load_dotenv

from .config import BitbucketConfig
from .document_types import Document

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger("mcp-bitbucket-integration")


class BitbucketIntegrationManager:
    """Handles repository integrations, permissions, protection rules, and analytics for Bitbucket."""

    def __init__(self, workspace: Optional[str] = None, username: Optional[str] = None, app_password: Optional[str] = None):
        url = os.getenv("BITBUCKET_URL", "https://api.bitbucket.org/2.0")
        workspace = workspace or os.getenv("BITBUCKET_WORKSPACE")
        username = username or os.getenv("BITBUCKET_USERNAME")
        app_password = app_password or os.getenv("BITBUCKET_APP_PASSWORD")

        if not all([url, workspace, username, app_password]):
            raise ValueError("Missing required Bitbucket environment variables")

        self.config = BitbucketConfig(
            url=url, 
            workspace=workspace, 
            username=username, 
            app_password=app_password
        )
        
        self.auth = (self.config.username, self.config.app_password)
        self.headers = {"Content-Type": "application/json"}
        
    def _make_api_request(self, method: str, endpoint: str, data: Optional[Dict] = None, params: Optional[Dict] = None) -> Dict:
        """
        Make a direct request to the Bitbucket REST API.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint path (without base URL)
            data: Optional payload for POST/PUT requests
            params: Optional query parameters
            
        Returns:
            Dictionary containing the API response
        """
        # Ensure endpoint starts with / and doesn't include base URL
        if not endpoint.startswith("/"):
            endpoint = f"/{endpoint}"
            
        api_url = f"{self.config.url.rstrip('/')}{endpoint}"
        
        try:
            if method.upper() == "GET":
                response = requests.get(api_url, auth=self.auth, headers=self.headers, params=params)
            elif method.upper() == "POST":
                response = requests.post(api_url, json=data, auth=self.auth, headers=self.headers, params=params)
            elif method.upper() == "PUT":
                response = requests.put(api_url, json=data, auth=self.auth, headers=self.headers, params=params)
            elif method.upper() == "DELETE":
                response = requests.delete(api_url, auth=self.auth, headers=self.headers, params=params)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
                
            if response.status_code >= 400:
                error_msg = f"API request failed: {response.status_code} - {response.text}"
                logger.error(error_msg)
                raise ValueError(error_msg)
                
            # Return JSON response or empty dict for 204 No Content
            return response.json() if response.content else {}
            
        except Exception as e:
            logger.error(f"Error making API request to {endpoint}: {str(e)}")
            raise

    def _paginate_results(self, endpoint: str, params: Optional[Dict] = None) -> List[Dict]:
        """
        Paginate through all results from a Bitbucket API endpoint.
        
        Args:
            endpoint: The API endpoint to call
            params: Optional query parameters
            
        Returns:
            List of all objects from all pages
        """
        if params is None:
            params = {}
            
        results = []
        has_next = True
        url = endpoint
        
        while has_next:
            response = self._make_api_request("GET", url, params=params)
            
            # Add the values from this page to our results
            if "values" in response:
                results.extend(response["values"])
                
            # Check if there's a next page
            if "next" in response:
                # Extract the path from the full URL
                url_parts = response["next"].split(self.config.url)
                if len(url_parts) > 1:
                    url = url_parts[1]
                    # Clear the params since they're already in the URL
                    params = {}
                else:
                    has_next = False
            else:
                has_next = False
                
        return results
        
    # Webhook Management
    def list_webhooks(self, repo_slug: str) -> List[Dict]:
        """
        List webhooks for a repository.
        
        Args:
            repo_slug: The repository slug
            
        Returns:
            List of webhook objects
        """
        endpoint = f"/repositories/{self.config.workspace}/{repo_slug}/hooks"
        return self._paginate_results(endpoint)
        
    def get_webhook(self, repo_slug: str, webhook_uuid: str) -> Dict:
        """
        Get details of a specific webhook.
        
        Args:
            repo_slug: The repository slug
            webhook_uuid: The webhook UUID
            
        Returns:
            Webhook details
        """
        endpoint = f"/repositories/{self.config.workspace}/{repo_slug}/hooks/{webhook_uuid}"
        return self._make_api_request("GET", endpoint)
        
    def create_webhook(self, repo_slug: str, url: str, description: str = "", 
                      events: List[str] = None, active: bool = True) -> Dict:
        """
        Create a new webhook.
        
        Args:
            repo_slug: The repository slug
            url: The URL to send webhook events to
            description: Optional webhook description
            events: Optional list of events to trigger the webhook
            active: Whether the webhook is active
            
        Returns:
            Webhook details
        """
        endpoint = f"/repositories/{self.config.workspace}/{repo_slug}/hooks"
        
        # Default events if none provided
        if events is None:
            events = ["repo:push", "pullrequest:created", "pullrequest:updated", "pullrequest:fulfilled"]
            
        data = {
            "url": url,
            "description": description,
            "events": events,
            "active": active
        }
        
        return self._make_api_request("POST", endpoint, data=data)
        
    def update_webhook(self, repo_slug: str, webhook_uuid: str, url: Optional[str] = None,
                      description: Optional[str] = None, events: Optional[List[str]] = None, 
                      active: Optional[bool] = None) -> Dict:
        """
        Update an existing webhook.
        
        Args:
            repo_slug: The repository slug
            webhook_uuid: The webhook UUID
            url: Optional new URL
            description: Optional new description
            events: Optional new list of events
            active: Optional new active status
            
        Returns:
            Updated webhook details
        """
        endpoint = f"/repositories/{self.config.workspace}/{repo_slug}/hooks/{webhook_uuid}"
        
        # Get current webhook details
        webhook = self.get_webhook(repo_slug, webhook_uuid)
        
        # Create update data with only the fields that are provided
        data = {}
        if url is not None:
            data["url"] = url
        if description is not None:
            data["description"] = description
        if events is not None:
            data["events"] = events
        if active is not None:
            data["active"] = active
            
        return self._make_api_request("PUT", endpoint, data=data)
        
    def delete_webhook(self, repo_slug: str, webhook_uuid: str) -> Dict:
        """
        Delete a webhook.
        
        Args:
            repo_slug: The repository slug
            webhook_uuid: The webhook UUID
            
        Returns:
            Empty dict on success
        """
        endpoint = f"/repositories/{self.config.workspace}/{repo_slug}/hooks/{webhook_uuid}"
        return self._make_api_request("DELETE", endpoint)
        
    # Repository Permissions Management
    def get_repository_permissions(self, repo_slug: str) -> List[Dict]:
        """
        Get permissions for a repository.
        
        Args:
            repo_slug: The repository slug
            
        Returns:
            List of permission objects
        """
        endpoint = f"/repositories/{self.config.workspace}/{repo_slug}/permissions"
        return self._paginate_results(endpoint)
        
    def get_user_permission(self, repo_slug: str, user_uuid: str) -> Dict:
        """
        Get permission for a specific user.
        
        Args:
            repo_slug: The repository slug
            user_uuid: The user UUID
            
        Returns:
            User permission details
        """
        endpoint = f"/repositories/{self.config.workspace}/{repo_slug}/permissions/users/{user_uuid}"
        return self._make_api_request("GET", endpoint)
        
    def grant_user_permission(self, repo_slug: str, user_uuid: str, permission: str) -> Dict:
        """
        Grant permission to a user for a repository.
        
        Args:
            repo_slug: The repository slug
            user_uuid: The user UUID
            permission: The permission to grant (admin, write, read)
            
        Returns:
            User permission details
        """
        endpoint = f"/repositories/{self.config.workspace}/{repo_slug}/permissions/users/{user_uuid}"
        data = {"permission": permission}
        return self._make_api_request("PUT", endpoint, data=data)
        
    def revoke_user_permission(self, repo_slug: str, user_uuid: str) -> Dict:
        """
        Revoke permission from a user for a repository.
        
        Args:
            repo_slug: The repository slug
            user_uuid: The user UUID
            
        Returns:
            Empty dict on success
        """
        endpoint = f"/repositories/{self.config.workspace}/{repo_slug}/permissions/users/{user_uuid}"
        return self._make_api_request("DELETE", endpoint)
        
    def list_group_permissions(self, repo_slug: str) -> List[Dict]:
        """
        List group permissions for a repository.
        
        Args:
            repo_slug: The repository slug
            
        Returns:
            List of group permission objects
        """
        endpoint = f"/repositories/{self.config.workspace}/{repo_slug}/permissions/groups"
        return self._paginate_results(endpoint)
        
    def grant_group_permission(self, repo_slug: str, group_slug: str, permission: str) -> Dict:
        """
        Grant permission to a group for a repository.
        
        Args:
            repo_slug: The repository slug
            group_slug: The group slug
            permission: The permission to grant (admin, write, read)
            
        Returns:
            Group permission details
        """
        endpoint = f"/repositories/{self.config.workspace}/{repo_slug}/permissions/groups/{group_slug}"
        data = {"permission": permission}
        return self._make_api_request("PUT", endpoint, data=data)
        
    def revoke_group_permission(self, repo_slug: str, group_slug: str) -> Dict:
        """
        Revoke permission from a group for a repository.
        
        Args:
            repo_slug: The repository slug
            group_slug: The group slug
            
        Returns:
            Empty dict on success
        """
        endpoint = f"/repositories/{self.config.workspace}/{repo_slug}/permissions/groups/{group_slug}"
        return self._make_api_request("DELETE", endpoint)
        
    # Branch Restrictions (Protection Rules)
    def list_branch_restrictions(self, repo_slug: str) -> List[Dict]:
        """
        List branch restrictions for a repository.
        
        Args:
            repo_slug: The repository slug
            
        Returns:
            List of branch restriction objects
        """
        endpoint = f"/repositories/{self.config.workspace}/{repo_slug}/branch-restrictions"
        return self._paginate_results(endpoint)
        
    def get_branch_restriction(self, repo_slug: str, restriction_id: int) -> Dict:
        """
        Get details of a specific branch restriction.
        
        Args:
            repo_slug: The repository slug
            restriction_id: The branch restriction ID
            
        Returns:
            Branch restriction details
        """
        endpoint = f"/repositories/{self.config.workspace}/{repo_slug}/branch-restrictions/{restriction_id}"
        return self._make_api_request("GET", endpoint)
        
    def create_branch_restriction(self, repo_slug: str, kind: str, pattern: str, 
                                users: Optional[List[str]] = None, groups: Optional[List[str]] = None,
                                value: Optional[int] = None) -> Dict:
        """
        Create a new branch restriction.
        
        Args:
            repo_slug: The repository slug
            kind: The restriction kind (push, delete, force, require_approvals_to_merge, etc.)
            pattern: The branch pattern to restrict
            users: Optional list of user UUIDs to exempt from the restriction
            groups: Optional list of group UUIDs to exempt from the restriction
            value: Optional additional value for the restriction (e.g., number of approvals)
            
        Returns:
            Branch restriction details
        """
        endpoint = f"/repositories/{self.config.workspace}/{repo_slug}/branch-restrictions"
        
        data = {
            "kind": kind,
            "pattern": pattern
        }
        
        if users:
            data["users"] = [{"uuid": uuid} for uuid in users]
            
        if groups:
            data["groups"] = [{"uuid": uuid} for uuid in groups]
            
        if value is not None:
            data["value"] = value
            
        return self._make_api_request("POST", endpoint, data=data)
        
    def update_branch_restriction(self, repo_slug: str, restriction_id: int, 
                                pattern: Optional[str] = None, users: Optional[List[str]] = None,
                                groups: Optional[List[str]] = None, value: Optional[int] = None) -> Dict:
        """
        Update an existing branch restriction.
        
        Args:
            repo_slug: The repository slug
            restriction_id: The branch restriction ID
            pattern: Optional new branch pattern
            users: Optional new list of user UUIDs to exempt
            groups: Optional new list of group UUIDs to exempt
            value: Optional new value for the restriction
            
        Returns:
            Updated branch restriction details
        """
        endpoint = f"/repositories/{self.config.workspace}/{repo_slug}/branch-restrictions/{restriction_id}"
        
        # Get current restriction details
        restriction = self.get_branch_restriction(repo_slug, restriction_id)
        
        # Create update data with only the fields that are provided
        data = {
            "kind": restriction["kind"]  # Kind cannot be changed
        }
        
        if pattern is not None:
            data["pattern"] = pattern
            
        if users is not None:
            data["users"] = [{"uuid": uuid} for uuid in users]
            
        if groups is not None:
            data["groups"] = [{"uuid": uuid} for uuid in groups]
            
        if value is not None:
            data["value"] = value
            
        return self._make_api_request("PUT", endpoint, data=data)
        
    def delete_branch_restriction(self, repo_slug: str, restriction_id: int) -> Dict:
        """
        Delete a branch restriction.
        
        Args:
            repo_slug: The repository slug
            restriction_id: The branch restriction ID
            
        Returns:
            Empty dict on success
        """
        endpoint = f"/repositories/{self.config.workspace}/{repo_slug}/branch-restrictions/{restriction_id}"
        return self._make_api_request("DELETE", endpoint)
        
    # Repository Default Reviewers
    def list_default_reviewers(self, repo_slug: str) -> List[Dict]:
        """
        List default reviewers for a repository.
        
        Args:
            repo_slug: The repository slug
            
        Returns:
            List of default reviewer objects
        """
        endpoint = f"/repositories/{self.config.workspace}/{repo_slug}/default-reviewers"
        return self._paginate_results(endpoint)
        
    def add_default_reviewer(self, repo_slug: str, user_uuid: str) -> Dict:
        """
        Add a default reviewer to a repository.
        
        Args:
            repo_slug: The repository slug
            user_uuid: The user UUID
            
        Returns:
            Default reviewer details
        """
        endpoint = f"/repositories/{self.config.workspace}/{repo_slug}/default-reviewers/{user_uuid}"
        return self._make_api_request("PUT", endpoint)
        
    def remove_default_reviewer(self, repo_slug: str, user_uuid: str) -> Dict:
        """
        Remove a default reviewer from a repository.
        
        Args:
            repo_slug: The repository slug
            user_uuid: The user UUID
            
        Returns:
            Empty dict on success
        """
        endpoint = f"/repositories/{self.config.workspace}/{repo_slug}/default-reviewers/{user_uuid}"
        return self._make_api_request("DELETE", endpoint)
        
    # Repository Insights and Reports
    def get_repository_commits_stats(self, repo_slug: str, include: str = None) -> Dict:
        """
        Get commit statistics for a repository.
        
        Args:
            repo_slug: The repository slug
            include: Optional branch or tag to include
            
        Returns:
            Commit statistics
        """
        endpoint = f"/repositories/{self.config.workspace}/{repo_slug}/commits"
        params = {}
        if include:
            params["include"] = include
            
        # Make initial request to get total count
        response = self._make_api_request("GET", endpoint, params=params)
        
        # Calculate statistics
        total_commits = 0
        if "pagelen" in response and "size" in response:
            total_commits = response["size"]
            
        # Get authors statistics
        authors = {}
        for commit in response.get("values", []):
            author = commit.get("author", {}).get("raw", "Unknown")
            if author in authors:
                authors[author] += 1
            else:
                authors[author] = 1
                
        # Format the result
        return {
            "total_commits": total_commits,
            "authors": [{"name": author, "commits": count} for author, count in authors.items()],
            "repo_slug": repo_slug
        }
        
    def get_repository_activity(self, repo_slug: str) -> Dict:
        """
        Get activity statistics for a repository.
        
        Args:
            repo_slug: The repository slug
            
        Returns:
            Activity statistics
        """
        # Get pull requests
        pr_endpoint = f"/repositories/{self.config.workspace}/{repo_slug}/pullrequests"
        pr_response = self._make_api_request("GET", pr_endpoint)
        
        # Get branches
        branch_endpoint = f"/repositories/{self.config.workspace}/{repo_slug}/refs/branches"
        branch_response = self._make_api_request("GET", branch_endpoint)
        
        # Calculate statistics
        total_prs = pr_response.get("size", 0)
        open_prs = 0
        for pr in pr_response.get("values", []):
            if pr.get("state") == "OPEN":
                open_prs += 1
                
        # Format the result
        return {
            "total_pull_requests": total_prs,
            "open_pull_requests": open_prs,
            "total_branches": branch_response.get("size", 0),
            "repo_slug": repo_slug
        }
        
    def get_repository_contributors(self, repo_slug: str) -> List[Dict]:
        """
        Get contributor statistics for a repository.
        
        Args:
            repo_slug: The repository slug
            
        Returns:
            List of contributor statistics
        """
        # This requires a bit more complex analysis
        commits = self._paginate_results(f"/repositories/{self.config.workspace}/{repo_slug}/commits")
        
        # Analyze the commits to track contributors
        contributors = {}
        for commit in commits:
            author = commit.get("author", {})
            raw_author = author.get("raw", "Unknown")
            
            # Try to get a proper name
            user = author.get("user", {})
            display_name = user.get("display_name", raw_author)
            
            # Track contributions
            if display_name in contributors:
                contributors[display_name]["commits"] += 1
            else:
                avatar = user.get("links", {}).get("avatar", {}).get("href", "")
                contributors[display_name] = {
                    "name": display_name,
                    "commits": 1,
                    "avatar": avatar,
                    "username": user.get("username", "")
                }
                
        # Convert to list and sort by commit count
        contributor_list = list(contributors.values())
        contributor_list.sort(key=lambda x: x["commits"], reverse=True)
        
        return contributor_list