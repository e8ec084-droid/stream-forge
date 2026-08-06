import json
import time
import random
from datetime import datetime, timezone
from confluent_kafka import Producer

# 1. Kafka Configuration with Batch/Linger Tuning
conf = {
    'bootstrap.servers': 'localhost:9092',
    'client.id': 'truck-sensor-producer',
    'linger.ms': 10,        # Wait up to 10ms to batch messages together
    'batch.size': 16384     # Max batch size in bytes (16KB)
}

producer = Producer(conf)
topic_name = "truck_telemetry"

def delivery_report(err, msg):
    """ Callback triggered when a message is delivered or fails. """
    if err is not None:
        print(f"Message delivery failed: {err}")
    else:
        # Keeping output minimal to avoid terminal clutter during load testing
        pass

def generate_telemetry():
    """ Generates mock IoT data for trucks. """
    truck_id = f"TRUCK_{random.randint(100, 999)}"
    temperature = round(random.uniform(-10.0, 40.0), 2)
    
    # Updated: Use timezone-aware UTC datetime
    timestamp = datetime.now(timezone.utc).isoformat()
    
    return {
        "truck_id": truck_id,
        "temperature": temperature,
        "timestamp": timestamp
    }

print("Starting IoT Telemetry Generator... Press Ctrl+C to stop.")

try:
    while True:
        # 2. Generate the mock data
        data = generate_telemetry()
        
        # 3. Produce to Kafka
        # We use the truck_id as the key to ensure data for the same truck goes to the same partition
        producer.produce(
            topic=topic_name,
            key=data["truck_id"],
            value=json.dumps(data),
            callback=delivery_report
        )
        
        # Trigger any available delivery report callbacks
        producer.poll(0)
        
        # Sleep briefly to simulate real-time sensor intervals
        time.sleep(0.1)

except KeyboardInterrupt:
    print("\nStopping producer...")
finally:
    # Wait for any outstanding messages to be delivered and delivery reports to be received
    producer.flush()
    print("Producer shutdown complete.")