import logging
import os
from datetime import datetime
from typing import Dict, List, Optional, Union, Any

from atlassian import Jira
from dotenv import load_dotenv

from .config import JiraConfig
from .document_types import Document
from .preprocessing import TextPreprocessor

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger("mcp-jira")


class JiraFetcher:
    """Handles fetching and parsing content from Jira."""

    def __init__(self):
        url = os.getenv("JIRA_URL")
        username = os.getenv("JIRA_USERNAME")
        token = os.getenv("JIRA_API_TOKEN")

        if not all([url, username, token]):
            raise ValueError("Missing required Jira environment variables")

        self.config = JiraConfig(url=url, username=username, api_token=token)
        self.jira = Jira(
            url=self.config.url,
            username=self.config.username,
            password=self.config.api_token,  # API token is used as password
            cloud=True,
        )
        self.preprocessor = TextPreprocessor(self.config.url)

    def _clean_text(self, text: str) -> str:
        """
        Clean text content by:
        1. Processing user mentions and links
        2. Converting HTML/wiki markup to markdown
        """
        if not text:
            return ""

        return self.preprocessor.clean_jira_text(text)

    def _parse_date(self, date_str: str) -> str:
        """Parse date string to handle various ISO formats."""
        if not date_str:
            return ""

        # Handle various timezone formats
        if "+0000" in date_str:
            date_str = date_str.replace("+0000", "+00:00")
        elif "-0000" in date_str:
            date_str = date_str.replace("-0000", "+00:00")
        # Handle other timezone formats like +0900, -0500, etc.
        elif len(date_str) >= 5 and date_str[-5] in "+-" and date_str[-4:].isdigit():
            # Insert colon between hours and minutes of timezone
            date_str = date_str[:-2] + ":" + date_str[-2:]

        try:
            date = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
            return date.strftime("%Y-%m-%d")
        except Exception as e:
            logger.warning(f"Error parsing date {date_str}: {e}")
            return date_str

    def get_issue(self, issue_key: str, expand: Optional[str] = None) -> Document:
        """
        Get a single issue with all its details.

        Args:
            issue_key: The issue key (e.g. 'PROJ-123')
            expand: Optional fields to expand

        Returns:
            Document containing issue content and metadata
        """
        try:
            issue = self.jira.issue(issue_key, expand=expand)

            # Process description and comments
            description = self._clean_text(issue["fields"].get("description", ""))

            # Get comments
            comments = []
            if "comment" in issue["fields"]:
                for comment in issue["fields"]["comment"]["comments"]:
                    processed_comment = self._clean_text(comment["body"])
                    created = self._parse_date(comment["created"])
                    author = comment["author"].get("displayName", "Unknown")
                    comments.append({"body": processed_comment, "created": created, "author": author})

            # Format created date using new parser
            created_date = self._parse_date(issue["fields"]["created"])

            # Get custom fields (handle objects with value property)
            name_field = issue["fields"].get("customfield_10057", {})
            dept_field = issue["fields"].get("customfield_10058", {})
            
            # Extract values from fields
            name = name_field.get("value", "") if isinstance(name_field, dict) else str(name_field)
            dept = dept_field.get("value", "") if isinstance(dept_field, dict) else str(dept_field)
            
            # Get issue links
            issue_links = []
            if "issuelinks" in issue["fields"]:
                for link in issue["fields"]["issuelinks"]:
                    link_type = link["type"]["name"]
                    inward = link["type"]["inward"]
                    outward = link["type"]["outward"]
                    
                    if "inwardIssue" in link:
                        linked_issue = link["inwardIssue"]
                        direction = "inward"
                        relationship = inward
                    elif "outwardIssue" in link:
                        linked_issue = link["outwardIssue"]
                        direction = "outward"
                        relationship = outward
                    else:
                        continue
                    
                    issue_links.append({
                        "type": link_type,
                        "relationship": relationship,
                        "direction": direction,
                        "issue_key": linked_issue["key"],
                        "issue_summary": linked_issue["fields"]["summary"],
                        "issue_type": linked_issue["fields"]["issuetype"]["name"]
                    })
            
            # Combine content in a more structured way
            content = f"""Issue: {issue_key}
Title: {issue['fields'].get('summary', '')}
Type: {issue['fields']['issuetype']['name']}
Status: {issue['fields']['status']['name']}
Created: {created_date}
Name: {name}
Dept: {dept}

Description:
{description}
"""

            # Add issue links if any
            if issue_links:
                content += "\nLinks:\n"
                for link in issue_links:
                    content += f"- {link['relationship']} {link['issue_key']} ({link['issue_type']}): {link['issue_summary']}\n"

            # Add comments
            content += "\nComments:\n" + "\n".join(
                [f"{c['created']} - {c['author']}: {c['body']}" for c in comments]
            )

            # Streamlined metadata with only essential information
            metadata = {
                "key": issue_key,
                "title": issue["fields"].get("summary", ""),
                "type": issue["fields"]["issuetype"]["name"],
                "status": issue["fields"]["status"]["name"],
                "created_date": created_date,
                "priority": issue["fields"].get("priority", {}).get("name", "None"),
                "link": f"{self.config.url.rstrip('/')}/browse/{issue_key}",
                "name": name,
                "dept": dept
            }

            return Document(page_content=content, metadata=metadata)

        except Exception as e:
            logger.error(f"Error fetching issue {issue_key}: {str(e)}")
            raise

    def search_issues(
        self, jql: str, fields: str = "*all", start: int = 0, limit: int = 50, expand: Optional[str] = None
    ) -> List[Document]:
        """
        Search for issues using JQL.

        Args:
            jql: JQL query string
            fields: Comma-separated string of fields to return
            start: Starting index
            limit: Maximum results to return
            expand: Fields to expand

        Returns:
            List of Documents containing matching issues
        """
        try:
            results = self.jira.jql(jql, fields=fields, start=start, limit=limit, expand=expand)

            documents = []
            for issue in results["issues"]:
                # Get full issue details
                doc = self.get_issue(issue["key"], expand=expand)
                documents.append(doc)

            return documents

        except Exception as e:
            logger.error(f"Error searching issues with JQL {jql}: {str(e)}")
            raise

    def get_project_issues(self, project_key: str, start: int = 0, limit: int = 50) -> List[Document]:
        """
        Get all issues for a project.

        Args:
            project_key: The project key
            start: Starting index
            limit: Maximum results to return

        Returns:
            List of Documents containing project issues
        """
        jql = f"project = {project_key} ORDER BY created DESC"
        return self.search_issues(jql, start=start, limit=limit)
        
    def get_issue_link_types(self) -> List[dict]:
        """
        Get all available issue link types.
        
        Returns:
            List of issue link types
        """
        try:
            # Use the Jira REST API directly to get issue link types
            api_url = f"{self.config.url}/rest/api/3/issueLinkType"
            auth = (self.config.username, self.config.api_token)
            headers = {"Content-Type": "application/json"}
            
            import requests
            response = requests.get(
                api_url,
                auth=auth,
                headers=headers
            )
            
            if response.status_code >= 400:
                error_msg = f"Failed to get issue link types: {response.status_code} - {response.text}"
                logger.error(error_msg)
                raise ValueError(error_msg)
            
            result = response.json()
            return result.get("issueLinkTypes", [])
            
        except Exception as e:
            logger.error(f"Error getting issue link types: {str(e)}")
            raise
    
    def create_issue_link(self, link_type: str, outward_issue: str, inward_issue: str) -> None:
        """
        Create a link between two issues.
        
        Args:
            link_type: The type of link (e.g., 'Relates', 'Blocks', 'is blocked by')
            outward_issue: The issue key that is the source of the link
            inward_issue: The issue key that is the target of the link
            
        Returns:
            None
        """
        try:
            # Use the Jira REST API directly to create the issue link
            api_url = f"{self.config.url}/rest/api/3/issueLink"
            auth = (self.config.username, self.config.api_token)
            headers = {"Content-Type": "application/json"}
            
            # Create link data
            link_data = {
                "type": {
                    "name": link_type
                },
                "outwardIssue": {
                    "key": outward_issue
                },
                "inwardIssue": {
                    "key": inward_issue
                }
            }
            
            import requests
            response = requests.post(
                api_url,
                json=link_data,
                auth=auth,
                headers=headers
            )
            
            if response.status_code >= 400:
                error_msg = f"Failed to create issue link: {response.status_code} - {response.text}"
                logger.error(error_msg)
                raise ValueError(error_msg)
            
            logger.info(f"Created link between {outward_issue} and {inward_issue}")
            
        except Exception as e:
            logger.error(f"Error creating issue link: {str(e)}")
            raise
        
    def create_project(self, key: str, name: str, project_type: str = "software", template: str = "com.pyxis.greenhopper.jira:basic-software-development-template") -> dict:
        """
        Create a new Jira project.
        
        Args:
            key: The project key (must be uppercase, e.g., 'MOXY')
            name: The project name
            project_type: The project type (software, business, service_desk)
            template: The project template
            
        Returns:
            Dictionary containing the created project details
        """
        try:
            # Ensure key is uppercase
            key = key.upper()
            
            # Get the current user's account ID
            myself = self.jira.myself()
            lead_account_id = myself["accountId"]
            
            # Create project data
            project_data = {
                "key": key,
                "name": name,
                "projectTypeKey": project_type,
                "projectTemplateKey": template,
                "leadAccountId": lead_account_id
            }
            
            # Use the Jira REST API directly to create the project
            api_url = f"{self.config.url}/rest/api/3/project"
            auth = (self.config.username, self.config.api_token)
            headers = {"Content-Type": "application/json"}
            
            import requests
            response = requests.post(
                api_url,
                json=project_data,
                auth=auth,
                headers=headers
            )
            
            if response.status_code >= 400:
                error_msg = f"Failed to create project: {response.status_code} - {response.text}"
                logger.error(error_msg)
                raise ValueError(error_msg)
            
            logger.info(f"Created project {key}: {name}")
            return response.json()
            
        except Exception as e:
            logger.error(f"Error creating project {key}: {str(e)}")
            raise
            
    def create_issue(self, project_key: str, summary: str, issue_type: str = "Task", 
                    description: str = "", labels: List[str] = None, 
                    priority: str = "Medium", parent_key: str = None, epic_link: str = None,
                    name: str = None, dept: str = None) -> dict:
        """
        Create a new Jira issue or subtask.
        
        Args:
            project_key: The project key (e.g., 'MOXY')
            summary: The issue summary/title
            issue_type: The issue type (e.g., 'Task', 'Bug', 'Story', 'Subtask')
            description: The issue description
            labels: List of labels to apply to the issue
            priority: The issue priority (e.g., 'Highest', 'High', 'Medium', 'Low', 'Lowest')
            parent_key: The parent issue key (for subtasks)
            epic_link: The Epic issue key to link this issue to (for Stories)
            name: REQUIRED: The name value for the custom field
            dept: REQUIRED: The department value for the custom field
            
        Returns:
            Dictionary containing the created issue details
        """
        try:
            # Ensure required parameters are provided
            if name is None:
                raise ValueError("'name' is a required parameter and must be provided")
            if dept is None:
                raise ValueError("'dept' is a required parameter and must be provided")
                
            # Ensure project key is uppercase
            project_key = project_key.upper()
            
            # Get the current user's account ID
            myself = self.jira.myself()
            account_id = myself["accountId"]
            
            # Format description with markdown
            if description:
                description = {
                    "type": "doc",
                    "version": 1,
                    "content": [
                        {
                            "type": "paragraph",
                            "content": [
                                {
                                    "type": "text",
                                    "text": description
                                }
                            ]
                        }
                    ]
                }
            
            # Create issue data with custom fields
            issue_data = {
                "fields": {
                    "project": {
                        "key": project_key
                    },
                    "summary": summary,  # No prefix added
                    "issuetype": {
                        "name": issue_type
                    },
                    "priority": {
                        "name": priority
                    },
                    # Add custom fields with values provided by user
                    "customfield_10057": [name],  # Name field
                    "customfield_10058": [dept]  # Dept field
                }
            }
            
            # Add description if provided
            if description:
                issue_data["fields"]["description"] = description
                
            # Labels are not supported in this Jira instance
            # Commenting out to avoid errors
            # if labels:
            #     issue_data["fields"]["labels"] = labels
                
            # Add parent if this is a subtask
            if parent_key and issue_type.lower() == "subtask":
                issue_data["fields"]["parent"] = {
                    "key": parent_key
                }
                
            # Epic link will be created after the issue is created
            
            # Use the Jira REST API directly to create the issue
            api_url = f"{self.config.url}/rest/api/3/issue"
            auth = (self.config.username, self.config.api_token)
            headers = {"Content-Type": "application/json"}
            
            import requests
            response = requests.post(
                api_url,
                json=issue_data,
                auth=auth,
                headers=headers
            )
            
            if response.status_code >= 400:
                error_msg = f"Failed to create issue: {response.status_code} - {response.text}"
                logger.error(error_msg)
                raise ValueError(error_msg)
            
            result = response.json()
            issue_key = result.get("key")
            logger.info(f"Created issue {issue_key}: {summary}")
            
            # Create a link to the Epic if provided
            if epic_link and issue_type.lower() == "story":
                self.create_issue_link("Relates", issue_key, epic_link)
                logger.info(f"Linked issue {issue_key} to Epic {epic_link}")
            
            # Get the full issue details
            issue = self.get_issue(issue_key)
            
            result = {
                "key": issue_key,
                "summary": summary,
                "type": issue_type,
                "url": f"{self.config.url.rstrip('/')}/browse/{issue_key}",
                "project": project_key
            }
            
            # Add epic link information if provided
            if epic_link and issue_type.lower() == "story":
                result["epic_link"] = epic_link
                
            return result
            
        except Exception as e:
            logger.error(f"Error creating issue in project {project_key}: {str(e)}")
            raise
            
    def update_issue(self, issue_key: str, summary: Optional[str] = None, 
                    description: Optional[str] = None, issue_type: Optional[str] = None,
                    priority: Optional[str] = None, fields: Optional[Dict[str, Any]] = None) -> dict:
        """
        Update an existing Jira issue.
        
        Args:
            issue_key: The issue key to update (e.g., 'PROJ-123')
            summary: Optional new summary/title
            description: Optional new description
            issue_type: Optional new issue type
            priority: Optional new priority
            fields: Optional dictionary of additional fields to update
            
        Returns:
            Dictionary containing the updated issue details
        """
        try:
            # Get the current issue to get its version number
            current_issue = self.jira.issue(issue_key)
            version = current_issue["fields"]["versions"][0]["id"] if current_issue.get("fields", {}).get("versions") else None
            
            # Prepare update data
            update_data = {
                "fields": {}
            }
            
            # Add fields that are provided
            if summary:
                update_data["fields"]["summary"] = summary
                
            if description:
                # Format description with markdown
                update_data["fields"]["description"] = {
                    "type": "doc",
                    "version": 1,
                    "content": [
                        {
                            "type": "paragraph",
                            "content": [
                                {
                                    "type": "text",
                                    "text": description
                                }
                            ]
                        }
                    ]
                }
                
            if issue_type:
                update_data["fields"]["issuetype"] = {
                    "name": issue_type
                }
                
            if priority:
                update_data["fields"]["priority"] = {
                    "name": priority
                }
                
            # Add any additional fields
            if fields:
                for field_key, field_value in fields.items():
                    update_data["fields"][field_key] = field_value
            
            # Use the Jira REST API directly to update the issue
            api_url = f"{self.config.url}/rest/api/3/issue/{issue_key}"
            auth = (self.config.username, self.config.api_token)
            headers = {"Content-Type": "application/json"}
            
            import requests
            response = requests.put(
                api_url,
                json=update_data,
                auth=auth,
                headers=headers
            )
            
            if response.status_code >= 400:
                error_msg = f"Failed to update issue: {response.status_code} - {response.text}"
                logger.error(error_msg)
                raise ValueError(error_msg)
            
            logger.info(f"Updated issue {issue_key}")
            
            # Get the updated issue details
            updated_issue = self.get_issue(issue_key)
            
            result = {
                "key": issue_key,
                "summary": updated_issue.metadata.get("title"),
                "type": updated_issue.metadata.get("type"),
                "status": updated_issue.metadata.get("status"),
                "url": updated_issue.metadata.get("link"),
                "updated": True
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error updating issue {issue_key}: {str(e)}")
            raise
            
    def transition_issue(self, issue_key: str, transition_name: str) -> dict:
        """
        Transition an issue to a different status.
        
        Args:
            issue_key: The issue key to transition (e.g., 'PROJ-123')
            transition_name: The name of the transition to perform (e.g., 'In Progress', 'Done')
            
        Returns:
            Dictionary containing the transitioned issue details
        """
        try:
            # Get available transitions for the issue
            transitions = self.jira.get_issue_transitions(issue_key)
            
            # Find the transition ID that matches the requested name
            transition_id = None
            for transition in transitions:
                if transition["name"].lower() == transition_name.lower():
                    transition_id = transition["id"]
                    break
                    
            if not transition_id:
                available_transitions = ", ".join([t["name"] for t in transitions])
                error_msg = f"Transition '{transition_name}' not found for issue {issue_key}. Available transitions: {available_transitions}"
                logger.error(error_msg)
                raise ValueError(error_msg)
            
            # Perform the transition
            self.jira.issue_transition(issue_key, transition_id)
            
            logger.info(f"Transitioned issue {issue_key} to '{transition_name}'")
            
            # Get the updated issue details
            updated_issue = self.get_issue(issue_key)
            
            result = {
                "key": issue_key,
                "summary": updated_issue.metadata.get("title"),
                "type": updated_issue.metadata.get("type"),
                "status": updated_issue.metadata.get("status"),
                "url": updated_issue.metadata.get("link"),
                "transitioned_to": transition_name
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error transitioning issue {issue_key}: {str(e)}")
            raise
            
    def add_comment(self, issue_key: str, comment: str) -> dict:
        """
        Add a comment to an issue.
        
        Args:
            issue_key: The issue key to comment on (e.g., 'PROJ-123')
            comment: The comment text
            
        Returns:
            Dictionary containing the comment details
        """
        try:
            # Format comment with markdown
            comment_data = {
                "body": {
                    "type": "doc",
                    "version": 1,
                    "content": [
                        {
                            "type": "paragraph",
                            "content": [
                                {
                                    "type": "text",
                                    "text": comment
                                }
                            ]
                        }
                    ]
                }
            }
            
            # Use the Jira REST API directly to add the comment
            api_url = f"{self.config.url}/rest/api/3/issue/{issue_key}/comment"
            auth = (self.config.username, self.config.api_token)
            headers = {"Content-Type": "application/json"}
            
            import requests
            response = requests.post(
                api_url,
                json=comment_data,
                auth=auth,
                headers=headers
            )
            
            if response.status_code >= 400:
                error_msg = f"Failed to add comment: {response.status_code} - {response.text}"
                logger.error(error_msg)
                raise ValueError(error_msg)
            
            result = response.json()
            
            logger.info(f"Added comment to issue {issue_key}")
            
            # Format the response
            comment_result = {
                "id": result.get("id"),
                "issue_key": issue_key,
                "author": result.get("author", {}).get("displayName"),
                "created": self._parse_date(result.get("created")),
                "body": comment
            }
            
            return comment_result
            
        except Exception as e:
            logger.error(f"Error adding comment to issue {issue_key}: {str(e)}")
            raise
            
    def get_issue_transitions(self, issue_key: str) -> List[dict]:
        """
        Get available transitions for an issue.
        
        Args:
            issue_key: The issue key (e.g., 'PROJ-123')
            
        Returns:
            List of available transitions
        """
        try:
            transitions = self.jira.get_issue_transitions(issue_key)
            
            # Format the response
            formatted_transitions = []
            for transition in transitions:
                formatted_transitions.append({
                    "id": transition.get("id"),
                    "name": transition.get("name"),
                    "to_status": transition.get("to", {}).get("name")
                })
                
            return formatted_transitions
            
        except Exception as e:
            logger.error(f"Error getting transitions for issue {issue_key}: {str(e)}")
            raise
            
    def create_epic(self, project_key: str, summary: str, description: str = "", 
                  priority: str = "Medium", epic_name: Optional[str] = None, 
                  epic_color: Optional[str] = None, name: str = None, dept: str = None) -> dict:
        """
        Create a new Epic in Jira.
        
        Args:
            project_key: The project key (e.g., 'MOXY')
            summary: The Epic summary/title
            description: The Epic description
            priority: The Epic priority (e.g., 'Highest', 'High', 'Medium', 'Low', 'Lowest')
            epic_name: Optional short name for the Epic (displayed on the Epic card)
            epic_color: Optional color for the Epic (e.g., 'ghx-label-1', 'ghx-label-2', etc.)
            name: REQUIRED: The name value for the custom field
            dept: REQUIRED: The department value for the custom field
            
        Returns:
            Dictionary containing the created Epic details
        """
        try:
            # Ensure required parameters are provided
            if name is None:
                raise ValueError("'name' is a required parameter and must be provided")
            if dept is None:
                raise ValueError("'dept' is a required parameter and must be provided")
                
            # Ensure project key is uppercase
            project_key = project_key.upper()
            
            # If epic_name is not provided, use the summary
            if not epic_name:
                epic_name = summary[:60] if len(summary) > 60 else summary
                
            # Format description with markdown
            if description:
                description = {
                    "type": "doc",
                    "version": 1,
                    "content": [
                        {
                            "type": "paragraph",
                            "content": [
                                {
                                    "type": "text",
                                    "text": description
                                }
                            ]
                        }
                    ]
                }
            
            # Create Epic data with custom fields
            epic_data = {
                "fields": {
                    "project": {
                        "key": project_key
                    },
                    "summary": summary,  # No prefix added
                    "issuetype": {
                        "name": "Epic"
                    },
                    "priority": {
                        "name": priority
                    },
                    # Add custom fields with values provided by user
                    "customfield_10057": [name],  # Name field
                    "customfield_10058": [dept],  # Dept field
                    "customfield_10011": epic_name  # Epic Name field
                }
            }
            
            # Add description if provided
            if description:
                epic_data["fields"]["description"] = description
                
            # Add epic color if provided
            if epic_color:
                epic_data["fields"]["customfield_10010"] = epic_color
                
            # Use the Jira REST API directly to create the Epic
            api_url = f"{self.config.url}/rest/api/3/issue"
            auth = (self.config.username, self.config.api_token)
            headers = {"Content-Type": "application/json"}
            
            import requests
            response = requests.post(
                api_url,
                json=epic_data,
                auth=auth,
                headers=headers
            )
            
            if response.status_code >= 400:
                error_msg = f"Failed to create Epic: {response.status_code} - {response.text}"
                logger.error(error_msg)
                raise ValueError(error_msg)
            
            result = response.json()
            epic_key = result.get("key")
            logger.info(f"Created Epic {epic_key}: {summary}")
            
            # Get the full Epic details
            epic = self.get_issue(epic_key)
            
            result = {
                "key": epic_key,
                "summary": summary,
                "epic_name": epic_name,
                "type": "Epic",
                "url": f"{self.config.url.rstrip('/')}/browse/{epic_key}",
                "project": project_key
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error creating Epic in project {project_key}: {str(e)}")
            raise
            
    def get_epic_issues(self, epic_key: str, include_subtasks: bool = True) -> dict:
        """
        Get all issues linked to an Epic in a structured format.
        
        Args:
            epic_key: The Epic issue key (e.g., 'PROJ-123')
            include_subtasks: Whether to include subtasks of issues linked to the Epic
            
        Returns:
            Dictionary containing the Epic details and linked issues
        """
        try:
            # Verify that the issue is an Epic
            epic = self.get_issue(epic_key)
            if epic.metadata.get("type") != "Epic":
                error_msg = f"Issue {epic_key} is not an Epic"
                logger.error(error_msg)
                raise ValueError(error_msg)
            
            # Get all issues linked to the Epic
            jql = f"'Epic Link' = {epic_key} ORDER BY created DESC"
            linked_issues = self.search_issues(jql)
            
            # Get subtasks if requested
            if include_subtasks:
                for issue in linked_issues:
                    issue_key = issue.metadata.get("key")
                    subtask_jql = f"parent = {issue_key} ORDER BY created DESC"
                    subtasks = self.search_issues(subtask_jql)
                    if subtasks:
                        # Add subtasks to the issue metadata
                        issue.metadata["subtasks"] = [
                            {
                                "key": subtask.metadata.get("key"),
                                "summary": subtask.metadata.get("title"),
                                "status": subtask.metadata.get("status"),
                                "type": subtask.metadata.get("type")
                            }
                            for subtask in subtasks
                        ]
            
            # Format the response
            result = {
                "epic": {
                    "key": epic_key,
                    "summary": epic.metadata.get("title"),
                    "status": epic.metadata.get("status"),
                    "url": epic.metadata.get("link")
                },
                "issues": [
                    {
                        "key": issue.metadata.get("key"),
                        "summary": issue.metadata.get("title"),
                        "status": issue.metadata.get("status"),
                        "type": issue.metadata.get("type"),
                        "url": issue.metadata.get("link"),
                        "subtasks": issue.metadata.get("subtasks", []) if include_subtasks else []
                    }
                    for issue in linked_issues
                ],
                "total_issues": len(linked_issues),
                "completed_issues": len([issue for issue in linked_issues if issue.metadata.get("status") == "Done"])
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting issues for Epic {epic_key}: {str(e)}")
            raise
            
    def update_epic_progress(self, epic_key: str) -> dict:
        """
        Update Epic progress tracking based on linked issues.
        
        Args:
            epic_key: The Epic issue key (e.g., 'PROJ-123')
            
        Returns:
            Dictionary containing the updated Epic progress
        """
        try:
            # Get all issues linked to the Epic
            epic_issues = self.get_epic_issues(epic_key)
            
            # Calculate progress
            total_issues = epic_issues.get("total_issues", 0)
            completed_issues = epic_issues.get("completed_issues", 0)
            
            progress_percentage = 0
            if total_issues > 0:
                progress_percentage = int((completed_issues / total_issues) * 100)
            
            # Update the Epic with the progress
            # Note: This is a simplified implementation as the actual Epic progress
            # field may vary depending on the Jira instance configuration
            fields = {
                "customfield_10014": progress_percentage  # Example field for Epic progress
            }
            
            # Update the Epic
            self.update_issue(epic_key, fields=fields)
            
            # Return the progress information
            result = {
                "epic_key": epic_key,
                "total_issues": total_issues,
                "completed_issues": completed_issues,
                "progress_percentage": progress_percentage,
                "updated": True
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error updating progress for Epic {epic_key}: {str(e)}")
            raise
            
    def get_issue_attachments(self, issue_key: str) -> List[dict]:
        """
        Get all attachments for an issue.
        
        Args:
            issue_key: The issue key (e.g., 'PROJ-123')
            
        Returns:
            List of attachment details
        """
        try:
            # Get the issue with the attachments field
            issue = self.jira.issue(issue_key, fields="attachment")
            
            # Extract attachments
            attachments = []
            if "attachment" in issue["fields"]:
                for attachment in issue["fields"]["attachment"]:
                    attachments.append({
                        "id": attachment.get("id"),
                        "filename": attachment.get("filename"),
                        "size": attachment.get("size"),
                        "content_type": attachment.get("mimeType"),
                        "created": self._parse_date(attachment.get("created")),
                        "author": attachment.get("author", {}).get("displayName"),
                        "url": attachment.get("content")
                    })
            
            return attachments
            
        except Exception as e:
            logger.error(f"Error getting attachments for issue {issue_key}: {str(e)}")
            raise
            
    def attach_file_to_issue(self, issue_key: str, file_path: str, comment: Optional[str] = None) -> dict:
        """
        Attach a file to a Jira issue.
        
        Args:
            issue_key: The issue key (e.g., 'PROJ-123')
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
            
            # Attach the file to the issue
            attachment = self.jira.add_attachment(
                issue_key=issue_key,
                attachment=file_path,
                filename=file_name
            )
            
            # Return attachment details
            return {
                "id": attachment.get("id"),
                "filename": attachment.get("filename"),
                "size": attachment.get("size"),
                "content_type": content_type,
                "issue_key": issue_key,
                "url": attachment.get("content")
            }
            
        except Exception as e:
            logger.error(f"Error attaching file {file_path} to issue {issue_key}: {str(e)}")
            raise
