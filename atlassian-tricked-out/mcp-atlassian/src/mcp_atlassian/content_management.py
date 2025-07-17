"""
Confluence Content Management Module

This module provides enhanced capabilities for managing Confluence content,
including content properties, restrictions, labels, macros, and exports.
"""

import json
import logging
import os
from typing import Dict, List, Optional, Any, Union, BinaryIO

import requests

from .config import ConfluenceConfig
from .confluence import ConfluenceFetcher  # Import for advanced capabilities

logger = logging.getLogger(__name__)


class ConfluenceContentManager:
    """Class for managing Confluence content with enhanced capabilities."""

    def __init__(self, config: ConfluenceConfig):
        """
        Initialize the Content Manager with Confluence configuration.

        Args:
            config: ConfluenceConfig object with Confluence connection details
        """
        self.base_url = config.url.rstrip("/")
        self.auth = (config.username, config.api_token)
        self.headers = {"Content-Type": "application/json"}
        self.confluence_fetcher = ConfluenceFetcher(config.url, config.username, config.api_token)
        logger.debug(f"Initialized ConfluenceContentManager with base URL: {self.base_url}")

    def _make_api_request(
        self, method: str, endpoint: str, params: Optional[Dict] = None, data: Optional[Dict] = None
    ) -> Dict:
        """
        Make an API request to Confluence.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint to call
            params: Optional query parameters
            data: Optional data to send in request body

        Returns:
            Response data as dictionary
        """
        url = f"{self.base_url}/rest/api{endpoint}"
        json_data = json.dumps(data) if data else None

        try:
            response = requests.request(
                method=method,
                url=url,
                params=params,
                data=json_data,
                headers=self.headers,
                auth=self.auth,
            )

            if response.status_code == 204:  # No Content
                return {"status": "success"}

            if response.status_code >= 400:
                error_msg = f"API request failed: {response.status_code} - {response.text}"
                logger.error(error_msg)
                raise ValueError(error_msg)

            return response.json() if response.text else {}

        except requests.RequestException as e:
            error_msg = f"Request error for {url}: {str(e)}"
            logger.error(error_msg)
            raise ValueError(error_msg)

    # Content Properties
    def get_content_properties(self, content_id: str) -> List[Dict]:
        """
        Get all properties for a content item.

        Args:
            content_id: The content ID

        Returns:
            List of property dictionaries
        """
        params = {"expand": "content,version"}
        response = self._make_api_request("GET", f"/content/{content_id}/property", params=params)
        return response.get("results", [])

    def get_content_property(self, content_id: str, property_key: str) -> Dict:
        """
        Get a specific property for a content item.

        Args:
            content_id: The content ID
            property_key: The property key

        Returns:
            Property data
        """
        params = {"expand": "content,version"}
        return self._make_api_request("GET", f"/content/{content_id}/property/{property_key}", params=params)

    def set_content_property(self, content_id: str, property_key: str, value: Any) -> Dict:
        """
        Set a property for a content item.

        Args:
            content_id: The content ID
            property_key: The property key
            value: The property value

        Returns:
            Updated property data
        """
        data = {
            "key": property_key,
            "value": value
        }
        
        try:
            # Try to update existing property
            return self._make_api_request(
                "PUT", f"/content/{content_id}/property/{property_key}", data=data
            )
        except ValueError:
            # Property doesn't exist, create it
            return self._make_api_request(
                "POST", f"/content/{content_id}/property", data=data
            )

    def delete_content_property(self, content_id: str, property_key: str) -> Dict:
        """
        Delete a property from a content item.

        Args:
            content_id: The content ID
            property_key: The property key

        Returns:
            Status response
        """
        return self._make_api_request("DELETE", f"/content/{content_id}/property/{property_key}")

    # Content Restrictions
    def get_content_restrictions(self, content_id: str) -> Dict:
        """
        Get restrictions for a content item.

        Args:
            content_id: The content ID

        Returns:
            Restrictions data
        """
        params = {"expand": "restrictions.user,restrictions.group"}
        return self._make_api_request("GET", f"/content/{content_id}/restriction", params=params)

    def add_content_restriction(
        self, content_id: str, operation: str, type_: str, subject: str
    ) -> Dict:
        """
        Add a restriction to a content item.

        Args:
            content_id: The content ID
            operation: Restriction operation (read, update)
            type_: Subject type (user, group)
            subject: User or group name

        Returns:
            Updated restrictions data
        """
        data = {
            "operation": operation,
            type_: [subject]
        }
        
        return self._make_api_request(
            "PUT", f"/content/{content_id}/restriction/byOperation/{operation}", data=data
        )

    def delete_content_restriction(
        self, content_id: str, operation: str, type_: str, subject: str
    ) -> Dict:
        """
        Delete a restriction from a content item.

        Args:
            content_id: The content ID
            operation: Restriction operation (read, update)
            type_: Subject type (user, group)
            subject: User or group name

        Returns:
            Status response
        """
        return self._make_api_request(
            "DELETE", f"/content/{content_id}/restriction/byOperation/{operation}/{type_}/{subject}"
        )

    # Labels
    def get_content_labels(self, content_id: str) -> List[Dict]:
        """
        Get labels for a content item.

        Args:
            content_id: The content ID

        Returns:
            List of label dictionaries
        """
        response = self._make_api_request("GET", f"/content/{content_id}/label")
        return response.get("results", [])

    def add_content_label(self, content_id: str, label: str) -> Dict:
        """
        Add a label to a content item.

        Args:
            content_id: The content ID
            label: The label to add

        Returns:
            Updated label data
        """
        data = [{"name": label, "prefix": "global"}]
        return self._make_api_request("POST", f"/content/{content_id}/label", data=data)

    def remove_content_label(self, content_id: str, label: str) -> Dict:
        """
        Remove a label from a content item.

        Args:
            content_id: The content ID
            label: The label to remove

        Returns:
            Status response
        """
        return self._make_api_request("DELETE", f"/content/{content_id}/label?name={label}")

    def search_content_by_label(self, label: str) -> List[Dict]:
        """
        Search for content by label.

        Args:
            label: The label to search for

        Returns:
            List of content items
        """
        cql = f"label = {label}"
        params = {
            "cql": cql,
            "limit": 100,
            "expand": "metadata.labels"
        }
        
        response = self._make_api_request("GET", "/content/search", params=params)
        return response.get("results", [])

    # Macros
    def get_available_macros(self) -> List[Dict]:
        """
        Get all available macros.

        Returns:
            List of macro dictionaries
        """
        response = self._make_api_request("GET", "/macro")
        return response.get("results", [])

    def get_macro_details(self, macro_key: str) -> Dict:
        """
        Get details for a specific macro.

        Args:
            macro_key: The macro key

        Returns:
            Macro data
        """
        return self._make_api_request("GET", f"/macro/{macro_key}")

    def add_macro_to_content(
        self, content_id: str, macro_key: str, macro_params: Dict, content_version: int
    ) -> Dict:
        """
        Add a macro to content.

        Args:
            content_id: The content ID
            macro_key: The macro key
            macro_params: Macro parameters
            content_version: Content version number

        Returns:
            Updated content data
        """
        # Get current content
        current_content = self.confluence_fetcher.get_page(content_id)
        
        # Get macro body HTML from Confluence API
        macro_data = {
            "name": macro_key,
            "params": macro_params,
            "body": ""
        }
        
        macro_url = f"{self.base_url}/rest/tinymce/1/macro/preview"
        
        try:
            response = requests.post(
                url=macro_url,
                json=macro_data,
                headers=self.headers,
                auth=self.auth
            )
            
            if response.status_code >= 400:
                error_msg = f"Macro preview failed: {response.status_code} - {response.text}"
                logger.error(error_msg)
                raise ValueError(error_msg)
                
            macro_html = response.text
            
            # Get current body
            current_body = current_content.get("body", {}).get("storage", {}).get("value", "")
            
            # Append macro HTML to body
            new_body = current_body + macro_html
            
            # Update page
            return self.confluence_fetcher.update_page(
                page_id=content_id,
                title=current_content.get("title", ""),
                body=new_body,
                version=content_version
            )
            
        except requests.RequestException as e:
            error_msg = f"Request error for {macro_url}: {str(e)}"
            logger.error(error_msg)
            raise ValueError(error_msg)

    # Versions
    def get_content_versions(self, content_id: str) -> List[Dict]:
        """
        Get all versions of a content item.

        Args:
            content_id: The content ID

        Returns:
            List of version dictionaries
        """
        params = {"expand": "content"}
        response = self._make_api_request("GET", f"/content/{content_id}/version", params=params)
        return response.get("results", [])

    def compare_content_versions(
        self, content_id: str, source_version: int, target_version: int
    ) -> Dict:
        """
        Compare two versions of a content item.

        Args:
            content_id: The content ID
            source_version: Source version number
            target_version: Target version number

        Returns:
            Comparison data
        """
        params = {
            "sourceVersion": source_version,
            "targetVersion": target_version
        }
        
        return self._make_api_request(
            "GET", f"/content/{content_id}/version/diff", params=params
        )

    def restore_content_version(self, content_id: str, version_number: int) -> Dict:
        """
        Restore a previous version of a content item.

        Args:
            content_id: The content ID
            version_number: Version number to restore

        Returns:
            Updated content data
        """
        # Get current content to get current version
        current_content = self.confluence_fetcher.get_page(content_id)
        current_version = current_content.get("version", {}).get("number", 0)
        
        # Get the version to restore
        target_version = self._make_api_request(
            "GET", f"/content/{content_id}/version/{version_number}", 
            params={"expand": "content"}
        )
        
        # Extract the body
        target_body = target_version.get("content", {}).get("body", {}).get("storage", {}).get("value", "")
        
        # Update with the old version content
        return self.confluence_fetcher.update_page(
            page_id=content_id,
            title=current_content.get("title", ""),
            body=target_body,
            version=current_version
        )

    # Export
    def export_content(
        self, content_id: str, export_format: str = "pdf", save_to_file: Optional[str] = None
    ) -> Union[Dict, str]:
        """
        Export content to a specific format.

        Args:
            content_id: The content ID
            export_format: Export format (pdf, word, html, xml)
            save_to_file: Optional file path to save the exported content

        Returns:
            Export data or file path
        """
        export_formats = {
            "pdf": "/pdf",
            "word": "/word",
            "html": "/export/html",
            "xml": "/export/xml"
        }
        
        if export_format not in export_formats:
            raise ValueError(f"Unsupported export format: {export_format}")
            
        export_url = f"{self.base_url}/rest/api/content/{content_id}{export_formats[export_format]}"
        
        try:
            # Need to use non-JSON content type for exports
            headers = {}  # Use default headers
            
            response = requests.get(
                url=export_url,
                headers=headers,
                auth=self.auth
            )
            
            if response.status_code >= 400:
                error_msg = f"Export failed: {response.status_code} - {response.text}"
                logger.error(error_msg)
                raise ValueError(error_msg)
                
            # Save to file if requested
            if save_to_file:
                os.makedirs(os.path.dirname(os.path.abspath(save_to_file)), exist_ok=True)
                
                with open(save_to_file, "wb") as f:
                    f.write(response.content)
                
                return {
                    "status": "success",
                    "message": f"Exported content saved to {save_to_file}",
                    "file_path": save_to_file
                }
            
            # Return binary data info
            return {
                "status": "success",
                "content_type": response.headers.get("Content-Type", ""),
                "content_length": len(response.content),
                "content_id": content_id,
                "export_format": export_format
            }
            
        except requests.RequestException as e:
            error_msg = f"Request error for {export_url}: {str(e)}"
            logger.error(error_msg)
            raise ValueError(error_msg)

    # Advanced Content Operations
    def create_page_with_attachments(
        self, space_key: str, title: str, body: str, attachments: Dict[str, BinaryIO], parent_id: Optional[str] = None
    ) -> Dict:
        """
        Create a page with attachments.

        Args:
            space_key: The space key
            title: Page title
            body: Page body in storage format
            attachments: Dictionary of filename: file_object pairs
            parent_id: Optional parent page ID

        Returns:
            Created page data with attachment info
        """
        # Create the page first
        page = self.confluence_fetcher.create_page(space_key, title, body, parent_id)
        page_id = page.get("id")
        
        # Add attachments
        attachment_results = []
        for filename, file_obj in attachments.items():
            try:
                attachment = self.confluence_fetcher.attach_file(
                    page_id, filename, file_obj
                )
                attachment_results.append({
                    "filename": filename,
                    "id": attachment.get("id", ""),
                    "status": "success"
                })
            except ValueError as e:
                attachment_results.append({
                    "filename": filename,
                    "status": "error",
                    "message": str(e)
                })
        
        return {
            "page": page,
            "attachments": attachment_results
        }

    def batch_update_pages(
        self, updates: List[Dict[str, Any]]
    ) -> List[Dict]:
        """
        Update multiple pages in a single operation.

        Args:
            updates: List of update dictionaries with page_id, title, body, and version

        Returns:
            List of update results
        """
        results = []
        
        for update in updates:
            try:
                page_id = update.get("page_id")
                title = update.get("title")
                body = update.get("body")
                version = update.get("version")
                
                if not all([page_id, body, version]):
                    results.append({
                        "page_id": page_id,
                        "status": "error",
                        "message": "Missing required parameters: page_id, body, version"
                    })
                    continue
                
                # Ensure we have a title
                if not title:
                    page = self.confluence_fetcher.get_page(page_id)
                    title = page.get("title", "Untitled")
                
                # Update the page
                updated_page = self.confluence_fetcher.update_page(
                    page_id=page_id,
                    title=title,
                    body=body,
                    version=version
                )
                
                results.append({
                    "page_id": page_id,
                    "status": "success",
                    "new_version": updated_page.get("version", {}).get("number", 0)
                })
                
            except ValueError as e:
                results.append({
                    "page_id": update.get("page_id", "unknown"),
                    "status": "error",
                    "message": str(e)
                })
        
        return results

    def batch_move_content(
        self, content_moves: List[Dict[str, str]]
    ) -> List[Dict]:
        """
        Move multiple content items in a single operation.

        Args:
            content_moves: List of move dictionaries with content_id, target_space, and target_parent

        Returns:
            List of move results
        """
        results = []
        
        for move in content_moves:
            try:
                content_id = move.get("content_id")
                target_space = move.get("target_space")
                target_parent = move.get("target_parent")
                
                if not content_id:
                    results.append({
                        "content_id": "unknown",
                        "status": "error",
                        "message": "Missing required parameter: content_id"
                    })
                    continue
                
                # Get current content
                content = self.confluence_fetcher.get_page(content_id)
                title = content.get("title", "")
                version = content.get("version", {}).get("number", 0)
                
                # Move the content
                moved_content = self.confluence_fetcher.move_page(
                    page_id=content_id,
                    target_space_key=target_space,
                    target_title=title,
                    target_parent_id=target_parent
                )
                
                results.append({
                    "content_id": content_id,
                    "status": "success",
                    "new_space": moved_content.get("space", {}).get("key", ""),
                    "new_parent": moved_content.get("ancestors", [{}])[-1].get("id", "") if moved_content.get("ancestors") else ""
                })
                
            except ValueError as e:
                results.append({
                    "content_id": move.get("content_id", "unknown"),
                    "status": "error",
                    "message": str(e)
                })
        
        return results

    def add_comment_with_mentions(
        self, content_id: str, comment_text: str, mentions: List[str]
    ) -> Dict:
        """
        Add a comment to content with user mentions.

        Args:
            content_id: The content ID
            comment_text: Comment text
            mentions: List of usernames to mention

        Returns:
            Created comment data
        """
        # Process mentions
        for username in mentions:
            comment_text = comment_text.replace(
                f"@{username}", 
                f"<ac:link><ri:user ri:username=\"{username}\" /></ac:link>"
            )
        
        # Create the comment
        data = {
            "type": "comment",
            "container": {"id": content_id, "type": "page"},
            "body": {
                "storage": {
                    "value": comment_text,
                    "representation": "storage"
                }
            }
        }
        
        return self._make_api_request("POST", "/content", data=data)

    def get_content_children(
        self, content_id: str, child_type: Optional[str] = None
    ) -> List[Dict]:
        """
        Get children of a content item.

        Args:
            content_id: The content ID
            child_type: Optional child type (comment, attachment)

        Returns:
            List of child content items
        """
        params = {"expand": "body.storage,version"}
        endpoint = f"/content/{content_id}/child"
        
        if child_type:
            endpoint = f"{endpoint}/{child_type}"
            
        response = self._make_api_request("GET", endpoint, params=params)
        return response.get("results", [])