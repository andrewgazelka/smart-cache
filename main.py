from smart_cache import smart_cache


def abc():
    x = 2+3
    return x


@smart_cache
def tester():
    return 1 + abc()


if __name__ == "__main__":
    print(tester())
