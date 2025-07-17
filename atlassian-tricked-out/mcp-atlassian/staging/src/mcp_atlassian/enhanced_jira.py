"""
Enhanced Jira manager for MCP Atlassian integration.

This module provides enhanced Jira functionality with custom field management,
caching, and advanced features.
"""

import logging
import time
from typing import Dict, List, Any, Optional, Union

from jira import JIRA
from jira.resources import Issue, Project

logger = logging.getLogger("mcp-atlassian-enhanced-jira")

class EnhancedJiraManager:
    """Enhanced Jira manager with support for custom fields and improved API handling."""

    # Cache settings
    CACHE_TTL = 600  # 10 minutes
    
    # Custom field constants (for reference)
    CUSTOM_FIELD_NAME = "customfield_10057"
    CUSTOM_FIELD_DEPARTMENT = "customfield_10058"
    CUSTOM_FIELD_EPIC_LINK = "customfield_10059"
    
    def __init__(self, url: str, username: str, api_token: str):
        """
        Initialize Enhanced Jira manager.
        
        Args:
            url: Jira URL
            username: Jira username
            api_token: Jira API token
        """
        self.url = url
        self.username = username
        self.api_token = api_token
        self.client = None
        
        # Cache storage
        self._cache: Dict[str, Dict[str, Any]] = {
            "projects": {"data": None, "timestamp": 0},
            "issues": {},
            "fields": {"data": None, "timestamp": 0},
            "statuses": {"data": None, "timestamp": 0},
            "issue_types": {"data": None, "timestamp": 0},
        }
        
        # Connect to Jira
        self._connect()
    
    def _connect(self):
        """Connect to Jira API."""
        try:
            self.client = JIRA(
                server=self.url,
                basic_auth=(self.username, self.api_token)
            )
            logger.info(f"Connected to Jira at {self.url}")
        except Exception as e:
            logger.error(f"Failed to connect to Jira: {str(e)}")
            raise
    
    def _get_from_cache(self, cache_key: str, sub_key: Optional[str] = None) -> Optional[Any]:
        """
        Get data from cache if available and not expired.
        
        Args:
            cache_key: Main cache key
            sub_key: Sub-key for nested caches
            
        Returns:
            Any: Cached data or None
        """
        cache = self._cache.get(cache_key)
        
        if not cache:
            return None
        
        if sub_key is not None:
            # Get from nested cache
            nested_cache = cache.get(sub_key)
            if not nested_cache:
                return None
                
            if time.time() - nested_cache.get("timestamp", 0) > self.CACHE_TTL:
                return None
                
            return nested_cache.get("data")
        else:
            # Get from main cache
            if time.time() - cache.get("timestamp", 0) > self.CACHE_TTL:
                return None
                
            return cache.get("data")
    
    def _set_in_cache(self, cache_key: str, data: Any, sub_key: Optional[str] = None):
        """
        Set data in cache.
        
        Args:
            cache_key: Main cache key
            data: Data to cache
            sub_key: Sub-key for nested caches
        """
        if cache_key not in self._cache:
            self._cache[cache_key] = {}
        
        if sub_key is not None:
            # Set in nested cache
            if not isinstance(self._cache[cache_key], dict):
                self._cache[cache_key] = {}
                
            self._cache[cache_key][sub_key] = {
                "data": data,
                "timestamp": time.time()
            }
        else:
            # Set in main cache
            self._cache[cache_key] = {
                "data": data,
                "timestamp": time.time()
            }
    
    def get_projects(self, use_cache: bool = True) -> List[Project]:
        """
        Get all projects.
        
        Args:
            use_cache: Whether to use cache
            
        Returns:
            List[Project]: List of projects
        """
        if use_cache:
            cached = self._get_from_cache("projects")
            if cached:
                return cached
        
        projects = self.client.projects()
        self._set_in_cache("projects", projects)
        
        return projects
    
    def get_issue(self, issue_key: str, use_cache: bool = True) -> Issue:
        """
        Get issue by key.
        
        Args:
            issue_key: Issue key
            use_cache: Whether to use cache
            
        Returns:
            Issue: Issue
        """
        if use_cache:
            cached = self._get_from_cache("issues", issue_key)
            if cached:
                return cached
        
        issue = self.client.issue(issue_key)
        self._set_in_cache("issues", issue, issue_key)
        
        return issue
    
    def get_custom_fields(self, use_cache: bool = True) -> Dict[str, Dict[str, Any]]:
        """
        Get all custom fields.
        
        Args:
            use_cache: Whether to use cache
            
        Returns:
            Dict[str, Dict[str, Any]]: Dictionary of custom fields
        """
        if use_cache:
            cached = self._get_from_cache("fields")
            if cached:
                return cached
        
        fields = self.client.fields()
        
        # Convert to dictionary with name as key
        fields_dict = {}
        for field in fields:
            if field.get("custom", False):
                fields_dict[field["name"]] = field
        
        self._set_in_cache("fields", fields_dict)
        
        return fields_dict
    
    def get_custom_field_id(self, field_name: str) -> Optional[str]:
        """
        Get custom field ID by name.
        
        Args:
            field_name: Field name
            
        Returns:
            Optional[str]: Field ID or None
        """
        fields = self.get_custom_fields()
        
        for name, field in fields.items():
            if name.lower() == field_name.lower():
                return field["id"]
        
        return None
    
    def create_issue(self, project_key: str, summary: str, description: str, 
                    issue_type: str = "Task", name: Optional[str] = None, 
                    dept: Optional[str] = None, custom_fields: Optional[Dict[str, Any]] = None) -> Issue:
        """
        Create issue with enhanced functionality.
        
        Args:
            project_key: Project key
            summary: Issue summary
            description: Issue description
            issue_type: Issue type
            name: Name (for customfield_10057)
            dept: Department (for customfield_10058)
            custom_fields: Custom fields dictionary
            
        Returns:
            Issue: Created issue
        """
        # Prepare fields
        fields = {
            "project": project_key,
            "summary": summary,
            "description": description,
            "issuetype": {"name": issue_type},
        }
        
        # Add required custom fields
        if name is not None:
            fields[self.CUSTOM_FIELD_NAME] = [name]
        
        if dept is not None:
            fields[self.CUSTOM_FIELD_DEPARTMENT] = [dept]
        
        # Add additional custom fields
        if custom_fields:
            fields.update(custom_fields)
        
        # Create issue
        issue = self.client.create_issue(fields=fields)
        
        # Clear issues cache
        self._cache["issues"] = {}
        
        return issue
    
    def create_epic(self, project_key: str, name: str, summary: str, description: str,
                   dept: Optional[str] = None, custom_fields: Optional[Dict[str, Any]] = None) -> Issue:
        """
        Create epic with enhanced functionality.
        
        Args:
            project_key: Project key
            name: Epic name (also used for customfield_10057)
            summary: Epic summary
            description: Epic description
            dept: Department (for customfield_10058)
            custom_fields: Custom fields dictionary
            
        Returns:
            Issue: Created epic
        """
        # Prepare fields
        fields = {
            "project": project_key,
            "summary": summary,
            "description": description,
            "issuetype": {"name": "Epic"},
        }
        
        # Add required custom fields
        fields[self.CUSTOM_FIELD_NAME] = [name]
        
        if dept is not None:
            fields[self.CUSTOM_FIELD_DEPARTMENT] = [dept]
        
        # Add additional custom fields
        if custom_fields:
            fields.update(custom_fields)
        
        # Create epic
        epic = self.client.create_issue(fields=fields)
        
        # Clear issues cache
        self._cache["issues"] = {}
        
        return epic
    
    def update_issue(self, issue_key: str, fields: Dict[str, Any]) -> Issue:
        """
        Update issue fields.
        
        Args:
            issue_key: Issue key
            fields: Fields to update
            
        Returns:
            Issue: Updated issue
        """
        self.client.issue_update(issue_key, fields)
        
        # Clear cache for this issue
        if "issues" in self._cache and issue_key in self._cache["issues"]:
            del self._cache["issues"][issue_key]
        
        # Get updated issue
        return self.get_issue(issue_key, use_cache=False)
    
    def add_comment(self, issue_key: str, comment: str) -> Any:
        """
        Add comment to issue.
        
        Args:
            issue_key: Issue key
            comment: Comment text
            
        Returns:
            Any: Comment
        """
        result = self.client.add_comment(issue_key, comment)
        
        # Clear cache for this issue
        if "issues" in self._cache and issue_key in self._cache["issues"]:
            del self._cache["issues"][issue_key]
        
        return result
    
    def search_issues(self, jql: str, max_results: int = 50, 
                     fields: Optional[List[str]] = None) -> List[Issue]:
        """
        Search issues with JQL.
        
        Args:
            jql: JQL query
            max_results: Maximum results
            fields: Fields to include
            
        Returns:
            List[Issue]: List of issues
        """
        return self.client.search_issues(jql, maxResults=max_results, fields=fields)
    
    def bulk_create_issues(self, issues: List[Dict[str, Any]]) -> List[Issue]:
        """
        Create multiple issues in bulk.
        
        Args:
            issues: List of issue field dictionaries
            
        Returns:
            List[Issue]: List of created issues
        """
        created_issues = []
        
        for issue_fields in issues:
            created = self.client.create_issue(fields=issue_fields)
            created_issues.append(created)
        
        # Clear issues cache
        self._cache["issues"] = {}
        
        return created_issues
    
    def transition_issue(self, issue_key: str, transition: Union[str, int]) -> None:
        """
        Transition issue to new status.
        
        Args:
            issue_key: Issue key
            transition: Transition ID or name
        """
        self.client.transition_issue(issue_key, transition)
        
        # Clear cache for this issue
        if "issues" in self._cache and issue_key in self._cache["issues"]:
            del self._cache["issues"][issue_key]
    
    def assign_issue(self, issue_key: str, assignee: str) -> None:
        """
        Assign issue to user.
        
        Args:
            issue_key: Issue key
            assignee: Username
        """
        self.client.assign_issue(issue_key, assignee)
        
        # Clear cache for this issue
        if "issues" in self._cache and issue_key in self._cache["issues"]:
            del self._cache["issues"][issue_key]
    
    def get_transitions(self, issue_key: str) -> List[Dict[str, Any]]:
        """
        Get available transitions for issue.
        
        Args:
            issue_key: Issue key
            
        Returns:
            List[Dict[str, Any]]: List of transitions
        """
        return self.client.transitions(issue_key)
    
    def add_issues_to_epic(self, epic_key: str, issues: List[str]) -> None:
        """
        Add issues to epic.
        
        Args:
            epic_key: Epic key
            issues: List of issue keys
        """
        for issue_key in issues:
            self.client.add_issues_to_epic(epic_key, [issue_key])
            
            # Clear cache for this issue
            if "issues" in self._cache and issue_key in self._cache["issues"]:
                del self._cache["issues"][issue_key]
        
        # Clear cache for epic
        if "issues" in self._cache and epic_key in self._cache["issues"]:
            del self._cache["issues"][epic_key]
    
    def get_project_components(self, project_key: str) -> List[Dict[str, Any]]:
        """
        Get project components.
        
        Args:
            project_key: Project key
            
        Returns:
            List[Dict[str, Any]]: List of components
        """
        return self.client.project_components(project_key)
    
    def create_component(self, project_key: str, name: str, description: str = "", 
                         lead: Optional[str] = None) -> Dict[str, Any]:
        """
        Create project component.
        
        Args:
            project_key: Project key
            name: Component name
            description: Component description
            lead: Component lead username
            
        Returns:
            Dict[str, Any]: Created component
        """
        return self.client.create_component(name=name, project=project_key, 
                                          description=description, leadUserName=lead)
    
    def get_project_versions(self, project_key: str) -> List[Dict[str, Any]]:
        """
        Get project versions.
        
        Args:
            project_key: Project key
            
        Returns:
            List[Dict[str, Any]]: List of versions
        """
        return self.client.project_versions(project_key)
    
    def create_version(self, project_key: str, name: str, description: str = "", 
                       released: bool = False, archived: bool = False) -> Dict[str, Any]:
        """
        Create project version.
        
        Args:
            project_key: Project key
            name: Version name
            description: Version description
            released: Whether version is released
            archived: Whether version is archived
            
        Returns:
            Dict[str, Any]: Created version
        """
        return self.client.create_version(name=name, project=project_key, 
                                        description=description, released=released, 
                                        archived=archived)
EOF < /dev/null
