from smart_cache import smart_cache


@smart_cache
def fib(n):
    if n == 0:
        return 0
    if n == 1:
        return 1
    return fib(n - 1) + fib(n - 2)


if __name__ == "__main__":
    print(fib(6))
