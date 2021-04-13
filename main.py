import dis
import hashlib
import pickle
from os import path


def get_instruction_hash(instructions):
    to_hash = [str((ins.opcode, ins.argval)) for ins in instructions]
    hash_str = ' '.join(to_hash).encode('utf-8')
    res = hashlib.sha256(hash_str, usedforsecurity=False).hexdigest()
    return res


def get_function_hash(f):
    return get_instruction_hash(dis.get_instructions(f))


def get_referenced_function_names(instructions) -> list[str]:
    return [ins.argval for ins in instructions if ins.opname == 'LOAD_GLOBAL']


def function_deep_hash(input_func):
    closed_set = set()
    instruction_hashes = []
    frontier = set()

    base_instructions = dis.get_instructions(input_func)
    instruction_hashes.append(get_instruction_hash(base_instructions))
    child_names = get_referenced_function_names(base_instructions)
    for name in child_names:
        frontier.add(name)

    while len(frontier) > 0:
        func_name = frontier.pop()
        closed_set.add(func_name)
        func_ref = globals()[func_name]
        instructions = dis.get_instructions(func_ref)
        instruction_hashes.append(get_instruction_hash(instructions))
        child_names = get_referenced_function_names(instructions)
        for child_name in child_names:
            if child_name not in closed_set:
                frontier.add(child_name)

    hash_str = ' '.join(instruction_hashes).encode('utf-8')
    return hashlib.sha256(hash_str, usedforsecurity=False).hexdigest()


def smart_cache(input_func):
    deep_hash = function_deep_hash(input_func)
    func_name = input_func.__name__
    cache_file_name = func_name + '.pickle'
    cache = {}

    if path.exists(cache_file_name):
        with open(cache_file_name, 'rb') as cache_file:
            cache_hash, cache_temp = pickle.load(cache_file)
            if cache_hash == deep_hash:
                cache = cache_temp

    def wrapper(*args, **kwargs):
        frozen_set = frozenset(kwargs.items())
        hash_input = hash((*args, *frozen_set))
        if hash_input in cache:
            print("cached")
            return cache[hash_input]
        result = input_func(*args, **kwargs)
        cache[hash_input] = result

        with open(cache_file_name, 'wb') as cache_file:
            pickle.dump((deep_hash, cache), cache_file, protocol=4)

        return result

    return wrapper


@smart_cache
def function_to_cache(a):
    return a + 2


if __name__ == "__main__":
    function_to_cache(1)
    # function_to_cache(1)
