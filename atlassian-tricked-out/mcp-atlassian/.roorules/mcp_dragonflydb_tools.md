dragonflydb

Tools (13)
Resources (0)
Errors (0)

set
Set the value of a DragonflyDB key
Parameters
key*
DragonflyDB key
value*
Value to set
expiry
Expiry time in seconds (optional)

get
Get the value of a DragonflyDB key
Parameters
key*
DragonflyDB key

delete
Delete a DragonflyDB key
Parameters
key*
DragonflyDB key to delete

list
Get DragonflyDB keys matching a pattern
Parameters
pattern*
Pattern to match keys (e.g., user:*, *)

stream_publish
Publish a message to a DragonflyDB stream
Parameters
stream*
Stream name
message*
Message to publish (key-value pairs)
id
Message ID (optional, defaults to * for auto-generation)

stream_read
Read messages from a DragonflyDB stream
Parameters
stream*
Stream name
count
Maximum number of messages to read
id
Start reading from this ID (optional, defaults to 0 for all messages)

list_streams
List all DragonflyDB streams
Parameters
pattern
Pattern to match stream names (optional, defaults to *)

vector_create_index
Create a new vector index
Parameters
index*
Index name
dimensions*
Number of dimensions for vectors (default: 1536)
distance_metric
Distance metric (COSINE, IP, L2)
index_type
Index type (HNSW, FLAT)
m
M parameter for HNSW index (default: 16)
ef_construction
EF construction parameter for HNSW index (default: 200)

vector_add
Add a vector to an index
Parameters
index*
Index name
id*
Vector ID
vector*
Vector values
metadata
Metadata to associate with the vector (optional)

vector_search
Search for similar vectors
Parameters
index*
Index name
vector*
Query vector
k
Number of results to return (default: 10)
filter
Filter expression (optional)

vector_delete
Delete a vector from an index
Parameters
index*
Index name
id*
Vector ID to delete

vector_list_indexes
List all vector indexes
Parameters
(No parameters)

vector_get_index_info
Get information about a vector index
Parameters
index*
Index name