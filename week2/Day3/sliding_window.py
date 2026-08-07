# Sliding Window Example

temperatures = [34, 35, 36, 37, 38]
window_size = 3

print("===== Sliding Window Output =====")

for i in range(len(temperatures) - window_size + 1):
    window = temperatures[i:i + window_size]
    average = sum(window) / window_size

    print(f"\nWindow {i + 1}")
    print(f"Temperatures: {window}")
    print(f"Average Temperature: {average:.2f}")