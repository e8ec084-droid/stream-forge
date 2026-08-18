# Week 4 - Day 2
# R3 - Windowing & Aggregation Specialist
# Exactly-Once Semantics Check

processed_events = set()


def process_event(event_id, value):
    """Process an event only once using its unique event ID."""

    if event_id in processed_events:
        print(f"SKIPPED: Duplicate event {event_id}")
        return False

    processed_events.add(event_id)
    print(f"PROCESSED: Event {event_id} -> {value}")
    return True


print("=== Week 4 Day 2: Exactly-Once Semantics Check ===")

process_event("event-001", 34)
process_event("event-002", 35)
process_event("event-001", 34)
process_event("event-003", 36)

print("\nProcessed Events:", sorted(processed_events))

if len(processed_events) == 3:
    print("PASS: Duplicate events were prevented.")
else:
    print("FAIL: Duplicate event processing detected.")