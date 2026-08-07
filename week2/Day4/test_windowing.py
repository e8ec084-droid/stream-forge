def test_tumbling():
    data = [10, 20, 30, 40]
    expected = [[10, 20], [30, 40]]

    result = [data[i:i+2] for i in range(0, len(data), 2)]

    assert result == expected
    print("Tumbling Window Test Passed")


def test_hopping():
    data = [1, 2, 3, 4, 5]
    expected = [[1, 2, 3], [3, 4, 5]]

    result = [data[i:i+3] for i in range(0, len(data)-2, 2)]

    assert result == expected
    print("Hopping Window Test Passed")


def test_sliding():
    data = [34, 35, 36, 37, 38]
    expected = [[34, 35, 36], [35, 36, 37], [36, 37, 38]]

    result = [data[i:i+3] for i in range(len(data)-2)]

    assert result == expected
    print("Sliding Window Test Passed")


test_tumbling()
test_hopping()
test_sliding()