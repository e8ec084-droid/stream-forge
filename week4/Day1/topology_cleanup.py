# Week 4 - Day 1
# R3 - Windowing & Aggregation Specialist
# Topology Code Cleanup

def calculate_window_average(window):
    """Calculate the average value of a streaming window."""
    if not window:
        return 0.0

    return sum(window) / len(window)


def validate_window(window, window_size):
    """Validate that the window contains the expected number of values."""
    return len(window) == window_size


def process_window(window, window_size):
    """Validate and calculate the average for a streaming window."""
    if not validate_window(window, window_size):
        print("WARNING: Window size is not correct.")
        return None

    average = calculate_window_average(window)

    print("Window:", window)
    print("Window Size:", len(window))
    print("Average:", average)

    return average


# Test data
window = [34, 35, 36]
window_size = 3

print("=== Week 4 Day 1: Topology Code Cleanup ===")

result = process_window(window, window_size)

if result is not None:
    print("PASS: Cleaned window processing completed successfully.")
else:
    print("FAIL: Window processing failed.")