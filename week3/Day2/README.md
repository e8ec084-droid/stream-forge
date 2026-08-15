# Week 3 - Day 2: Rolling Average Continuity After Recovery

## Role

R3 - Windowing & Aggregation Specialist

## Objective

Test rolling-average continuity after state recovery and verify that the rolling average continues correctly after an application restart.

## Implementation

* Created a rolling window with temperature values.
* Calculated the initial rolling average.
* Saved the current window state before restart.
* Simulated an application restart.
* Recovered the saved rolling window state.
* Added a new temperature value after recovery.
* Maintained the fixed window size.
* Recalculated the rolling average.
* Verified that the rolling average continued correctly after recovery.

## Test Result

Initial Window: [34, 35, 36]

Initial Average: 35.0

Recovered Window: [34, 35, 36]

Recovered Average: 35.0

Updated Window: [35, 36, 37]

Updated Average: 36.0

PASS: Rolling average continued correctly after recovery.

## Conclusion

The rolling window state was successfully recovered after the simulated application restart, and the rolling average continued correctly with the new data.
