from .pytype import *


class NodupRehashPool:
    def __init__(
        self,
        pool: set = None,
        hash_func: Callable[[Hashable], str] = None,
        rehash_func: Callable[[str], str] = None,
    ):
        self.pool = pool or set()
        self.hash_func = hash_func
        self.rehash_func = rehash_func

    def __call__(
        self,
        key: Hashable,
        hash_func: Callable[[Hashable], str] = None,
        rehash_func: Callable[[str], str] = None,
    ) -> str:
        hash_func = self.hash_func or hash_func
        rehash_func = self.rehash_func or rehash_func
        key = hash_func(key)
        while key in self.pool:
            key = rehash_func(key)
        self.pool.add(key)
        return key

    def dump(self, path: StrPath):
        import json

        with Path(path).open("w") as f:
            json.dump(list(self.pool), f)
