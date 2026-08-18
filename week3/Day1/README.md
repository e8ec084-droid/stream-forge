# Week 3 - Day 1: State Recovery

## Role
R3 - Windowing & Aggregation Specialist

## Objective
Implement state recovery for a streaming window so that the
window state can be restored after an application restart.

## Implementation
- Saved the current window state.
- Simulated an application restart.
- Recovered the saved window state.
- Recalculated the average temperature.
- Verified that the recovered state matches the original state.

## Test Result

Recovered Window: [34, 35, 36]

Recovered Average: 35.0

PASS: Window state survived restart.

## Conclusion
The window state was successfully saved and recovered after
a simulated application restart without losing the data.