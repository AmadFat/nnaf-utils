from nnaf_utils.encoding import NodupRehashPool
from alive_progress import alive_bar


if __name__ == "__main__":
    from xxhash import xxh128_hexdigest as hash64
    from os import urandom

    pool = NodupRehashPool()

    hash_func = lambda x: hash64(bytes(x, encoding="utf-8"))
    rehash_func = lambda x: hash64(bytes(x, encoding="utf-8") + urandom(32))

    with alive_bar(int(1 << 20), title="Generating keys") as bar:
        for _ in range(int(1 << 20)):
            key = pool(
                key = str(_),
                hash_func = hash_func,
                rehash_func = rehash_func,
            )
            bar()

    pool.dump("./pool.json")
