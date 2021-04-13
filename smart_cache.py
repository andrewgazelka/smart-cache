import dis
import hashlib
import inspect
import pickle
import sys
from os import path


def __get_instruction_hash(instructions):
    to_hash = [str((ins.opcode, ins.argval)) for ins in instructions]
    hash_str = ' '.join(to_hash).encode('utf-8')
    res = hashlib.sha256(hash_str, usedforsecurity=False).hexdigest()
    return res


def __get_function_hash(f):
    return __get_instruction_hash(dis.get_instructions(f))


def __get_referenced_function_names(instructions) -> list[str]:
    return [ins.argval for ins in instructions if ins.opcode == 116]


def __function_deep_hash(input_func):
    module = inspect.getmodule(input_func)
    closed_set = set()
    instruction_hashes = []
    frontier = set()

    base_instructions = list(dis.get_instructions(input_func))
    instruction_hashes.append(__get_instruction_hash(base_instructions))
    child_names = __get_referenced_function_names(base_instructions)
    for name in child_names:
        frontier.add(name)

    while len(frontier) > 0:
        func_name = frontier.pop()
        closed_set.add(func_name)
        func_ref = getattr(module, func_name, None)
        instructions = dis.get_instructions(func_ref)
        instruction_hashes.append(__get_instruction_hash(instructions))
        child_names = __get_referenced_function_names(instructions)
        for child_name in child_names:
            if child_name not in closed_set:
                frontier.add(child_name)

    hash_str = ' '.join(instruction_hashes).encode('utf-8')
    return hashlib.sha256(hash_str, usedforsecurity=False).hexdigest()


def smart_cache(input_func):
    deep_hash = __function_deep_hash(input_func)
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
            return cache[hash_input]
        result = input_func(*args, **kwargs)
        cache[hash_input] = result

        with open(cache_file_name, 'wb') as cache_file:
            pickle.dump((deep_hash, cache), cache_file, protocol=4)

        return result

    return wrapper
