from .pytype import *


class NodupRehashPool:

    def __init__(self, pool: set = None):
        self.pool = pool or set()

    def __call__(
        self,
        key: Hashable,
        hash_func: Callable[[Hashable], str] = ...,
        rehash_func: Callable[[str], str] = ...,
    ) -> str:
        key = hash_func(key)
        while key in self.pool:
            key = rehash_func(key)
        self.pool.add(key)
        return key

    def dump(self, path: StrPath):
        import json

        with Path(path).open("w") as f:
            json.dump(list(self.pool), f)
