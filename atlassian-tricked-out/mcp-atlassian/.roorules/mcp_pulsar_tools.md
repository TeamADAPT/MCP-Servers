pulsar

Tools (25)
Resources (0)
Errors (0)

create_topic
Create a new Pulsar topic
Parameters
topic*
Topic name (e.g., persistent://public/default/my-topic)
partitions
Number of partitions

list_topics
List all topics in a namespace
Parameters
namespace
Namespace (e.g., public/default)

send_message
Send a message to a topic
Parameters
topic*
Topic name (e.g., persistent://public/default/my-topic)
message*
Message content

get_messages
Read messages from a topic
Parameters
topic*
Topic name (e.g., persistent://public/default/my-topic)
subscription*
Subscription name
count
Number of messages to retrieve

get_stats
Get topic statistics
Parameters
topic*
Topic name (e.g., persistent://public/default/my-topic)

delete_topic
Delete a Pulsar topic
Parameters
topic*
Topic name (e.g., persistent://public/default/my-topic)
force
Force delete the topic without waiting for consumers to disconnect

create_subscription
Create a subscription for a topic
Parameters
topic*
Topic name (e.g., persistent://public/default/my-topic)
subscription*
Subscription name
type
Subscription type

list_subscriptions
List all subscriptions for a topic
Parameters
topic*
Topic name (e.g., persistent://public/default/my-topic)

delete_subscription
Delete a subscription
Parameters
topic*
Topic name (e.g., persistent://public/default/my-topic)
subscription*
Subscription name
force
Force delete the subscription without waiting for consumers to disconnect

create_consumer_group
Create a consumer group for a topic
Parameters
topic*
Topic name (e.g., persistent://public/default/my-topic)
group*
Consumer group name
subscription
Subscription name (defaults to group name if not provided)
type
Subscription type

list_consumer_groups
List all consumer groups for a topic
Parameters
topic*
Topic name (e.g., persistent://public/default/my-topic)

delete_consumer_group
Delete a consumer group
Parameters
topic*
Topic name (e.g., persistent://public/default/my-topic)
group*
Consumer group name

read_with_subscription_type
Read messages using a specific subscription type
Parameters
topic*
Topic name (e.g., persistent://public/default/my-topic)
subscription*
Subscription name
type*
Subscription type
count
Number of messages to retrieve

create_schema
Create or update a schema for a topic
Parameters
topic*
Topic name (e.g., persistent://public/default/my-topic)
schema*
Schema definition

get_schema
Get the schema for a topic
Parameters
topic*
Topic name (e.g., persistent://public/default/my-topic)
version
Schema version (optional, latest if not provided)

delete_schema
Delete the schema for a topic
Parameters
topic*
Topic name (e.g., persistent://public/default/my-topic)

create_partitioned_topic
Create a partitioned topic
Parameters
topic*
Topic name (e.g., persistent://public/default/my-topic)
partitions*
Number of partitions

update_partitioned_topic
Update the number of partitions for a topic
Parameters
topic*
Topic name (e.g., persistent://public/default/my-topic)
partitions*
New number of partitions (must be greater than current)

get_partitioned_topic_metadata
Get metadata for a partitioned topic
Parameters
topic*
Topic name (e.g., persistent://public/default/my-topic)

create_multi_topic_subscription
Create a subscription for multiple topics
Parameters
topics*
List of topic names
subscription*
Subscription name
type
Subscription type

read_from_multi_topic
Read messages from multiple topics
Parameters
topics*
List of topic names
subscription*
Subscription name
count
Number of messages to retrieve

set_retention_policy
Set retention policy for a topic
Parameters
topic*
Topic name (e.g., persistent://public/default/my-topic)
retentionSizeInMB
Retention size in MB (-1 for infinite)
retentionTimeInMinutes
Retention time in minutes (-1 for infinite)

get_retention_policy
Get retention policy for a topic
Parameters
topic*
Topic name (e.g., persistent://public/default/my-topic)

enable_compaction
Enable compaction for a topic
Parameters
topic*
Topic name (e.g., persistent://public/default/my-topic)
threshold
Compaction threshold in bytes

trigger_compaction
Trigger compaction for a topic
Parameters
topic*
Topic name (e.g., persistent://public/default/my-topic)

compaction_status
Get compaction status for a topic
Parameters
topic*
Topic name (e.g., persistent://public/default/my-topic)