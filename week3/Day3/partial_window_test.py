WINDOW_SIZE = 3


def calculate_average(window):
    return sum(window) / len(window)


def test_partial_windows():
    # Partial window with one value
    window_1 = [34]
    average_1 = calculate_average(window_1)

    print("Partial Window 1:", window_1)
    print("Average:", average_1)

    # Partial window with two values
    window_2 = [34, 35]
    average_2 = calculate_average(window_2)

    print("\nPartial Window 2:", window_2)
    print("Average:", average_2)

    # Complete window
    window_3 = [34, 35, 36]
    average_3 = calculate_average(window_3)

    print("\nComplete Window:", window_3)
    print("Average:", average_3)

    # Validation
    if average_1 == 34.0 and average_2 == 34.5 and average_3 == 35.0:
        print("\nPASS: Partial window edge cases were handled correctly.")
    else:
        print("\nFAIL: Partial window test failed.")


test_partial_windows()