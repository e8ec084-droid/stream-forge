from confluent_kafka import Producer
import time
import json
from datetime import datetime, timezone

conf = {
    'bootstrap.servers': 'localhost:9092',
    'client.id': 'full-scale-tester',
    'linger.ms': 50,
    'batch.size': 65536,
    'compression.type': 'lz4',
    'acks': 'all',
    'queue.buffering.max.messages': 1000000
}

producer = Producer(conf)
topic_name = "truck_telemetry"
total_messages = 500000

print(f"Starting Full Scale Load Test: Sending {total_messages} messages...")
start_time = time.time()

for i in range(total_messages):
    payload = {
        "truck_id": f"TRUCK_{i % 50000}",
        "temperature": 22.5,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    producer.produce(topic_name, value=json.dumps(payload).encode('utf-8'))
    
    if i % 100000 == 0 and i > 0:
        print(f"Sent {i} messages...")
        producer.poll(0)

print("Flushing remaining messages to Kafka (this may take a moment)...")
producer.flush()

end_time = time.time()
duration = end_time - start_time
throughput = total_messages / duration

print("--- Full Scale Test Results ---")
print(f"Total Messages: {total_messages}")
print(f"Time Taken: {duration:.2f} seconds")
print(f"Throughput: {throughput:.2f} messages/second")