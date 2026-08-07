def sliding_window(data, size):
    for i in range(len(data) - size + 1):
        yield data[i:i + size]


def process_stream(data):
    print("Streaming Started...\n")

    for index, window in enumerate(sliding_window(data, 3), start=1):
        average = sum(window) / len(window)

        print(f"Window {index}")
        print("Temperatures:", window)
        print(f"Average Temperature: {average:.2f}")
        print()


temperature_stream = [34, 35, 36, 37, 38]

process_stream(temperature_stream)