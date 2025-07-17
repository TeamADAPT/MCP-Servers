"""
Jira Service Management Knowledge Base Integration Module.

This module provides integration with Jira Service Management Knowledge Base functionality,
allowing for knowledge base article management and integration with service desk operations.

Author: Claude Code
Date: May 7, 2025
"""

import logging
from typing import Dict, List, Optional, Union, Any
import os
import requests

# Configure logging
logger = logging.getLogger("mcp-jsm-kb")

class JSMKnowledgeBase:
    """
    Handles operations related to Jira Service Management Knowledge Base.
    
    This class provides an interface to JSM Knowledge Base functionality
    including article management, article-request linking, and searching.
    """
    
    def __init__(self, jsm_client=None, url=None, username=None, api_token=None):
        """
        Initialize the JSM Knowledge Base handler.
        
        Args:
            jsm_client: Existing JiraServiceManager instance (optional)
            url: The JSM URL (defaults to environment variable or jsm_client)
            username: The JSM username (defaults to environment variable or jsm_client)
            api_token: The JSM API token (defaults to environment variable or jsm_client)
        """
        if jsm_client:
            self.url = jsm_client.url
            self.auth = jsm_client.auth
            self.headers = jsm_client.headers
            self.api_base = jsm_client.api_base
            self._make_api_request = jsm_client._make_api_request
        else:
            self.url = url or os.getenv("JSM_URL") or os.getenv("JIRA_URL")
            self.username = username or os.getenv("JSM_USERNAME") or os.getenv("JIRA_USERNAME")
            self.api_token = api_token or os.getenv("JSM_API_TOKEN") or os.getenv("JIRA_API_TOKEN")
            
            if not all([self.url, self.username, self.api_token]):
                raise ValueError("Missing required JSM environment variables")
            
            # Ensure URL doesn't end with a slash
            self.url = self.url.rstrip("/")
            
            # Base API URL for JSM
            self.api_base = f"{self.url}/rest/servicedeskapi"
            
            # Authentication tuple for requests
            self.auth = (self.username, self.api_token)
            
            # Standard headers for API requests
            self.headers = {
                "Accept": "application/json",
                "Content-Type": "application/json"
            }
            
            logger.info(f"Initialized JSM Knowledge Base handler for {self.url}")
            
    def _make_api_request(self, method: str, endpoint: str, data: Optional[Dict] = None, params: Optional[Dict] = None) -> Dict:
        """
        Make a request to the JSM API.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint path (without base URL)
            data: Optional payload for POST/PUT requests
            params: Optional query parameters
            
        Returns:
            Dictionary containing the API response
        """
        # Ensure endpoint starts with /
        if not endpoint.startswith("/"):
            endpoint = f"/{endpoint}"
            
        url = f"{self.api_base}{endpoint}"
        
        try:
            if method.upper() == "GET":
                response = requests.get(url, auth=self.auth, headers=self.headers, params=params)
            elif method.upper() == "POST":
                response = requests.post(url, json=data, auth=self.auth, headers=self.headers, params=params)
            elif method.upper() == "PUT":
                response = requests.put(url, json=data, auth=self.auth, headers=self.headers, params=params)
            elif method.upper() == "DELETE":
                response = requests.delete(url, json=data, auth=self.auth, headers=self.headers, params=params)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
                
            # Handle response and raise appropriate exceptions
            if response.status_code >= 400:
                error_msg = f"JSM API Error: {response.status_code} - {response.text}"
                logger.error(error_msg)
                
                # Handle specific error codes
                if response.status_code == 404:
                    raise ValueError("Knowledge base resource not found")
                elif response.status_code == 403:
                    raise ValueError("Permission denied - check JSM scopes")
                elif response.status_code == 400:
                    raise ValueError(f"Bad request: {response.text}")
                else:
                    raise ValueError(error_msg)
            
            # Return JSON response or empty dict for 204 No Content
            return response.json() if response.content else {}
            
        except requests.RequestException as e:
            logger.error(f"Error making JSM API request to {endpoint}: {str(e)}")
            raise ValueError(f"JSM API request failed: {str(e)}")
            
    # ======= KNOWLEDGE BASE OPERATIONS =======
    
    def get_knowledge_bases(self, start: int = 0, limit: int = 50) -> Dict:
        """
        Get all knowledge bases available to the user.
        
        Args:
            start: Starting index for pagination
            limit: Maximum results to return
            
        Returns:
            Dictionary containing knowledge base information
        """
        params = {"start": start, "limit": limit}
        return self._make_api_request("GET", "/knowledgebase", params=params)
    
    def get_knowledge_base(self, knowledge_base_id: str) -> Dict:
        """
        Get details about a specific knowledge base.
        
        Args:
            knowledge_base_id: The ID of the knowledge base
            
        Returns:
            Dictionary containing knowledge base details
        """
        return self._make_api_request("GET", f"/knowledgebase/{knowledge_base_id}")
    
    def search_articles(self, query: str, knowledge_base_id: Optional[str] = None, 
                       start: int = 0, limit: int = 50) -> Dict:
        """
        Search knowledge base articles.
        
        Args:
            query: Search query string
            knowledge_base_id: Optional knowledge base ID to scope the search
            start: Starting index for pagination
            limit: Maximum results to return
            
        Returns:
            Dictionary containing article search results
        """
        params = {
            "query": query,
            "start": start,
            "limit": limit
        }
        
        if knowledge_base_id:
            params["knowledgeBaseId"] = knowledge_base_id
            
        return self._make_api_request("GET", "/knowledgebase/article/search", params=params)
    
    def get_article(self, article_id: str) -> Dict:
        """
        Get details about a specific knowledge base article.
        
        Args:
            article_id: The ID of the article
            
        Returns:
            Dictionary containing article details
        """
        return self._make_api_request("GET", f"/knowledgebase/article/{article_id}")
    
    def create_article(self, knowledge_base_id: str, title: str, 
                      body: str, draft: bool = False, 
                      labels: Optional[List[str]] = None) -> Dict:
        """
        Create a new knowledge base article.
        
        Args:
            knowledge_base_id: The ID of the knowledge base
            title: Article title
            body: Article body content (HTML format)
            draft: Whether to create as draft (default: False)
            labels: Optional list of labels to apply to the article
            
        Returns:
            Dictionary containing the created article details
        """
        data = {
            "knowledgeBaseId": knowledge_base_id,
            "title": title,
            "body": body,
            "draft": draft
        }
        
        if labels:
            data["labels"] = labels
            
        return self._make_api_request("POST", "/knowledgebase/article", data=data)
    
    def update_article(self, article_id: str, title: Optional[str] = None, 
                      body: Optional[str] = None, draft: Optional[bool] = None,
                      labels: Optional[List[str]] = None) -> Dict:
        """
        Update an existing knowledge base article.
        
        Args:
            article_id: The ID of the article to update
            title: Optional new article title
            body: Optional new article body content (HTML format)
            draft: Optional new draft status
            labels: Optional new list of labels
            
        Returns:
            Dictionary containing the updated article details
        """
        data = {}
        
        if title is not None:
            data["title"] = title
            
        if body is not None:
            data["body"] = body
            
        if draft is not None:
            data["draft"] = draft
            
        if labels is not None:
            data["labels"] = labels
            
        if not data:
            raise ValueError("At least one field must be provided for update")
            
        return self._make_api_request("PUT", f"/knowledgebase/article/{article_id}", data=data)
    
    def delete_article(self, article_id: str) -> Dict:
        """
        Delete a knowledge base article.
        
        Args:
            article_id: The ID of the article to delete
            
        Returns:
            Dictionary containing result information
        """
        return self._make_api_request("DELETE", f"/knowledgebase/article/{article_id}")
    
    # ======= ARTICLE-REQUEST OPERATIONS =======
    
    def get_linked_articles(self, issue_id_or_key: str, start: int = 0, limit: int = 50) -> Dict:
        """
        Get articles linked to a customer request.
        
        Args:
            issue_id_or_key: The ID or key of the issue
            start: Starting index for pagination
            limit: Maximum results to return
            
        Returns:
            Dictionary containing linked article information
        """
        params = {"start": start, "limit": limit}
        return self._make_api_request("GET", f"/request/{issue_id_or_key}/article", params=params)
    
    def link_article_to_request(self, issue_id_or_key: str, article_id: str) -> Dict:
        """
        Link a knowledge base article to a customer request.
        
        Args:
            issue_id_or_key: The ID or key of the issue
            article_id: The ID of the article to link
            
        Returns:
            Dictionary containing link information
        """
        data = {"articleId": article_id}
        return self._make_api_request("POST", f"/request/{issue_id_or_key}/article", data=data)
    
    def unlink_article_from_request(self, issue_id_or_key: str, article_id: str) -> Dict:
        """
        Unlink a knowledge base article from a customer request.
        
        Args:
            issue_id_or_key: The ID or key of the issue
            article_id: The ID of the article to unlink
            
        Returns:
            Dictionary containing result information
        """
        data = {"articleId": article_id}
        return self._make_api_request("DELETE", f"/request/{issue_id_or_key}/article", data=data)
    
    # ======= KNOWLEDGE BASE SUGGESTIONS =======
    
    def suggest_articles(self, service_desk_id: str, request_type_id: str, 
                        query: str, start: int = 0, limit: int = 5) -> Dict:
        """
        Get article suggestions for a service desk request type.
        
        Args:
            service_desk_id: The ID of the service desk
            request_type_id: The ID of the request type
            query: Search query for relevant articles
            start: Starting index for pagination
            limit: Maximum results to return
            
        Returns:
            Dictionary containing suggested articles
        """
        data = {
            "serviceDeskId": service_desk_id,
            "requestTypeId": request_type_id,
            "query": query
        }
        
        params = {"start": start, "limit": limit}
        
        return self._make_api_request("POST", "/knowledgebase/article/suggestion", 
                                    data=data, params=params)