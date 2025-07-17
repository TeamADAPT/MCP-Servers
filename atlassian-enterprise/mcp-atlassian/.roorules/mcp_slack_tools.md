slack

Tools (13)
Resources (0)
Errors (0)

send_message
Send a message to a Slack channel
Parameters
channel*
Channel name or ID
text*
Message text
blocks
Optional: Slack blocks for rich formatting

create_channel
Create a new Slack channel
Parameters
name*
Channel name (lowercase letters, numbers, hyphens, and underscores only)
is_private
Whether the channel should be private
create_webhook
Whether to create a webhook for the channel

create_webhook
Create a new incoming webhook for a channel
Parameters
channel_name*
Channel name (lowercase letters, numbers, hyphens, and underscores only)
webhook_name
Optional: Name for the webhook (defaults to uppercase channel name)

list_channels
List all channels in the workspace
Parameters
limit
Maximum number of channels to return
types
Types of channels to list (e.g., "public_channel,private_channel")

post_webhook
Post a message using a webhook
Parameters
webhook*
Webhook name or URL
text*
Message text
blocks
Optional: Slack blocks for rich formatting

upload_file
Upload a file to a Slack channel
Parameters
channel*
Channel ID or name to upload to
content*
File content
filename*
Name of the file
filetype
File type (e.g., "text", "json", "javascript", "python")
title
Title of the file
initial_comment
Initial comment for the file
thread_ts
Timestamp of the message to thread the file under

read_messages
Read messages from a Slack channel
Parameters
channel*
Channel name or ID
limit
Maximum number of messages to return