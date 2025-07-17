"""
Confluence Advanced Content Management Module.

This module provides advanced content management functionality for Confluence.
"""

import logging
import json
import requests
from typing import Dict, List, Optional, Any, Union

from .config import ConfluenceConfig

# Configure logging
logger = logging.getLogger("mcp-atlassian")


class ConfluenceContentManager:
    """Manages advanced content features like macros, properties, labels and version control."""

    def __init__(self, config: ConfluenceConfig):
        """
        Initialize the ConfluenceContentManager.

        Args:
            config: ConfluenceConfig object with Confluence credentials
        """
        self.config = config
        self.base_url = config.url
        self.auth = (config.username, config.api_token)
        self.headers = {"Content-Type": "application/json"}
        
    def _make_api_request(self, method: str, endpoint: str, data: Optional[Dict] = None,
                         params: Optional[Dict] = None, files: Optional[Dict] = None) -> Dict:
        """
        Make an API request to Confluence.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint (without base URL)
            data: Request data
            params: Query parameters
            files: Files for multipart/form-data requests
            
        Returns:
            Response data as dictionary
        
        Raises:
            ValueError: For API errors with appropriate message
        """
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = requests.request(
                method=method,
                url=url,
                json=data,
                params=params,
                files=files,
                auth=self.auth,
                headers=self.headers
            )
            
            # Check for errors
            if response.status_code >= 400:
                error_msg = f"API request failed: {response.status_code} - {response.text}"
                logger.error(error_msg)
                raise ValueError(error_msg)
                
            if response.status_code == 204:  # No content
                return {}
                
            return response.json()
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Request error: {str(e)}"
            logger.error(error_msg)
            raise ValueError(error_msg)
    
    # Content Properties Management
    
    def get_content_properties(self, content_id: str) -> Dict:
        """
        Get all properties for a content.
        
        Args:
            content_id: The content ID
            
        Returns:
            Dictionary containing content properties
        """
        return self._make_api_request("GET", f"/rest/api/content/{content_id}/property")
    
    def get_content_property(self, content_id: str, property_key: str) -> Dict:
        """
        Get a specific property for a content.
        
        Args:
            content_id: The content ID
            property_key: The property key
            
        Returns:
            Dictionary containing property details
        """
        return self._make_api_request(
            "GET", 
            f"/rest/api/content/{content_id}/property/{property_key}"
        )
    
    def set_content_property(self, content_id: str, property_key: str, property_value: Any) -> Dict:
        """
        Set a property for a content.
        
        Args:
            content_id: The content ID
            property_key: The property key
            property_value: The property value (can be any JSON-serializable value)
            
        Returns:
            Dictionary containing property details
        """
        property_data = {
            "key": property_key,
            "value": property_value
        }
        
        try:
            # Try to get the property first (to update it if it exists)
            existing = self.get_content_property(content_id, property_key)
            
            # If it exists, update it
            if existing:
                property_data["version"] = {
                    "number": existing.get("version", {}).get("number", 0) + 1
                }
                
                return self._make_api_request(
                    "PUT", 
                    f"/rest/api/content/{content_id}/property/{property_key}", 
                    data=property_data
                )
                
        except ValueError:
            # Property doesn't exist, create it
            pass
            
        return self._make_api_request(
            "POST", 
            f"/rest/api/content/{content_id}/property", 
            data=property_data
        )
    
    def delete_content_property(self, content_id: str, property_key: str) -> Dict:
        """
        Delete a property from a content.
        
        Args:
            content_id: The content ID
            property_key: The property key
            
        Returns:
            Empty dictionary on success
        """
        return self._make_api_request(
            "DELETE", 
            f"/rest/api/content/{content_id}/property/{property_key}"
        )
    
    # Content Restrictions Management
    
    def get_content_restrictions(self, content_id: str) -> Dict:
        """
        Get restrictions for a content.
        
        Args:
            content_id: The content ID
            
        Returns:
            Dictionary containing content restrictions
        """
        return self._make_api_request(
            "GET", 
            f"/rest/api/content/{content_id}/restriction"
        )
    
    def add_content_restriction(self, content_id: str, restriction_type: str, 
                               subject_type: str, subject_key: str) -> Dict:
        """
        Add a restriction to a content.
        
        Args:
            content_id: The content ID
            restriction_type: The restriction type ("read" or "update")
            subject_type: The subject type ("user" or "group")
            subject_key: The key of the user or group
            
        Returns:
            Dictionary containing the added restriction
        """
        restriction_data = {
            "operation": restriction_type,
            subject_type: {
                "results": [
                    {"name": subject_key}
                ]
            }
        }
        
        return self._make_api_request(
            "PUT", 
            f"/rest/api/content/{content_id}/restriction/byOperation/{restriction_type}", 
            data=restriction_data
        )
    
    def delete_content_restriction(self, content_id: str, restriction_type: str,
                                 subject_type: str, subject_key: str) -> Dict:
        """
        Delete a restriction from a content.
        
        Args:
            content_id: The content ID
            restriction_type: The restriction type ("read" or "update")
            subject_type: The subject type ("user" or "group")
            subject_key: The key of the user or group
            
        Returns:
            Empty dictionary on success
        """
        return self._make_api_request(
            "DELETE", 
            f"/rest/api/content/{content_id}/restriction/byOperation/{restriction_type}/{subject_type}/{subject_key}"
        )
    
    # Labels Management
    
    def get_content_labels(self, content_id: str, prefix: Optional[str] = None) -> List[Dict]:
        """
        Get labels for a content.
        
        Args:
            content_id: The content ID
            prefix: Optional prefix to filter labels
            
        Returns:
            List of labels
        """
        params = {}
        if prefix:
            params["prefix"] = prefix
            
        response = self._make_api_request(
            "GET", 
            f"/rest/api/content/{content_id}/label", 
            params=params
        )
        
        return response.get("results", [])
    
    def add_label(self, content_id: str, label: str, prefix: Optional[str] = None) -> List[Dict]:
        """
        Add a label to a content.
        
        Args:
            content_id: The content ID
            label: The label name
            prefix: Optional label prefix (default: "global")
            
        Returns:
            List of added labels
        """
        label_data = [
            {
                "prefix": prefix or "global",
                "name": label
            }
        ]
        
        response = self._make_api_request(
            "POST", 
            f"/rest/api/content/{content_id}/label", 
            data=label_data
        )
        
        return response.get("results", [])
    
    def add_multiple_labels(self, content_id: str, labels: List[str], 
                           prefix: Optional[str] = None) -> List[Dict]:
        """
        Add multiple labels to a content.
        
        Args:
            content_id: The content ID
            labels: List of label names
            prefix: Optional label prefix (default: "global")
            
        Returns:
            List of added labels
        """
        label_data = [
            {
                "prefix": prefix or "global",
                "name": label
            }
            for label in labels
        ]
        
        response = self._make_api_request(
            "POST", 
            f"/rest/api/content/{content_id}/label", 
            data=label_data
        )
        
        return response.get("results", [])
    
    def remove_label(self, content_id: str, label: str, prefix: Optional[str] = None) -> Dict:
        """
        Remove a label from a content.
        
        Args:
            content_id: The content ID
            label: The label name
            prefix: Optional label prefix (default: "global")
            
        Returns:
            Empty dictionary on success
        """
        params = {
            "name": label
        }
        
        if prefix:
            params["prefix"] = prefix
            
        return self._make_api_request(
            "DELETE", 
            f"/rest/api/content/{content_id}/label", 
            params=params
        )
    
    def get_content_by_label(self, label: str, space_key: Optional[str] = None,
                            content_type: Optional[str] = None,
                            start: int = 0, limit: int = 25) -> Dict:
        """
        Find content with a specific label.
        
        Args:
            label: The label name to search for
            space_key: Optional space key to limit search
            content_type: Optional content type filter ("page", "blogpost")
            start: Starting index for pagination
            limit: Maximum number of results to return
            
        Returns:
            Dictionary containing matching content
        """
        params = {
            "start": start,
            "limit": limit,
            "label": label
        }
        
        if space_key:
            params["spaceKey"] = space_key
            
        if content_type:
            params["type"] = content_type
            
        return self._make_api_request("GET", "/rest/api/content", params=params)
    
    # Macros Management
    
    def get_available_macros(self) -> List[Dict]:
        """
        Get a list of available macros.
        
        Returns:
            List of available macros
        """
        response = self._make_api_request("GET", "/rest/api/macro")
        return response.get("results", [])
    
    def get_macro_details(self, macro_key: str) -> Dict:
        """
        Get details about a specific macro.
        
        Args:
            macro_key: The macro key
            
        Returns:
            Dictionary containing macro details
        """
        return self._make_api_request("GET", f"/rest/api/macro/{macro_key}")
    
    def add_macro_to_page(self, content_id: str, macro_key: str, macro_parameters: Dict,
                         macro_body: Optional[str] = None) -> Dict:
        """
        Add a macro to a page or blog post.
        
        Note: This operation requires getting the content, updating it, and saving it.
        
        Args:
            content_id: The content ID
            macro_key: The macro key (e.g., "info", "code", "jira")
            macro_parameters: Parameters for the macro
            macro_body: Optional body for body macros
            
        Returns:
            Dictionary containing updated content
        """
        # Get the current content
        content = self._make_api_request(
            "GET", 
            f"/rest/api/content/{content_id}", 
            params={"expand": "body.storage,version"}
        )
        
        # Get the current body and version
        body = content.get("body", {}).get("storage", {}).get("value", "")
        version = content.get("version", {}).get("number", 0)
        
        # Create the macro HTML
        macro_html = f'<ac:structured-macro ac:name="{macro_key}">'
        
        # Add parameters
        for key, value in macro_parameters.items():
            macro_html += f'<ac:parameter ac:name="{key}">{value}</ac:parameter>'
        
        # Add body if provided
        if macro_body:
            macro_html += f'<ac:plain-text-body><![CDATA[{macro_body}]]></ac:plain-text-body>'
            
        macro_html += '</ac:structured-macro>'
        
        # Append the macro to the body
        new_body = body + macro_html
        
        # Update the content
        update_data = {
            "version": {
                "number": version + 1
            },
            "title": content.get("title", ""),
            "type": content.get("type", "page"),
            "body": {
                "storage": {
                    "value": new_body,
                    "representation": "storage"
                }
            }
        }
        
        return self._make_api_request("PUT", f"/rest/api/content/{content_id}", data=update_data)
    
    # Version Management
    
    def get_content_versions(self, content_id: str, start: int = 0, limit: int = 25) -> Dict:
        """
        Get versions of a content.
        
        Args:
            content_id: The content ID
            start: Starting index for pagination
            limit: Maximum number of versions to return
            
        Returns:
            Dictionary containing content versions
        """
        params = {
            "start": start,
            "limit": limit
        }
        
        return self._make_api_request(
            "GET", 
            f"/rest/api/content/{content_id}/version", 
            params=params
        )
    
    def get_content_version(self, content_id: str, version_number: int) -> Dict:
        """
        Get a specific version of a content.
        
        Args:
            content_id: The content ID
            version_number: The version number
            
        Returns:
            Dictionary containing version details
        """
        return self._make_api_request(
            "GET", 
            f"/rest/api/content/{content_id}/version/{version_number}"
        )
    
    def compare_versions(self, content_id: str, source_version: int, target_version: int) -> Dict:
        """
        Compare two versions of a content.
        
        Args:
            content_id: The content ID
            source_version: The source version number
            target_version: The target version number
            
        Returns:
            Dictionary containing comparison details
        """
        return self._make_api_request(
            "GET", 
            f"/rest/api/content/{content_id}/diff", 
            params={
                "source": source_version,
                "target": target_version
            }
        )
    
    def restore_version(self, content_id: str, version_number: int) -> Dict:
        """
        Restore a content to a previous version.
        
        Args:
            content_id: The content ID
            version_number: The version number to restore
            
        Returns:
            Dictionary containing restored content
        """
        # Get the content version to restore
        version = self.get_content_version(content_id, version_number)
        
        # Get the current content
        current = self._make_api_request(
            "GET", 
            f"/rest/api/content/{content_id}", 
            params={"expand": "version"}
        )
        
        current_version = current.get("version", {}).get("number", 0)
        
        # Get the content body for the version to restore
        version_content = self._make_api_request(
            "GET", 
            f"/rest/api/content/{content_id}", 
            params={
                "version": version_number,
                "expand": "body.storage"
            }
        )
        
        body = version_content.get("body", {}).get("storage", {}).get("value", "")
        
        # Update the content with the restored body
        update_data = {
            "version": {
                "number": current_version + 1,
                "message": f"Restored from version {version_number}"
            },
            "title": current.get("title", ""),
            "type": current.get("type", "page"),
            "body": {
                "storage": {
                    "value": body,
                    "representation": "storage"
                }
            }
        }
        
        return self._make_api_request("PUT", f"/rest/api/content/{content_id}", data=update_data)
    
    # Content Export and Import
    
    def export_content(self, content_id: str, export_type: str = "pdf",
                      status: str = "current", expand: Optional[str] = None) -> bytes:
        """
        Export content to a file format.
        
        Args:
            content_id: The content ID
            export_type: The export format ("pdf", "word", "html", "xml")
            status: The content status to export ("current" or "draft")
            expand: Optional fields to expand
            
        Returns:
            Binary data of the exported file
        """
        params = {
            "status": status,
            "type": export_type
        }
        
        if expand:
            params["expand"] = expand
            
        url = f"{self.base_url}/rest/api/content/{content_id}/export"
        
        try:
            response = requests.get(
                url=url,
                params=params,
                auth=self.auth,
                headers={"Accept": "*/*"}
            )
            
            # Check for errors
            if response.status_code >= 400:
                error_msg = f"Export failed: {response.status_code} - {response.text}"
                logger.error(error_msg)
                raise ValueError(error_msg)
                
            return response.content
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Export request error: {str(e)}"
            logger.error(error_msg)
            raise ValueError(error_msg)
    
    def save_exported_content(self, content_id: str, file_path: str, export_type: str = "pdf") -> str:
        """
        Export content and save it to a file.
        
        Args:
            content_id: The content ID
            file_path: The path to save the exported file
            export_type: The export format ("pdf", "word", "html", "xml")
            
        Returns:
            Path to the saved file
        """
        content = self.export_content(content_id, export_type)
        
        try:
            with open(file_path, "wb") as f:
                f.write(content)
                
            return file_path
            
        except IOError as e:
            error_msg = f"Error saving exported content: {str(e)}"
            logger.error(error_msg)
            raise ValueError(error_msg)
    
    # Advanced Content Creation and Editing
    
    def create_page_with_attachments(self, space_key: str, title: str, content: str,
                                   parent_id: Optional[str] = None,
                                   attachments: Optional[List[str]] = None,
                                   content_type: str = "markdown") -> Dict:
        """
        Create a page with attachments in a single operation.
        
        Args:
            space_key: The space key
            title: The page title
            content: The page content
            parent_id: Optional parent page ID
            attachments: Optional list of file paths to attach
            content_type: The content type ("markdown" or "storage")
            
        Returns:
            Dictionary containing created page details with attachments
        """
        # Create the page first
        from .confluence import ConfluenceFetcher
        fetcher = ConfluenceFetcher()
        
        page = fetcher.create_page(
            space_key=space_key,
            title=title,
            content=content,
            parent_id=parent_id,
            content_type=content_type
        )
        
        # If no attachments, return the page
        if not attachments:
            return page
            
        # Add attachments
        page_id = page.get("page_id")
        attached_files = []
        
        for file_path in attachments:
            try:
                attachment = fetcher.attach_file(page_id, file_path)
                attached_files.append(attachment)
            except Exception as e:
                logger.error(f"Error attaching file {file_path}: {str(e)}")
                
        # Add attachments to the result
        page["attachments"] = attached_files
        
        return page
    
    def batch_update_content(self, updates: List[Dict]) -> List[Dict]:
        """
        Update multiple pages in batch.
        
        Args:
            updates: List of updates, each containing:
                    - content_id: The content ID
                    - title: Optional new title
                    - content: Optional new content
                    - content_type: Optional content type ("markdown" or "storage")
                    - version_message: Optional version message
            
        Returns:
            List of updated content details
        """
        from .confluence import ConfluenceFetcher
        fetcher = ConfluenceFetcher()
        
        results = []
        
        for update in updates:
            content_id = update.get("content_id")
            title = update.get("title")
            content = update.get("content")
            content_type = update.get("content_type", "markdown")
            message = update.get("version_message")
            
            try:
                result = fetcher.update_page(
                    page_id=content_id,
                    title=title,
                    content=content,
                    content_type=content_type,
                    message=message
                )
                
                results.append(result)
                
            except Exception as e:
                logger.error(f"Error updating content {content_id}: {str(e)}")
                results.append({
                    "page_id": content_id,
                    "error": str(e),
                    "updated": False
                })
                
        return results
    
    def batch_move_content(self, moves: List[Dict]) -> List[Dict]:
        """
        Move multiple pages in batch.
        
        Args:
            moves: List of moves, each containing:
                  - content_id: The content ID
                  - target_parent_id: Optional new parent ID
                  - target_space_key: Optional new space key
                  - position: Optional position
            
        Returns:
            List of moved content details
        """
        from .confluence import ConfluenceFetcher
        fetcher = ConfluenceFetcher()
        
        results = []
        
        for move in moves:
            content_id = move.get("content_id")
            target_parent_id = move.get("target_parent_id")
            target_space_key = move.get("target_space_key")
            position = move.get("position")
            
            try:
                result = fetcher.move_page(
                    page_id=content_id,
                    target_parent_id=target_parent_id,
                    target_space_key=target_space_key,
                    position=position
                )
                
                results.append(result)
                
            except Exception as e:
                logger.error(f"Error moving content {content_id}: {str(e)}")
                results.append({
                    "page_id": content_id,
                    "error": str(e),
                    "moved": False
                })
                
        return results
    
    def add_comment_with_mentions(self, content_id: str, comment_text: str, 
                                mentions: Optional[List[str]] = None) -> Dict:
        """
        Add a comment to content with user mentions.
        
        Args:
            content_id: The content ID
            comment_text: The comment text
            mentions: Optional list of usernames to mention
            
        Returns:
            Dictionary containing created comment details
        """
        # Format mentions if provided
        if mentions:
            for username in mentions:
                # Add mention markup - [~username]
                mention_markup = f"[~{username}]"
                # Ensure it's only added once
                if mention_markup not in comment_text:
                    comment_text = f"{mention_markup} {comment_text}"
        
        # Create the comment
        comment_data = {
            "type": "comment",
            "container": {
                "id": content_id,
                "type": "page"
            },
            "body": {
                "storage": {
                    "value": comment_text,
                    "representation": "storage"
                }
            }
        }
        
        return self._make_api_request("POST", "/rest/api/content", data=comment_data)
    
    def get_content_children(self, content_id: str, expand: Optional[str] = None) -> Dict:
        """
        Get children of a content (comments, attachments, etc.).
        
        Args:
            content_id: The content ID
            expand: Optional fields to expand
            
        Returns:
            Dictionary containing content children
        """
        params = {}
        if expand:
            params["expand"] = expand
            
        return self._make_api_request(
            "GET", 
            f"/rest/api/content/{content_id}/child", 
            params=params
        )