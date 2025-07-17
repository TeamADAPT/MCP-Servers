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
logger = logging.getLogger("mcp-bitbucket-pipeline")


class BitbucketPipelineManager:
    """Handles operations for Bitbucket Pipelines."""

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
    
    # Pipeline Management
    def get_pipeline_config(self, repo_slug: str) -> Dict:
        """
        Get the Bitbucket Pipelines configuration for a repository.
        
        Args:
            repo_slug: The repository slug
            
        Returns:
            Pipeline configuration
        """
        endpoint = f"/repositories/{self.config.workspace}/{repo_slug}/pipelines_config"
        return self._make_api_request("GET", endpoint)
        
    def enable_pipelines(self, repo_slug: str) -> Dict:
        """
        Enable Bitbucket Pipelines for a repository.
        
        Args:
            repo_slug: The repository slug
            
        Returns:
            Pipeline configuration
        """
        endpoint = f"/repositories/{self.config.workspace}/{repo_slug}/pipelines_config"
        data = {"enabled": True}
        return self._make_api_request("PUT", endpoint, data=data)
        
    def disable_pipelines(self, repo_slug: str) -> Dict:
        """
        Disable Bitbucket Pipelines for a repository.
        
        Args:
            repo_slug: The repository slug
            
        Returns:
            Pipeline configuration
        """
        endpoint = f"/repositories/{self.config.workspace}/{repo_slug}/pipelines_config"
        data = {"enabled": False}
        return self._make_api_request("PUT", endpoint, data=data)
        
    def list_pipelines(self, repo_slug: str, sort_by: str = "-created_on") -> List[Dict]:
        """
        List pipeline executions for a repository.
        
        Args:
            repo_slug: The repository slug
            sort_by: Field to sort by (prefix with - for descending order)
            
        Returns:
            List of pipeline execution objects
        """
        endpoint = f"/repositories/{self.config.workspace}/{repo_slug}/pipelines/"
        params = {"sort": sort_by}
        return self._paginate_results(endpoint, params=params)
        
    def get_pipeline(self, repo_slug: str, pipeline_uuid: str) -> Dict:
        """
        Get details of a specific pipeline execution.
        
        Args:
            repo_slug: The repository slug
            pipeline_uuid: The pipeline execution UUID
            
        Returns:
            Pipeline execution details
        """
        endpoint = f"/repositories/{self.config.workspace}/{repo_slug}/pipelines/{pipeline_uuid}"
        return self._make_api_request("GET", endpoint)
        
    def stop_pipeline(self, repo_slug: str, pipeline_uuid: str) -> Dict:
        """
        Stop a running pipeline execution.
        
        Args:
            repo_slug: The repository slug
            pipeline_uuid: The pipeline execution UUID
            
        Returns:
            Pipeline execution details
        """
        endpoint = f"/repositories/{self.config.workspace}/{repo_slug}/pipelines/{pipeline_uuid}/stopPipeline"
        return self._make_api_request("POST", endpoint)
        
    def get_pipeline_steps(self, repo_slug: str, pipeline_uuid: str) -> List[Dict]:
        """
        Get the steps of a pipeline execution.
        
        Args:
            repo_slug: The repository slug
            pipeline_uuid: The pipeline execution UUID
            
        Returns:
            List of pipeline step objects
        """
        endpoint = f"/repositories/{self.config.workspace}/{repo_slug}/pipelines/{pipeline_uuid}/steps/"
        return self._paginate_results(endpoint)
        
    def get_step_log(self, repo_slug: str, pipeline_uuid: str, step_uuid: str) -> str:
        """
        Get the log for a specific pipeline step.
        
        Args:
            repo_slug: The repository slug
            pipeline_uuid: The pipeline execution UUID
            step_uuid: The step UUID
            
        Returns:
            Step log content
        """
        endpoint = f"/repositories/{self.config.workspace}/{repo_slug}/pipelines/{pipeline_uuid}/steps/{step_uuid}/log"
        
        # Use requests directly to get the raw log content
        api_url = f"{self.config.url.rstrip('/')}{endpoint}"
        response = requests.get(api_url, auth=self.auth)
        
        if response.status_code >= 400:
            error_msg = f"API request failed: {response.status_code} - {response.text}"
            logger.error(error_msg)
            raise ValueError(error_msg)
            
        return response.text
        
    def run_pipeline(self, repo_slug: str, branch: str, pipeline: Optional[str] = None, 
                    variables: Optional[List[Dict]] = None) -> Dict:
        """
        Run a pipeline on a specific branch.
        
        Args:
            repo_slug: The repository slug
            branch: The branch to run the pipeline on
            pipeline: Optional specific pipeline target name
            variables: Optional list of pipeline variables
            
        Returns:
            Pipeline execution details
        """
        endpoint = f"/repositories/{self.config.workspace}/{repo_slug}/pipelines/"
        
        data = {
            "target": {
                "ref_type": "branch",
                "ref_name": branch,
                "type": "pipeline_ref_target"
            }
        }
        
        if pipeline:
            data["target"]["selector"] = {"type": "custom", "pattern": pipeline}
            
        if variables:
            data["variables"] = variables
            
        return self._make_api_request("POST", endpoint, data=data)
        
    # Pipeline Variables
    def list_variables(self, repo_slug: str) -> List[Dict]:
        """
        List pipeline variables for a repository.
        
        Args:
            repo_slug: The repository slug
            
        Returns:
            List of variable objects
        """
        endpoint = f"/repositories/{self.config.workspace}/{repo_slug}/pipelines_config/variables/"
        return self._paginate_results(endpoint)
        
    def create_variable(self, repo_slug: str, key: str, value: str, secured: bool = False) -> Dict:
        """
        Create a new pipeline variable.
        
        Args:
            repo_slug: The repository slug
            key: The variable key
            value: The variable value
            secured: Whether the variable is secured (masked in logs)
            
        Returns:
            Variable details
        """
        endpoint = f"/repositories/{self.config.workspace}/{repo_slug}/pipelines_config/variables/"
        
        data = {
            "key": key,
            "value": value,
            "secured": secured
        }
        
        return self._make_api_request("POST", endpoint, data=data)
        
    def update_variable(self, repo_slug: str, variable_uuid: str, key: str = None, 
                       value: str = None, secured: bool = None) -> Dict:
        """
        Update an existing pipeline variable.
        
        Args:
            repo_slug: The repository slug
            variable_uuid: The variable UUID
            key: Optional new key
            value: Optional new value
            secured: Optional new secured status
            
        Returns:
            Updated variable details
        """
        endpoint = f"/repositories/{self.config.workspace}/{repo_slug}/pipelines_config/variables/{variable_uuid}"
        
        # Get current variable details (we only need to know if it's secured)
        current_var = self._make_api_request("GET", endpoint)
        
        data = {}
        if key is not None:
            data["key"] = key
        if value is not None:
            data["value"] = value
        if secured is not None:
            data["secured"] = secured
        else:
            data["secured"] = current_var.get("secured", False)
            
        return self._make_api_request("PUT", endpoint, data=data)
        
    def delete_variable(self, repo_slug: str, variable_uuid: str) -> Dict:
        """
        Delete a pipeline variable.
        
        Args:
            repo_slug: The repository slug
            variable_uuid: The variable UUID
            
        Returns:
            Empty dict on success
        """
        endpoint = f"/repositories/{self.config.workspace}/{repo_slug}/pipelines_config/variables/{variable_uuid}"
        return self._make_api_request("DELETE", endpoint)
        
    # Deployment Management
    def list_environments(self, repo_slug: str) -> List[Dict]:
        """
        List deployment environments for a repository.
        
        Args:
            repo_slug: The repository slug
            
        Returns:
            List of environment objects
        """
        endpoint = f"/repositories/{self.config.workspace}/{repo_slug}/environments/"
        return self._paginate_results(endpoint)
        
    def get_environment(self, repo_slug: str, environment_uuid: str) -> Dict:
        """
        Get details of a specific deployment environment.
        
        Args:
            repo_slug: The repository slug
            environment_uuid: The environment UUID
            
        Returns:
            Environment details
        """
        endpoint = f"/repositories/{self.config.workspace}/{repo_slug}/environments/{environment_uuid}"
        return self._make_api_request("GET", endpoint)
        
    def create_environment(self, repo_slug: str, name: str, environment_type: str = "Test", 
                          environment_lock: bool = False) -> Dict:
        """
        Create a new deployment environment.
        
        Args:
            repo_slug: The repository slug
            name: The environment name
            environment_type: The environment type (Test, Staging, Production)
            environment_lock: Whether the environment is locked for deployments
            
        Returns:
            Environment details
        """
        endpoint = f"/repositories/{self.config.workspace}/{repo_slug}/environments/"
        
        data = {
            "name": name,
            "environment_type": {
                "name": environment_type
            },
            "lock": environment_lock
        }
        
        return self._make_api_request("POST", endpoint, data=data)
        
    def update_environment(self, repo_slug: str, environment_uuid: str, name: Optional[str] = None,
                          environment_type: Optional[str] = None, environment_lock: Optional[bool] = None) -> Dict:
        """
        Update an existing deployment environment.
        
        Args:
            repo_slug: The repository slug
            environment_uuid: The environment UUID
            name: Optional new name
            environment_type: Optional new environment type
            environment_lock: Optional new lock status
            
        Returns:
            Updated environment details
        """
        endpoint = f"/repositories/{self.config.workspace}/{repo_slug}/environments/{environment_uuid}"
        
        # Get current environment details
        current_env = self.get_environment(repo_slug, environment_uuid)
        
        data = {}
        if name is not None:
            data["name"] = name
        if environment_type is not None:
            data["environment_type"] = {"name": environment_type}
        if environment_lock is not None:
            data["lock"] = environment_lock
            
        return self._make_api_request("PUT", endpoint, data=data)
        
    def delete_environment(self, repo_slug: str, environment_uuid: str) -> Dict:
        """
        Delete a deployment environment.
        
        Args:
            repo_slug: The repository slug
            environment_uuid: The environment UUID
            
        Returns:
            Empty dict on success
        """
        endpoint = f"/repositories/{self.config.workspace}/{repo_slug}/environments/{environment_uuid}"
        return self._make_api_request("DELETE", endpoint)
        
    def list_deployments(self, repo_slug: str, environment_uuid: Optional[str] = None) -> List[Dict]:
        """
        List deployments for a repository.
        
        Args:
            repo_slug: The repository slug
            environment_uuid: Optional environment UUID to filter deployments
            
        Returns:
            List of deployment objects
        """
        if environment_uuid:
            endpoint = f"/repositories/{self.config.workspace}/{repo_slug}/environments/{environment_uuid}/deployments"
        else:
            endpoint = f"/repositories/{self.config.workspace}/{repo_slug}/deployments/"
            
        return self._paginate_results(endpoint)
        
    def get_deployment(self, repo_slug: str, deployment_uuid: str) -> Dict:
        """
        Get details of a specific deployment.
        
        Args:
            repo_slug: The repository slug
            deployment_uuid: The deployment UUID
            
        Returns:
            Deployment details
        """
        endpoint = f"/repositories/{self.config.workspace}/{repo_slug}/deployments/{deployment_uuid}"
        return self._make_api_request("GET", endpoint)
        
    # Build Status Management
    def create_build_status(self, repo_slug: str, commit_hash: str, state: str,
                          key: str, name: str, url: str, description: Optional[str] = None) -> Dict:
        """
        Create a build status for a commit.
        
        Args:
            repo_slug: The repository slug
            commit_hash: The commit hash
            state: The build state (SUCCESSFUL, FAILED, INPROGRESS, STOPPED)
            key: The unique key that identifies the build status
            name: The name of the build status
            url: The URL to link to the build status
            description: Optional description of the build status
            
        Returns:
            Build status details
        """
        endpoint = f"/repositories/{self.config.workspace}/{repo_slug}/commit/{commit_hash}/statuses/build"
        
        data = {
            "state": state,
            "key": key,
            "name": name,
            "url": url
        }
        
        if description:
            data["description"] = description
            
        return self._make_api_request("POST", endpoint, data=data)
        
    def list_build_statuses(self, repo_slug: str, commit_hash: str) -> List[Dict]:
        """
        List build statuses for a commit.
        
        Args:
            repo_slug: The repository slug
            commit_hash: The commit hash
            
        Returns:
            List of build status objects
        """
        endpoint = f"/repositories/{self.config.workspace}/{repo_slug}/commit/{commit_hash}/statuses"
        return self._paginate_results(endpoint)
        
    def get_build_status(self, repo_slug: str, commit_hash: str, key: str) -> Optional[Dict]:
        """
        Get a specific build status for a commit.
        
        Args:
            repo_slug: The repository slug
            commit_hash: The commit hash
            key: The unique key that identifies the build status
            
        Returns:
            Build status details or None if not found
        """
        statuses = self.list_build_statuses(repo_slug, commit_hash)
        for status in statuses:
            if status.get("key") == key:
                return status
                
        return None