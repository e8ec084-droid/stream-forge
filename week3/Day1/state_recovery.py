import json
import os

STATE_FILE = "window_state.json"


def save_state(window_data):
    state = {
        "window": window_data,
        "average": sum(window_data) / len(window_data)
    }

    with open(STATE_FILE, "w") as file:
        json.dump(state, file)

    print("Window state saved successfully.")


def load_state():
    if not os.path.exists(STATE_FILE):
        print("No previous state found.")
        return None

    with open(STATE_FILE, "r") as file:
        state = json.load(file)

    print("Window state recovered successfully.")
    return state


window = [34, 35, 36]

save_state(window)

print("\n--- Simulating application restart ---\n")

recovered_state = load_state()

if recovered_state:
    print("Recovered Window:", recovered_state["window"])
    print("Recovered Average:", recovered_state["average"])

    if recovered_state["window"] == window:
        print("PASS: Window state survived restart.")
    else:
        print("FAIL: Window state changed after restart.")