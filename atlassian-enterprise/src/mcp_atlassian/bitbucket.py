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
logger = logging.getLogger("mcp-bitbucket")


class BitbucketManager:
    """Handles operations for Bitbucket repositories and resources."""

    def __init__(self):
        url = os.getenv("BITBUCKET_URL", "https://api.bitbucket.org/2.0")
        workspace = os.getenv("BITBUCKET_WORKSPACE")
        username = os.getenv("BITBUCKET_USERNAME")
        app_password = os.getenv("BITBUCKET_APP_PASSWORD")

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

    # Repository Management
    def list_repositories(self) -> List[Dict]:
        """
        List all repositories in the workspace.
        
        Returns:
            List of repository objects
        """
        endpoint = f"/repositories/{self.config.workspace}"
        return self._paginate_results(endpoint)
        
    def get_repository(self, repo_slug: str) -> Dict:
        """
        Get details of a specific repository.
        
        Args:
            repo_slug: The repository slug
            
        Returns:
            Repository details
        """
        endpoint = f"/repositories/{self.config.workspace}/{repo_slug}"
        return self._make_api_request("GET", endpoint)
        
    def create_repository(self, repo_slug: str, repo_name: str, description: str = "", 
                         is_private: bool = True, fork_policy: str = "no_forks", 
                         has_wiki: bool = False, has_issues: bool = False) -> Dict:
        """
        Create a new repository in the workspace.
        
        Args:
            repo_slug: The repository slug (URL-friendly name)
            repo_name: The display name for the repository
            description: Optional repository description
            is_private: Whether the repository is private
            fork_policy: Fork policy (no_forks, no_public_forks, allow_forks)
            has_wiki: Whether to enable the wiki
            has_issues: Whether to enable issue tracking
            
        Returns:
            Repository details
        """
        endpoint = f"/repositories/{self.config.workspace}/{repo_slug}"
        data = {
            "scm": "git",
            "name": repo_name,
            "description": description,
            "is_private": is_private,
            "fork_policy": fork_policy,
            "has_wiki": has_wiki,
            "has_issues": has_issues
        }
        
        return self._make_api_request("POST", endpoint, data=data)
        
    def update_repository(self, repo_slug: str, repo_name: Optional[str] = None, 
                         description: Optional[str] = None, is_private: Optional[bool] = None,
                         fork_policy: Optional[str] = None, has_wiki: Optional[bool] = None, 
                         has_issues: Optional[bool] = None) -> Dict:
        """
        Update an existing repository.
        
        Args:
            repo_slug: The repository slug
            repo_name: Optional new display name for the repository
            description: Optional new repository description
            is_private: Optional new privacy setting
            fork_policy: Optional new fork policy
            has_wiki: Optional new wiki setting
            has_issues: Optional new issue tracking setting
            
        Returns:
            Updated repository details
        """
        endpoint = f"/repositories/{self.config.workspace}/{repo_slug}"
        
        # Get current repository details
        current_repo = self.get_repository(repo_slug)
        
        # Create update data with only the fields that are provided
        data = {}
        if repo_name is not None:
            data["name"] = repo_name
        if description is not None:
            data["description"] = description
        if is_private is not None:
            data["is_private"] = is_private
        if fork_policy is not None:
            data["fork_policy"] = fork_policy
        if has_wiki is not None:
            data["has_wiki"] = has_wiki
        if has_issues is not None:
            data["has_issues"] = has_issues
            
        return self._make_api_request("PUT", endpoint, data=data)
        
    def delete_repository(self, repo_slug: str) -> Dict:
        """
        Delete a repository.
        
        Args:
            repo_slug: The repository slug
            
        Returns:
            Empty dict on success
        """
        endpoint = f"/repositories/{self.config.workspace}/{repo_slug}"
        return self._make_api_request("DELETE", endpoint)
        
    # Branch Management
    def list_branches(self, repo_slug: str) -> List[Dict]:
        """
        List all branches in a repository.
        
        Args:
            repo_slug: The repository slug
            
        Returns:
            List of branch objects
        """
        endpoint = f"/repositories/{self.config.workspace}/{repo_slug}/refs/branches"
        return self._paginate_results(endpoint)
        
    def get_branch(self, repo_slug: str, branch_name: str) -> Dict:
        """
        Get details of a specific branch.
        
        Args:
            repo_slug: The repository slug
            branch_name: The branch name
            
        Returns:
            Branch details
        """
        endpoint = f"/repositories/{self.config.workspace}/{repo_slug}/refs/branches/{branch_name}"
        return self._make_api_request("GET", endpoint)
        
    def create_branch(self, repo_slug: str, branch_name: str, target_hash: str) -> Dict:
        """
        Create a new branch in a repository.
        
        Args:
            repo_slug: The repository slug
            branch_name: The name for the new branch
            target_hash: The commit hash to branch from
            
        Returns:
            Branch details
        """
        endpoint = f"/repositories/{self.config.workspace}/{repo_slug}/refs/branches"
        data = {
            "name": branch_name,
            "target": {
                "hash": target_hash
            }
        }
        
        return self._make_api_request("POST", endpoint, data=data)
        
    def delete_branch(self, repo_slug: str, branch_name: str) -> Dict:
        """
        Delete a branch.
        
        Args:
            repo_slug: The repository slug
            branch_name: The branch name
            
        Returns:
            Empty dict on success
        """
        endpoint = f"/repositories/{self.config.workspace}/{repo_slug}/refs/branches/{branch_name}"
        return self._make_api_request("DELETE", endpoint)
        
    # Commit Management
    def list_commits(self, repo_slug: str, branch: Optional[str] = None) -> List[Dict]:
        """
        List commits in a repository.
        
        Args:
            repo_slug: The repository slug
            branch: Optional branch name to filter commits
            
        Returns:
            List of commit objects
        """
        endpoint = f"/repositories/{self.config.workspace}/{repo_slug}/commits"
        params = {}
        if branch:
            params["include"] = branch
            
        return self._paginate_results(endpoint, params=params)
        
    def get_commit(self, repo_slug: str, commit_hash: str) -> Dict:
        """
        Get details of a specific commit.
        
        Args:
            repo_slug: The repository slug
            commit_hash: The commit hash
            
        Returns:
            Commit details
        """
        endpoint = f"/repositories/{self.config.workspace}/{repo_slug}/commit/{commit_hash}"
        return self._make_api_request("GET", endpoint)
        
    def get_commit_diff(self, repo_slug: str, commit_hash: str) -> str:
        """
        Get the diff for a specific commit.
        
        Args:
            repo_slug: The repository slug
            commit_hash: The commit hash
            
        Returns:
            Commit diff as a string
        """
        endpoint = f"/repositories/{self.config.workspace}/{repo_slug}/diff/{commit_hash}"
        
        # Use requests directly to get the raw diff content
        api_url = f"{self.config.url.rstrip('/')}{endpoint}"
        response = requests.get(api_url, auth=self.auth)
        
        if response.status_code >= 400:
            error_msg = f"API request failed: {response.status_code} - {response.text}"
            logger.error(error_msg)
            raise ValueError(error_msg)
            
        return response.text
        
    # Pull Request Management
    def list_pull_requests(self, repo_slug: str, state: str = "OPEN") -> List[Dict]:
        """
        List pull requests in a repository.
        
        Args:
            repo_slug: The repository slug
            state: Filter by state (OPEN, MERGED, DECLINED, SUPERSEDED)
            
        Returns:
            List of pull request objects
        """
        endpoint = f"/repositories/{self.config.workspace}/{repo_slug}/pullrequests"
        params = {"state": state}
        
        return self._paginate_results(endpoint, params=params)
        
    def get_pull_request(self, repo_slug: str, pull_request_id: int) -> Dict:
        """
        Get details of a specific pull request.
        
        Args:
            repo_slug: The repository slug
            pull_request_id: The pull request ID
            
        Returns:
            Pull request details
        """
        endpoint = f"/repositories/{self.config.workspace}/{repo_slug}/pullrequests/{pull_request_id}"
        return self._make_api_request("GET", endpoint)
        
    def create_pull_request(self, repo_slug: str, title: str, source_branch: str, 
                           destination_branch: str, description: str = "",
                           close_source_branch: bool = False, reviewers: List[str] = None) -> Dict:
        """
        Create a new pull request.
        
        Args:
            repo_slug: The repository slug
            title: The pull request title
            source_branch: The source branch name
            destination_branch: The destination branch name
            description: Optional pull request description
            close_source_branch: Whether to close the source branch after merging
            reviewers: Optional list of reviewer account IDs
            
        Returns:
            Pull request details
        """
        endpoint = f"/repositories/{self.config.workspace}/{repo_slug}/pullrequests"
        
        data = {
            "title": title,
            "description": description,
            "source": {
                "branch": {
                    "name": source_branch
                }
            },
            "destination": {
                "branch": {
                    "name": destination_branch
                }
            },
            "close_source_branch": close_source_branch
        }
        
        # Add reviewers if provided
        if reviewers:
            data["reviewers"] = [{"uuid": reviewer_id} for reviewer_id in reviewers]
            
        return self._make_api_request("POST", endpoint, data=data)
        
    def update_pull_request(self, repo_slug: str, pull_request_id: int, title: Optional[str] = None,
                           description: Optional[str] = None, destination_branch: Optional[str] = None,
                           reviewers: Optional[List[str]] = None) -> Dict:
        """
        Update an existing pull request.
        
        Args:
            repo_slug: The repository slug
            pull_request_id: The pull request ID
            title: Optional new title
            description: Optional new description
            destination_branch: Optional new destination branch
            reviewers: Optional new list of reviewer account IDs
            
        Returns:
            Updated pull request details
        """
        endpoint = f"/repositories/{self.config.workspace}/{repo_slug}/pullrequests/{pull_request_id}"
        
        # Get current pull request details
        current_pr = self.get_pull_request(repo_slug, pull_request_id)
        
        # Create update data with only the fields that are provided
        data = {}
        if title is not None:
            data["title"] = title
        if description is not None:
            data["description"] = description
            
        # Update destination branch if provided
        if destination_branch is not None:
            data["destination"] = {
                "branch": {
                    "name": destination_branch
                }
            }
            
        # Update reviewers if provided
        if reviewers is not None:
            data["reviewers"] = [{"uuid": reviewer_id} for reviewer_id in reviewers]
            
        return self._make_api_request("PUT", endpoint, data=data)
        
    def merge_pull_request(self, repo_slug: str, pull_request_id: int, 
                          merge_strategy: str = "merge_commit", message: Optional[str] = None,
                          close_source_branch: Optional[bool] = None) -> Dict:
        """
        Merge a pull request.
        
        Args:
            repo_slug: The repository slug
            pull_request_id: The pull request ID
            merge_strategy: The merge strategy (merge_commit, squash, fast_forward)
            message: Optional custom merge commit message
            close_source_branch: Whether to close the source branch after merging
            
        Returns:
            Merged pull request details
        """
        endpoint = f"/repositories/{self.config.workspace}/{repo_slug}/pullrequests/{pull_request_id}/merge"
        
        data = {
            "merge_strategy": merge_strategy
        }
        
        if message is not None:
            data["message"] = message
            
        if close_source_branch is not None:
            data["close_source_branch"] = close_source_branch
            
        return self._make_api_request("POST", endpoint, data=data)
        
    def decline_pull_request(self, repo_slug: str, pull_request_id: int, reason: Optional[str] = None) -> Dict:
        """
        Decline a pull request.
        
        Args:
            repo_slug: The repository slug
            pull_request_id: The pull request ID
            reason: Optional reason for declining
            
        Returns:
            Declined pull request details
        """
        endpoint = f"/repositories/{self.config.workspace}/{repo_slug}/pullrequests/{pull_request_id}/decline"
        
        data = {}
        if reason is not None:
            data["reason"] = reason
            
        return self._make_api_request("POST", endpoint, data=data)
        
    # Pull Request Comments and Reviews
    def list_pull_request_comments(self, repo_slug: str, pull_request_id: int) -> List[Dict]:
        """
        List comments on a pull request.
        
        Args:
            repo_slug: The repository slug
            pull_request_id: The pull request ID
            
        Returns:
            List of comment objects
        """
        endpoint = f"/repositories/{self.config.workspace}/{repo_slug}/pullrequests/{pull_request_id}/comments"
        return self._paginate_results(endpoint)
        
    def add_pull_request_comment(self, repo_slug: str, pull_request_id: int, content: str,
                               parent_id: Optional[int] = None) -> Dict:
        """
        Add a comment to a pull request.
        
        Args:
            repo_slug: The repository slug
            pull_request_id: The pull request ID
            content: The comment content (supports Markdown)
            parent_id: Optional parent comment ID (for replies)
            
        Returns:
            Comment details
        """
        endpoint = f"/repositories/{self.config.workspace}/{repo_slug}/pullrequests/{pull_request_id}/comments"
        
        data = {
            "content": {
                "raw": content
            }
        }
        
        if parent_id is not None:
            data["parent"] = {
                "id": parent_id
            }
            
        return self._make_api_request("POST", endpoint, data=data)
        
    def approve_pull_request(self, repo_slug: str, pull_request_id: int) -> Dict:
        """
        Approve a pull request.
        
        Args:
            repo_slug: The repository slug
            pull_request_id: The pull request ID
            
        Returns:
            Approval details
        """
        endpoint = f"/repositories/{self.config.workspace}/{repo_slug}/pullrequests/{pull_request_id}/approve"
        return self._make_api_request("POST", endpoint)
        
    def unapprove_pull_request(self, repo_slug: str, pull_request_id: int) -> Dict:
        """
        Remove approval from a pull request.
        
        Args:
            repo_slug: The repository slug
            pull_request_id: The pull request ID
            
        Returns:
            Empty dict on success
        """
        endpoint = f"/repositories/{self.config.workspace}/{repo_slug}/pullrequests/{pull_request_id}/approve"
        return self._make_api_request("DELETE", endpoint)
        
    def request_changes(self, repo_slug: str, pull_request_id: int, content: str) -> Dict:
        """
        Request changes on a pull request (adds a comment flagged as needing changes).
        
        Args:
            repo_slug: The repository slug
            pull_request_id: The pull request ID
            content: The review content
            
        Returns:
            Comment details
        """
        # Bitbucket API doesn't have a direct "request changes" concept
        # We implement it as a specially formatted comment
        comment_content = f"⚠️ **Changes Requested**\n\n{content}"
        return self.add_pull_request_comment(repo_slug, pull_request_id, comment_content)