# Week 4 - Day 2: Exactly-Once Semantics Check

## Role
R3 - Windowing & Aggregation Specialist

## Objective
Verify exactly-once processing so that duplicate streaming events are not processed more than once.

## Implementation
- Assigned a unique ID to each event.
- Stored processed event IDs in a set.
- Checked whether an event was already processed.
- Skipped duplicate events.
- Verified the final set of processed events.

## Test Result

Event event-001 was processed once.

Duplicate event-001 was skipped.

Event event-002 was processed once.

Event event-003 was processed once.

PASS: Duplicate events were prevented.

## Conclusion
Exactly-once semantics were successfully verified by preventing duplicate event processing.