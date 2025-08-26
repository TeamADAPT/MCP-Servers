redis-serverglobal


Tools (15)
Resources (2)
Errors (0)
set
Set the value of a Redis key
Parameters
key*
Redis key
value*
Value to set
expiry
Expiry time in seconds (optional)
get
Get the value of a Redis key
Parameters
key*
Redis key
delete
Delete a Redis key
Parameters
key*
Redis key to delete
list
Get Redis keys matching a pattern
Parameters
pattern*
Pattern to match keys (e.g., user:*, *)
stream_publish
Publish a message to a Redis stream
Parameters
stream*
Stream name
message*
Message to publish (key-value pairs)
id
Message ID (optional, defaults to * for auto-generation)
stream_read
Read messages from a Redis stream
Parameters
stream*
Stream name
count
Maximum number of messages to read
id
Start reading from this ID (optional, defaults to 0 for all messages)
list_streams
List all Redis streams
Parameters
pattern
Pattern to match stream names (optional, defaults to *)
create_task
Create a new task in Redis
Parameters
id
Task ID (optional, will be generated if not provided)
type*
Task type
data*
Task data
status
Task status (optional, defaults to 'pending')
priority
Task priority (optional, defaults to 0)
get_task
Get a task by ID
Parameters
id*
Task ID
update_task
Update a task
Parameters
id*
Task ID
data
Task data (optional)
status
Task status (optional)
priority
Task priority (optional)
complete_task
Mark a task as completed
Parameters
id*
Task ID
result
Task result (optional)
list_tasks
List tasks based on criteria
Parameters
type
Filter by task type (optional)
status
Filter by task status (optional)
pattern
Filter by task ID pattern (optional)
set_state
Set a state value in Redis
Parameters
key*
State key
value*
State value
expiry
Expiry time in seconds (optional)
get_state
Get a state value from Redis
Parameters
key*
State key
delete_state
Delete a state from Redis
Parameters
key*
State key