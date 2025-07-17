"""
JSM Knowledge Base Module

This module provides functionality for working with Jira Service Management (JSM)
knowledge bases, including creating and linking articles.
"""

import json
import logging
import os
from typing import Dict, List, Optional, Any, Union

import requests

from .jsm import JiraServiceManager

logger = logging.getLogger(__name__)

class JSMKnowledgeBase:
    """
    Manages Jira Service Management knowledge base operations.
    """

    def __init__(
        self, 
        jsm_client: Optional[JiraServiceManager] = None,
        url: Optional[str] = None, 
        username: Optional[str] = None, 
        api_token: Optional[str] = None
    ):
        """
        Initialize the JSM Knowledge Base Manager.

        Args:
            jsm_client: Optional existing JSM client
            url: JSM URL (if not using existing client)
            username: JSM username (if not using existing client)
            api_token: JSM API token (if not using existing client)
        """
        if jsm_client:
            self.jsm_client = jsm_client
            self.url = jsm_client.url
            self.auth = jsm_client.auth
            self.headers = jsm_client.headers
        else:
            # Create new client
            self.jsm_client = JiraServiceManager(url, username, api_token)
            self.url = self.jsm_client.url
            self.auth = self.jsm_client.auth
            self.headers = self.jsm_client.headers
        
        logger.debug(f"Initialized JSMKnowledgeBase with URL: {self.url}")

    def _make_api_request(
        self, method: str, endpoint: str, params: Optional[Dict] = None, data: Optional[Dict] = None
    ) -> Dict:
        """
        Make an API request to the JSM API.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint (without base URL)
            params: Optional query parameters
            data: Optional data for POST/PUT requests

        Returns:
            Response as dictionary
        """
        url = f"{self.url}/rest/servicedeskapi{endpoint}"
        json_data = json.dumps(data) if data else None
        
        try:
            response = requests.request(
                method=method,
                url=url,
                params=params,
                data=json_data,
                headers=self.headers,
                auth=self.auth
            )
            
            if response.status_code == 204:  # No Content
                return {"status": "success"}
                
            if response.status_code >= 400:
                error_msg = f"JSM API request failed: {response.status_code}"
                if response.status_code == 404:
                    error_msg = f"Resource not found: {url}"
                elif response.status_code == 403:
                    error_msg = f"Permission denied for: {url}"
                elif response.status_code == 400:
                    error_msg = f"Bad request: {response.text}"
                else:
                    error_msg = f"API request failed ({response.status_code}): {response.text}"
                
                logger.error(error_msg)
                raise ValueError(error_msg)
                
            return response.json()
            
        except requests.RequestException as e:
            error_msg = f"Request error for {url}: {str(e)}"
            logger.error(error_msg)
            raise ValueError(error_msg)

    # Knowledge Base Operations
    def get_knowledge_bases(self, start: int = 0, limit: int = 50) -> List[Dict]:
        """
        Get all knowledge bases.

        Args:
            start: Starting index for pagination
            limit: Maximum number of results to return

        Returns:
            List of knowledge bases
        """
        params = {
            "start": start,
            "limit": limit
        }
        
        response = self._make_api_request("GET", "/knowledgebase", params=params)
        return response.get("values", [])

    def get_knowledge_base(self, knowledge_base_id: str) -> Dict:
        """
        Get a specific knowledge base.

        Args:
            knowledge_base_id: The knowledge base ID

        Returns:
            Knowledge base details
        """
        return self._make_api_request("GET", f"/knowledgebase/{knowledge_base_id}")

    # Article Operations
    def search_articles(
        self, query: Optional[str] = None, 
        knowledge_base_id: Optional[str] = None,
        highlight: bool = False,
        start: int = 0, limit: int = 50
    ) -> List[Dict]:
        """
        Search for articles.

        Args:
            query: Optional search query
            knowledge_base_id: Optional knowledge base ID
            highlight: Whether to highlight matched terms
            start: Starting index for pagination
            limit: Maximum number of results to return

        Returns:
            List of matching articles
        """
        params = {
            "start": start,
            "limit": limit
        }
        
        if query:
            params["query"] = query
            
        if knowledge_base_id:
            params["knowledgeBaseId"] = knowledge_base_id
            
        if highlight:
            params["highlight"] = "true"
        
        response = self._make_api_request("GET", "/knowledgebase/article", params=params)
        return response.get("values", [])

    def get_article(self, article_id: str) -> Dict:
        """
        Get a specific article.

        Args:
            article_id: The article ID

        Returns:
            Article details
        """
        return self._make_api_request("GET", f"/knowledgebase/article/{article_id}")

    def create_article(
        self, knowledge_base_id: str, title: str, body: str, 
        draft: bool = False, labels: Optional[List[str]] = None
    ) -> Dict:
        """
        Create a new article.

        Args:
            knowledge_base_id: The knowledge base ID
            title: Article title
            body: Article body (HTML format)
            draft: Whether to create as draft
            labels: Optional list of labels

        Returns:
            Created article
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

    def update_article(
        self, article_id: str, 
        title: Optional[str] = None, 
        body: Optional[str] = None,
        draft: Optional[bool] = None,
        labels: Optional[List[str]] = None
    ) -> Dict:
        """
        Update an article.

        Args:
            article_id: The article ID
            title: Optional new title
            body: Optional new body
            draft: Optional draft status
            labels: Optional new labels

        Returns:
            Updated article
        """
        # Make sure at least one field is being updated
        if not any([title, body, draft is not None, labels]):
            raise ValueError("At least one field must be updated")
            
        data = {}
        
        if title:
            data["title"] = title
            
        if body:
            data["body"] = body
            
        if draft is not None:
            data["draft"] = draft
            
        if labels is not None:
            data["labels"] = labels
            
        return self._make_api_request("PUT", f"/knowledgebase/article/{article_id}", data=data)

    def delete_article(self, article_id: str) -> Dict:
        """
        Delete an article.

        Args:
            article_id: The article ID

        Returns:
            Status response
        """
        return self._make_api_request("DELETE", f"/knowledgebase/article/{article_id}")

    # Article-Request Integration
    def get_linked_articles(
        self, request_id: str, start: int = 0, limit: int = 50
    ) -> List[Dict]:
        """
        Get articles linked to a request.

        Args:
            request_id: The request ID
            start: Starting index for pagination
            limit: Maximum number of results to return

        Returns:
            List of linked articles
        """
        params = {
            "start": start,
            "limit": limit
        }
        
        response = self._make_api_request(
            "GET", f"/request/{request_id}/article", params=params
        )
        return response.get("values", [])

    def link_article_to_request(self, request_id: str, article_id: str) -> Dict:
        """
        Link an article to a request.

        Args:
            request_id: The request ID
            article_id: The article ID

        Returns:
            Status response
        """
        data = {
            "articleId": article_id
        }
        
        return self._make_api_request("POST", f"/request/{request_id}/article", data=data)

    def unlink_article_from_request(self, request_id: str, article_id: str) -> Dict:
        """
        Unlink an article from a request.

        Args:
            request_id: The request ID
            article_id: The article ID

        Returns:
            Status response
        """
        return self._make_api_request(
            "DELETE", f"/request/{request_id}/article/{article_id}"
        )

    # Suggestions
    def suggest_articles(
        self, service_desk_id: str, request_type_id: str, 
        query: Optional[str] = None, limit: int = 5
    ) -> List[Dict]:
        """
        Get article suggestions for a request type.

        Args:
            service_desk_id: The service desk ID
            request_type_id: The request type ID
            query: Optional search query
            limit: Maximum number of results to return

        Returns:
            List of suggested articles
        """
        params = {
            "limit": limit
        }
        
        if query:
            params["query"] = query
            
        response = self._make_api_request(
            "GET", 
            f"/servicedesk/{service_desk_id}/requesttype/{request_type_id}/article",
            params=params
        )
        return response.get("values", [])