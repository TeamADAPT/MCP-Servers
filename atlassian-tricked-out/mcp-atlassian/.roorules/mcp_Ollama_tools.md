Ollama

Tools (10)
Resources (0)
Errors (0)

serve
Start Ollama server
Parameters
(No parameters)

create
Create a model from a Modelfile
Parameters
name*
Name for the model
modelfile*
Path to Modelfile

show
Show information for a model
Parameters
name*
Name of the model

run
Run a model
Parameters
name*
Name of the model
prompt*
Prompt to send to the model
timeout
Timeout in milliseconds (default: 60000)

pull
Pull a model from a registry
Parameters
name*
Name of the model to pull

push
Push a model to a registry
Parameters
name*
Name of the model to push

list
List models
Parameters
(No parameters)

cp
Copy a model
Parameters
source*
Source model name
destination*
Destination model name

rm
Remove a model
Parameters
name*
Name of the model to remove

chat_completion
OpenAI-compatible chat completion API
Parameters
model*
Name of the Ollama model to use
messages*
Array of messages in the conversation
temperature
Sampling temperature (0-2)
timeout
Timeout in milliseconds (default: 60000)