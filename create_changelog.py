from confluent_kafka.admin import AdminClient, NewTopic

admin_client = AdminClient({'bootstrap.servers': 'localhost:9092'})
topic_name = "truck_state_changelog"

new_topic = NewTopic(
    topic=topic_name,
    num_partitions=10,
    replication_factor=1,
    config={'cleanup.policy': 'compact'}
)

fs = admin_client.create_topics([new_topic])

for topic, f in fs.items():
    try:
        f.result()
        print(f"Changelog topic '{topic}' created successfully with compaction enabled.")
    except Exception as e:
        print(f"Failed to create topic '{topic}': {e}")