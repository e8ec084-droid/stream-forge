# Week 3 - Day 3: Partial Window Edge-Case Testing

## Role

R3 - Windowing & Aggregation Specialist

## Objective

Test edge cases for partial windows and verify that the rolling average handles incomplete windows correctly without causing errors.

## Implementation

* Created test cases for partial rolling windows.
* Tested a window containing only one value.
* Tested a window containing two values.
* Tested a complete window containing three values.
* Calculated the average for each window.
* Verified that partial windows are processed correctly.
* Checked that the rolling window maintains the expected size when new data is added.

## Test Result

Partial Window 1: [34]

Average: 34.0

Partial Window 2: [34, 35]

Average: 34.5

Complete Window: [34, 35, 36]

Average: 35.0

PASS: Partial window edge cases were handled correctly.

## Conclusion

The rolling window successfully handled partial windows with one or two values and calculated the averages correctly. The test confirmed that incomplete windows do not cause errors during processing.
