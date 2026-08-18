def calculate_average(window):
    if not window:
        return 0
    return sum(window) / len(window)


def test_window_average():
    window = [34, 35, 36]
    expected = 35.0

    result = calculate_average(window)

    return result == expected


def test_partial_window():
    window = [34, 35]
    expected = 34.5

    result = calculate_average(window)

    return result == expected


def test_empty_window():
    window = []
    expected = 0

    result = calculate_average(window)

    return result == expected


print("Running Regression Test Suite...")
print()

tests = {
    "Window Average Test": test_window_average(),
    "Partial Window Test": test_partial_window(),
    "Empty Window Test": test_empty_window()
}

all_passed = True

for test_name, result in tests.items():
    if result:
        print(f"{test_name}: PASS")
    else:
        print(f"{test_name}: FAIL")
        all_passed = False

print()

if all_passed:
    print("PASS: Regression test suite completed successfully.")
else:
    print("FAIL: Some regression tests failed.")