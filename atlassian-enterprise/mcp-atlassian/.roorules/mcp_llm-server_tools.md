llm-server

Tools (5)
Resources (0)
Errors (0)

chat
Chat with the Claude AI model
Parameters
provider
The AI provider to use (only anthropic supported)
model
Model to use (e.g., claude-3-7-sonnet-20250219)
messages*
Array of chat messages
temperature
Sampling temperature (0-2)
maxTokens
Maximum tokens to generate

toggle_logging
Enable or disable automatic conversation logging
Parameters
enabled*
Whether to enable automatic logging

list_models
List available models for a provider
Parameters
provider*
The provider to list models for

web_search
Perform a web search and generate a response based on the search results
Parameters
query*
The search query or brainstorming topic
mode
The search mode (search or brainstorm)
saveToMarkdown
Whether to save the results to a Markdown file