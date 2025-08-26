atlassian

Tools (27)
Resources (0)
Errors (0)

confluence_search
Search Confluence
Parameters
query*
Search query

confluence_get_page
Get a Confluence page
Parameters
page_id*
Page ID

confluence_get_comments
Get comments for a Confluence page
Parameters
page_id*
Page ID

confluence_create_page
Create a new Confluence page
Parameters
space_key*
Space key
title*
Page title
content*
Page content
parent_id
Parent page ID

confluence_create_page_from_file
Create a Confluence page from a file
Parameters
space_key*
Space key
title*
Page title
file_path*
Path to the file
parent_id
Parent page ID

confluence_attach_file
Attach a file to a Confluence page
Parameters
page_id*
Page ID
file_path*
Path to the file
comment
Comment for the attachment

confluence_get_page_history
Get the history of a Confluence page
Parameters
page_id*
Page ID

confluence_restore_page_version
Restore a previous version of a Confluence page
Parameters
page_id*
Page ID
version*
Version number to restore

confluence_update_page
Update a Confluence page
Parameters
page_id*
Page ID
title*
Page title
content*
Page content
version
Page version

confluence_move_page
Move a Confluence page
Parameters
page_id*
Page ID
target_parent_id*
Target parent page ID

confluence_get_page_tree
Get the page tree for a Confluence page
Parameters
page_id*
Page ID

jira_get_issue
Get a Jira issue
Parameters
issue_key*
Issue key

jira_search
Search Jira issues
Parameters
jql*
JQL query

jira_get_project_issues
Get issues for a Jira project
Parameters
project_key*
Project key

jira_create_project
Create a new Jira project
Parameters
key*
Project key
name*
Project name
lead*
Project lead username
type*
Project type

jira_create_issue
Create a new Jira issue
Parameters
project_key*
Project key
issue_type*
Issue type
summary*
Issue summary
description
Issue description
assignee
Assignee username
priority
Issue priority
labels
Issue labels

jira_get_issue_link_types
Get Jira issue link types
Parameters
(No parameters)

jira_create_issue_link
Create a link between Jira issues
Parameters
link_type*
Link type
inward_issue*
Inward issue key
outward_issue*
Outward issue key
comment
Comment for the link

jira_update_issue
Update a Jira issue
Parameters
issue_key*
Issue key
fields*
Fields to update

jira_transition_issue
Transition a Jira issue
Parameters
issue_key*
Issue key
transition_id*
Transition ID
comment
Comment for the transition

jira_add_comment
Add a comment to a Jira issue
Parameters
issue_key*
Issue key
comment*
Comment text

jira_create_epic
Create a new Jira epic
Parameters
project_key*
Project key
summary*
Epic summary
description
Epic description

jira_get_epic_issues
Get issues for a Jira epic
Parameters
epic_key*
Epic key

jira_update_epic_progress
Update the progress of a Jira epic
Parameters
epic_key*
Epic key

jira_get_issue_attachments
Get attachments for a Jira issue
Parameters
issue_key*
Issue key

jira_attach_file_to_issue
Attach a file to a Jira issue
Parameters
issue_key*
Issue key
file_path*
Path to the file
comment
Comment for the attachment

jira_get_issue_transitions
Get available transitions for a Jira issue
Parameters
issue_key*
Issue key