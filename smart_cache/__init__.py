"""A library to cache pure funcions"""
import dis
import hashlib
import inspect
import pickle

from queue import Empty, Queue

import threading
from os import path
from threading import Thread
from dataclasses import dataclass, field


@dataclass
class CacheData:
    """Used to cache data"""

    cache_file_name: str
    deep_hash: str | None = None
    loaded: bool = False

    """Maps from {argument hash} -> value"""
    cache_map: dict = field(default_factory=dict)


# a queue of data that needs to be cached and written to disk
to_cache_queue = Queue(maxsize=100)


def worker():
    """A worker thread which sends and caches all data produced"""
    while threading.main_thread().is_alive():
        try:
            data: CacheData = to_cache_queue.get(
                timeout=0.1
            )  # 0.1 second. Allows for checking if the main thread is alive
            while not to_cache_queue.empty():  # so we only write the latest value
                data = to_cache_queue.get(block=False)  # get the most recent data
                to_cache_queue.task_done()

            # write a pair of (function_hash, data) to a pickle file (Python standard for storing)
            with open(data.cache_file_name, "wb") as cache_file:
                obj = (data.deep_hash, data.cache_map)
                pickle.dump(obj, file=cache_file, protocol=4)
            to_cache_queue.task_done()
        except Empty:
            continue


worker_thread = Thread(target=worker)
worker_thread.start()


def __get_instruction_hash(instructions) -> str:
    """Given a list of instructions get the hash"""
    to_hash_list = [str((ins.opcode, ins.argval)) for ins in instructions]
    to_hash_bytes = " ".join(to_hash_list).encode("utf-8")
    return hashlib.sha256(to_hash_bytes, usedforsecurity=False).hexdigest()


LOAD_GLOBAL_OPCODE = 116


def __get_referenced_function_names(instructions) -> list[str]:
    """take in a list of instructions and get the functions that current function references"""
    return [ins.argval for ins in instructions if ins.opcode == LOAD_GLOBAL_OPCODE]


def __function_deep_hash(input_func: callable) -> str:
    """
    Performs a DFS on the functions referenced by `input_func` and obtains a
    list of their instruction hashes this function then performs a second hash
    of hashes to obtain a single hash.
    """
    module = inspect.getmodule(input_func)
    closed_set = set()

    # hashes of the instruction set in every function we progress to
    instruction_hashes = []
    frontier = set()

    base_instructions = []
    try:
        base_instructions = list(dis.get_instructions(input_func))
    except TypeError:
        base_instructions = []

    instruction_hashes.append(__get_instruction_hash(base_instructions))
    child_names = __get_referenced_function_names(base_instructions)
    for name in child_names:
        frontier.add(name)

    while len(frontier) > 0:
        func_name = frontier.pop()
        closed_set.add(func_name)
        func_ref = getattr(module, func_name, None)

        instructions = []
        if func_ref is None:
            instructions = []
        else:
            try:
                instructions = dis.get_instructions(func_ref)
            except TypeError:
                instructions = []
        instruction_hashes.append(__get_instruction_hash(instructions))
        child_names = __get_referenced_function_names(instructions)
        for child_name in child_names:
            if child_name not in closed_set:
                frontier.add(child_name)

    hash_str = " ".join(instruction_hashes).encode("utf-8")
    return hashlib.sha256(hash_str, usedforsecurity=False).hexdigest()


def smart_cache(input_func: callable):
    """The annotation to create a smart cache"""

    func_name: str = input_func.__name__

    cache_data = CacheData(
        cache_file_name=f"{func_name}.pickle"
    )  # because we need a reference not a value or compile error

    def __load_cache():
        cache_data.deep_hash = __function_deep_hash(input_func)
        if path.exists(cache_data.cache_file_name):
            with open(cache_data.cache_file_name, "rb") as cache_file:
                cache_function_hash, cache_value = pickle.load(file=cache_file)
                if cache_function_hash == cache_data.deep_hash:
                    cache_data.cache_map = cache_value

        cache_data.loaded = True

    def wrapper(*args, **kwargs):
        if not cache_data.loaded:  # If this is the first time running the function
            __load_cache()

        named_input_arguments = frozenset(kwargs.items())
        argument_hash = hash((*args, *named_input_arguments))

        if argument_hash in cache_data.cache_map:
            # if we the data in the cache return it
            return cache_data.cache_map[argument_hash]

        # we do not have the data in the cache—calculate it manually.
        result = input_func(*args, **kwargs)

        cache_data.cache_map[argument_hash] = result

        # put into queue to write to cache file
        to_cache_queue.put(cache_data, block=False)
        return result

    return wrapper
