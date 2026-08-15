from week2.Day1.tumbling_window import tumbling_window
from week2.Day2.hopping_window import hopping_window
from week2.Day3.sliding_window import sliding_window


def main():
    data = [1, 2, 3, 4, 5]

    print("===== Final Windowing Validation =====")

    tumbling_result = tumbling_window(data, 2)
    print("Tumbling Window:", tumbling_result)

    hopping_result = hopping_window(data, 3, 2)
    print("Hopping Window:", hopping_result)

    sliding_result = sliding_window(data, 3)
    print("Sliding Window:", sliding_result)

    assert tumbling_result == [[1, 2], [3, 4], [5]]
    assert hopping_result == [[1, 2, 3], [3, 4, 5]]
    assert sliding_result == [[1, 2, 3], [2, 3, 4], [3, 4, 5]]

    print("\nAll final validation checks PASSED!")


if __name__ == "__main__":
    main()