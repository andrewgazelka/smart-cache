# Smart Cache
<sub><sup>This is not production ready! There are still likely many bugs and there are several performance improvements which can be made</sup></sub>

There are several Python caching alternatives, but there is only one to rule them all 💍.

Introducing smart cache—apply the `@smart_cache` decorator and all inputs
with the same hash will be cached cross-run. Furthermore,
**the cache will be invalidated if the method bytecode OR the bytecode of method dependencies changes**. This allows for fast rapid prototyping. You do not have to focus on which
functions have been changed, _Smart Cache_ does the work for you.

The only thing to pay attention to is that your functions are *pure*! If they have 
side effects, smart cache will not work.

## Benchmarks
Running the `fib` (cached) and `bad_fib` in `example/example.py` we get after one run. Cached is `O(1)`.

```
total time cached: 0.48ms
total time uncached: 31723.69ms
difference:  0
```

The first run we get 
```
total time cached: 0.58ms
total time uncached: 31840.58ms
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
