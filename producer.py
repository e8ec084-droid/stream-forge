import json
import time
import random
from datetime import datetime, timezone
from confluent_kafka import Producer

conf = {
    'bootstrap.servers': 'localhost:9092',
    'client.id': 'truck-sensor-producer',
    'linger.ms': 50,
    'batch.size': 65536,
    'compression.type': 'lz4',
    'retries': 5,
    'retry.backoff.ms': 500,
    'delivery.timeout.ms': 120000,
    'acks': 'all'
}

producer = Producer(conf)
topic_name = "truck_telemetry"

def delivery_report(err, msg):
    if err is not None:
        print(f"Message delivery failed: {err}")

def generate_telemetry():
    truck_id = f"TRUCK_{random.randint(1, 50000)}"
    temperature = round(random.uniform(-10.0, 40.0), 2)
    timestamp = datetime.now(timezone.utc).isoformat()
    
    return {
        "truck_id": truck_id,
        "temperature": temperature,
        "timestamp": timestamp
    }

print("Starting IoT Telemetry Generator... Press Ctrl+C to stop.")

try:
    while True:
        data = generate_telemetry()
        
        producer.produce(
            topic=topic_name,
            key=data["truck_id"],
            value=json.dumps(data),
            callback=delivery_report
        )
        
        producer.poll(0)
        time.sleep(0.01)

except KeyboardInterrupt:
    print("\nStopping producer...")
finally:
    producer.flush()
    print("Producer shutdown complete.")