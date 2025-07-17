"""Test the base implementation with credentials."""

import os
import sys
import logging
from dotenv import load_dotenv
from src.mcp_atlassian.confluence import ConfluenceFetcher
from src.mcp_atlassian.jira import JiraFetcher

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                   handlers=[logging.StreamHandler(sys.stdout)])
logger = logging.getLogger("mcp-test")

# Load environment variables
load_dotenv()
logger.info(f"CONFLUENCE_URL: {os.getenv('CONFLUENCE_URL')}")
logger.info(f"CONFLUENCE_USERNAME: {os.getenv('CONFLUENCE_USERNAME')}")
logger.info(f"JIRA_URL: {os.getenv('JIRA_URL')}")
logger.info(f"JIRA_USERNAME: {os.getenv('JIRA_USERNAME')}")

def main():
    """Test basic functionality of the base implementation."""
    logger.info("Testing base implementation with credentials...")
    
    # Test Confluence connection
    if all([os.getenv("CONFLUENCE_URL"), os.getenv("CONFLUENCE_USERNAME"), os.getenv("CONFLUENCE_API_TOKEN")]):
        logger.info("Testing Confluence connection...")
        try:
            confluence_fetcher = ConfluenceFetcher()
            spaces = confluence_fetcher.confluence.get_all_spaces(start=0, limit=5)
            logger.info(f"Successfully connected to Confluence. Found {len(spaces['results'])} spaces.")
            for space in spaces['results']:
                logger.info(f"Space: {space['name']} ({space['key']})")
        except Exception as e:
            logger.error(f"Error connecting to Confluence: {e}")
    else:
        logger.warning("Confluence credentials not found in environment.")
    
    # Test Jira connection
    if all([os.getenv("JIRA_URL"), os.getenv("JIRA_USERNAME"), os.getenv("JIRA_API_TOKEN")]):
        logger.info("Testing Jira connection...")
        try:
            jira_fetcher = JiraFetcher()
            projects = jira_fetcher.jira.projects()
            project_list = projects[:5] if len(projects) > 5 else projects
            logger.info(f"Successfully connected to Jira. Found {len(projects)} projects.")
            for project in project_list:
                logger.info(f"Project: {project['name']} ({project['key']})")
        except Exception as e:
            logger.error(f"Error connecting to Jira: {e}")
    else:
        logger.warning("Jira credentials not found in environment.")

if __name__ == "__main__":
    main()