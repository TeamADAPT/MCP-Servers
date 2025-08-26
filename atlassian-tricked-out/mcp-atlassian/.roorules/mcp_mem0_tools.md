mem0

Tools (4)
Resources (0)
Errors (0)

add_memory
Add a new memory
Parameters
memory*
Memory content to add
user_id*
User ID to associate with the memory

add_conversation
Add a conversation as a memory
Parameters
messages*
Array of conversation messages
user_id*
User ID to associate with the memory

search_memories
Search for memories
Parameters
query*
Search query
user_id*
User ID to search memories for
limit
Maximum number of results to return

generate_with_claude
Generate a response using Claude 3.7 with memory context
Parameters
prompt*
Prompt to send to Claude
user_id*
User ID to retrieve memories for
system_prompt
Optional system prompt
temperature
Temperature for generation (0.0 to 1.0)
max_tokens
Maximum number of tokens to generate