NATS


Tools (14)
Resources (0)
Errors (0)
create_stream
Create a new NATS JetStream stream
Parameters
name*
Stream name
subjects*
Subjects to include in the stream
retention
Retention policy (limits, interest, workqueue)
max_msgs
Maximum number of messages in the stream
max_bytes
Maximum size of the stream in bytes
max_age
Maximum age of messages in the stream (in seconds)
storage
Storage type (file, memory)
replicas
Number of replicas
delete_stream
Delete a NATS JetStream stream
Parameters
name*
Stream name
get_stream_info
Get information about a NATS JetStream stream
Parameters
name*
Stream name
list_streams
List all NATS JetStream streams
create_consumer
Create a new NATS JetStream consumer
Parameters
stream*
Stream name
name*
Consumer name
durable
Whether the consumer is durable
deliver_subject
Subject to deliver messages to
deliver_group
Delivery group name
filter_subject
Filter subject
deliver_policy
Delivery policy (all, last, new, by_start_time, by_start_sequence)
ack_policy
Acknowledgment policy (none, all, explicit)
replay_policy
Replay policy (instant, original)
delete_consumer
Delete a NATS JetStream consumer
Parameters
stream*
Stream name
name*
Consumer name
get_consumer_info
Get information about a NATS JetStream consumer
Parameters
stream*
Stream name
name*
Consumer name
list_consumers
List all consumers for a NATS JetStream stream
Parameters
stream*
Stream name
publish_message
Publish a message to a NATS subject
Parameters
subject*
Subject to publish to
data*
Message data (will be converted to JSON)
headers
Message headers
publish_jetstream_message
Publish a message to a NATS JetStream stream
Parameters
stream
Stream name
subject*
Subject to publish to
data*
Message data (will be converted to JSON)
headers
Message headers
consume_messages
Consume messages from a NATS JetStream consumer
Parameters
stream*
Stream name
consumer*
Consumer name
batch
Maximum number of messages to consume
timeout
Timeout in milliseconds
subscribe_subject
Subscribe to a NATS subject and receive messages
Parameters
subject*
Subject to subscribe to
queue
Queue group name
max
Maximum number of messages to receive
timeout
Timeout in milliseconds
get_server_info
Get information about the NATS server
get_jetstream_account_info
Get JetStream account information