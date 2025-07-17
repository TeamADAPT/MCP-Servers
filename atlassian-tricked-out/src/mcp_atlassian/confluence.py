import logging
import os
from typing import Optional

from atlassian import Confluence
from dotenv import load_dotenv

from .config import ConfluenceConfig
from .document_types import Document
from .preprocessing import TextPreprocessor

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger("mcp-atlassian")


class ConfluenceFetcher:
    """Handles fetching and parsing content from Confluence."""

    def __init__(self):
        url = os.getenv("CONFLUENCE_URL")
        username = os.getenv("CONFLUENCE_USERNAME")
        token = os.getenv("CONFLUENCE_API_TOKEN")

        if not all([url, username, token]):
            raise ValueError("Missing required Confluence environment variables")

        self.config = ConfluenceConfig(url=url, username=username, api_token=token)
        self.confluence = Confluence(
            url=self.config.url,
            username=self.config.username,
            password=self.config.api_token,  # API token is used as password
            cloud=True,
        )
        self.preprocessor = TextPreprocessor(self.config.url, self.confluence)

    def _process_html_content(self, html_content: str, space_key: str) -> tuple[str, str]:
        return self.preprocessor.process_html_content(html_content, space_key)
        
    def _clean_html_content(self, html_content: str) -> str:
        """
        Clean HTML content by converting it to markdown.
        This is a compatibility method for older code that uses _clean_html_content.
        """
        _, markdown = self.preprocessor.process_html_content(html_content, "")
        return markdown

    def get_spaces(self, start: int = 0, limit: int = 10):
        """Get all available spaces."""
        return self.confluence.get_all_spaces(start=start, limit=limit)

    def get_page_content(self, page_id: str, clean_html: bool = True) -> Document:
        """Get content of a specific page."""
        page = self.confluence.get_page_by_id(page_id=page_id, expand="body.storage,version,space")
        space_key = page.get("space", {}).get("key", "")

        content = page["body"]["storage"]["value"]
        processed_html, processed_markdown = self._process_html_content(content, space_key)

        # Get author information from version
        version = page.get("version", {})
        author = version.get("by", {})

        metadata = {
            "page_id": page_id,
            "title": page["title"],
            "version": version.get("number"),
            "url": f"{self.config.url}/wiki/spaces/{space_key}/pages/{page_id}",
            "space_key": space_key,
            "author_name": author.get("displayName"),
            "space_name": page.get("space", {}).get("name", ""),
            "last_modified": version.get("when"),
        }

        return Document(page_content=processed_markdown if clean_html else processed_html, metadata=metadata)

    def get_page_by_title(self, space_key: str, title: str, clean_html: bool = True) -> Optional[Document]:
        """Get page content by space key and title."""
        try:
            page = self.confluence.get_page_by_title(space=space_key, title=title, expand="body.storage,version")

            if not page:
                return None

            content = page["body"]["storage"]["value"]
            if clean_html:
                content = self._clean_html_content(content)

            metadata = {
                "page_id": page["id"],
                "title": page["title"],
                "version": page.get("version", {}).get("number"),
                "space_key": space_key,
                "url": f"{self.config.url}/wiki/spaces/{space_key}/pages/{page['id']}",
            }

            return Document(page_content=content, metadata=metadata)

        except Exception as e:
            logger.error(f"Error fetching page: {str(e)}")
            return None

    def get_space_pages(
        self, space_key: str, start: int = 0, limit: int = 10, clean_html: bool = True
    ) -> list[Document]:
        """Get all pages from a specific space."""
        pages = self.confluence.get_all_pages_from_space(
            space=space_key, start=start, limit=limit, expand="body.storage"
        )

        documents = []
        for page in pages:
            content = page["body"]["storage"]["value"]
            if clean_html:
                content = self._clean_html_content(content)

            metadata = {
                "page_id": page["id"],
                "title": page["title"],
                "space_key": space_key,
                "version": page.get("version", {}).get("number"),
                "url": f"{self.config.url}/wiki/spaces/{space_key}/pages/{page['id']}",
            }

            documents.append(Document(page_content=content, metadata=metadata))

        return documents

    def get_page_comments(self, page_id: str, clean_html: bool = True) -> list[Document]:
        """Get all comments for a specific page."""
        page = self.confluence.get_page_by_id(page_id=page_id, expand="space")
        space_key = page.get("space", {}).get("key", "")
        space_name = page.get("space", {}).get("name", "")

        comments = self.confluence.get_page_comments(content_id=page_id, expand="body.view.value,version", depth="all")[
            "results"
        ]

        comment_documents = []
        for comment in comments:
            body = comment["body"]["view"]["value"]
            processed_html, processed_markdown = self._process_html_content(body, space_key)

            # Get author information from version.by instead of author
            author = comment.get("version", {}).get("by", {})

            metadata = {
                "page_id": page_id,
                "comment_id": comment["id"],
                "last_modified": comment.get("version", {}).get("when"),
                "type": "comment",
                "author_name": author.get("displayName"),
                "space_key": space_key,
                "space_name": space_name,
            }

            comment_documents.append(
                Document(page_content=processed_markdown if clean_html else processed_html, metadata=metadata)
            )

        return comment_documents

    def search(self, cql: str, limit: int = 10) -> list[Document]:
        """Search content using Confluence Query Language (CQL)."""
        try:
            results = self.confluence.cql(cql=cql, limit=limit)
            documents = []

            for result in results.get("results", []):
                content = result.get("content", {})
                if content.get("type") == "page":
                    metadata = {
                        "page_id": content["id"],
                        "title": result["title"],
                        "space": result.get("resultGlobalContainer", {}).get("title"),
                        "url": f"{self.config.url}{result['url']}",
                        "last_modified": result.get("lastModified"),
                        "type": content["type"],
                    }

                    # Use the excerpt as page_content since it's already a good summary
                    documents.append(Document(page_content=result.get("excerpt", ""), metadata=metadata))

            return documents
        except Exception as e:
            logger.error(f"Search failed with error: {str(e)}")
            return []
            
    def create_page(self, space_key: str, title: str, content: str, parent_id: Optional[str] = None, 
                   content_type: str = "markdown") -> dict:
        """
        Create a new Confluence page.
        
        Args:
            space_key: The space key where the page will be created
            title: The title of the page
            content: The content of the page (markdown or storage format)
            parent_id: Optional parent page ID for hierarchical organization
            content_type: The type of content ('markdown' or 'storage')
            
        Returns:
            Dictionary containing the created page details
        """
        try:
            # Convert markdown to storage format if needed
            if content_type.lower() == "markdown":
                # Use the Confluence API to convert markdown to storage format
                import requests
                
                auth = (self.config.username, self.config.api_token)
                headers = {"Content-Type": "application/json"}
                
                # Use the Confluence REST API to convert markdown to storage format
                api_url = f"{self.config.url}/rest/api/contentbody/convert/storage"
                
                response = requests.post(
                    api_url,
                    json={
                        "value": content,
                        "representation": "wiki"
                    },
                    auth=auth,
                    headers=headers
                )
                
                if response.status_code >= 400:
                    error_msg = f"Failed to convert markdown: {response.status_code} - {response.text}"
                    logger.error(error_msg)
                    raise ValueError(error_msg)
                
                # Get the converted storage format
                storage_format = response.json().get("value", content)
            else:
                # Assume content is already in storage format
                storage_format = content
            
            # Create the page
            page = self.confluence.create_page(
                space=space_key,
                title=title,
                body=storage_format,
                parent_id=parent_id,
                representation="storage"
            )
            
            # Get the created page ID
            page_id = page.get("id")
            
            # Return page details
            return {
                "page_id": page_id,
                "title": title,
                "space_key": space_key,
                "url": f"{self.config.url}/wiki/spaces/{space_key}/pages/{page_id}",
                "parent_id": parent_id
            }
            
        except Exception as e:
            logger.error(f"Error creating page in space {space_key}: {str(e)}")
            raise
            
    def create_page_from_file(self, space_key: str, title: str, file_path: str, parent_id: Optional[str] = None) -> dict:
        """
        Create a new Confluence page from a markdown file.
        
        Args:
            space_key: The space key where the page will be created
            title: The title of the page
            file_path: Path to the markdown file
            parent_id: Optional parent page ID for hierarchical organization
            
        Returns:
            Dictionary containing the created page details
        """
        try:
            # Read the markdown file
            import os
            
            if not os.path.exists(file_path):
                error_msg = f"File not found: {file_path}"
                logger.error(error_msg)
                raise FileNotFoundError(error_msg)
            
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            # Create the page using the content from the file
            return self.create_page(
                space_key=space_key,
                title=title,
                content=content,
                parent_id=parent_id,
                content_type="markdown"
            )
            
        except Exception as e:
            logger.error(f"Error creating page from file {file_path}: {str(e)}")
            raise
            
    def attach_file(self, page_id: str, file_path: str, comment: Optional[str] = None) -> dict:
        """
        Attach a file to a Confluence page.
        
        Args:
            page_id: The ID of the page to attach the file to
            file_path: Path to the file to attach
            comment: Optional comment for the attachment
            
        Returns:
            Dictionary containing the attachment details
        """
        try:
            import os
            import mimetypes
            
            if not os.path.exists(file_path):
                error_msg = f"File not found: {file_path}"
                logger.error(error_msg)
                raise FileNotFoundError(error_msg)
            
            # Get the file name and content type
            file_name = os.path.basename(file_path)
            content_type, _ = mimetypes.guess_type(file_path)
            
            if content_type is None:
                content_type = "application/octet-stream"
            
            # Attach the file to the page
            attachment = self.confluence.attach_file(
                filename=file_path,
                page_id=page_id,
                title=file_name,
                comment=comment
            )
            
            # Return attachment details
            return {
                "id": attachment.get("id"),
                "title": attachment.get("title"),
                "file_name": file_name,
                "content_type": content_type,
                "page_id": page_id,
                "url": f"{self.config.url}/wiki/download/attachments/{page_id}/{file_name}"
            }
            
        except Exception as e:
            logger.error(f"Error attaching file {file_path} to page {page_id}: {str(e)}")
            raise
            
    def get_page_history(self, page_id: str, limit: int = 10) -> list[dict]:
        """
        Get the version history of a Confluence page.
        
        Args:
            page_id: The ID of the page to get the history for
            limit: Maximum number of versions to return
            
        Returns:
            List of dictionaries containing version details
        """
        try:
            # Get the current page
            page = self.confluence.get_page_by_id(
                page_id=page_id,
                expand="version"
            )
            
            # Format the response
            versions = []
            
            # Add the current version to the list
            current_version = page.get("version", {})
            current_by = current_version.get("by", {})
            versions.append({
                "number": current_version.get("number"),
                "when": current_version.get("when"),
                "message": current_version.get("message", ""),
                "author": {
                    "name": current_by.get("displayName", ""),
                    "email": current_by.get("email", ""),
                    "username": current_by.get("username", "")
                },
                "page_id": page_id,
                "minor_edit": current_version.get("minorEdit", False)
            })
            
            # Get previous versions
            current_version_number = current_version.get("number", 1)
            for version_number in range(current_version_number - 1, 0, -1):
                if len(versions) >= limit:
                    break
                    
                try:
                    # Get the previous version
                    version_page = self.confluence.get_page_by_id(
                        page_id=page_id,
                        version=version_number
                    )
                    
                    # Get version information
                    version = version_page.get("version", {})
                    by = version.get("by", {})
                    
                    # Format the version details
                    versions.append({
                        "number": version.get("number"),
                        "when": version.get("when"),
                        "message": version.get("message", ""),
                        "author": {
                            "name": by.get("displayName", ""),
                            "email": by.get("email", ""),
                            "username": by.get("username", "")
                        },
                        "page_id": page_id,
                        "minor_edit": version.get("minorEdit", False)
                    })
                except:
                    # Skip versions that don't exist
                    continue
            
            return versions
            
        except Exception as e:
            logger.error(f"Error getting page history for page {page_id}: {str(e)}")
            raise
            
    def restore_page_version(self, page_id: str, version_number: int) -> dict:
        """
        Restore a Confluence page to a previous version.
        
        Args:
            page_id: The ID of the page to restore
            version_number: The version number to restore to
            
        Returns:
            Dictionary containing the restored page details
        """
        try:
            # Get the current page
            page = self.confluence.get_page_by_id(
                page_id=page_id,
                expand="version,body.storage,space"
            )
            
            # Get the version to restore
            try:
                version_content = self.confluence.get_page_by_id(
                    page_id=page_id,
                    version=version_number,
                    expand="body.storage"
                )
            except Exception as e:
                error_msg = f"Version {version_number} not found for page {page_id}: {str(e)}"
                logger.error(error_msg)
                raise ValueError(error_msg)
            
            # Update the page with the content of the version to restore
            updated_page = self.confluence.update_page(
                page_id=page_id,
                title=page.get("title"),
                body=version_content.get("body", {}).get("storage", {}).get("value", ""),
                version=page.get("version", {}).get("number", 0) + 1,
                representation="storage",
                message=f"Restored to version {version_number}"
            )
            
            # Return the updated page details
            space_key = page.get("space", {}).get("key", "")
            return {
                "page_id": page_id,
                "title": updated_page.get("title"),
                "version": updated_page.get("version", {}).get("number"),
                "space_key": space_key,
                "url": f"{self.config.url}/wiki/spaces/{space_key}/pages/{page_id}",
                "restored_from_version": version_number
            }
            
        except Exception as e:
            logger.error(f"Error restoring page {page_id} to version {version_number}: {str(e)}")
            raise
            
    def update_page(self, page_id: str, title: Optional[str] = None, content: Optional[str] = None, 
                   content_type: str = "markdown", message: Optional[str] = None) -> dict:
        """
        Update an existing Confluence page.
        
        Args:
            page_id: The ID of the page to update
            title: Optional new title for the page
            content: Optional new content for the page
            content_type: The type of content ('markdown' or 'storage')
            message: Optional message for the update
            
        Returns:
            Dictionary containing the updated page details
        """
        try:
            # Get the current page
            page = self.confluence.get_page_by_id(
                page_id=page_id,
                expand="version,body.storage,space"
            )
            
            # Use the current title if not provided
            if not title:
                title = page.get("title")
                
            # Use the current content if not provided
            if not content:
                content = page.get("body", {}).get("storage", {}).get("value", "")
                content_type = "storage"  # Force storage type for existing content
            
            # Convert markdown to storage format if needed
            if content_type.lower() == "markdown":
                # Use the Confluence API to convert markdown to storage format
                import requests
                
                auth = (self.config.username, self.config.api_token)
                headers = {"Content-Type": "application/json"}
                
                # Use the Confluence REST API to convert markdown to storage format
                api_url = f"{self.config.url}/rest/api/contentbody/convert/storage"
                
                response = requests.post(
                    api_url,
                    json={
                        "value": content,
                        "representation": "wiki"
                    },
                    auth=auth,
                    headers=headers
                )
                
                if response.status_code >= 400:
                    error_msg = f"Failed to convert markdown: {response.status_code} - {response.text}"
                    logger.error(error_msg)
                    raise ValueError(error_msg)
                
                # Get the converted storage format
                storage_format = response.json().get("value", content)
            else:
                # Assume content is already in storage format
                storage_format = content
            
            # Get the current version number
            current_version = page.get("version", {}).get("number", 0)
            
            # Update the page
            updated_page = self.confluence.update_page(
                page_id=page_id,
                title=title,
                body=storage_format,
                version=current_version + 1,
                representation="storage",
                message=message
            )
            
            # Return the updated page details
            space_key = page.get("space", {}).get("key", "")
            return {
                "page_id": page_id,
                "title": updated_page.get("title"),
                "version": updated_page.get("version", {}).get("number"),
                "space_key": space_key,
                "url": f"{self.config.url}/wiki/spaces/{space_key}/pages/{page_id}",
                "updated": True
            }
            
        except Exception as e:
            logger.error(f"Error updating page {page_id}: {str(e)}")
            raise
            
    def move_page(self, page_id: str, target_parent_id: Optional[str] = None, 
                 target_space_key: Optional[str] = None, position: Optional[int] = None) -> dict:
        """
        Move a Confluence page to a different parent or space.
        
        Args:
            page_id: The ID of the page to move
            target_parent_id: Optional ID of the new parent page
            target_space_key: Optional key of the new space
            position: Optional position among siblings (0-based index)
            
        Returns:
            Dictionary containing the moved page details
        """
        try:
            # Get the current page
            page = self.confluence.get_page_by_id(
                page_id=page_id,
                expand="version,ancestors,space"
            )
            
            # Get the current space key
            current_space_key = page.get("space", {}).get("key", "")
            
            # Use the current space if not provided
            if not target_space_key:
                target_space_key = current_space_key
                
            # Get the current content
            content = self.confluence.get_page_by_id(
                page_id=page_id,
                expand="body.storage"
            ).get("body", {}).get("storage", {}).get("value", "")
            
            # If moving to a different space, we need to create a new page and delete the old one
            if target_space_key != current_space_key:
                # Create a new page in the target space
                new_page = self.create_page(
                    space_key=target_space_key,
                    title=page.get("title"),
                    content=content,
                    parent_id=target_parent_id,
                    content_type="storage"
                )
                
                # Delete the old page
                self.confluence.remove_page(page_id=page_id)
                
                # Return the new page details
                return {
                    "page_id": new_page.get("page_id"),
                    "title": new_page.get("title"),
                    "space_key": target_space_key,
                    "url": new_page.get("url"),
                    "moved": True,
                    "moved_to_space": True
                }
            
            # If just moving to a different parent in the same space
            if target_parent_id:
                # Use the Confluence REST API directly to move the page
                api_url = f"{self.config.url}/rest/api/content/{page_id}"
                auth = (self.config.username, self.config.api_token)
                headers = {"Content-Type": "application/json"}
                
                # Prepare the update data
                update_data = {
                    "version": {
                        "number": page.get("version", {}).get("number", 0) + 1
                    },
                    "ancestors": [
                        {
                            "id": target_parent_id
                        }
                    ]
                }
                
                # Add position if provided
                if position is not None:
                    update_data["position"] = position
                
                import requests
                response = requests.put(
                    api_url,
                    json=update_data,
                    auth=auth,
                    headers=headers
                )
                
                if response.status_code >= 400:
                    error_msg = f"Failed to move page: {response.status_code} - {response.text}"
                    logger.error(error_msg)
                    raise ValueError(error_msg)
                
                # Get the updated page
                updated_page = self.confluence.get_page_by_id(page_id=page_id)
                
                # Return the updated page details
                return {
                    "page_id": page_id,
                    "title": updated_page.get("title"),
                    "space_key": current_space_key,
                    "url": f"{self.config.url}/wiki/spaces/{current_space_key}/pages/{page_id}",
                    "moved": True,
                    "moved_to_parent": True
                }
            
            # If no target parent or space, just reorder
            if position is not None:
                # Use the Confluence REST API directly to reorder the page
                api_url = f"{self.config.url}/rest/api/content/{page_id}"
                auth = (self.config.username, self.config.api_token)
                headers = {"Content-Type": "application/json"}
                
                # Prepare the update data
                update_data = {
                    "version": {
                        "number": page.get("version", {}).get("number", 0) + 1
                    },
                    "position": position
                }
                
                import requests
                response = requests.put(
                    api_url,
                    json=update_data,
                    auth=auth,
                    headers=headers
                )
                
                if response.status_code >= 400:
                    error_msg = f"Failed to reorder page: {response.status_code} - {response.text}"
                    logger.error(error_msg)
                    raise ValueError(error_msg)
                
                # Get the updated page
                updated_page = self.confluence.get_page_by_id(page_id=page_id)
                
                # Return the updated page details
                return {
                    "page_id": page_id,
                    "title": updated_page.get("title"),
                    "space_key": current_space_key,
                    "url": f"{self.config.url}/wiki/spaces/{current_space_key}/pages/{page_id}",
                    "moved": True,
                    "reordered": True
                }
            
            # If no changes requested
            return {
                "page_id": page_id,
                "title": page.get("title"),
                "space_key": current_space_key,
                "url": f"{self.config.url}/wiki/spaces/{current_space_key}/pages/{page_id}",
                "moved": False,
                "message": "No changes requested"
            }
            
        except Exception as e:
            logger.error(f"Error moving page {page_id}: {str(e)}")
            raise
            
    def get_page_tree(self, space_key: str, root_page_id: Optional[str] = None, 
                     depth: int = 3, expand: Optional[str] = None) -> dict:
        """
        Get a hierarchical tree of pages in a space.
        
        Args:
            space_key: The space key
            root_page_id: Optional ID of the root page (if not provided, gets the space root)
            depth: Maximum depth of the tree (1-5)
            expand: Optional fields to expand
            
        Returns:
            Dictionary containing the page tree
        """
        try:
            # Limit depth to a reasonable range
            depth = max(1, min(depth, 5))
            
            # If no root page ID is provided, get the space home page
            if not root_page_id:
                space = self.confluence.get_space(space_key, expand="homepage")
                if "homepage" in space and space["homepage"]:
                    root_page_id = space["homepage"]["id"]
                else:
                    # If no homepage, return all top-level pages
                    top_pages = self.confluence.get_all_pages_from_space(
                        space=space_key,
                        start=0,
                        limit=100,
                        expand=expand,
                        status=None,
                        content_type="page"
                    )
                    
                    # Filter to only include pages without ancestors (top-level)
                    top_level_pages = []
                    for page in top_pages:
                        page_with_ancestors = self.confluence.get_page_by_id(
                            page_id=page["id"],
                            expand="ancestors"
                        )
                        if not page_with_ancestors.get("ancestors"):
                            top_level_pages.append(page)
                    
                    # Return the top-level pages
                    return {
                        "space_key": space_key,
                        "pages": [
                            {
                                "id": page["id"],
                                "title": page["title"],
                                "url": f"{self.config.url}/wiki/spaces/{space_key}/pages/{page['id']}",
                                "children": []
                            }
                            for page in top_level_pages
                        ]
                    }
            
            # Get the root page
            root_page = self.confluence.get_page_by_id(
                page_id=root_page_id,
                expand="children.page,ancestors"
            )
            
            # Build the tree recursively
            def build_tree(page_id, current_depth):
                if current_depth > depth:
                    return []
                
                # Get the page with its children
                page = self.confluence.get_page_by_id(
                    page_id=page_id,
                    expand="children.page"
                )
                
                # Get the children
                children = []
                if "children" in page and "page" in page["children"] and "results" in page["children"]["page"]:
                    for child in page["children"]["page"]["results"]:
                        children.append({
                            "id": child["id"],
                            "title": child["title"],
                            "url": f"{self.config.url}/wiki/spaces/{space_key}/pages/{child['id']}",
                            "children": build_tree(child["id"], current_depth + 1)
                        })
                
                return children
            
            # Build the tree starting from the root page
            children = build_tree(root_page_id, 1)
            
            # Return the tree
            return {
                "space_key": space_key,
                "root_page": {
                    "id": root_page["id"],
                    "title": root_page["title"],
                    "url": f"{self.config.url}/wiki/spaces/{space_key}/pages/{root_page['id']}",
                    "children": children
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting page tree for space {space_key}: {str(e)}")
            raise
