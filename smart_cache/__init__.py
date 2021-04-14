import dis
import hashlib
import inspect
import pickle
import queue
import threading
from os import path
from threading import Thread


class CacheData:
    calculated = False
    cache_file_name: str
    cache = {}
    deep_hash: str


# since we only care about latest
q = queue.Queue(maxsize=100)


def worker():
    while threading.main_thread().is_alive():
        try:
            data: CacheData = q.get(timeout=0.1) # 0.1 second. Allows for checking if the main thread is alive
            while not q.empty(): # so we only write the latest value
                data = q.get(block=False)
            with open(data.cache_file_name, 'wb') as cache_file:
                pickle.dump((data.deep_hash, data.cache), cache_file, protocol=4)
            q.task_done()
        except queue.Empty:
            continue


t = Thread(target=worker)
t.start()


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
        if func_ref is None:
            raise Exception("no func ref for %s" % func_name)
        instructions = dis.get_instructions(func_ref)
        instruction_hashes.append(__get_instruction_hash(instructions))
        child_names = __get_referenced_function_names(instructions)
        for child_name in child_names:
            if child_name not in closed_set:
                frontier.add(child_name)

    hash_str = ' '.join(instruction_hashes).encode('utf-8')
    return hashlib.sha256(hash_str, usedforsecurity=False).hexdigest()


# A thread that consumes data
def consumer(in_q):
    while True:
        # Get some data
        data = in_q.get()
        # Process the data


def smart_cache(input_func):
    data = CacheData()  # because we need a reference not a value or compile error

    func_name = input_func.__name__

    data.cache_file_name = func_name + '.pickle'

    def wrapper(*args, **kwargs):
        if not data.calculated:
            data.deep_hash = __function_deep_hash(input_func)
            if path.exists(data.cache_file_name):
                with open(data.cache_file_name, 'rb') as cache_file:
                    cache_hash, cache_temp = pickle.load(cache_file)
                    if cache_hash == data.deep_hash:
                        data.cache = cache_temp

            data.calculated = True
        frozen_set = frozenset(kwargs.items())
        hash_input = hash((*args, *frozen_set))
        if hash_input in data.cache:
            return data.cache[hash_input]
        result = input_func(*args, **kwargs)
        data.cache[hash_input] = result
        q.put(data, block=False)
        return result

    return wrapper
