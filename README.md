# Smart Cache

[![PyPI pyversions](https://img.shields.io/pypi/pyversions/smart-cache.svg)](https://pypi.python.org/pypi/smart-cache/)
[![PyPI version shields.io](https://img.shields.io/pypi/v/smart-cache.svg)](https://pypi.python.org/pypi/smart-cache/)
![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)

<sub><sup>This is not production ready! There are still likely many bugs and there are several performance improvements which can be made</sup></sub>

There are several Python caching alternatives, but there is only one to rule them all 💍.

Introducing smart cache—apply the `@smart_cache` decorator and all inputs
with the same hash will be cached cross-run. Furthermore,
**the cache will be invalidated if the method bytecode OR the bytecode of method dependencies changes**. This allows for fast rapid prototyping. You do not have to focus on which
functions have been changed, _Smart Cache_ does the work for you.

The only thing to pay attention to is that your functions are *pure*! This <sub><sup>basically</sub></sup> means that the same arguments will always yield the same result.  If this isn't the case, then don't include the `@smart_cache` decorator on that function—the function can't be cached!

## Installation

```bash
pip3 install smart-cache
```

## Benchmarks
Let's benchmark the times between cached and non-cached versions of recursive fibonacci.
```python
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
```

The first run (without any previous caching) we get times of
```
total time cached: 0.58ms
total time uncached: 31840.58ms
difference:  0
```

The second time will be even faster—we only need one lookup since `fib(40)` is cached. We get
```
total time cached: 0.48ms
total time uncached: 31723.69ms
difference:  0
```

## Simple Example
Suppose we run
```python
def abc():
    x = 2+2
    return x


@smart_cache
def tester():
    return 1 + abc()


if __name__ == "__main__":
    print(tester())
```

Only the first time we run this will
results not be cached.

Suppose we make a modification to `abc`

```python
def abc():
    x = 2+3
    return x
```

All caches will be invalidated. However, if `abc` were
changed to

```python
def abc():
    # this is a comment
    x = 2+2
    return x
```

The cache will not be invalidated because even though the 
code changes—none of the byte code changes.

Similary if we add another function `xyz()`,

```python

def xyz(a_param):
    return a_param*2
```

The cache will _also_ NOT be invalidated because although
the bytecode of the file changes, the bytecode of neither the function `tester`
or its dependencies change.

## Recursive Functions
Recursive functions also work as expected!
```python
@smart_cache
def fib(n):
    if n == 0:
        return 0
    if n == 1:
        return 1
    return fib(n - 1) + fib(n - 2)


if __name__ == "__main__":
    print(fib(6))
```

will run in `O(n)` time when it is first run
and `O(1)` the time after that.
