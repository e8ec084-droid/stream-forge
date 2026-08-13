from confluent_kafka.admin import AdminClient, ConfigResource

admin_client = AdminClient({'bootstrap.servers': 'localhost:9092'})

topic_config = ConfigResource(ConfigResource.Type.TOPIC, 'truck_telemetry')
topic_config.set_config('retention.ms', '604800000')

fs = admin_client.alter_configs([topic_config])

for res, f in fs.items():
    try:
        f.result()
        print(f"Production tuning successful: 7-day retention set for {res.name}")
    except Exception as e:
        print(f"Failed to tune topic {res.name}: {e}")