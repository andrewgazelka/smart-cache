"""Examples"""
import time

from smart_cache import smart_cache


@smart_cache
def fib(n: int):
    """Recursive fibonacci sequence (cached)"""

    print(f"uncached fib {n}")
    if n == 0:
        return 0
    if n == 1:
        return 1
    return fib(n - 1) + fib(n - 2)


def bad_fib(n: int):
    """Recursive fibonacci sequence (not cached)"""
    if n == 0:
        return 0
    if n == 1:
        return 1
    return bad_fib(n - 1) + bad_fib(n - 2)


if __name__ == "__main__":
    start = time.time()
    cached_result = fib(40)
    end = time.time()

    d_time = (end - start) * 1000
    print(f"total time cached: {d_time:.2f}ms")

    start = time.time()
    actual_result = bad_fib(40)
    end = time.time()

    d_time = (end - start) * 1000
    print(f"total time uncached: {d_time:.2f}ms")

    difference = actual_result - cached_result
    print("difference: ", difference)
