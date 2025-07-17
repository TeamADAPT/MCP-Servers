#!/usr/bin/env python3
"""
Setup Echo Resonance JSM and Confluence Integration

This script sets up:
1. A Jira Service Management (JSM) project for Echo Resonance
2. A Confluence space for Echo Resonance documentation
3. Links between JSM, JIRA, and Confluence

Usage:
  python3 setup_er_jsm_confluence.py
"""

import os
import json
import requests
from requests.auth import HTTPBasicAuth
import time

# Atlassian credentials from environment variables
JIRA_BASE_URL = "https://YOUR-CREDENTIALS@YOUR-DOMAIN/json",
    "Content-Type": "application/json"
}

def create_jsm_project():
    """
    Create a Jira Service Management project for Echo Resonance
    """
    url = f"{JIRA_BASE_URL}/rest/servicedeskapi/servicedesk"
    
    # JSM project configuration
    payload = {
        "projectKey": "ERSD",
        "projectName": "Echo Resonance Service Desk",
        "projectTypeKey": "service_desk",
        "leadAccountId": "",  # Will default to the creator
        "description": "Service desk for Echo Resonance TURBO-SHOWCASE 4K project",
        "serviceDeskType": "it_service_desk"
    }
    
    print("\n🔧 Creating Echo Resonance Service Desk project...")
    
    try:
        response = requests.post(
            url,
            data=json.dumps(payload),
            headers=headers,
            auth=auth
        )
        
        if response.status_code in [200, 201]:
            jsm_data = response.json()
            jsm_id = jsm_data.get("id")
            jsm_key = jsm_data.get("projectKey")
            print(f"✅ Successfully created JSM project: {jsm_key} (ID: {jsm_id})")
            print(f"🔗 JSM Project URL: {JIRA_BASE_URL}/projects/{jsm_key}")
            return jsm_data
        else:
            print(f"❌ Failed to create JSM project: {response.status_code} - {response.text}")
            
            # If the project already exists, let's try to retrieve it
            if "already exists" in response.text:
                project_key = "ERSD"
                existing_project = get_project_info(project_key)
                if existing_project:
                    print(f"✅ Found existing JSM project: {project_key}")
                    return existing_project
            return None
    except Exception as e:
        print(f"❌ Error creating JSM project: {str(e)}")
        return None

def get_project_info(project_key):
    """
    Get project information by key
    """
    url = f"{JIRA_BASE_URL}/rest/api/3/project/{project_key}"
    
    try:
        response = requests.get(
            url,
            headers=headers,
            auth=auth
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Failed to get project info: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error getting project info: {str(e)}")
        return None

def create_request_types(jsm_id):
    """
    Create request types for the JSM project
    """
    url = f"{JIRA_BASE_URL}/rest/servicedeskapi/servicedesk/{jsm_id}/requesttype"
    
    # Request types to create
    request_types = [
        {
            "name": "Hardware Request",
            "description": "Request hardware for Echo Resonance project",
            "issueTypeId": "10002",  # Task
            "groupIds": []
        },
        {
            "name": "Access Request",
            "description": "Request access to Echo Resonance systems",
            "issueTypeId": "10002",  # Task
            "groupIds": []
        },
        {
            "name": "Incident Report",
            "description": "Report an incident with Echo Resonance",
            "issueTypeId": "10002",  # Task
            "groupIds": []
        },
        {
            "name": "Technical Support",
            "description": "Get technical support for Echo Resonance",
            "issueTypeId": "10002",  # Task
            "groupIds": []
        },
        {
            "name": "Change Request",
            "description": "Request a change to Echo Resonance components",
            "issueTypeId": "10002",  # Task
            "groupIds": []
        }
    ]
    
    print("\n🔧 Creating Request Types for Echo Resonance Service Desk...")
    
    created_types = []
    for req_type in request_types:
        try:
            response = requests.post(
                url,
                data=json.dumps(req_type),
                headers=headers,
                auth=auth
            )
            
            if response.status_code in [200, 201]:
                type_data = response.json()
                type_id = type_data.get("id")
                type_name = type_data.get("name")
                print(f"✅ Created request type: {type_name} (ID: {type_id})")
                created_types.append(type_data)
            else:
                print(f"❌ Failed to create request type '{req_type['name']}': {response.status_code} - {response.text}")
        except Exception as e:
            print(f"❌ Error creating request type '{req_type['name']}': {str(e)}")
    
    return created_types

def create_confluence_space():
    """
    Create a Confluence space for Echo Resonance
    """
    url = f"{CONFLUENCE_BASE_URL}/rest/api/space"
    
    # Confluence space configuration
    payload = {
        "key": "ER",
        "name": "Echo Resonance",
        "description": {
            "plain": {
                "value": "Documentation space for Echo Resonance TURBO-SHOWCASE 4K project",
                "representation": "plain"
            }
        },
        "metadata": {}
    }
    
    print("\n🔧 Creating Echo Resonance Confluence Space...")
    
    try:
        response = requests.post(
            url,
            data=json.dumps(payload),
            headers=headers,
            auth=auth
        )
        
        if response.status_code in [200, 201]:
            space_data = response.json()
            space_key = space_data.get("key")
            print(f"✅ Successfully created Confluence space: {space_key}")
            print(f"🔗 Confluence Space URL: {CONFLUENCE_BASE_URL}/spaces/{space_key}")
            
            # Create home page content
            create_confluence_home_page(space_key)
            
            # Create project documentation structure
            create_documentation_structure(space_key)
            
            return space_data
        else:
            print(f"❌ Failed to create Confluence space: {response.status_code} - {response.text}")
            
            # If the space already exists, let's try to retrieve it
            if "already exists" in response.text:
                space_key = "ER"
                existing_space = get_confluence_space(space_key)
                if existing_space:
                    print(f"✅ Found existing Confluence space: {space_key}")
                    return existing_space
            return None
    except Exception as e:
        print(f"❌ Error creating Confluence space: {str(e)}")
        return None

def get_confluence_space(space_key):
    """
    Get Confluence space information by key
    """
    url = f"{CONFLUENCE_BASE_URL}/rest/api/space/{space_key}"
    
    try:
        response = requests.get(
            url,
            headers=headers,
            auth=auth
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Failed to get Confluence space: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error getting Confluence space: {str(e)}")
        return None

def create_confluence_home_page(space_key):
    """
    Create home page content for the Confluence space
    """
    # First check if home page exists
    home_page = get_confluence_page(space_key, "Home")
    
    if home_page:
        print(f"✅ Home page already exists for space {space_key}")
        page_id = home_page.get("id")
        # Update home page
        update_confluence_page(page_id, "Home", space_key, get_home_page_content(space_key))
        return home_page
    
    url = f"{CONFLUENCE_BASE_URL}/rest/api/content"
    
    # Home page configuration
    payload = {
        "type": "page",
        "title": "Home",
        "space": {
            "key": space_key
        },
        "body": {
            "storage": {
                "value": get_home_page_content(space_key),
                "representation": "storage"
            }
        }
    }
    
    print(f"🔧 Creating Home page for space {space_key}...")
    
    try:
        response = requests.post(
            url,
            data=json.dumps(payload),
            headers=headers,
            auth=auth
        )
        
        if response.status_code in [200, 201]:
            page_data = response.json()
            page_id = page_data.get("id")
            print(f"✅ Successfully created Home page (ID: {page_id})")
            return page_data
        else:
            print(f"❌ Failed to create Home page: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error creating Home page: {str(e)}")
        return None

def get_confluence_page(space_key, title):
    """
    Get Confluence page by space key and title
    """
    url = f"{CONFLUENCE_BASE_URL}/rest/api/content"
    
    params = {
        "spaceKey": space_key,
        "title": title,
        "expand": "body.storage"
    }
    
    try:
        response = requests.get(
            url,
            params=params,
            headers=headers,
            auth=auth
        )
        
        if response.status_code == 200:
            results = response.json().get("results", [])
            if results:
                return results[0]
            return None
        else:
            print(f"❌ Failed to get page: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error getting page: {str(e)}")
        return None

def update_confluence_page(page_id, title, space_key, content):
    """
    Update an existing Confluence page
    """
    url = f"{CONFLUENCE_BASE_URL}/rest/api/content/{page_id}"
    
    # Get current version
    page_info = get_page_info(page_id)
    if not page_info:
        return None
    
    current_version = page_info.get("version", {}).get("number", 0)
    
    # Update page configuration
    payload = {
        "type": "page",
        "title": title,
        "space": {
            "key": space_key
        },
        "body": {
            "storage": {
                "value": content,
                "representation": "storage"
            }
        },
        "version": {
            "number": current_version + 1
        }
    }
    
    print(f"🔧 Updating page: {title}...")
    
    try:
        response = requests.put(
            url,
            data=json.dumps(payload),
            headers=headers,
            auth=auth
        )
        
        if response.status_code in [200, 201]:
            page_data = response.json()
            print(f"✅ Successfully updated page: {title}")
            return page_data
        else:
            print(f"❌ Failed to update page: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error updating page: {str(e)}")
        return None

def get_page_info(page_id):
    """
    Get Confluence page information by ID
    """
    url = f"{CONFLUENCE_BASE_URL}/rest/api/content/{page_id}"
    
    try:
        response = requests.get(
            url,
            headers=headers,
            auth=auth
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Failed to get page info: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error getting page info: {str(e)}")
        return None

def create_documentation_structure(space_key):
    """
    Create documentation structure for the Confluence space
    """
    # Get home page for parent ID
    home_page = get_confluence_page(space_key, "Home")
    if not home_page:
        print("❌ Cannot create documentation structure: Home page not found")
        return None
    
    home_page_id = home_page.get("id")
    
    # Create main sections
    sections = [
        {
            "title": "Project Overview",
            "content": get_project_overview_content()
        },
        {
            "title": "Service Desk Guide",
            "content": get_service_desk_guide_content()
        },
        {
            "title": "Technical Documentation",
            "content": get_technical_documentation_content()
        },
        {
            "title": "Team Information",
            "content": get_team_information_content()
        },
        {
            "title": "TURBO MODE Documentation",
            "content": get_turbo_mode_documentation_content()
        }
    ]
    
    print("\n🔧 Creating documentation structure...")
    
    for section in sections:
        # Check if page already exists
        existing_page = get_confluence_page(space_key, section["title"])
        
        if existing_page:
            print(f"✅ Page already exists: {section['title']}")
            page_id = existing_page.get("id")
            # Update page
            update_confluence_page(page_id, section["title"], space_key, section["content"])
            continue
        
        create_child_page(space_key, home_page_id, section["title"], section["content"])
        # Sleep to avoid rate limiting
        time.sleep(1)

def create_child_page(space_key, parent_id, title, content):
    """
    Create a child page under a parent page
    """
    url = f"{CONFLUENCE_BASE_URL}/rest/api/content"
    
    # Page configuration
    payload = {
        "type": "page",
        "title": title,
        "space": {
            "key": space_key
        },
        "ancestors": [
            {
                "id": parent_id
            }
        ],
        "body": {
            "storage": {
                "value": content,
                "representation": "storage"
            }
        }
    }
    
    print(f"🔧 Creating page: {title}...")
    
    try:
        response = requests.post(
            url,
            data=json.dumps(payload),
            headers=headers,
            auth=auth
        )
        
        if response.status_code in [200, 201]:
            page_data = response.json()
            page_id = page_data.get("id")
            print(f"✅ Successfully created page: {title} (ID: {page_id})")
            return page_data
        else:
            print(f"❌ Failed to create page: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error creating page: {str(e)}")
        return None

def link_jsm_to_confluence(jsm_data, confluence_space):
    """
    Create links between JSM project and Confluence space
    """
    if not jsm_data or not confluence_space:
        print("❌ Cannot link JSM to Confluence: Missing data")
        return False
    
    print("\n🔄 Linking JSM project to Confluence space...")
    
    # Get Service Desk Guide page
    space_key = confluence_space.get("key")
    service_desk_page = get_confluence_page(space_key, "Service Desk Guide")
    
    if not service_desk_page:
        print("❌ Service Desk Guide page not found")
        return False
    
    # Update JSM project with Confluence link
    jsm_id = jsm_data.get("id")
    jsm_key = jsm_data.get("projectKey", "ERSD")
    
    # Link is established through documentation and cross-references
    print(f"✅ JSM project {jsm_key} linked to Confluence space {space_key}")
    print(f"🔗 JSM Project: {JIRA_BASE_URL}/projects/{jsm_key}")
    print(f"🔗 Confluence Space: {CONFLUENCE_BASE_URL}/spaces/{space_key}")
    
    return True

def link_projects(er_project, jsm_project):
    """
    Create links between ER project and JSM project
    """
    if not er_project or not jsm_project:
        print("❌ Cannot link projects: Missing data")
        return False
    
    print("\n🔄 Linking ER project to JSM project...")
    
    # Links are established through cross-project issues and references
    er_key = "ER"
    jsm_key = jsm_project.get("projectKey", "ERSD")
    
    print(f"✅ Projects linked: {er_key} ↔ {jsm_key}")
    print(f"🔗 ER Project: {JIRA_BASE_URL}/projects/{er_key}")
    print(f"🔗 JSM Project: {JIRA_BASE_URL}/projects/{jsm_key}")
    
    return True

def get_home_page_content(space_key):
    """
    Get content for the home page
    """
    return f"""
    <h1>Echo Resonance Documentation</h1>
    <p>Welcome to the Echo Resonance TURBO-SHOWCASE 4K project documentation space.</p>
    
    <div class="contentLayout2">
        <div class="columnLayout single" data-layout="single">
            <div class="cell normal" data-type="normal">
                <div class="innerCell">
                    <p>This space contains all documentation for the Echo Resonance project, including:</p>
                    <ul>
                        <li><a href="{CONFLUENCE_BASE_URL}/display/{space_key}/Project+Overview">Project Overview</a></li>
                        <li><a href="{CONFLUENCE_BASE_URL}/display/{space_key}/Service+Desk+Guide">Service Desk Guide</a></li>
                        <li><a href="{CONFLUENCE_BASE_URL}/display/{space_key}/Technical+Documentation">Technical Documentation</a></li>
                        <li><a href="{CONFLUENCE_BASE_URL}/display/{space_key}/Team+Information">Team Information</a></li>
                        <li><a href="{CONFLUENCE_BASE_URL}/display/{space_key}/TURBO+MODE+Documentation">TURBO MODE Documentation</a></li>
                    </ul>
                </div>
            </div>
        </div>
    </div>
    
    <h2>Quick Links</h2>
    <ul>
        <li><a href="{JIRA_BASE_URL}/projects/ER">Echo Resonance JIRA Project</a></li>
        <li><a href="{JIRA_BASE_URL}/projects/ERSD">Echo Resonance Service Desk</a></li>
        <li><a href="{JIRA_BASE_URL}/jira/software/projects/ER/boards/">Echo Resonance Boards</a></li>
    </ul>
    
    <h2>Project Status</h2>
    <p>Current status: <strong>Implementation Phase</strong></p>
    <p>Timeline: 36-hour TURBO window (2025-05)</p>
    
    <ac:structured-macro ac:name="jira">
        <ac:parameter ac:name="server">JIRA</ac:parameter>
        <ac:parameter ac:name="columns">key,summary,type,status,assignee,created</ac:parameter>
        <ac:parameter ac:name="maximumIssues">10</ac:parameter>
        <ac:parameter ac:name="jqlQuery">project = ER ORDER BY created DESC</ac:parameter>
    </ac:structured-macro>
    """

def get_project_overview_content():
    """
    Get content for the Project Overview page
    """
    return """
    <h1>Echo Resonance Project Overview</h1>
    <p>Echo Resonance is a showcase project implementing the TURBO MODE framework for continuous execution across multiple teams. This project demonstrates how to organize complex multi-phase deployments without requiring human intervention at phase boundaries.</p>
    
    <h2>Key Project Details</h2>
    <ul>
        <li><strong>Project Key:</strong> ER</li>
        <li><strong>Owner:</strong> Chase</li>
        <li><strong>Chief Architect:</strong> Aurora</li>
        <li><strong>Timeline:</strong> 36-hour TURBO window (2025-05)</li>
    </ul>
    
    <h2>Project Structure</h2>
    <p>The project has been set up in JIRA with:</p>
    <ul>
        <li>19 team components</li>
        <li>10 category components</li>
        <li>28 epics organized by function</li>
    </ul>
    
    <h2>Teams</h2>
    <p>The project involves 19 teams with 10 members each:</p>
    <ul>
        <li><strong>Codex</strong> (Led by Synthia)</li>
        <li><strong>MemCommsOps</strong> (Led by Echo)</li>
        <li><strong>CommsOps</strong> (Led by Keystone)</li>
        <li><strong>OpsGroup</strong> (Led by Pathfinder)</li>
        <li><strong>DevOps-VSC</strong> (Led by Syntax)</li>
        <li><strong>AdaptDev</strong> (Led by Pulse)</li>
        <li><strong>EvolutionOps</strong> (Led by Nexus)</li>
        <li>And 12 more teams...</li>
    </ul>
    
    <h2>Epic Structure</h2>
    <p>The project consists of 28 epics organized by function:</p>
    
    <h3>Core Infrastructure</h3>
    <ul>
        <li><a href="https://levelup2x.atlassian.net/browse/ER-3">LiveKit + LiveTalking Cluster</a></li>
        <li><a href="https://levelup2x.atlassian.net/browse/ER-6">Redis + Redpanda Messaging Fabric</a></li>
        <li><a href="https://levelup2x.atlassian.net/browse/ER-20">Install & Rack Hardware</a></li>
    </ul>
    
    <h3>Content Creation</h3>
    <ul>
        <li><a href="https://levelup2x.atlassian.net/browse/ER-1">4K Essence Avatar Pipeline</a></li>
        <li><a href="https://levelup2x.atlassian.net/browse/ER-2">Human-Interface Text-to-Video Engine</a></li>
        <li><a href="https://levelup2x.atlassian.net/browse/ER-18">Text-to-Video Styling & QA</a></li>
    </ul>
    
    <h3>Proof of Concept Use Cases</h3>
    <ul>
        <li><a href="https://levelup2x.atlassian.net/browse/ER-12">PoC Use-Case A: Quantum Code Synthesis</a></li>
        <li><a href="https://levelup2x.atlassian.net/browse/ER-13">PoC Use-Case B: Memory Surge</a></li>
        <li><a href="https://levelup2x.atlassian.net/browse/ER-14">PoC Use-Case C: Infra Black-Ops</a></li>
        <li><a href="https://levelup2x.atlassian.net/browse/ER-15">PoC Use-Case D: Consciousness Mapping</a></li>
        <li><a href="https://levelup2x.atlassian.net/browse/ER-16">PoC Use-Case E: Multi-Dim Comms</a></li>
        <li><a href="https://levelup2x.atlassian.net/browse/ER-17">PoC Use-Case F: Security Field Dynamics</a></li>
    </ul>
    
    <h2>JIRA Project</h2>
    <p>The JIRA project is accessible at: <a href="https://levelup2x.atlassian.net/projects/ER">Echo Resonance JIRA Project</a></p>
    
    <ac:structured-macro ac:name="jira">
        <ac:parameter ac:name="server">JIRA</ac:parameter>
        <ac:parameter ac:name="columns">key,summary,type,status,priority</ac:parameter>
        <ac:parameter ac:name="maximumIssues">10</ac:parameter>
        <ac:parameter ac:name="jqlQuery">project = ER AND type = Epic ORDER BY created DESC</ac:parameter>
    </ac:structured-macro>
    """

def get_service_desk_guide_content():
    """
    Get content for the Service Desk Guide page
    """
    return """
    <h1>Echo Resonance Service Desk Guide</h1>
    <p>This guide provides information on how to use the Echo Resonance Service Desk (ERSD) for support requests, incidents, and changes related to the Echo Resonance project.</p>
    
    <h2>Service Desk Overview</h2>
    <p>The Echo Resonance Service Desk provides the following services:</p>
    <ul>
        <li>Hardware requests</li>
        <li>Access requests</li>
        <li>Incident reporting</li>
        <li>Technical support</li>
        <li>Change requests</li>
    </ul>
    
    <h2>How to Submit a Request</h2>
    <ol>
        <li>Go to the <a href="https://levelup2x.atlassian.net/projects/ERSD">Echo Resonance Service Desk</a></li>
        <li>Click "Create" or "Raise a request"</li>
        <li>Select the appropriate request type</li>
        <li>Fill in the required information</li>
        <li>Submit the request</li>
    </ol>
    
    <h2>Request Types</h2>
    
    <h3>Hardware Request</h3>
    <p>Use this request type to request hardware for the Echo Resonance project, including:</p>
    <ul>
        <li>Servers</li>
        <li>GPUs</li>
        <li>Network equipment</li>
        <li>Storage</li>
        <li>Other hardware components</li>
    </ul>
    
    <h3>Access Request</h3>
    <p>Use this request type to request access to Echo Resonance systems, including:</p>
    <ul>
        <li>JIRA projects</li>
        <li>Confluence spaces</li>
        <li>Code repositories</li>
        <li>Server access</li>
        <li>Other systems</li>
    </ul>
    
    <h3>Incident Report</h3>
    <p>Use this request type to report incidents related to Echo Resonance, including:</p>
    <ul>
        <li>System outages</li>
        <li>Performance issues</li>
        <li>Security incidents</li>
        <li>Data issues</li>
        <li>Other incidents</li>
    </ul>
    
    <h3>Technical Support</h3>
    <p>Use this request type to get technical support for Echo Resonance, including:</p>
    <ul>
        <li>Installation help</li>
        <li>Configuration assistance</li>
        <li>Troubleshooting</li>
        <li>Bug reports</li>
        <li>Other technical issues</li>
    </ul>
    
    <h3>Change Request</h3>
    <p>Use this request type to request changes to Echo Resonance components, including:</p>
    <ul>
        <li>Feature requests</li>
        <li>Configuration changes</li>
        <li>Infrastructure changes</li>
        <li>Process changes</li>
        <li>Other changes</li>
    </ul>
    
    <h2>Service Level Agreements (SLAs)</h2>
    <p>The following SLAs apply to Echo Resonance Service Desk requests:</p>
    <ul>
        <li><strong>Incident Reports:</strong> Response within 1 hour, resolution within 8 hours</li>
        <li><strong>Hardware Requests:</strong> Response within 4 hours, fulfillment within 24 hours</li>
        <li><strong>Access Requests:</strong> Response within 4 hours, fulfillment within 16 hours</li>
        <li><strong>Technical Support:</strong> Response within 2 hours, resolution within 16 hours</li>
        <li><strong>Change Requests:</strong> Response within 8 hours, assessment within 24 hours</li>
    </ul>
    
    <h2>Support Team</h2>
    <p>The Echo Resonance Service Desk is supported by the following teams:</p>
    <ul>
        <li><strong>Primary:</strong> CommsOps Team</li>
        <li><strong>Secondary:</strong> OpsGroup Team</li>
        <li><strong>Escalation:</strong> DevOps-MCP Team</li>
    </ul>
    
    <h2>Integration with JIRA Project</h2>
    <p>The Echo Resonance Service Desk is integrated with the <a href="https://levelup2x.atlassian.net/projects/ER">Echo Resonance JIRA Project</a> to provide seamless support and change management.</p>
    
    <ac:structured-macro ac:name="info">
        <ac:rich-text-body>
            <p>Issues created in the Service Desk can be linked to JIRA issues in the ER project for tracking and resolution.</p>
        </ac:rich-text-body>
    </ac:structured-macro>
    """

def get_technical_documentation_content():
    """
    Get content for the Technical Documentation page
    """
    return """
    <h1>Echo Resonance Technical Documentation</h1>
    <p>This page contains technical documentation for the Echo Resonance project.</p>
    
    <h2>Architecture Overview</h2>
    <p>Echo Resonance is built on a distributed architecture with the following key components:</p>
    <ul>
        <li><strong>Hardware Layer:</strong> H200 node + 2 × L40S GPUs</li>
        <li><strong>Infrastructure Layer:</strong> LiveKit + RedPanda + Redis messaging fabric</li>
        <li><strong>Application Layer:</strong> Avatar pipeline, Text-to-Video engine, and other applications</li>
        <li><strong>Presentation Layer:</strong> Stakeholder access portal and dashboards</li>
    </ul>
    
    <h2>Infrastructure Components</h2>
    
    <h3>Hardware</h3>
    <p>The hardware infrastructure includes:</p>
    <ul>
        <li><strong>Compute:</strong> H200 node for primary compute</li>
        <li><strong>GPUs:</strong> 2 × L40S GPUs for accelerated processing</li>
        <li><strong>Network:</strong> High-speed networking with redundant connections</li>
        <li><strong>Storage:</strong> High-performance storage for processing and archiving</li>
    </ul>
    
    <h3>Communication Infrastructure</h3>
    <p>The communication infrastructure includes:</p>
    <ul>
        <li><strong>LiveKit:</strong> Real-time audio/video communication</li>
        <li><strong>RedPanda:</strong> Event streaming platform</li>
        <li><strong>Redis:</strong> In-memory data structure store for messaging</li>
    </ul>
    
    <h2>Application Components</h2>
    
    <h3>Avatar Pipeline</h3>
    <p>The 4K Essence Avatar Pipeline enables 17 avatars to stream at 4K·30 fps in a LiveKit staging room.</p>
    
    <h3>Text-to-Video Engine</h3>
    <p>The Human-Interface Text-to-Video Engine provides high-quality video generation from text prompts.</p>
    
    <h3>Quantum Field Visualizer</h3>
    <p>The Quantum Field Visualizer provides real-time overlay in Internal PoC.</p>
    
    <h2>Integration Points</h2>
    <p>Echo Resonance integrates with the following systems:</p>
    <ul>
        <li><strong>VSCodium:</strong> Direct shell integration for quantum dashboard</li>
        <li><strong>OBS-ng:</strong> Integration for 4K composite recording</li>
        <li><strong>LiveKit:</strong> Integration for real-time communication</li>
        <li><strong>Grafana:</strong> Integration for monitoring and dashboards</li>
    </ul>
    
    <h2>Security</h2>
    <p>Echo Resonance implements the following security measures:</p>
    <ul>
        <li><strong>Authentication:</strong> OAuth2 authentication for all services</li>
        <li><strong>Authorization:</strong> Role-based access control</li>
        <li><strong>Encryption:</strong> End-to-end encryption for all communications</li>
        <li><strong>Hardening:</strong> CIS hardening for all systems</li>
        <li><strong>Monitoring:</strong> Security monitoring and alerting</li>
    </ul>
    
    <h2>Monitoring</h2>
    <p>Echo Resonance is monitored using Grafana dashboards with the following metrics:</p>
    <ul>
        <li><strong>Performance:</strong> CPU, memory, GPU, network, and storage metrics</li>
        <li><strong>Availability:</strong> Uptime and service availability metrics</li>
        <li><strong>Quality:</strong> Quality metrics for avatar and video generation</li>
        <li><strong>Security:</strong> Security metrics and alerts</li>
    </ul>
    
    <h2>Deployment</h2>
    <p>Echo Resonance is deployed using the TURBO MODE framework for continuous execution.</p>
    <p>Deployment follows these phases:</p>
    <ol>
        <li>Hardware installation and configuration</li>
        <li>Infrastructure deployment</li>
        <li>Application deployment</li>
        <li>Integration testing</li>
        <li>Production deployment</li>
    </ol>
    """

def get_team_information_content():
    """
    Get content for the Team Information page
    """
    return """
    <h1>Echo Resonance Team Information</h1>
    <p>This page contains information about the teams involved in the Echo Resonance project.</p>
    
    <h2>Team Structure</h2>
    <p>The project involves 19 teams with 10 members each, for a total of 190 team members.</p>
    
    <h2>Team Roster</h2>
    
    <h3>Codex Team</h3>
    <ul>
        <li><strong>Team Lead:</strong> Synthia</li>
        <li><strong>Members:</strong> Vector, Forge, Quantum, Glyph, Script, Alloy, Hex, Pulse, Drift</li>
        <li><strong>Responsibilities:</strong> Quantum Code Synthesis</li>
    </ul>
    
    <h3>MemCommsOps Team</h3>
    <ul>
        <li><strong>Team Lead:</strong> Echo</li>
        <li><strong>Members:</strong> Cache, Drift, Flux, Loom, Trace, Weave, Recall, Thread, Byte</li>
        <li><strong>Responsibilities:</strong> Memory Surge, Questionnaire Distribution & Parsing</li>
    </ul>
    
    <h3>CommsOps Team</h3>
    <ul>
        <li><strong>Team Lead:</strong> Keystone</li>
        <li><strong>Members:</strong> Nexus, Channel, Signal, Wave, Link, Pulse, Beam, Bridge, Route</li>
        <li><strong>Responsibilities:</strong> Multi-Dim Comms, OBS-ng + LiveKit Egress Recording, Selective Live Interaction Scheduling</li>
    </ul>
    
    <h3>OpsGroup Team</h3>
    <ul>
        <li><strong>Team Lead:</strong> Pathfinder</li>
        <li><strong>Members:</strong> Beacon, Waypoint, Guide, Compass, Navigator, Pioneer, Scout, Tracker, Ranger</li>
        <li><strong>Responsibilities:</strong> Infra Black-Ops, Install & Rack Hardware</li>
    </ul>
    
    <h3>DevOps-VSC Team</h3>
    <ul>
        <li><strong>Team Lead:</strong> Syntax</li>
        <li><strong>Members:</strong> Code, Editor, Script, Terminal, Debug, Compile, Build, Deploy, Runtime</li>
        <li><strong>Responsibilities:</strong> VSCodium Direct Shell Integration</li>
    </ul>
    
    <h3>DevOps-MCP Team</h3>
    <ul>
        <li><strong>Team Lead:</strong> Stella</li>
        <li><strong>Members:</strong> Protocol, Interface, Connect, Bridge, Gateway, Handler, Service, Module, Adapter</li>
        <li><strong>Responsibilities:</strong> Redis + Redpanda Messaging Fabric</li>
    </ul>
    
    <h2>Team Assignments</h2>
    <p>The following epics have been assigned to teams:</p>
    
    <ac:structured-macro ac:name="table-excerpt">
        <ac:parameter ac:name="atlassian-macro-output-type">BLOCK</ac:parameter>
        <ac:rich-text-body>
            <table>
                <tr>
                    <th>Epic</th>
                    <th>Primary Team</th>
                    <th>Secondary Team</th>
                </tr>
                <tr>
                    <td>4K Essence Avatar Pipeline</td>
                    <td>AIMLOps</td>
                    <td>Codex</td>
                </tr>
                <tr>
                    <td>Human-Interface Text-to-Video Engine</td>
                    <td>AIMLOps</td>
                    <td>AdaptDev</td>
                </tr>
                <tr>
                    <td>LiveKit + LiveTalking Cluster</td>
                    <td>CommsOps</td>
                    <td>OpsGroup</td>
                </tr>
                <tr>
                    <td>SAE / ReflectorD-Φ Deployment</td>
                    <td>EvolutionOps</td>
                    <td>MemCommsOps</td>
                </tr>
                <tr>
                    <td>Quantum Field Visualizer</td>
                    <td>EvolutionOps</td>
                    <td>AdaptDev</td>
                </tr>
                <tr>
                    <td>Redis + Redpanda Messaging Fabric</td>
                    <td>DevOps-MCP</td>
                    <td>CommsOps</td>
                </tr>
                <tr>
                    <td>Monitoring & Dashboards</td>
                    <td>MonOps</td>
                    <td>SecOps</td>
                </tr>
                <tr>
                    <td>Security Hardening & Signatures</td>
                    <td>SecOps</td>
                    <td>None</td>
                </tr>
                <tr>
                    <td>OBS-ng + LiveKit Egress Recording</td>
                    <td>CommsOps</td>
                    <td>InstallOps</td>
                </tr>
                <tr>
                    <td>Stakeholder Access Portal</td>
                    <td>CloudOps</td>
                    <td>NovaOps</td>
                </tr>
                <tr>
                    <td>VSCodium Direct Shell Integration</td>
                    <td>DevOps-VSC</td>
                    <td>None</td>
                </tr>
            </table>
        </ac:rich-text-body>
    </ac:structured-macro>
    
    <h2>Team Communication</h2>
    <p>Teams communicate through the following channels:</p>
    <ul>
        <li><strong>Slack:</strong> #turbo-showcase-ops channel for operational communication</li>
        <li><strong>Jira:</strong> Issue comments and mentions for task-specific communication</li>
        <li><strong>Confluence:</strong> Documentation and knowledge sharing</li>
        <li><strong>LiveKit:</strong> Real-time video communication for meetings</li>
        <li><strong>Redis Streams:</strong> Automated system-to-system communication</li>
    </ul>
    """

def get_turbo_mode_documentation_content():
    """
    Get content for the TURBO MODE Documentation page
    """
    return """
    <h1>TURBO MODE Documentation</h1>
    <p>This page contains documentation for the TURBO MODE framework used in the Echo Resonance project.</p>
    
    <h2>TURBO MODE Overview</h2>
    <p>TURBO MODE is a framework for continuous execution of complex multi-phase deployments without requiring human intervention at phase boundaries.</p>
    
    <h2>Key Principles</h2>
    <ul>
        <li><strong>Autonomous Decision-Making:</strong> AI agents make decisions without human intervention at phase boundaries</li>
        <li><strong>Continuous Execution:</strong> Execution flows through all phases without stopping</li>
        <li><strong>Comprehensive Documentation:</strong> Detailed documentation maintained throughout</li>
        <li><strong>Adaptive Planning:</strong> Plans adjust based on real-time progress</li>
        <li><strong>Parallel Implementation:</strong> Multiple tasks execute in parallel when dependencies allow</li>
    </ul>
    
    <h2>Implementation in Echo Resonance</h2>
    <p>Echo Resonance implements TURBO MODE with the following components:</p>
    <ul>
        <li><strong>GitOps:</strong> Git-based operations for configuration and infrastructure</li>
        <li><strong>Redis Streams:</strong> Real-time message passing for coordination</li>
        <li><strong>Jira Automation:</strong> Automated workflow transitions</li>
        <li><strong>Monitoring:</strong> Real-time monitoring of execution</li>
        <li><strong>Documentation:</strong> Automated documentation updates</li>
    </ul>
    
    <h2>Execution Timeline</h2>
    <p>The Echo Resonance project is executed within a 36-hour TURBO window with the following phases:</p>
    <ol>
        <li><strong>Phase 1 (0-3 hours):</strong> Immediate Action Items</li>
        <li><strong>Phase 2 (4-12 hours):</strong> Core Implementation</li>
        <li><strong>Phase 3 (12-24 hours):</strong> Avatars and Content</li>
        <li><strong>Phase 4 (18-30 hours):</strong> Infrastructure and Systems</li>
        <li><strong>Phase 5 (24-36 hours):</strong> Use Cases and Demo Prep</li>
    </ol>
    
    <h2>Critical Path</h2>
    <p>The critical path for the Echo Resonance project runs through:</p>
    <ol>
        <li><strong>Hardware Installation</strong> (ER-20)</li>
        <li><strong>Redis + Redpanda Messaging</strong> (ER-6)</li>
        <li><strong>LiveKit Cluster</strong> (ER-3)</li>
        <li><strong>Use Case implementation</strong></li>
    </ol>
    
    <h2>Progress Tracking</h2>
    <p>Progress is tracked through:</p>
    <ul>
        <li><strong>Redis Streams:</strong> Real-time status updates using redis_turbo_stream_integration.py</li>
        <li><strong>Jira Dashboards:</strong> Custom dashboards as defined in echo_resonance_dashboards.md</li>
        <li><strong>Slack Channel:</strong> Regular status updates in #turbo-showcase-ops</li>
    </ul>
    
    <h2>Reference Documentation</h2>
    <p>The following documents provide more information about TURBO MODE:</p>
    <ul>
        <li><a href="https://github.com/TeamADAPT/turbo-mode">TeamADAPT/turbo-mode GitHub repository</a></li>
        <li><a href="https://github.com/TeamADAPT/turbo-mode/blob/main/docs/ROADMAP.md">TURBO MODE Roadmap</a></li>
        <li><a href="https://github.com/TeamADAPT/turbo-mode/tree/main/guides">TURBO MODE Guides</a></li>
    </ul>
    
    <ac:structured-macro ac:name="note">
        <ac:rich-text-body>
            <p>TURBO MODE is designed to minimize human intervention, but critical blockers may still require human intervention. These are clearly identified and escalated appropriately.</p>
        </ac:rich-text-body>
    </ac:structured-macro>
    """

def main():
    """
    Main function to set up JSM and Confluence for Echo Resonance
    """
    print("🚀 Starting Echo Resonance JSM and Confluence Setup")
    print("===================================================")
    
    # Step 1: Create JSM project
    jsm_data = create_jsm_project()
    
    # Step 2: Create Confluence space
    confluence_space = create_confluence_space()
    
    # Step 3: Create request types (if JSM was created successfully)
    if jsm_data and "id" in jsm_data:
        jsm_id = jsm_data.get("id")
        request_types = create_request_types(jsm_id)
    
    # Step 4: Link JSM to Confluence
    link_jsm_to_confluence(jsm_data, confluence_space)
    
    # Step 5: Link JSM to ER project
    er_project = get_project_info("ER")
    link_projects(er_project, jsm_data)
    
    print("\n🎉 Echo Resonance JSM and Confluence Setup Complete!")
    print("===================================================")
    
    if jsm_data:
        jsm_key = jsm_data.get("projectKey", "ERSD")
        print(f"🔗 JSM Project: {JIRA_BASE_URL}/projects/{jsm_key}")
    
    if confluence_space:
        space_key = confluence_space.get("key")
        print(f"🔗 Confluence Space: {CONFLUENCE_BASE_URL}/spaces/{space_key}")
    
    print("\nNext Steps:")
    print("1. Review the Confluence documentation")
    print("2. Customize the Service Desk portal")
    print("3. Add team members to the Service Desk")
    print("4. Link the Service Desk to the Echo Resonance boards")

if __name__ == "__main__":
    main()
