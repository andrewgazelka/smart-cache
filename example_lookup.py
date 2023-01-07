"""Examples"""
import time

from smart_cache import smart_cache


@smart_cache
def lookup(elem: str):
    print(f"uncached {elem}")
    return elem


if __name__ == "__main__":
    lookup("abc")
    lookup("abc asdbakls hlkajsdhalsd hlasjhdjklsa hdjaskhdkls")
