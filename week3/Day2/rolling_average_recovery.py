import json

STATE_FILE = "rolling_window_state.json"
WINDOW_SIZE = 3


def calculate_average(window):
    return sum(window) / len(window)


def save_state(window):
    with open(STATE_FILE, "w") as file:
        json.dump(window, file)


def load_state():
    with open(STATE_FILE, "r") as file:
        return json.load(file)


# Initial rolling window
window = [34, 35, 36]

print("Initial Window:", window)
print("Initial Average:", calculate_average(window))

# Save state before restart
save_state(window)

print("\n--- Simulating application restart ---")

# Recover state
recovered_window = load_state()

print("Recovered Window:", recovered_window)
print("Recovered Average:", calculate_average(recovered_window))

# Add new value after recovery
new_value = 37
recovered_window.append(new_value)

# Maintain rolling window size
if len(recovered_window) > WINDOW_SIZE:
    recovered_window.pop(0)

updated_average = calculate_average(recovered_window)

print("New Value Added:", new_value)
print("Updated Window:", recovered_window)
print("Updated Average:", updated_average)

# Validation
expected_window = [35, 36, 37]
expected_average = 36.0

if (
    recovered_window == expected_window
    and updated_average == expected_average
):
    print("\nPASS: Rolling average continued correctly after recovery.")
else:
    print("\nFAIL: Rolling average continuity check failed.")