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