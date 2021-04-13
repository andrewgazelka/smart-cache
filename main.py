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
    cache = {}

    def wrapper(*args, **kwargs):
        frozen_set = frozenset(kwargs.items())
        hash_input = hash((*args, *frozen_set))
        if hash_input in cache:
            return cache[hash_input]
        result = input_func(*args, **kwargs)
        cache[hash_input] = result
        return result

    return wrapper


@smart_cache
def function_to_cache(a):
    return a


if __name__ == "__main__":
    function_to_cache(1)
    function_to_cache(1)
