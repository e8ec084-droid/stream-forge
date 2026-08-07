from collections import defaultdict

# Sample truck temperature events
events = [
    {"timestamp": "10:00", "truck_id": "T1", "temperature": 34},
    {"timestamp": "10:00", "truck_id": "T2", "temperature": 35},
    {"timestamp": "10:01", "truck_id": "T1", "temperature": 36},
    {"timestamp": "10:01", "truck_id": "T2", "temperature": 37},
    {"timestamp": "10:02", "truck_id": "T1", "temperature": 38},
]

windows = defaultdict(list)

for event in events:
    windows[event["timestamp"]].append(event["temperature"])

print("===== Tumbling Window Output =====")

for window, temps in windows.items():
    average = sum(temps) / len(temps)
    print(f"\nWindow: {window}")
    print(f"Temperatures: {temps}")
    print(f"Average Temperature: {average:.2f}")