import time

from smart_cache import smart_cache


@smart_cache
def fib(n):
    if n == 0:
        return 0
    if n == 1:
        return 1
    return fib(n - 1) + fib(n - 2)


def bad_fib(n):
    if n == 0:
        return 0
    if n == 1:
        return 1
    return bad_fib(n - 1) + bad_fib(n - 2)


if __name__ == "__main__":
    start = time.time()
    cached_result = fib(40)
    end = time.time()

    print("total time cached: {:.2f}ms".format((end - start) * 1000))

    start = time.time()
    actual_result = bad_fib(40)
    end = time.time()
    print("total time uncached: {:.2f}ms".format((end - start) * 1000))

    difference = actual_result - cached_result
    print("difference: ", difference)
