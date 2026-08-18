import pytest

from week2.Day1.tumbling_window import tumbling_window
from week2.Day2.hopping_window import hopping_window
from week2.Day3.sliding_window import sliding_window


def test_tumbling_window():
    data = [1, 2, 3, 4, 5, 6]

    result = tumbling_window(data, 2)

    assert result == [[1, 2], [3, 4], [5, 6]]


def test_hopping_window():
    data = [1, 2, 3, 4, 5]

    result = hopping_window(data, 3, 2)

    assert result == [[1, 2, 3], [3, 4, 5]]


def test_sliding_window():
    data = [1, 2, 3, 4, 5]

    result = sliding_window(data, 3)

    assert result == [[1, 2, 3], [2, 3, 4], [3, 4, 5]]


def test_empty_input():
    assert tumbling_window([], 2) == []
    assert hopping_window([], 3, 2) == []
    assert sliding_window([], 3) == []


def test_invalid_window_size():
    with pytest.raises(ValueError):
        tumbling_window([1, 2, 3], 0)

    with pytest.raises(ValueError):
        hopping_window([1, 2, 3], 0, 1)

    with pytest.raises(ValueError):
        sliding_window([1, 2, 3], 0)