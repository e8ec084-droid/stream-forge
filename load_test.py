import json
import time
import random
from datetime import UTC, datetime
from confluent_kafka import Producer

conf = {
    'bootstrap.servers': 'localhost:9092',
    'client.id': 'truck-sensor-load-tester',
    'linger.ms': 50,
    'batch.size': 65536,
    'compression.type': 'lz4',
    'retries': 5,
    'retry.backoff.ms': 500
}

producer = Producer(conf)
topic_name = "truck_telemetry"
TARGET_MESSAGES = 100000

def generate_telemetry():
    return {
        "truck_id": f"TRUCK_{random.randint(1, 50000)}",
        "temperature": round(random.uniform(-10.0, 40.0), 2),
        "timestamp": datetime.now(UTC).isoformat()
    }

print(f"Starting Load Test: Sending {TARGET_MESSAGES} messages...")

start_time = time.time()

for i in range(TARGET_MESSAGES):
    data = generate_telemetry()
    producer.produce(
        topic=topic_name,
        key=data["truck_id"],
        value=json.dumps(data)
    )
    
    if i % 10000 == 0:
        producer.poll(0)

print("Flushing remaining messages to Kafka...")
producer.flush()

end_time = time.time()
duration = end_time - start_time
throughput = TARGET_MESSAGES / duration

print("--- Load Test Results ---")
print(f"Total Messages: {TARGET_MESSAGES}")
print(f"Time Taken: {duration:.2f} seconds")
print(f"Throughput: {throughput:.2f} messages/second")