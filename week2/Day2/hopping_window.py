from collections import defaultdict

# Sample truck temperature events
events = [
    {"timestamp": "10:00", "truck_id": "T1", "temperature": 34},
    {"timestamp": "10:01", "truck_id": "T2", "temperature": 35},
    {"timestamp": "10:02", "truck_id": "T1", "temperature": 36},
    {"timestamp": "10:03", "truck_id": "T2", "temperature": 37},
    {"timestamp": "10:04", "truck_id": "T1", "temperature": 38},
]

# Hopping windows (size = 3, hop = 1)
window_size = 3
hop = 1

windows = defaultdict(list)

for start in range(0, len(events), hop):
    end = start + window_size
    if end <= len(events):
        window_name = f"Window {start + 1}"
        for event in events[start:end]:
            windows[window_name].append(event["temperature"])

print("===== Hopping Window Output =====")

for window, temps in windows.items():
    average = sum(temps) / len(temps)
    print(f"\n{window}")
    print(f"Temperatures: {temps}")
    print(f"Average Temperature: {average:.2f}")