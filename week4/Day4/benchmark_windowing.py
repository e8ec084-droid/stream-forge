import time

from week2.Day1.tumbling_window import tumbling_window
from week2.Day2.hopping_window import hopping_window
from week2.Day3.sliding_window import sliding_window


data = list(range(10000))


def benchmark(function, *args):
    start_time = time.perf_counter()

    function(*args)

    end_time = time.perf_counter()

    return end_time - start_time


print("===== Windowing Performance Test =====")

tumbling_time = benchmark(tumbling_window, data, 100)
print(f"Tumbling Window Time: {tumbling_time:.6f} seconds")

hopping_time = benchmark(hopping_window, data, 100, 50)
print(f"Hopping Window Time: {hopping_time:.6f} seconds")

sliding_time = benchmark(sliding_window, data, 100)
print(f"Sliding Window Time: {sliding_time:.6f} seconds")