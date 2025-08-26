redpanda

Tools (11)
Resources (0)
Errors (0)

create_topic
Create a new Redpanda topic
Parameters
topic*
Topic name
partitions
Number of partitions (default: 3)
replicas
Number of replicas (default: 3)
retentionMs
Retention time in milliseconds (default: 7 days)
cleanupPolicy
Cleanup policy (delete or compact)

delete_topic
Delete a Redpanda topic
Parameters
topic*
Topic name

list_topics
List all Redpanda topics
Parameters
(No parameters)

describe_topic
Get detailed information about a Redpanda topic
Parameters
topic*
Topic name

produce_message
Produce a message to a Redpanda topic
Parameters
topic*
Topic name
key
Message key (optional)
value*
Message value (will be converted to JSON)
headers
Message headers (optional)
partition
Specific partition to produce to (optional)

consume_messages
Consume messages from a Redpanda topic
Parameters
topic*
Topic name
count
Maximum number of messages to consume (default: 10)
fromBeginning
Whether to consume from the beginning of the topic (default: false)
timeout
Timeout in milliseconds (default: 5000)
groupId
Consumer group ID (optional, default: generated)

list_consumer_groups
List all consumer groups
Parameters
(No parameters)

describe_consumer_group
Get detailed information about a consumer group
Parameters
groupId*
Consumer group ID

delete_consumer_group
Delete a consumer group
Parameters
groupId*
Consumer group ID

describe_cluster
Get information about the Redpanda cluster
Parameters
(No parameters)

get_cluster_health
Get health information about the Redpanda cluster
Parameters
(No parameters)