import json
import time
import random
from datetime import datetime, timezone
from confluent_kafka import Producer

# 1. Kafka Configuration - Tuned for High Throughput
conf = {
    'bootstrap.servers': 'localhost:9092',
    'client.id': 'truck-sensor-load-tester',
    'linger.ms': 50,          # Increased to let more messages batch together
    'batch.size': 65536,      # Increased to 64KB batches
    'compression.type': 'lz4' # Added lightweight compression for speed
}

producer = Producer(conf)
topic_name = "truck_telemetry"
TARGET_MESSAGES = 100000

def generate_telemetry():
    """ Generates mock IoT data for trucks. """
    return {
        "truck_id": f"TRUCK_{random.randint(1, 5000)}",
        "temperature": round(random.uniform(-10.0, 40.0), 2),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

print(f"Starting Load Test: Sending {TARGET_MESSAGES} messages...")

start_time = time.time()

for i in range(TARGET_MESSAGES):
    data = generate_telemetry()
    # Produce asynchronously without printing to the terminal to maximize speed
    producer.produce(
        topic=topic_name,
        key=data["truck_id"],
        value=json.dumps(data)
    )
    
    # Periodically poll to handle delivery reports and keep buffer from overflowing
    if i % 10000 == 0:
        producer.poll(0)

# Wait for all messages in the buffer to be delivered
print("Flushing remaining messages to Kafka...")
producer.flush()

end_time = time.time()
duration = end_time - start_time
throughput = TARGET_MESSAGES / duration

print("--- Load Test Results ---")
print(f"Total Messages: {TARGET_MESSAGES}")
print(f"Time Taken: {duration:.2f} seconds")
print(f"Throughput: {throughput:.2f} messages/second")