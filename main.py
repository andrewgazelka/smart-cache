import pickle
from os import path


# def get_instruction_hash(instructions):
#     to_hash = [str((ins.opcode, ins.argval)) for ins in instructions]
#     hash_str = ' '.join(to_hash).encode('utf-8')
#     res = hashlib.sha256(hash_str, usedforsecurity=False).hexdigest()
#     return res
#
#
# def get_function_hash(f):
#     return get_instruction_hash(dis.get_instructions(f))
#
#
# def get_referenced_function_names(instructions) -> list[str]:
#     return [ins.argval for ins in instructions if ins.opname == 'LOAD_GLOBAL']
#

def smart_cache(input_func):
    func_name = input_func.__name__
    cache_file_name = func_name + '.pickle'
    cache = {}

    if path.exists(cache_file_name):
        with open(cache_file_name, 'rb') as cache_file:
            cache = pickle.load(cache_file)


    def wrapper(*args, **kwargs):
        frozen_set = frozenset(kwargs.items())
        hash_input = hash((*args, *frozen_set))
        if hash_input in cache:
            print("cached")
            return cache[hash_input]
        result = input_func(*args, **kwargs)
        cache[hash_input] = result

        with open(cache_file_name, 'wb') as cache_file:
            pickle.dump(cache, cache_file, protocol=4)

        return result

    return wrapper


@smart_cache
def function_to_cache(a):
    return a


if __name__ == "__main__":
    function_to_cache(1)
    # function_to_cache(1)
